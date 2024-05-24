import express from "express";
import bodyParser from "body-parser";
import axios from "axios";
import cors from "cors";
import helmet from "helmet";
import { onRequest } from "firebase-functions/v2/https";

const app = express();

app.use(bodyParser.json());
app.use(cors());
app.use(helmet());

// Utility function to find the first toggle list with a specific name
async function findToggleListWithName(notion, blockId, name) {
  const response = await notion.get(`blocks/${blockId}/children`);
  for (const block of response.data.results) {
    if (
      block.type === "toggle" &&
      block.toggle.rich_text[0].plain_text === name
    ) {
      return block.id;
    }
    if (block.has_children) {
      const childToggleId = await findToggleListWithName(
        notion,
        block.id,
        name,
      );
      if (childToggleId) return childToggleId;
    }
  }
  return null;
}

// Endpoint to add a single note to a specific toggle list
app.post("/add-to-toggle", async (req, res) => {
  const { toggleName, content } = req.body;
  const notionApiKey = req.header("notionApiKey");
  const notionPageId = req.header("notionPageId");

  if (typeof content !== "string") {
    return res.status(400).send("Content must be a string");
  }

  if (!notionApiKey || !notionPageId) {
    return res.status(400).send("Missing Notion API Key or Page ID");
  }

  const notion = axios.create({
    baseURL: "https://api.notion.com/v1/",
    headers: {
      Authorization: `Bearer ${notionApiKey}`,
      "Notion-Version": "2022-06-28",
      "Content-Type": "application/json",
    },
  });

  try {
    const toggleListId = await findToggleListWithName(
      notion,
      notionPageId,
      toggleName,
    );

    if (!toggleListId) {
      return res
        .status(404)
        .send(`Toggle list with name "${toggleName}" not found`);
    }

    await notion.patch(`blocks/${toggleListId}/children`, {
      children: [
        {
          object: "block",
          type: "numbered_list_item",
          numbered_list_item: {
            rich_text: [
              {
                type: "text",
                text: {
                  content: content,
                },
              },
            ],
          },
        },
      ],
    });

    res.status(200).send(`Content added to toggle list "${toggleName}"`);
  } catch (error) {
    console.error(
      "Error:",
      error.response ? error.response.data : error.message,
    );
    res.status(500).send("Error adding content to toggle list");
  }
});

// Export the Express app as a Firebase function
export const api = onRequest(app);

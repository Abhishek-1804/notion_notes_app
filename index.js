import express from "express";
import bodyParser from "body-parser";
import axios from "axios";
import cors from "cors";
import helmet from "helmet";

const app = express();

app.use(bodyParser.json());
app.use(cors());
app.use(helmet());

// Utility function to find the first toggle list with a specific name
async function findToggleListWithName(notion, blockId, name) {
  try {
    const response = await notion.get(`blocks/${blockId}/children`);
    for (const block of response.data.results) {
      if (
        block.type === "toggle" &&
        block.toggle.rich_text[0].plain_text === name
      ) {
        return block.id;
      }
      if (block.has_children) {
        const childToggleId = await findToggleListWithName(notion, block.id, name);
        if (childToggleId) return childToggleId;
      }
    }
    return null;
  } catch (error) {
    console.error("Error in findToggleListWithName:", error.message);
    throw error;
  }
}

// Function to process notes sequentially
async function processNotesSequentially(notionApiKey, notionPageId, toggleName, contentArray) {
  const notion = axios.create({
    baseURL: "https://api.notion.com/v1/",
    headers: {
      Authorization: `Bearer ${notionApiKey}`,
      "Notion-Version": "2022-06-28",
      "Content-Type": "application/json",
    },
  });

  // Add Axios interceptors for debugging
  notion.interceptors.request.use((request) => {
    console.log("Starting Request:", request);
    return request;
  });

  notion.interceptors.response.use(
    (response) => response,
    (error) => {
      console.error("Axios Error:", error.response ? error.response.data : error.message);
      return Promise.reject(error);
    }
  );

  try {
    const toggleListId = await findToggleListWithName(notion, notionPageId, toggleName);
    if (!toggleListId) {
      throw new Error(`Toggle list with name "${toggleName}" not found`);
    }

    for (const content of contentArray) {
      if (content) {
        try {
          await notion.patch(`blocks/${toggleListId}/children`, {
            children: [
              {
                object: "block",
                type: "numbered_list_item",
                numbered_list_item: {
                  rich_text: [
                    {
                      type: "text",
                      text: { content: content },
                    },
                  ],
                },
              },
            ],
          });
        } catch (error) {
          console.error("Error adding content to Notion:", error.message);
        }
      }
    }
  } catch (error) {
    console.error("Error in processNotesSequentially:", error.message);
    throw error;
  }
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

  const contentArray = content
    .split(".")
    .map((item) => item.trim())
    .filter((item) => item.length > 0);

  // Respond to the client quickly
  res.status(200).send("Notes are being processed in the background");

  try {
    await processNotesSequentially(notionApiKey, notionPageId, toggleName, contentArray);
  } catch (error) {
    console.error("Unhandled error in /add-to-toggle endpoint:", error.message);
  }
});

// Start the Express server
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});

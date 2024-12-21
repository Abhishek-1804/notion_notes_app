import logging
import os
from functools import wraps
from threading import Thread
from typing import List, Optional, Dict

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)


class NotionClient:
    def __init__(self, api_key: str):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            }
        )

    def find_toggle_list_with_name(self, block_id: str, name: str) -> Optional[str]:
        """Find the first toggle list with a specific name."""
        try:
            response = self.session.get(
                f"https://api.notion.com/v1/blocks/{block_id}/children"
            )
            response.raise_for_status()
            for block in response.json()["results"]:
                if (
                    block["type"] == "toggle"
                    and block["toggle"]["rich_text"][0]["plain_text"] == name
                ):
                    return block["id"]
                if block.get("has_children"):
                    child_toggle_id = self.find_toggle_list_with_name(block["id"], name)
                    if child_toggle_id:
                        return child_toggle_id
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Notion API error in find_toggle_list: {str(e)}")
            raise

    def add_content_to_toggle(self, toggle_id: str, content: str) -> None:
        """Add content to a toggle list."""
        try:
            payload = {
                "children": [
                    {
                        "object": "block",
                        "type": "numbered_list_item",
                        "numbered_list_item": {
                            "rich_text": [
                                {"type": "text", "text": {"content": content}}
                            ]
                        },
                    }
                ]
            }
            response = self.session.patch(
                f"https://api.notion.com/v1/blocks/{toggle_id}/children", json=payload
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error adding content to Notion: {str(e)}")
            raise


def require_api_keys(f):
    """Decorator to validate required API keys."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"All headers received: {dict(request.headers)}")
        notion_api_key = request.headers.get("NOTION-API-KEY")

        if not notion_api_key:
            return jsonify(
                {
                    "error": "Missing API key in headers",
                    "details": "NOTION-API-KEY",
                }
            ), 400

        return f(*args, **kwargs)

    return decorated_function


def call_gpt(content: str, toggle_lists: List[str]) -> str:
    """Call GPT to determine the appropriate toggle list."""
    try:
        # Construct a dynamic list string for the prompt
        toggle_list_str = ", ".join(f"'{t}'" for t in toggle_lists)
        prompt = (
            f"You are a classifier that categorizes notes into specific lists. "
            f"Given the following note, classify it into exactly one of these categories: {toggle_list_str}. "
            f"Note to classify: '{content}'\n\n"
            "Respond with ONLY the category name, nothing else. "
            "If unsure, choose the first category."
        )

        logger.info(f"Sending to GPT: {content}")

        # Make the GPT request
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a categorization assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=10,
            temperature=0.3,
        )

        # Extract the response
        result = completion.choices[0].message.content
        logger.info(f"GPT response for '{content}': {result}")

        # Validate the response
        if result not in toggle_lists:
            logger.warning(
                f"Unexpected GPT response: {result}. Defaulting to first item in the list."
            )
            return toggle_lists[0]

        return result

    except Exception as e:
        logger.error(f"Error calling GPT: {str(e)}")
        return toggle_lists[0]  # Return first toggle list as default


def process_notes_sequentially(
    notion_client: NotionClient,
    page_id: Optional[str],
    toggle_name: str,
    content_array: List[str],
    toggle_lists_and_page_id: Optional[Dict[str, str]] = None,
) -> None:
    """Process notes sequentially and add them to appropriate toggle lists."""
    try:
        if toggle_name == "Use AI":
            if not toggle_lists_and_page_id:
                raise ValueError("Toggle lists and page IDs are required for AI mode")

            for content in content_array:
                if not content:
                    continue

                # Call GPT for classification
                gpt_toggle_name = call_gpt(
                    content, list(toggle_lists_and_page_id.keys())
                )
                logger.info(f"AI suggested toggle name: {gpt_toggle_name}")

                # Determine page ID dynamically
                dynamic_page_id = toggle_lists_and_page_id.get(gpt_toggle_name)
                if not dynamic_page_id:
                    logger.error(
                        f"Page ID not found for toggle list: {gpt_toggle_name}"
                    )
                    continue

                # Find the toggle list ID
                toggle_list_id = notion_client.find_toggle_list_with_name(
                    dynamic_page_id, gpt_toggle_name
                )
                if not toggle_list_id:
                    logger.error(f"Toggle list not found: {gpt_toggle_name}")
                    continue

                # Add content to the toggle list
                notion_client.add_content_to_toggle(toggle_list_id, content)

        else:
            if not page_id:
                raise ValueError("Page ID is required for manual toggle selection")

            toggle_list_id = notion_client.find_toggle_list_with_name(
                page_id, toggle_name
            )
            if not toggle_list_id:
                raise ValueError(f"Toggle list not found: {toggle_name}")

            for content in content_array:
                if content:
                    notion_client.add_content_to_toggle(toggle_list_id, content)

    except Exception as e:
        logger.error(f"Error in process_notes_sequentially: {str(e)}")
        raise


@app.route("/add-to-toggle", methods=["POST"])
@require_api_keys
def add_to_toggle():
    """Endpoint to add notes to a toggle list."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400

        # loading data in
        toggle_name = data.get("toggleName")
        content = data.get("content")

        if not toggle_name:
            return jsonify({"error": "Toggle name is required"}), 400

        if not isinstance(content, str):
            return jsonify({"error": "Content must be a string"}), 400

        # If manual mode, we must have NOTION-PAGE-ID in the headers
        if toggle_name != "Use AI" and "NOTION-PAGE-ID" not in request.headers:
            return jsonify(
                {"error": "Missing NOTION-PAGE-ID header for manual mode"}
            ), 400

        content_array = [item.strip() for item in content.split(".") if item.strip()]
        notion_client = NotionClient(request.headers["NOTION-API-KEY"])

        # Start processing in a background thread
        if toggle_name == "Use AI":
            toggle_lists_and_page_id = data.get("toggleLists")
            Thread(
                target=process_notes_sequentially,
                args=(
                    notion_client,
                    None,  # No page_id needed for AI mode
                    toggle_name,
                    content_array,
                    toggle_lists_and_page_id,
                ),
                daemon=True,
            ).start()
        else:
            Thread(
                target=process_notes_sequentially,
                args=(
                    notion_client,
                    request.headers["NOTION-PAGE-ID"],
                    toggle_name,
                    content_array,
                    None,  # No toggle_lists needed for manual mode
                ),
                daemon=True,
            ).start()

        # Return immediate success response
        return jsonify({"message": "Request accepted"}), 200

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=False)

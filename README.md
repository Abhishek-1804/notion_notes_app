# Notion Notes API Service

## Overview
This service allows users to dynamically add notes to toggle lists within their Notion workspace by making HTTP POST requests. The primary goal of this service is to allow users to efficiently add notes under toggle lists in their Notion pages. This is particularly useful for organizing tasks, action items, and other categorized notes.

---

## How to Set It Up

### 1. Get Your Personal Notion API Key
- Log in to [Notion](https://www.notion.so).
- Navigate to **Settings & Members** > **My Connections** > **+ Develop or Manage Integrations**.
- Create a new integration and copy the generated API key.

### 2. Get Your Notion Page ID
- Open the desired Notion page in your browser.
- Copy the last part of the URL after the `/`:
  ```
  https://www.notion.so/WorkspaceName/Page-Title-1234567890abcdef1234567890abcdef
  ```
  - **Page ID**: `1234567890abcdef1234567890abcdef`

---

## Adding Notes to Notion

### Endpoint
```
http://137.184.143.113/add-to-toggle
```

### Headers
Add the following headers:
- `Content-Type: application/json`
- `notionApiKey`: Your Notion integration token.
- `notionPageId`: The Page ID where the toggle list resides.

### Request Body
Send a JSON object in the following format:
```json
{
  "toggleName": "Action Items",
  "content": "testing."
}
```
- **Note**: Numbered items will be created after each period (`.`) in the content.

## Siri Shortcuts Integration
You can use the following template to create Siri Shortcuts for this service:
[Notion API Siri Shortcut Template](https://www.icloud.com/shortcuts/e71eef26684443278daddcd153cc5662)

This allows you to easily send notes to your Notion workspace using voice commands.



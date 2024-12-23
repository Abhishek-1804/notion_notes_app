# Notion Notes API Service

## Overview

This service allows users to dynamically add notes to toggle lists within their Notion workspace by making HTTP POST requests. The primary goal of this service is to allow users to efficiently add notes under toggle lists in their Notion pages. This is particularly useful for organizing tasks, action items, and other categorized notes.

---

## VPS Configuration and Traffic Routing

### Firewall Setup

- Only the SSH port (`22`) is allowed through the VPS firewall (using UFW):

  ```bash
  sudo ufw allow OpenSSH
  sudo ufw enable
  ```

- Port 3010 is exposed via Traefik in Docker. **Note:** Ports exposed via Docker bypass the firewall rules (a known issue where Docker overwrites existing iptables). This makes it crucial to ensure Traefik securely handles incoming traffic on exposed ports.

### How Traffic is Routed

1. **Port 3010 (VPS):**
   - Incoming HTTP requests to port 3010 on the VPS are forwarded to the internal port 80 in the Traefik container.

2. **Traefik Configuration:**
   - Traefik listens for incoming requests on port 3010 and reroutes them to the appropriate service based on its routing rules.
   - Example routing configuration in Traefik for the Notion Notes service:

     ```yaml
     labels:
       # Match requests with the `/add-to-toggle` path
       - "traefik.http.routers.app.rule=PathPrefix(`/add-to-toggle`)"
       # Forward the requests to the container's internal port 3000
       - "traefik.http.services.app.loadbalancer.server.port=3000"
     ```

   - Traefik uses this setup to forward traffic to the Express server running inside the `app` container.

3. **Express Server (Container):**
   - The Express server listens on port 3000 within the container.
   - Traefik forwards matching HTTP requests to this internal port based on the routing configuration.

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
http://137.184.143.113:3010/add-to-toggle
```

### Headers

Add the following headers:

- `NOTION-API-KEY`: Your Notion integration token.

### Request Body

Users can choose between two modes:

#### **1. Manual Mode**

- Provide the `NOTION-PAGE-ID` in the headers.
- Use the following format for the request body:

  ```json
  {
    "toggleName": "Action Items",
    "content": "testing."
  }
  ```

#### **2. AI Mode**

- Do **not** provide `notionPageId` in the headers.
- Instead, include a `toggleLists` dictionary in the request body. This dictionary should map toggle list names to their respective page IDs.

- Use the following format for the request body:

  ```json
  {
    "toggleName": "Use AI",
    "content": "testing.",
    "toggleLists": {
      "Action Items": "1234567890abcdef1234567890abcdef",
      "Work": "abcdef1234567890abcdef1234567890",
      "Groceries": "7890abcdef1234567890abcdef1234"
    }
  }
  ```

---

## Siri Shortcuts Integration

You can use the following template to create Siri Shortcuts for this service:
[Notion API Siri Shortcut Template](https://www.icloud.com/shortcuts/c92d9f27d7da46ce8761c25621db95bb)

This allows you to easily send notes to your Notion workspace using voice commands.

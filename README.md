# Purpose

- This is a Node.js application designed to help you easily add notes to your Notion workspace using Siri Shortcuts. This project allows you to send notes to a specific toggle list in Notion via a simple HTTP POST request. The project is also set up to be deployed using Firebase Functions, making it accessible from anywhere.

# Features

- Add notes to a specific toggle list in Notion.
- Integrate with Siri Shortcuts for quick note-taking.
- Deploy to Firebase Functions for easy access and scalability.
- Secure API endpoints with CORS and Helmet.

# Prerequisites

- Node.js and npm installed on your machine.
- Firebase CLI installed and configured.

# Local Development

## 1. Setting Up the Project

1. Clone the Repository:
   git clone https://github.com/Abhishek-1804/notion-note-taker.git
   cd notion-note-taker

2. Install Dependencies:
   npm install

3. Add Notion API Key and Page ID to post request headers:
   NOTION_API_KEY=your_notion_api_key
   NOTION_PAGE_ID=your_notion_page_id

4. Add toggleName and content to the post request body:

```bash
   {
   "toggleName": "your_toggle_name",
   "content": "your_note_content"
   }
```

5. Run the Local Server:
   node index.js

# 2. Firebase Deployment

## Setting Up Firebase

1. Install Firebase CLI:
   npm install -g firebase-tools

2. Login to Firebase:
   firebase login

3. Initialize Firebase in Your Project:
   firebase init

   - Select Functions and any other services you want to use.
   - Choose an existing Firebase project or create a new one.
   - Follow the prompts to set up Firebase in your project directory.

4. To test locally:

- Firebase init emulators
- Firebase emulators:start

5. Deploy to Firebase:
   firebase deploy --only functions

## Explanation of functions/index.js

- Imports necessary modules.
- Sets up Express server with middleware (body-parser, cors, helmet).
- Defines a utility function to find a toggle list by name.
- Sets up an endpoint to add a note to a specific toggle list.
- Exports the Express app as a Firebase function.

# 3. Setting Up Siri Shortcuts

- Set up the shortcut as per your requirements.
- Use the HTTP POST request URL as the endpoint for the shortcut.
- Add API keys in the headers.
- Add toggleName and content in the body.

# License

This project is licensed under the MIT License. See the LICENSE file for details.

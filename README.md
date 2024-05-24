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

# Explanation of index.js

- This file sets up an express server that listens for incoming HTTP POST requests and processes them to add notes to a specific toggle list in Notion.
- Input headers include the Notion API key and the Notion Page ID.
- The body includes the name of the toggle list and the content.
- Input content is split on the period into separate lines and processed sequentially.

# Firebase

## Setup

1. Install Firebase CLI: `npm install -g firebase-tools`.
2. Login to Firebase: `firebase login`.
3. Initialize Firebase Functions: `firebase init `. Select the project and choose JavaScript.
4. Install firebase emulators: `firebase init emulators`.
5. Run the emulators for local testing: `firebase emulators:start`.
6. Modify the index.js file in the functions directory to export the API using Firebase Functions
7. Deploy to Firebase Functions: `firebase deploy --only functions`.

# Siri Shortcuts

1. Set up a Siri Shortcut as per your requirements.
2. Pass in the appropriate headers and body to the API endpoint.

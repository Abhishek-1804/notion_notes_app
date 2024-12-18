# Use a lightweight Node.js image
FROM node:16-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install npm production packages
RUN npm install --production

# Copy the application code
COPY . .

# Start the application
CMD ["node", "index.js"]

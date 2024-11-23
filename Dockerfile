FROM registry.access.redhat.com/ubi8/nodejs-16:latest

# Set the working directory inside the container
WORKDIR /app

# Copy package.json, package-lock.json and index.js
COPY package*.json ./
COPY index.js ./ 

# Install npm production packages 
RUN npm install

# Start the application
CMD ["node", "index.js"]


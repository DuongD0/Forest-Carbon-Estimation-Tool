# Use an official Node.js runtime as the base image
FROM node:20-alpine

# Set working directory inside the container
WORKDIR /app

# Copy package files first (to leverage Docker layer caching)
COPY package.json ./

# Install dependencies (including dev dependencies)
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port used by the React dev server
EXPOSE 3000

# Start the React app in development mode
CMD ["npm", "start"]
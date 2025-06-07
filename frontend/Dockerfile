# Use an official Node.js runtime as the base image
FROM node:20-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files first to leverage Docker layer caching
COPY package.json package-lock.json ./

# Install exact dependencies defined in package-lock.json (clean & reproducible)
RUN npm ci

# Copy the rest of the application source code
COPY . .

# Build the React app for production
RUN npm run build

# Install a lightweight HTTP server to serve the production build
RUN npm install -g serve

# Expose port 3000
EXPOSE 3000

# Start the app
CMD ["serve", "-s", "build", "-l", "3000"]

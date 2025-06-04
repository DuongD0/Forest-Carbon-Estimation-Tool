# Use an official Node runtime as a parent image
FROM node:20-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and yarn.lock (or package-lock.json) first
# to leverage Docker cache
COPY package.json yarn.lock* package-lock.json* ./

# Install dependencies
# Using yarn, but could be npm install or pnpm install
# Use --frozen-lockfile for yarn/pnpm or ci for npm to ensure reproducible installs
RUN yarn install --frozen-lockfile

# Copy the rest of the frontend application code into the container at /app
COPY . .

# Build the React app for production
RUN yarn build

# Install serve to run the production build
RUN npm install -g serve

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run the production build using serve
CMD ["serve", "-s", "build", "-l", "3000"]


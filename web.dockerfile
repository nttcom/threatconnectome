# Stage 1: Build the JavaScript code
FROM node:22.19.0-alpine AS build

WORKDIR /app

# Copy package.json and package-lock.json, and install dependencies
COPY package*.json ./
RUN npm ci

# Copy the rest of the application code
COPY ./ .

# Build the application
RUN npm run build

# Stage 2: Serve the static files with Nginx
FROM nginx:1.29.1-alpine

# Copy the built files from the previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]

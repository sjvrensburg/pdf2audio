FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Create public and src directories if they don't exist
RUN mkdir -p public src

EXPOSE 3000

# Start development server
CMD ["npm", "start"]
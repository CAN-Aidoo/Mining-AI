# =============================================================================
# Mining AI Frontend Dockerfile - Node.js 22 LTS
# =============================================================================
FROM node:22-alpine

WORKDIR /app

# Install dependencies first (layer cache — only re-runs when package.json changes)
COPY package.json ./
RUN npm install

# Copy application source
COPY . .

EXPOSE 3000

# Development default (override to: npm run start in production)
CMD ["npm", "run", "dev"]

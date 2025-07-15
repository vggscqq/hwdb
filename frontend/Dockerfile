# Build stage
FROM node:20-alpine AS builder
WORKDIR /app

# Enable Corepack and prepare Yarn Berry
RUN corepack enable && corepack prepare yarn@stable --activate

# Copy dependency files and Yarn configuration
COPY package.json yarn.lock .yarnrc.yml ./
COPY .yarn ./.yarn

# Install dependencies
RUN yarn install --immutable

# Copy source code
COPY . .

# Build the application
RUN yarn build

# Production stage
FROM nginx:1.25-alpine
EXPOSE 80

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost/ || exit 1
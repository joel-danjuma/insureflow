# Stage 1: Build the application
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies separately to leverage Docker layer caching
COPY package*.json ./
RUN npm install --silent

# Copy source code
COPY . .

# Build the Next.js application with error handling
RUN npm run build || (echo "Build failed, checking logs..." && cat .next/build-manifest.json 2>/dev/null || echo "No build manifest found" && exit 1)

# Stage 2: Production image
FROM node:18-alpine
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Install curl for healthchecks
RUN apk add --no-cache curl

# Copy built assets from the builder stage
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Create a non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
USER nextjs

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

# Start the Next.js application
CMD ["npm", "start"] 
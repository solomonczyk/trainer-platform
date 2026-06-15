# ---- Frontend Dockerfile ----
# Multi-stage build for Next.js frontend

# Stage 1: Dependencies
FROM node:20-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --only=production && \
    cp -R node_modules /prod_node_modules && \
    npm ci

# Stage 2: Build
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build-time public env vars — must be passed as Docker build args
# (e.g. --build-arg NEXT_PUBLIC_API_BASE_URL=https://...)
# Railway passes these automatically from service variables configured as build args.
ARG NEXT_PUBLIC_API_BASE_URL
ARG NEXT_PUBLIC_APP_ENV

# Export build args as env vars so Next.js inlines them at build time
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_APP_ENV=$NEXT_PUBLIC_APP_ENV
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Production runner
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone output from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Set proper permissions
RUN chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

CMD ["node", "server.js"]

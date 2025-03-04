FROM node:22.14.0-alpine AS base

# Build stage
FROM base AS builder

WORKDIR /app

COPY ui/package.json ui/package-lock.json ui/next.config.ts ui/postcss.config.mjs ./
RUN npm install

COPY --chown=ui ui/public ./public
COPY --chown=ui ui/app ./app

RUN npm run build

# Production stage
FROM base AS ui

WORKDIR /app
RUN adduser -S -h /app ui

COPY --from=builder /app/public ./public
COPY --from=builder --chown=ui /app/.next/standalone ./
COPY --from=builder --chown=ui /app/.next/static ./.next/static

USER ui

CMD [ "node", "server.js" ]

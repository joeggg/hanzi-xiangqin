FROM node:22.14.0-alpine AS base

FROM base AS deps

WORKDIR /app

COPY package.json package-lock.json next.config.ts postcss.config.mjs .env ./
RUN npm install

COPY --chown=ui public ./public
COPY --chown=ui app ./app

# Build stage
FROM deps AS builder

RUN npm run build

# Production stage
FROM base AS production

WORKDIR /app
RUN adduser -S -h /app ui

COPY --from=builder /app/public ./public
COPY --from=builder --chown=ui /app/.next/standalone ./
COPY --from=builder --chown=ui /app/.next/static ./.next/static
COPY --from=builder --chown=ui /app/.env ./.env

USER ui

CMD [ "node", "server.js" ]

# Development stage
FROM deps AS development

WORKDIR /app
RUN adduser -S -h /app ui

USER ui

CMD [ "npm", "run", "dev" ]

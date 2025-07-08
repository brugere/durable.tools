# frontend/Dockerfile
FROM node:15 AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
# allow post-install so SWC downloads the correct arm64-musl binary
RUN npm ci
RUN npm i -D @swc/cli @swc/core

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build    # Next.js static + server build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=development
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json .
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]   # calls "next start" (see package.json)



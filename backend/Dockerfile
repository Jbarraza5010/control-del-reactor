# syntax=docker/dockerfile:1
# Imagen del backend de Control del Reactor (multi-stage).

# ---------- 1) Dependencias de producción + cliente Prisma generado ----------
FROM node:20-bookworm-slim AS deps
WORKDIR /app
RUN apt-get update -y && apt-get install -y --no-install-recommends openssl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY prisma ./prisma
RUN npx prisma generate

# ---------- 2) Compilación de TypeScript ----------
FROM node:20-bookworm-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY tsconfig.json tsconfig.build.json ./
COPY src ./src
RUN npx tsc -p tsconfig.build.json

# ---------- 3) Imagen final ----------
FROM node:20-bookworm-slim AS runtime
ENV NODE_ENV=production
WORKDIR /app
RUN apt-get update -y && apt-get install -y --no-install-recommends openssl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package.json ./
COPY prisma ./prisma
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN sed -i 's/\r$//' docker-entrypoint.sh && chmod +x docker-entrypoint.sh \
    && chown -R node:node /app
USER node
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=3s --start-period=20s --retries=5 \
  CMD node -e "fetch('http://localhost:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
ENTRYPOINT ["./docker-entrypoint.sh"]

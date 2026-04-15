FROM node:20-slim AS deps

ENV PNPM_HOME=/pnpm \
    PATH=/pnpm:$PATH

WORKDIR /app/frontend

RUN corepack enable

COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./

RUN pnpm install --frozen-lockfile

FROM node:20-slim AS builder

ENV PNPM_HOME=/pnpm \
    PATH=/pnpm:$PATH \
    NEXT_TELEMETRY_DISABLED=1

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

WORKDIR /app/frontend

RUN corepack enable

COPY --from=deps /app/frontend/node_modules ./node_modules
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
COPY frontend/components.json ./components.json
COPY frontend/eslint.config.mjs ./eslint.config.mjs
COPY frontend/next.config.ts ./next.config.ts
COPY frontend/postcss.config.mjs ./postcss.config.mjs
COPY frontend/tsconfig.json ./tsconfig.json
COPY frontend/public ./public
COPY frontend/src ./src

RUN pnpm build

FROM node:20-slim AS runtime

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

WORKDIR /app/frontend

RUN useradd --create-home --home-dir /home/appuser --shell /usr/sbin/nologin appuser

COPY --from=builder /app/frontend/.next/standalone ./
COPY --from=builder /app/frontend/.next/static ./.next/static
COPY --from=builder /app/frontend/public ./public

USER appuser

EXPOSE 3000

CMD ["node", "server.js"]

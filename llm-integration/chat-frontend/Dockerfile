# ---- Builder ----
FROM node:18-alpine AS builder
WORKDIR /app

COPY package*.json ./
# Prefer npm ci if you have a package-lock.json; falls back to npm install
RUN npm ci || npm install

COPY . .
RUN npm run build

# ---- Nginx runtime ----
FROM nginx:stable-alpine

# Build output directory (build | dist | out)
ARG BUILD_DIR=build

# Clean default html and copy our build artifacts
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/${BUILD_DIR} /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

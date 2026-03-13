FROM node:20-alpine

WORKDIR /app

COPY package.json /app/package.json
COPY apps/web /app/apps/web
COPY packages/shared-types /app/packages/shared-types

RUN npm install

WORKDIR /app/apps/web

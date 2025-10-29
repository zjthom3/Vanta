FROM node:20-alpine

RUN apk add --no-cache bash

WORKDIR /workspace/apps/web

COPY apps/web/package*.json ./
RUN if [ -f package.json ]; then npm install --legacy-peer-deps; fi

COPY apps/web .

CMD ["bash", "/workspace/infra/docker/start-web.sh"]

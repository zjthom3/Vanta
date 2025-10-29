#!/usr/bin/env bash
set -euo pipefail

cd /workspace/apps/web
if [ -f package.json ] && [ ! -d node_modules ]; then
  npm install --legacy-peer-deps
fi

npm run dev -- --hostname 0.0.0.0 --port 3000

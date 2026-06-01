#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/ui"

NPM_BIN="${NPM_BIN:-$(command -v npm || true)}"
LOCAL_NPM_CLI="../.tools/npm/package/bin/npm-cli.js"
NODE_BIN="${NODE_BIN:-}"
if [[ -z "$NODE_BIN" && -x "$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node" ]]; then
  NODE_BIN="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
fi
if [[ -z "$NODE_BIN" ]]; then
  NODE_BIN="$(command -v node || true)"
fi
if [[ -z "$NODE_BIN" && -x "/Applications/Codex.app/Contents/Resources/node" ]]; then
  NODE_BIN="/Applications/Codex.app/Contents/Resources/node"
fi
if [[ -z "$NPM_BIN" && -f "$LOCAL_NPM_CLI" && -n "$NODE_BIN" ]]; then
  NPM_BIN="$NODE_BIN $LOCAL_NPM_CLI"
fi

if [[ -z "$NPM_BIN" ]]; then
  echo "npm is required to run the Next.js UI." >&2
  echo "Install Node.js/npm or set NPM_BIN to your npm executable." >&2
  exit 1
fi

if [[ ! -d node_modules ]]; then
  echo "ui/node_modules is missing. Install UI dependencies first." >&2
  echo "Run: cd ui && npm install" >&2
  exit 1
fi

NEXT_TEST_WASM="${NEXT_TEST_WASM:-1}" \
NEXT_TEST_WASM_DIR="${NEXT_TEST_WASM_DIR:-$(pwd)/node_modules/@next/swc-wasm-nodejs}" \
FASTAPI_BASE_URL="${FASTAPI_BASE_URL:-http://127.0.0.1:8000}" \
$NPM_BIN run dev

#!/usr/bin/env bash
set -euo pipefail

UV_BIN="${UV_BIN:-$(command -v uv || true)}"
if [[ -z "$UV_BIN" && -x "$HOME/.local/bin/uv" ]]; then
  UV_BIN="$HOME/.local/bin/uv"
fi

if [[ -z "$UV_BIN" ]]; then
  echo "uv is required. Install it from https://docs.astral.sh/uv/" >&2
  exit 1
fi

"$UV_BIN" run uvicorn app:app --host "${HOST:-127.0.0.1}" --port "${PORT:-3000}"

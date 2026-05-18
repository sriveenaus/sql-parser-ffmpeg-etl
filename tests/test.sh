#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
mkdir -p /logs/verifier 2>/dev/null || true

# Install uv if not present
apt-get update && apt-get install -y curl python3 || true

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/0.9.7/install.sh | sh
fi
[ -f "$HOME/.local/bin/env" ] && source "$HOME/.local/bin/env" || true
export PATH="$HOME/.local/bin:$PATH"

# Run tests with pinned pytest version
set +e
uvx --with pytest==8.4.1 --with pytest-json-ctrf==0.3.5 pytest -rA \
    --ctrf /logs/verifier/ctrf.json \
    "$SCRIPT_DIR/test_task.py"
RC=$?
set -e

if [ "$RC" -eq 0 ]; then
    mkdir -p /logs/verifier 2>/dev/null && echo 1 > /logs/verifier/reward.txt || \
    (mkdir -p "$SCRIPT_DIR/.verifier" && echo 1 > "$SCRIPT_DIR/.verifier/reward.txt")
else
    mkdir -p /logs/verifier 2>/dev/null && echo 0 > /logs/verifier/reward.txt || \
    (mkdir -p "$SCRIPT_DIR/.verifier" && echo 0 > "$SCRIPT_DIR/.verifier/reward.txt")
fi


#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/app}"
export APP_DIR
mkdir -p "$APP_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

if [ -d "$SCRIPT_DIR/steps" ]; then
  STEPS_DIR="$SCRIPT_DIR/steps"
elif [ -d "$PWD/steps" ]; then
  STEPS_DIR="$PWD/steps"
else
  echo "Unable to find steps directory." >&2
  exit 1
fi

bash "$STEPS_DIR/milestone_1/solution/solve1.sh"
bash "$STEPS_DIR/milestone_2/solution/solve2.sh"
bash "$STEPS_DIR/milestone_3/solution/solve2.sh"

# Create reward file to indicate successful completion
echo "ETL pipeline completed successfully" > "$APP_DIR/reward.txt"

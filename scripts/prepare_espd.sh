#!/usr/bin/env bash
# Init espd submodule and apply Pd patches (does not modify espd/boards or sdkconfig).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ESPD="${ROOT}/espd"

if [[ ! -d "${ESPD}/.git" && ! -f "${ESPD}/.git" ]]; then
  echo "espd submodule missing — run: git submodule update --init --recursive" >&2
  exit 1
fi

"${ESPD}/scripts/apply-pd-patches.sh"
echo "prepare_espd: Pd patches applied (boards via ESPD_BOARDS_DIR at build time)"

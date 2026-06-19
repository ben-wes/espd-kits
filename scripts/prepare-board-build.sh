#!/usr/bin/env bash
# Generate board plugins + Kconfig.inc before idf.py set-target (CI and local kits).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ESPD="${ROOT}/espd"
BOARDS_DIR="${ESPD_BOARDS_DIR:-${ROOT}/boards}"

if [[ ! -d "${ESPD}/.git" && ! -f "${ESPD}/.git" ]]; then
  echo "espd submodule missing — run: git submodule update --init --recursive" >&2
  exit 1
fi

export ESPD_BOARDS_DIR="${BOARDS_DIR}"
python3 "${ESPD}/scripts/gen_board_plugins.py" "${ESPD}" --boards-dir "${BOARDS_DIR}"

# set-target runs kconfgen before CMake; stale sdkconfig would hide the board choice.
rm -f "${ESPD}/sdkconfig" "${ESPD}/sdkconfig.old"

if [[ "${1:-}" == "--refresh-managed" ]] || [[ "${ESPD_REFRESH_MANAGED:-}" == "1" ]]; then
  rm -rf "${ESPD}/managed_components" "${ESPD}/dependencies.lock"
  echo "prepare-board-build: removed managed_components + dependencies.lock"
fi

echo "prepare-board-build: plugins from ${BOARDS_DIR} (sdkconfig cleared)"

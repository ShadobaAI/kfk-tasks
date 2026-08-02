#!/usr/bin/env bash

set -uo pipefail

MCP_PORT="${MEMORY_BANK_PORT:-8767}"
MCP_HOST="${MEMORY_BANK_HOST:-127.0.0.1}"
MCP_ENDPOINT="${MEMORY_BANK_ENDPOINT:-/mcp}"

SCRIPT_DIR="$(
  CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1
  pwd
)"
PROJECTS_ROOT="$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"

export KAFKA_PROJECTS_ROOT="${KAFKA_PROJECTS_ROOT:-${PROJECTS_ROOT}}"
export PYTHONPATH="${SCRIPT_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}"

status=0
# Git Bash/MSYS otherwise rewrites endpoint /mcp as a Windows filesystem path.
export MSYS2_ARG_CONV_EXCL="${MSYS2_ARG_CONV_EXCL:-*}"
"${PYTHON_BIN}" -m memory_bank_mcp.server \
  --host "${MCP_HOST}" \
  --port "${MCP_PORT}" \
  --endpoint "${MCP_ENDPOINT}" || status=$?

if ((status == 0)); then
  exit 0
fi

printf '\nMemory Bank MCP failed to start (exit code %s).\n' "${status}" >&2
printf 'Check that Python dependencies are installed and port %s is free.\n' "${MCP_PORT}" >&2

if [[ -t 0 ]]; then
  read -r -p "Press Enter to close this window..."
fi

exit "${status}"

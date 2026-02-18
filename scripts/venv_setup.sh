#!/bin/bash

############################################################################
#
#    Apollos AI Virtual Environment Setup
#
#    Usage: ./scripts/venv_setup.sh
#
############################################################################

set -e

CURR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "${CURR_DIR}")"

# Colors
ORANGE='\033[38;5;208m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${ORANGE}"
cat << 'BANNER'
     █████╗  ██████╗ ███╗   ██╗ ██████╗
    ██╔══██╗██╔════╝ ████╗  ██║██╔═══██╗
    ███████║██║  ███╗██╔██╗ ██║██║   ██║
    ██╔══██║██║   ██║██║╚██╗██║██║   ██║
    ██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝
BANNER
echo -e "${NC}"
echo -e "    ${DIM}Virtual Environment Setup${NC}"
echo ""

# Preflight
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "    Deactivate your current venv first."
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "    uv not found. Install: https://docs.astral.sh/uv/"
    exit 1
fi

# Setup: creates .venv, installs all deps + dev deps + project (editable)
echo -e "    ${DIM}> uv sync --dev${NC}"
echo ""
cd ${REPO_ROOT} && uv sync --dev

# Copy activation command to clipboard
ACTIVATE_CMD="source .venv/bin/activate"
if command -v pbcopy &> /dev/null; then
    echo -n "${ACTIVATE_CMD}" | pbcopy
    CLIPBOARD_MSG="(Copied to clipboard)"
elif command -v xclip &> /dev/null; then
    echo -n "${ACTIVATE_CMD}" | xclip -selection clipboard
    CLIPBOARD_MSG="(Copied to clipboard)"
else
    CLIPBOARD_MSG=""
fi

echo ""
echo -e "    ${BOLD}Done.${NC}"
echo ""
echo -e "    ${DIM}Activate:${NC}  ${ACTIVATE_CMD} ${DIM}${CLIPBOARD_MSG}${NC}"
echo -e "    ${DIM}Or run:${NC}    uv run <command>"
echo ""

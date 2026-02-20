#!/bin/bash

############################################################################
#
#    Apollos AI Container Entrypoint
#
############################################################################

# Colors
ORANGE='\033[38;5;208m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${ORANGE}"
cat << 'BANNER'
     █████╗ ██████╗  ██████╗ ██╗     ██╗      ██████╗ ███████╗
    ██╔══██╗██╔══██╗██╔═══██╗██║     ██║     ██╔═══██╗██╔════╝
    ███████║██████╔╝██║   ██║██║     ██║     ██║   ██║███████╗
    ██╔══██║██╔═══╝ ██║   ██║██║     ██║     ██║   ██║╚════██║
    ██║  ██║██║     ╚██████╔╝███████╗███████╗╚██████╔╝███████║
    ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝╚══════╝ ╚═════╝ ╚══════╝
BANNER
echo -e "${NC}"

if [[ "$PRINT_ENV_ON_LOAD" = true || "$PRINT_ENV_ON_LOAD" = True ]]; then
    echo -e "    ${DIM}Environment:${NC}"
    printenv | sed 's/^/    /'
    echo ""
fi

if [[ "$WAIT_FOR_DB" = true || "$WAIT_FOR_DB" = True ]]; then
    echo -e "    ${DIM}Waiting for database at ${DB_HOST}:${DB_PORT}...${NC}"
    dockerize -wait tcp://$DB_HOST:$DB_PORT -timeout 300s
    echo -e "    ${BOLD}Database ready.${NC}"
    echo ""
fi

# Seed data/docs with sample documents if docs-seed has content and docs is empty
if [ -d /app/data/docs-seed ] && [ -n "$(ls -A /app/data/docs-seed 2>/dev/null)" ] && [ -z "$(ls -A /app/data/docs 2>/dev/null)" ]; then
    echo -e "    ${DIM}Seeding /app/data/docs with sample documents...${NC}"
    mkdir -p /app/data/docs
    cp -r /app/data/docs-seed/* /app/data/docs/
fi

case "$1" in
    chill)
        echo -e "    ${DIM}Mode: chill${NC}"
        echo -e "    ${BOLD}Container running.${NC}"
        echo ""
        while true; do sleep 18000; done
        ;;
    *)
        echo -e "    ${DIM}> $@${NC}"
        echo ""
        exec "$@"
        ;;
esac

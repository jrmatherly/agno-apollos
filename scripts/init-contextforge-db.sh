#!/bin/bash
# Creates the contextforge database for the MCP Gateway service.
# Mounted into /docker-entrypoint-initdb.d/ on apollos-db.
# PostgreSQL runs these scripts only on first initialization (empty data volume).
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE contextforge OWNER $POSTGRES_USER;
EOSQL

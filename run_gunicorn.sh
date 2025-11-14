#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate
if [[ -f .env ]]; then export $(grep -v '^#' .env | xargs); fi
exec gunicorn -c gunicorn.conf.py wsgi:app

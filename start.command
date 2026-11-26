#!/usr/bin/env bash
cd "$(dirname "$0")"
exec python3 scripts/dev_server.py --port 8781 --open

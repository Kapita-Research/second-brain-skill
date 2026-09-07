#!/bin/zsh
# Double-click to start (or re-open) the live Second Brain dashboard.
cd "$(dirname "$0")"
exec /usr/bin/env python3 dashboard_server.py --open

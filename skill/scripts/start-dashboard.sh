#!/bin/sh
# Start (or re-open) the live Second Brain dashboard. Serves the vault this file
# sits in; press Ctrl-C to stop it. Linux/BSD equivalent of the macOS
# "Start Dashboard.command" — mark it executable (chmod +x) to double-click it,
# or run it from a terminal.
cd "$(dirname "$0")" || exit 1
exec python3 dashboard_server.py --open

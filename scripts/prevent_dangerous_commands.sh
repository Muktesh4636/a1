#!/bin/bash

# Dangerous Command Prevention Wrapper
# This script intercepts dangerous Docker Compose commands that could delete data

# Add to ~/.bashrc or ~/.bash_aliases:
# alias docker-compose='bash /path/to/prevent_dangerous_commands.sh docker-compose'
# alias docker='bash /path/to/prevent_dangerous_commands.sh docker'

# For docker compose (new syntax)
if command -v docker >/dev/null 2>&1; then
    docker() {
        if [ "$1" = "compose" ] && [ "$2" = "down" ]; then
            # Check for -v flag (volume deletion)
            for arg in "$@"; do
                if [ "$arg" = "-v" ] || [ "$arg" = "--volumes" ]; then
                    echo ""
                    echo "⚠️  ⚠️  ⚠️  DANGER: PREVENTING DATA DELETION ⚠️  ⚠️  ⚠️"
                    echo ""
                    echo "You tried to run: docker compose down -v"
                    echo "This command would DELETE ALL DATABASE DATA!"
                    echo ""
                    echo "If you really want to delete all data:"
                    echo "  1. Create a backup first"
                    echo "  2. Use: docker compose down -v --force-confirm-delete"
                    echo ""
                    echo "Otherwise, use safe restart:"
                    echo "  docker compose down  (preserves data)"
                    echo ""
                    return 1
                fi
            done
        fi
        
        # Call original docker command
        command docker "$@"
    }
fi

# Export function
export -f docker







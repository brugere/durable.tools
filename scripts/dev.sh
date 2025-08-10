#!/bin/bash
# Development helper script for durable.tools

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

show_help() {
    cat << EOF
Development Helper Script for durable.tools

Usage: $0 <command> [options]

Commands:
    start           Start local development environment
    stop            Stop local development environment
    restart         Restart local development environment
    build           Build and start local environment
    logs            Show logs from local environment
    shell           Open shell in a running container
    status          Show status of local containers
    clean           Clean up local containers and volumes
    help            Show this help message

Examples:
    $0 start                    # Start local dev environment
    $0 build                   # Rebuild and start
    $0 logs                    # Show all logs
    $0 shell frontend          # Open shell in frontend container
    $0 shell backend           # Open shell in backend container

Environment Files:
    - docker-compose.local.yml    # Local development
    - docker-compose.prod.yml     # Production (VPS)
    - docker-compose.yml          # Legacy (deprecated)
EOF
}

start_dev() {
    echo "🚀 Starting local development environment..."
    docker compose -f docker-compose.local.yml up -d
    echo "✅ Local environment started!"
    echo "📱 Frontend: http://localhost:3000"
    echo "🔧 Backend:  http://localhost:8000"
    echo "📊 View logs: $0 logs"
}

stop_dev() {
    echo "🛑 Stopping local development environment..."
    docker compose -f docker-compose.local.yml down
    echo "✅ Local environment stopped!"
}

restart_dev() {
    echo "🔄 Restarting local development environment..."
    stop_dev
    sleep 2
    start_dev
}

build_dev() {
    echo "🔨 Building and starting local development environment..."
    docker compose -f docker-compose.local.yml up --build -d
    echo "✅ Local environment built and started!"
    echo "📱 Frontend: http://localhost:3000"
    echo "🔧 Backend:  http://localhost:8000"
}

show_logs() {
    echo "📋 Showing logs from local environment..."
    docker compose -f docker-compose.local.yml logs -f
}

open_shell() {
    local service="${1:-}"
    if [ -z "$service" ]; then
        echo "❌ Please specify a service (frontend or backend)"
        echo "Usage: $0 shell <service>"
        exit 1
    fi
    
    echo "🐚 Opening shell in $service container..."
    docker compose -f docker-compose.local.yml exec "$service" /bin/bash
}

show_status() {
    echo "📊 Local development environment status:"
    docker compose -f docker-compose.local.yml ps
}

clean_dev() {
    echo "🧹 Cleaning up local development environment..."
    docker compose -f docker-compose.local.yml down -v
    echo "✅ Local environment cleaned up!"
}

# Main command handling
case "${1:-help}" in
    start)
        start_dev
        ;;
    stop)
        stop_dev
        ;;
    restart)
        restart_dev
        ;;
    build)
        build_dev
        ;;
    logs)
        show_logs
        ;;
    shell)
        open_shell "${2:-}"
        ;;
    status)
        show_status
        ;;
    clean)
        clean_dev
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac

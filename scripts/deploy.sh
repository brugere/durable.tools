#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<USAGE
Usage: $(basename "$0") --host HOST [--user USER] [--path /opt/durable.tools] [--services "frontend backend"] [--no-cache] [--pull] [--domain eco-lavelinge.fr]

Examples:
  $(basename "$0") --host 51.210.241.37 --user debian --domain eco-lavelinge.fr
  $(basename "$0") --host 51.210.241.37 --no-cache --services "frontend backend"

Flags:
  -h, --host       VPS IP or hostname (required)
  -u, --user       SSH user (default: debian)
  -p, --path       Remote project path (default: /opt/durable.tools)
  -s, --services   Space-separated services to build (default: all services)
      --no-cache   Build images without cache
      --pull       Pull base images before build
  -d, --domain     Public domain for post-deploy HTTPS check (optional)
USAGE
}

HOST=""
USER="debian"
DEST="/opt/durable.tools"
SERVICES=""
NO_CACHE=false
DO_PULL=false
DOMAIN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--host) HOST="${2:-}"; shift 2 ;;
    -u|--user) USER="${2:-}"; shift 2 ;;
    -p|--path) DEST="${2:-}"; shift 2 ;;
    -s|--services) SERVICES="${2:-}"; shift 2 ;;
    --no-cache) NO_CACHE=true; shift ;;
    --pull) DO_PULL=true; shift ;;
    -d|--domain) DOMAIN="${2:-}"; shift 2 ;;
    *) echo "Unknown argument: $1"; print_usage; exit 2 ;;
  esac
done

if [[ -z "$HOST" ]]; then
  echo "Error: --host is required"
  print_usage
  exit 2
fi

SSH_OPTS=( -o BatchMode=yes -o StrictHostKeyChecking=accept-new )

echo "==> Ensuring remote path $DEST exists on $USER@$HOST"
ssh "${SSH_OPTS[@]}" "$USER@$HOST" "mkdir -p '$DEST'"

echo "==> Syncing repository to $USER@$HOST:$DEST"
RSYNC_EXCLUDES=(
  --exclude .git
  --exclude .DS_Store
  --exclude node_modules
  --exclude "frontend/node_modules"
  --exclude ".next"
  --exclude "frontend/.next"
  --exclude ".venv"
  --exclude "__pycache__"
)
rsync -az --delete "${RSYNC_EXCLUDES[@]}" -e "ssh ${SSH_OPTS[*]}" "$(git rev-parse --show-toplevel)/" "$USER@$HOST:$DEST"

REMOTE_BUILD_CMDS=(
  "set -e"
  "cd '$DEST'"
)

if [[ "$DO_PULL" == true ]]; then
  REMOTE_BUILD_CMDS+=( "docker compose pull" )
fi

BUILD_CMD="docker compose build"
if [[ "$NO_CACHE" == true ]]; then
  BUILD_CMD+=" --no-cache"
fi
if [[ -n "$SERVICES" ]]; then
  echo "==> Building services: $SERVICES"
  BUILD_CMD+=" $SERVICES"
else
  echo "==> Building all services"
fi
REMOTE_BUILD_CMDS+=( "$BUILD_CMD" )

REMOTE_BUILD_CMDS+=( "docker compose up -d" )
REMOTE_BUILD_CMDS+=( "docker compose ps" )

echo "==> Deploying on remote host"
ssh "${SSH_OPTS[@]}" "$USER@$HOST" "bash -lc '${REMOTE_BUILD_CMDS[*]}'"

echo "==> Verifying services"
ssh "${SSH_OPTS[@]}" "$USER@$HOST" bash -lc "\
  set -e; \
  echo 'HTTP status:'; curl -sSI http://127.0.0.1/ | head -n 5; echo; \
  echo 'API sample (local):'; curl -sSf http://127.0.0.1/v1/statistics | head -c 200; echo; \
  if [[ -n '$DOMAIN' ]]; then \
    echo 'HTTPS status:'; curl -sSI https://$DOMAIN/ | head -n 8; echo; \
    echo 'API sample (public):'; curl -sSf https://$DOMAIN/v1/statistics | head -c 200; echo; \
  fi \
"

echo "==> Done"



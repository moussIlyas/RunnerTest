#!/usr/bin/env bash
# Small helper around docker compose for the self-hosted runner.
set -euo pipefail

cd "$(dirname "$0")"

usage() {
  echo "usage: $0 {up|down|restart|logs|status}" >&2
  exit 2
}

if [[ ! -f .env ]]; then
  echo "error: runner/.env is missing." >&2
  echo "       cp .env.example .env  and fill in REPO_URL + ACCESS_TOKEN." >&2
  exit 1
fi

if grep -qE 'YOUR_GITHUB_USER|YOUR_REPO|REPLACE_ME' .env; then
  echo "error: runner/.env still contains placeholder values." >&2
  echo "       Set REPO_URL and ACCESS_TOKEN first." >&2
  exit 1
fi

case "${1:-up}" in
  up)
    docker compose up -d --build
    echo "Runner starting. Follow the registration with: $0 logs"
    ;;
  down)
    # Sends SIGTERM: the entrypoint deregisters the runner from GitHub.
    docker compose down
    ;;
  restart)
    docker compose restart
    ;;
  logs)
    docker compose logs -f --tail=100
    ;;
  status)
    docker compose ps
    ;;
  *)
    usage
    ;;
esac

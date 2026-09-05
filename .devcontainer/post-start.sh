#!/usr/bin/env bash

set -euo pipefail

cd /workspace

readonly API_LOG_FILE="/tmp/order-management-api.log"
readonly API_PID_FILE="/tmp/order-management-api.pid"
readonly WEB_LOG_FILE="/tmp/order-management-web.log"
readonly WEB_PID_FILE="/tmp/order-management-web.pid"

start_service() {
  local name="$1"
  local url="$2"
  local log_file="$3"
  local pid_file="$4"
  shift 4

  if curl --fail --silent --show-error --max-time 2 "$url" > /dev/null; then
    echo "$name is already available at $url"
    return
  fi

  if [[ -f "$pid_file" ]]; then
    local previous_pid
    previous_pid="$(cat "$pid_file")"
    if [[ "$previous_pid" =~ ^[0-9]+$ ]] && kill -0 "$previous_pid" 2>/dev/null; then
      kill "$previous_pid"
    fi
  fi

  setsid "$@" > "$log_file" 2>&1 < /dev/null &
  echo "$!" > "$pid_file"

  for _ in {1..30}; do
    if curl --fail --silent --show-error --max-time 2 "$url" > /dev/null; then
      echo "$name is available at $url"
      return
    fi
    sleep 1
  done

  echo "$name did not become available. Recent log output:"
  tail -n 30 "$log_file"
  return 1
}

python -m pip install --user -r apps/api/requirements.txt
npm ci --prefix apps/web
alembic -c alembic.ini upgrade head
DATABASE_URL="${TEST_DATABASE_URL}" alembic -c alembic.ini upgrade head

start_service \
  "FastAPI" \
  "http://localhost:8000/consume-status" \
  "$API_LOG_FILE" \
  "$API_PID_FILE" \
  python -m uvicorn app.main:app --app-dir apps/api --host 0.0.0.0 --port 8000 --reload

start_service \
  "Vite" \
  "http://localhost:5173" \
  "$WEB_LOG_FILE" \
  "$WEB_PID_FILE" \
  npm run dev --prefix apps/web -- --host 0.0.0.0 --port 5173

#!/usr/bin/env bash

set -euo pipefail

cd /workspace

python -m pip install --user -r apps/api/requirements.txt
npm ci --prefix apps/web
alembic -c alembic.ini upgrade head
DATABASE_URL="${TEST_DATABASE_URL}" alembic -c alembic.ini upgrade head

#!/bin/bash
# Deployment script invoked by the Jenkins deploy stage.
set -e
APP_DIR="${DEPLOY_DIR:-$HOME/enp461-deploy}"
PYTHON="${VENV:+$VENV/bin/python3}"
PYTHON="${PYTHON:-python3}"

mkdir -p "$APP_DIR"
rsync -a --exclude ".git" --exclude "__pycache__" --exclude ".pytest_cache" --exclude ".venv" ./ "$APP_DIR/"

# stop any previous instance owned by this user
pkill -f "python3 app.py" 2>/dev/null || true

cd "$APP_DIR/app"
nohup "$PYTHON" app.py > "$APP_DIR/deploy.log" 2>&1 &

# verify the health endpoint (up to 10 attempts)
for i in $(seq 1 10); do
  sleep 2
  if curl -sf http://localhost:5000/health > /dev/null; then
    echo "Deployment verified: health OK (attempt $i)"
    curl -s http://localhost:5000/
    exit 0
  fi
done
echo "Deployment FAILED: health endpoint not responding" >&2
cat "$APP_DIR/deploy.log" >&2
exit 1

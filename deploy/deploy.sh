#!/bin/bash
# Deployment script invoked by the Jenkins deploy stage.
set -e
APP_DIR="$HOME/enp461-deploy"
mkdir -p "$APP_DIR"
rsync -a --exclude ".git" --exclude "__pycache__" --exclude ".pytest_cache" ./ "$APP_DIR/"
pkill -f "flask-run|app.py" 2>/dev/null || true
cd "$APP_DIR/app"
nohup python3 app.py > "$APP_DIR/deploy.log" 2>&1 &
sleep 3
curl -sf http://localhost:5000/health && echo "Deployment verified: health OK"

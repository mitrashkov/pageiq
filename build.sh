#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- Building PageIQ API ---"

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Define the persistent browser path
# Render's /opt/render/project/src is the most reliable place for persistence
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.playwright

echo "--- Installing Playwright Chromium ---"
echo "Target path: $PLAYWRIGHT_BROWSERS_PATH"

# Force installation of chromium into the persistent directory
python -m playwright install chromium

# List contents for verification in build logs
echo "--- Verifying installation ---"
if [ -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    ls -R "$PLAYWRIGHT_BROWSERS_PATH" | head -n 20
else
    echo "ERROR: Playwright browsers directory not found after installation!"
    exit 1
fi

echo "--- Build Complete ---"

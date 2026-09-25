#!/bin/sh
# A real Chrome the user logs into once (Google SSO, dashboards) and keeps open; takes attach with { cdp: true }.
# Why: Google blocks sign-in inside Playwright's Chromium, and many dashboards (WorkOS) keep only session cookies,
# so a persistent profile loses the login when the browser closes. Never close this window during the production.
PROFILE="${1:?profile dir}"; URL="${2:-about:blank}"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --user-data-dir="$PROFILE" --remote-debugging-port=9333 \
  --window-size=1920,1100 --no-first-run "$URL" >/dev/null 2>&1 &
echo "chrome with CDP on http://127.0.0.1:9333"

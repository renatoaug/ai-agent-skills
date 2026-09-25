#!/bin/sh
# Serve a real, clean shell in the browser (ttyd) so Playwright can record it like any page.
# Usage: adapters/terminal.sh <workdir> [prompt-label]
# - clean env (env -i): the recorded CLI never inherits the recording agent's session markers
# - big font (27) so text survives 1080p; dark theme matching the overlays
# - `claude` wrapper: loads ONLY the MCP servers in <workdir>/.mcp-demo.json (hides personal integrations from /mcp)
set -e
WD="$1"; LABEL="${2:-demo}"; ZD="$WD/.zd"; mkdir -p "$ZD"
cat > "$ZD/.zshrc" <<RC
export PATH=\$HOME/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
export BROWSER=/usr/bin/true
PROMPT='%F{cyan}$LABEL%f %F{245}\$%f '
unsetopt BEEP PROMPT_SP
claude() { if [[ "\$1" == "mcp" || ! -f $WD/.mcp-demo.json ]]; then command claude "\$@"; else command claude --strict-mcp-config --mcp-config $WD/.mcp-demo.json "\$@"; fi }
cd $WD
clear
RC
pkill ttyd 2>/dev/null || true
cd "$WD" && env -i HOME="$HOME" USER="$USER" LOGNAME="$USER" TERM=xterm-256color LANG=en_US.UTF-8 PATH=/opt/homebrew/bin:/usr/bin:/bin \
  ttyd -W -p 7681 -t fontSize=27 -t 'fontFamily=Menlo, monospace' \
  -t 'theme={"background":"#0b0d18","foreground":"#e6e6f0","cursor":"#7df9ff"}' -t disableLeaveAlert=true \
  env ZDOTDIR="$ZD" zsh >/dev/null 2>&1 &
echo "terminal on http://localhost:7681 (workdir $WD)"

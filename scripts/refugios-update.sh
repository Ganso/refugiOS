#!/bin/bash
# refugiOS - Updater launcher
# Runs the latest published installer in update mode, so the list of books,
# mirrors and checksums is always the current one. With REFUGIOS_SRC_DIR
# pointing to a checkout of the repository, that copy is used instead.

SCRIPTS_DIR="$HOME/refugiOS/Scripts"
REPO_URL="${REPO_URL:-https://raw.githubusercontent.com/Ganso/refugiOS/main}"

# Source localization system
t() { echo "$1"; }
[ -s "$SCRIPTS_DIR/i18n.sh" ] && source "$SCRIPTS_DIR/i18n.sh"

finish() {
    echo
    if [ -t 0 ]; then
        read -r -p "$(t press_enter)" _ 2>/dev/null || true
    fi
    exit "$1"
}

if [ -n "${REFUGIOS_SRC_DIR:-}" ] && [ -f "$REFUGIOS_SRC_DIR/install.sh" ]; then
    bash "$REFUGIOS_SRC_DIR/install.sh" --update
    finish $?
fi

if ! curl -sfI --max-time 15 "$REPO_URL/install.sh" >/dev/null 2>&1; then
    echo
    echo "$(t update_no_connection)"
    finish 1
fi

curl -fsSL "$REPO_URL/install.sh" | bash -s -- --update
finish "${PIPESTATUS[1]}"

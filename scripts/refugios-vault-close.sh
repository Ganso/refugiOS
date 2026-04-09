#!/bin/bash
SCRIPTS_DIR="$HOME/refugiOS/Scripts"

# Source localization system
t() { echo "$1"; }
[ -s "$SCRIPTS_DIR/i18n.sh" ] && source "$SCRIPTS_DIR/i18n.sh"

if [ -d "$HOME/Desktop" ]; then DIR="$HOME/Desktop/PRIVATE_VAULT"
else DIR="$HOME/Escritorio/PRIVATE_VAULT"; fi

echo "$(t vault_close)..."
sudo umount "$DIR" || true
sudo cryptsetup close active_vault || true
rmdir "$DIR" || true
echo "Buffers cleared from RAM. The vault has been sealed without exposing vectors."
sleep 3

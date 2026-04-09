#!/bin/bash
set -e
FILE="$HOME/refugiOS/Vaults/personal_data.img"
SCRIPTS_DIR="$HOME/refugiOS/Scripts"

# Source localization system
t() { echo "$1"; }
[ -s "$SCRIPTS_DIR/i18n.sh" ] && source "$SCRIPTS_DIR/i18n.sh"

if [ -d "$HOME/Desktop" ]; then DIR="$HOME/Desktop/PRIVATE_VAULT"
else DIR="$HOME/Escritorio/PRIVATE_VAULT"; fi

mkdir -p "$DIR"
echo "$(t vault_open)..."
sudo cryptsetup open "$FILE" active_vault
# Translocate logical reading from `/dev/mapper` to a directory visible to the GUI.
sudo mount /dev/mapper/active_vault "$DIR"
sudo chown -R $USER:$USER "$DIR"
echo "The Vault is ready for viewing."
sleep 3

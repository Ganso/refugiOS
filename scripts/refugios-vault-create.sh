#!/bin/bash
set -e
FILE="$HOME/refugiOS/Vaults/personal_data.img"
SCRIPTS_DIR="$HOME/refugiOS/Scripts"

# Source localization system
t() { echo "$1"; }
[ -s "$SCRIPTS_DIR/i18n.sh" ] && source "$SCRIPTS_DIR/i18n.sh"

echo "$(t vault_create)..."
# dd fills the area with random data that we will later occupy.
dd if=/dev/urandom of="$FILE" bs=1M count=3072 status=progress
sudo cryptsetup luksFormat "$FILE"
sudo cryptsetup open "$FILE" active_vault
sudo mkfs.ext4 /dev/mapper/active_vault
sudo cryptsetup close active_vault
echo "Vault manufactured and grafted. Session can be safely closed after 5 seconds..."
sleep 5

#!/bin/bash
# refugiOS - Vault Closing (Wrapper)
# Delegates to the unified Python vault manager
SCRIPTS_DIR="$HOME/refugiOS/Scripts"
python3 "$SCRIPTS_DIR/refugios-vault.py" close < /dev/tty

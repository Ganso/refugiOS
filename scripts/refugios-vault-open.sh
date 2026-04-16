#!/bin/bash
# refugiOS - Vault Opening (Wrapper)
# Delegates to the unified Python vault manager
SCRIPTS_DIR="$HOME/refugiOS/Scripts"
python3 "$SCRIPTS_DIR/refugios-vault.py" open < /dev/tty

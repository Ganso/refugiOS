#!/bin/bash
# refugiOS - Vault Creation (Wrapper)
# Delegates to the unified Python vault manager
SCRIPTS_DIR="$HOME/refugiOS/Scripts"
python3 "$SCRIPTS_DIR/refugios-vault.py" create < /dev/tty

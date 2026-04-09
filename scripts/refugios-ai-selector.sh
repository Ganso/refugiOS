#!/bin/bash
# Local re-detection in case you run the USB on a future computer with much extra power.
AI_DIR="$HOME/refugiOS/AI"
SCRIPTS_DIR="$HOME/refugiOS/Scripts"

# Source localization system
t() { echo "$1"; }
[ -s "$SCRIPTS_DIR/i18n.sh" ] && source "$SCRIPTS_DIR/i18n.sh"

RAM_MB=$(free -m | awk '/^Mem:/{print $2}')

HAS_MAX=0; HAS_MED=0; HAS_BASE=0; HAS_MIN=0
[ -f "$AI_DIR/advanced-model.gguf" ]     && HAS_MAX=1
[ -f "$AI_DIR/intermediate-model.gguf" ] && HAS_MED=1
[ -f "$AI_DIR/basic-model.gguf" ]        && HAS_BASE=1
[ -f "$AI_DIR/minimal-model.gguf" ]      && HAS_MIN=1

if [ "$RAM_MB" -lt 1024 ] && [ "$HAS_MIN" -eq 1 ]; then
    MODEL="minimal-model.gguf"
elif [ "$RAM_MB" -ge 14000 ] && [ "$HAS_MAX" -eq 1 ]; then
    MODEL="advanced-model.gguf"
elif [ "$RAM_MB" -ge 7000 ] && [ "$HAS_MED" -eq 1 ]; then
    MODEL="intermediate-model.gguf"
elif [ "$HAS_BASE" -eq 1 ]; then
    MODEL="basic-model.gguf"
else
    MODEL="minimal-model.gguf"
fi

cd "$AI_DIR"
# Generate an internal loop server on port 8080 interacting with Llamafile
./llamafile -m "$MODEL" --ctx-size 4096 --server &
LLAMA_PID=$!
sleep 5
epiphany-browser http://localhost:8080 2>/dev/null || xdg-open http://localhost:8080 2>/dev/null
echo "$(t ai_purge_notice)"
wait $LLAMA_PID

#!/bin/bash
# refugiOS - AI Model Selector
# Detects hardware capabilities, shows installed models via dialog,
# and auto-selects the most powerful model the system can run safely.

AI_DIR="$HOME/refugiOS/AI"
SCRIPTS_DIR="$HOME/refugiOS/Scripts"

# Source localization system
t() { echo "$1"; }
[ -s "$SCRIPTS_DIR/i18n.sh" ] && source "$SCRIPTS_DIR/i18n.sh"

# ============================================================================
# Hardware Detection
# ============================================================================

# Total RAM in MB
TOTAL_RAM_MB=$(free -m | awk '/^Mem:/{print $2}')

# VRAM detection in MB (0 if no dedicated GPU)
VRAM_MB=0

# NVIDIA GPU
if command -v nvidia-smi &>/dev/null; then
    VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d '[:space:]')
    if ! [[ "$VRAM_MB" =~ ^[0-9]+$ ]]; then
        VRAM_MB=0
    fi
fi

# AMD GPU (sysfs)
if [ "$VRAM_MB" -eq 0 ] && [ -d /sys/class/drm ]; then
    for card in /sys/class/drm/card*/device/mem_info_vram_total; do
        if [ -f "$card" ]; then
            vram_bytes=$(cat "$card" 2>/dev/null)
            if [ -n "$vram_bytes" ] && [ "$vram_bytes" -gt 0 ] 2>/dev/null; then
                VRAM_MB=$((vram_bytes / 1024 / 1024))
                break
            fi
        fi
    done
fi

# Intel integrated GPU shares system RAM (no separate VRAM to add)

# Safety margin: 2 GB (2048 MB) - CRITICAL to avoid USB swap freeze
SAFETY_MARGIN_MB=2048

# Usable memory for AI = RAM + VRAM - safety margin
USABLE_MB=$((TOTAL_RAM_MB + VRAM_MB - SAFETY_MARGIN_MB))
if [ "$USABLE_MB" -lt 0 ]; then
    USABLE_MB=0
fi

HAS_GPU="No"
if [ "$VRAM_MB" -gt 0 ]; then
    HAS_GPU="Yes (${VRAM_MB}MB)"
fi

# ============================================================================
# Model Registry (ordered smallest to largest)
# Format: id|symlink|display_label|min_usable_mb
# min_usable_mb = minimum USABLE memory (after safety margin) to run smoothly
# ============================================================================

declare -a MODEL_IDS=()
declare -a MODEL_SYMLINKS=()
declare -a MODEL_LABELS=()
declare -a MODEL_MIN_RAM=()

register_model() {
    MODEL_IDS+=("$1")
    MODEL_SYMLINKS+=("$2")
    MODEL_LABELS+=("$3")
    MODEL_MIN_RAM+=("$4")
}

register_model "ia_min"   "minimal-model.gguf"   "Qwen3-0.6B (~380MB)"     1024
register_model "ia_base"  "basic-model.gguf"     "Gemma-4-E4B-it (~4.7GB)" 6144
register_model "ia_med"   "intermediate-model.gguf" "Qwen3-8B (~4.8GB)"    6144
register_model "ia_max"   "advanced-model.gguf"  "Qwen3-14B (~8.6GB)"      10240
register_model "ia_ultra" "ultra-model.gguf"     "Gemma-4-26B-A4B (~16.2GB)" 18432

# ============================================================================
# Build dialog menu with only installed models
# ============================================================================

MENU_ITEMS=()
DEFAULT_ITEM=""
BEST_IDX=-1
BEST_MIN_RAM=0

for i in "${!MODEL_IDS[@]}"; do
    mid="${MODEL_IDS[$i]}"
    msymlink="${MODEL_SYMLINKS[$i]}"
    mlabel="${MODEL_LABELS[$i]}"
    mminram="${MODEL_MIN_RAM[$i]}"

    # Check if model file exists (follow symlinks)
    if [ -f "$AI_DIR/$msymlink" ]; then
        if [ "$USABLE_MB" -ge "$mminram" ]; then
            status="[OK]"
            # Track the most powerful model that fits
            if [ "$mminram" -ge "$BEST_MIN_RAM" ]; then
                BEST_MIN_RAM="$mminram"
                BEST_IDX="$i"
                DEFAULT_ITEM="$mid"
            fi
        else
            status="[LOW_RAM]"
        fi
        MENU_ITEMS+=("$mid" "$mlabel $status")
    fi
done

# No models installed
if [ ${#MENU_ITEMS[@]} -eq 0 ]; then
    dialog --msgbox "No AI models installed.\n\nRun the refugiOS installer to download models first." 10 60
    exit 1
fi

# If no model fits in usable memory, default to smallest installed
if [ -z "$DEFAULT_ITEM" ]; then
    for i in "${!MODEL_IDS[@]}"; do
        msymlink="${MODEL_SYMLINKS[$i]}"
        if [ -f "$AI_DIR/$msymlink" ]; then
            DEFAULT_ITEM="${MODEL_IDS[$i]}"
            BEST_IDX="$i"
            break
        fi
    done
fi

# ============================================================================
# Show dialog menu
# ============================================================================

HW_INFO="RAM: ${TOTAL_RAM_MB}MB | VRAM: ${VRAM_MB}MB | Usable for AI: ${USABLE_MB}MB (2GB OS reserved)"

CHOICE=$(dialog --stdout \
    --title "refugiOS - AI Model Selector" \
    --default-item "$DEFAULT_ITEM" \
    --menu "$HW_INFO\n\nSelect a model to run:" \
    16 72 8 \
    "${MENU_ITEMS[@]}")

if [ $? -ne 0 ] || [ -z "$CHOICE" ]; then
    exit 0
fi

# Resolve selected model symlink
SELECTED_SYMLINK=""
for i in "${!MODEL_IDS[@]}"; do
    if [ "${MODEL_IDS[$i]}" = "$CHOICE" ]; then
        SELECTED_SYMLINK="${MODEL_SYMLINKS[$i]}"
        break
    fi
done

if [ -z "$SELECTED_SYMLINK" ]; then
    dialog --msgbox "Error: Could not resolve selected model." 8 50
    exit 1
fi

clear

cd "$AI_DIR"

# ============================================================================
# Launch Llamafile
# ============================================================================

NGL_FLAG=""
if [ "$VRAM_MB" -gt 0 ]; then
    # Dedicated GPU available: full offloading
    NGL_FLAG="-ngl 99"
elif ! grep -q avx2 /proc/cpuinfo; then
    # No AVX2: disable GPU offloading to avoid crashes
    NGL_FLAG="-ngl 0"
fi

# Start llamafile server on port 8080
./llamafile -m "$SELECTED_SYMLINK" --ctx-size 4096 $NGL_FLAG --server &
LLAMA_PID=$!
sleep 5

# Open browser to AI chat interface
epiphany-browser --new-window http://localhost:8080 2>/dev/null || xdg-open http://localhost:8080 2>/dev/null

echo "$(t ai_purge_notice)"
wait $LLAMA_PID

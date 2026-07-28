#!/bin/bash
# Tests de los scripts Bash corregidos: C5 (i18n), C13-C16 (lanzadores),
# C17-C18 (test_boot.sh). No requiere privilegios: usa dobles de los binarios
# externos (dialog, curl, llamafile, qemu, epiphany-browser) en un PATH falso.
set -uo pipefail

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$TESTS_DIR")"
WORK="$(mktemp -d)"
FAILED=0

trap 'rm -rf "$WORK"' EXIT

check() {
    if [ "$1" == "0" ]; then
        echo "   [OK]   $2"
    else
        echo "   [FAIL] $2"
        FAILED=1
    fi
}

# ============================================================================
# C5 - i18n.sh: el idioma persistido gana al del entorno
# ============================================================================
echo "=> C5: precedencia de idioma"

export HOME="$WORK/home"
mkdir -p "$HOME"

echo "es" > "$HOME/.refugios_lang"
OUT=$(LANG=en_US.UTF-8 bash -c "source '$REPO_DIR/scripts/i18n.sh'; t vault_create")
[ "$OUT" == "CREANDO BÓVEDA SEGURA" ]
check $? "el idioma persistido (es) gana sobre LANG=en_US.UTF-8 (obtenido: $OUT)"

rm -f "$HOME/.refugios_lang"
OUT=$(LANG=en_US.UTF-8 bash -c "source '$REPO_DIR/scripts/i18n.sh'; t vault_create")
[ "$OUT" == "CREATING SECURE VAULT" ]
check $? "sin fichero persistido se autodetecta desde LANG (obtenido: $OUT)"

echo "en" > "$HOME/.refugios_lang"
OUT=$(LANG=es_ES.UTF-8 bash -c "source '$REPO_DIR/scripts/i18n.sh'; t vault_create")
[ "$OUT" == "CREATING SECURE VAULT" ]
check $? "el idioma persistido (en) gana sobre LANG=es_ES.UTF-8 (obtenido: $OUT)"

OUT=$(bash -c "source '$REPO_DIR/scripts/i18n.sh'; t clave_que_no_existe")
[ "$OUT" == "clave_que_no_existe" ]
check $? "una clave inexistente devuelve la propia clave (fallback intacto)"

OUT=$(bash -c "source '$REPO_DIR/scripts/i18n.sh'; bash -c 't vault_create'")
[ "$OUT" == "CREATING SECURE VAULT" ]
check $? "la función t() se exporta a los procesos hijo"

rm -f "$HOME/.refugios_lang"

# ============================================================================
# C16 - refugios-kiwix.sh: orden natural de versiones
# ============================================================================
echo "=> C16: seleccion de la version mas reciente de Kiwix"

mkdir -p "$HOME/refugiOS/Apps" "$HOME/refugiOS/Scripts" "$WORK/bin"
cp "$REPO_DIR/scripts/i18n.sh" "$HOME/refugiOS/Scripts/"
for v in 2.3.1 2.9.1 2.10.0; do
    printf '#!/bin/bash\necho LANZADO:%s "$@"\n' "$v" \
        > "$HOME/refugiOS/Apps/kiwix-desktop_x86_64_${v}.appimage"
    chmod +x "$HOME/refugiOS/Apps/kiwix-desktop_x86_64_${v}.appimage"
done
# Una version sin permiso de ejecucion no debe elegirse jamas
printf '#!/bin/bash\necho NO_EJECUTABLE\n' > "$HOME/refugiOS/Apps/kiwix-desktop_x86_64_3.0.0.appimage"
chmod 644 "$HOME/refugiOS/Apps/kiwix-desktop_x86_64_3.0.0.appimage"

touch "$WORK/prueba.zim"
# PATH sin kiwix-desktop ni flatpak para forzar el fallback por find
cat > "$WORK/bin/flatpak" <<'EOF'
#!/bin/bash
exit 1
EOF
chmod +x "$WORK/bin/flatpak"

OUT=$(PATH="$WORK/bin:/usr/bin:/bin" bash "$REPO_DIR/scripts/refugios-kiwix.sh" "$WORK/prueba.zim" 2>&1)
grep -q "LANZADO:2.10.0" <<<"$OUT"
check $? "elige la 2.10.0 y no la 2.9.1 (obtenido: $OUT)"

grep -q "NO_EJECUTABLE" <<<"$OUT"
[ $? -ne 0 ]
check $? "descarta el AppImage sin permiso de ejecucion"

# ============================================================================
# C13/C14/C15 - refugios-ai-selector.sh
# ============================================================================
echo "=> C13-C15: motor de IA"

AI_DIR="$HOME/refugiOS/AI"
mkdir -p "$AI_DIR"

cat > "$WORK/bin/dialog" <<'EOF'
#!/bin/bash
# Doble de dialog: registra lo mostrado y responde siempre con el modelo de prueba
echo "DIALOG: $*" >> "$DIALOG_LOG"
for arg in "$@"; do
    if [ "$arg" == "--msgbox" ]; then exit 0; fi
done
echo "ia_min"
EOF
cat > "$WORK/bin/epiphany-browser" <<'EOF'
#!/bin/bash
echo "NAVEGADOR_ABIERTO $(date +%s)" >> "$BROWSER_LOG"
EOF
cat > "$WORK/bin/xdg-open" <<'EOF'
#!/bin/bash
echo "NAVEGADOR_ABIERTO $(date +%s)" >> "$BROWSER_LOG"
EOF
chmod +x "$WORK/bin/dialog" "$WORK/bin/epiphany-browser" "$WORK/bin/xdg-open"

export DIALOG_LOG="$WORK/dialog.log"
export BROWSER_LOG="$WORK/browser.log"
: > "$DIALOG_LOG"; : > "$BROWSER_LOG"

# C15: sin llamafile instalado
touch "$AI_DIR/minimal-model.gguf"
PATH="$WORK/bin:/usr/bin:/bin" bash "$REPO_DIR/scripts/refugios-ai-selector.sh" >/dev/null 2>&1
[ $? -ne 0 ]
check $? "C15: sin llamafile el script termina con codigo != 0"
grep -q -- "--msgbox" "$DIALOG_LOG"
check $? "C15: se avisa al usuario con un mensaje de dialog"

# C14/C13: llamafile falso que tarda en levantar el puerto
PORT=18080
cat > "$AI_DIR/llamafile" <<EOF
#!/bin/bash
# Simula la carga lenta de un modelo grande: 8 segundos antes de servir
sleep 8
exec python3 -m http.server $PORT --bind 127.0.0.1
EOF
chmod +x "$AI_DIR/llamafile"

: > "$BROWSER_LOG"
START=$(date +%s)
REFUGIOS_AI_PORT=$PORT REFUGIOS_AI_WAIT=60 \
    PATH="$WORK/bin:/usr/bin:/bin" bash "$REPO_DIR/scripts/refugios-ai-selector.sh" >/dev/null 2>&1 &
SELECTOR_PID=$!

# Esperar a que el navegador se abra (o a que se agote el tiempo)
for _ in $(seq 1 40); do
    [ -s "$BROWSER_LOG" ] && break
    sleep 1
done

[ -s "$BROWSER_LOG" ]
check $? "C14: el navegador acaba abriendose"

if [ -s "$BROWSER_LOG" ]; then
    OPENED=$(awk '{print $2}' "$BROWSER_LOG" | head -1)
    ELAPSED=$((OPENED - START))
    [ "$ELAPSED" -ge 7 ]
    check $? "C14: espera a que el servidor responda antes de abrir (${ELAPSED}s, el modelo tarda 8s)"
fi

# C13: al terminar el selector no puede quedar el motor de IA en memoria
kill "$SELECTOR_PID" 2>/dev/null
sleep 3
pgrep -f "http.server $PORT" >/dev/null
[ $? -ne 0 ]
check $? "C13: no queda ningun proceso de IA huerfano tras cerrar el lanzador"
pkill -f "http.server $PORT" 2>/dev/null

# ============================================================================
# C17/C18 - test_boot.sh
# ============================================================================
echo "=> C17-C18: test_boot.sh"

cat > "$WORK/bin/qemu-system-x86_64" <<'EOF'
#!/bin/bash
echo "QEMU_ARGS: $*" > "$QEMU_LOG"
EOF
chmod +x "$WORK/bin/qemu-system-x86_64"
export QEMU_LOG="$WORK/qemu.log"

BOOT_WORK="$WORK/boot"
mkdir -p "$BOOT_WORK/scripts"
cp "$REPO_DIR/scripts/test_boot.sh" "$BOOT_WORK/scripts/"
truncate -s 1M "$BOOT_WORK/refugios-base-16G-en.img"

OUT=$(PATH="$WORK/bin:/usr/bin:/bin" bash "$BOOT_WORK/scripts/test_boot.sh" -s 16G -l en 2>&1)
grep -q "refugios-base-16G-en.img" "$QEMU_LOG" 2>/dev/null
check $? "C17: '-s 16G -l en' encuentra la imagen (antes componia un nombre sin idioma)"

OUT=$(PATH="$WORK/bin:/usr/bin:/bin" bash "$BOOT_WORK/scripts/test_boot.sh" 16G 2>&1)
grep -q "refugios-base-16G-en.img" "$QEMU_LOG" 2>/dev/null
check $? "C17: la forma antigua 'test_boot.sh 16G' sigue funcionando"

RAM=$(grep -o '\-m [0-9]*G' "$QEMU_LOG" | head -1 | grep -o '[0-9]*')
[ -n "$RAM" ] && [ "$RAM" -ge 2 ] && [ "$RAM" -le 8 ]
check $? "C18: la RAM se calcula dentro del rango [2G, 8G] (obtenido: ${RAM:-vacio}G)"

# Simular un anfitrion con poca memoria disponible
cat > "$WORK/bin/awk" <<'EOF'
#!/bin/bash
# Devuelve 1 GB de MemAvailable cuando se consulta /proc/meminfo
for arg in "$@"; do
    case "$arg" in
        *MemAvailable*) echo 1048576; exit 0 ;;
    esac
done
exec /usr/bin/awk "$@"
EOF
chmod +x "$WORK/bin/awk"
PATH="$WORK/bin:/usr/bin:/bin" bash "$BOOT_WORK/scripts/test_boot.sh" -s 16G -l en >/dev/null 2>&1
grep -q -- "-m 2G" "$QEMU_LOG"
check $? "C18: con solo 1 GB disponible se asigna el minimo de 2G (antes se pedian 8G fijos)"
rm -f "$WORK/bin/awk"

echo
if [ "$FAILED" -eq 0 ]; then
    echo "=> unit_bash.sh: TODO CORRECTO"
else
    echo "=> unit_bash.sh: HAY FALLOS"
fi
exit $FAILED

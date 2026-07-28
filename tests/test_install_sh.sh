#!/bin/bash
# Tests de install.sh (C3 Developer Mode, C4 validaciones).
#
# Se monta un "repositorio local" falso cuyos install.py / i18n.py son marcadores
# reconocibles: si el bootstrapper los sobrescribe con la version de GitHub, el
# marcador desaparece y el test lo detecta. Necesita red para ser significativo.
#
#   tests/run_in_container.sh bash tests/test_install_sh.sh
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

MARKER="MARCADOR_LOCAL_DEL_TEST"

prepare_fake_repo() {
    local dir="$1"
    rm -rf "$dir"
    mkdir -p "$dir/scripts"
    cp "$REPO_DIR/install.sh" "$dir/"
    cp "$REPO_DIR/scripts/i18n.sh" "$dir/scripts/"
    printf '# %s\nprint("instalador local ejecutado")\n' "$MARKER" > "$dir/install.py"
    printf '# %s\nREFUGIOS_LANG="es"\ndef T(k):\n    return k\n' "$MARKER" > "$dir/i18n.py"
}

if curl -sfI --max-time 10 https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh >/dev/null 2>&1; then
    HAS_NET=1
else
    HAS_NET=0
    echo "   AVISO: sin conexion; el test de Developer Mode pierde valor"
fi

# ============================================================================
# C3 - Developer Mode: los ficheros locales no se sobrescriben desde GitHub
# ============================================================================
echo "=> C3: Developer Mode (red disponible: $HAS_NET)"

export HOME="$WORK/home"
mkdir -p "$HOME"
prepare_fake_repo "$WORK/repo"

DEBUG=1 bash "$WORK/repo/install.sh" > "$WORK/run1.log" 2>&1
grep -q "instalador local ejecutado" "$WORK/run1.log"
check $? "se ejecuta el install.py local, no el descargado"

grep -q "$MARKER" "$HOME/refugiOS/install.py"
check $? "C3: install.py local sobrevive (no lo pisa el wget de GitHub)"

grep -q "$MARKER" "$HOME/refugiOS/i18n.py"
check $? "C3: i18n.py local sobrevive"

grep -q "Developer Mode" "$WORK/run1.log"
check $? "C3: el modo desarrollador se anuncia explicitamente"

# Segunda ejecucion: los cambios locales posteriores deben seguir ganando
echo "# SEGUNDA_VERSION_LOCAL" >> "$WORK/repo/install.py"
DEBUG=1 bash "$WORK/repo/install.sh" > "$WORK/run2.log" 2>&1
grep -q "SEGUNDA_VERSION_LOCAL" "$HOME/refugiOS/install.py"
check $? "C3: una edicion local posterior se propaga (antes el destino ya no se tocaba)"

# ============================================================================
# C3 (contrario) - sin ficheros locales se descarga de GitHub
# ============================================================================
if [ "$HAS_NET" == "1" ]; then
    echo "=> C3: modo normal (sin copia local)"
    export HOME="$WORK/home2"
    mkdir -p "$HOME"
    mkdir -p "$WORK/solo_sh"
    cp "$REPO_DIR/install.sh" "$WORK/solo_sh/"

    DEBUG=1 timeout 180 bash "$WORK/solo_sh/install.sh" > "$WORK/run3.log" 2>&1
    [ -s "$HOME/refugiOS/install.py" ]
    check $? "sin copia local se descarga el instalador desde GitHub"

    grep -q "$MARKER" "$HOME/refugiOS/install.py" 2>/dev/null
    [ $? -ne 0 ]
    check $? "el instalador descargado es el remoto, no un resto del test"
fi

# ============================================================================
# C4 - validaciones de i18n.py y de /dev/tty
# ============================================================================
echo "=> C4: validaciones"

export HOME="$WORK/home3"
mkdir -p "$HOME"
prepare_fake_repo "$WORK/repo_vacio"
: > "$WORK/repo_vacio/i18n.py"   # i18n.py existe pero esta vacio

DEBUG=1 bash "$WORK/repo_vacio/install.sh" > "$WORK/run4.log" 2>&1
STATUS=$?
[ "$STATUS" -ne 0 ]
check $? "C4: con i18n.py vacio se aborta (codigo $STATUS)"

grep -qiE "i18n|idioma|localization" "$WORK/run4.log"
check $? "C4: el mensaje de error identifica el modulo de idiomas"

export HOME="$WORK/home4"
mkdir -p "$HOME"
prepare_fake_repo "$WORK/repo_tty"
setsid env DEBUG=1 bash "$WORK/repo_tty/install.sh" < /dev/null > "$WORK/run5.log" 2>&1
STATUS=$?
grep -q "instalador local ejecutado" "$WORK/run5.log"
check $? "C4: sin terminal el instalador se lanza igualmente (codigo $STATUS)"

grep -qiE "terminal|tty" "$WORK/run5.log"
check $? "C4: se avisa de que no hay terminal disponible"

# Developer Mode sin scripts/i18n.sh local: no debe abortar por 'set -e'
export HOME="$WORK/home5"
mkdir -p "$HOME"
prepare_fake_repo "$WORK/repo_sin_i18nsh"
rm -f "$WORK/repo_sin_i18nsh/scripts/i18n.sh"
DEBUG=1 bash "$WORK/repo_sin_i18nsh/install.sh" > "$WORK/run6.log" 2>&1
grep -q "instalador local ejecutado" "$WORK/run6.log"
check $? "C3: sin scripts/i18n.sh local el arranque no se interrumpe"


echo
if [ "$FAILED" -eq 0 ]; then
    echo "=> test_install_sh.sh: TODO CORRECTO"
else
    echo "=> test_install_sh.sh: HAY FALLOS"
fi
exit $FAILED

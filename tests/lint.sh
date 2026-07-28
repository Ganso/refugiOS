#!/bin/bash
# Comprobacion estatica de todos los scripts del proyecto.
# Sin argumentos: sintaxis (bash -n / py_compile) y, si esta disponible, shellcheck.
set -uo pipefail

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$TESTS_DIR")"
cd "$REPO_DIR"

FAILED=0

SH_FILES=(
    build_all.sh
    install.sh
    scripts/build_refugios.sh
    scripts/i18n.sh
    scripts/refugios-ai-selector.sh
    scripts/refugios-kiwix.sh
    scripts/refugios-maps.sh
    scripts/test_boot.sh
)
PY_FILES=(install.py i18n.py scripts/refugios-vault.py)

echo "=> Sintaxis Bash (bash -n)"
for f in "${SH_FILES[@]}"; do
    if bash -n "$f" 2>/tmp/lint_err; then
        echo "   [OK]   $f"
    else
        echo "   [FAIL] $f"
        cat /tmp/lint_err
        FAILED=1
    fi
done

echo "=> Sintaxis Python (py_compile)"
for f in "${PY_FILES[@]}"; do
    if python3 -m py_compile "$f" 2>/tmp/lint_err; then
        echo "   [OK]   $f"
    else
        echo "   [FAIL] $f"
        cat /tmp/lint_err
        FAILED=1
    fi
done

if command -v shellcheck >/dev/null 2>&1; then
    echo "=> shellcheck (informativo, no bloquea)"
    for f in "${SH_FILES[@]}"; do
        count=$(shellcheck -f gcc "$f" 2>/dev/null | wc -l)
        echo "   $f: $count avisos"
    done
else
    echo "=> shellcheck no disponible (se ejecuta dentro del contenedor de pruebas)"
fi

rm -f /tmp/lint_err
exit $FAILED

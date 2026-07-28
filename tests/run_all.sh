#!/bin/bash
# Suite completa de tests de refugiOS.
#
#   bash tests/run_all.sh          # todo salvo el build completo de imagen
#   bash tests/run_all.sh --quick  # solo lo que no necesita contenedor
#
# No requiere sudo: lo que necesita root se ejecuta en un contenedor privilegiado.
set -uo pipefail

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUICK=0
[ "${1:-}" == "--quick" ] && QUICK=1

FAILED=0
run() {
    echo
    echo "==============================================================="
    echo "== $1"
    echo "==============================================================="
    shift
    "$@" || FAILED=1
}

run "Comprobacion estatica (bash -n / py_compile)" bash "$TESTS_DIR/lint.sh"
run "Scripts Bash: i18n, lanzadores y test_boot" bash "$TESTS_DIR/unit_bash.sh"

if [ "$QUICK" -eq 0 ]; then
    run "install.py: descargas, timeouts, dialog y codigo de salida" \
        bash "$TESTS_DIR/run_in_container.sh" python3 -W ignore tests/unit_install.py
    run "install.sh: modo desarrollador y validaciones" \
        bash "$TESTS_DIR/run_in_container.sh" bash tests/test_install_sh.sh
    run "Bovedas: verificacion de contrasena y ciclo completo" \
        bash "$TESTS_DIR/run_in_container.sh" bash tests/test_vault.sh
    run "build_refugios.sh: aborto ante fallo e imagen limpia" \
        bash "$TESTS_DIR/run_in_container.sh" bash tests/test_build.sh
fi

echo
if [ "$FAILED" -eq 0 ]; then
    echo "=== SUITE COMPLETA: TODO CORRECTO ==="
else
    echo "=== SUITE COMPLETA: HAY FALLOS ==="
fi
exit $FAILED

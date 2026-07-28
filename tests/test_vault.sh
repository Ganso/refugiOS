#!/bin/bash
# Tests del gestor de bovedas (C6 verificacion de contrasena, C7 HOME ausente).
#
# Ejercita el mismo comando cryptsetup que emite refugios-vault.py, extraido del
# propio fichero para que el test se entere si alguien cambia las opciones.
# Requiere root real (cryptsetup), asi que va en el contenedor privilegiado:
#
#   tests/run_in_container.sh bash tests/test_vault.sh
set -uo pipefail

if [ "${REFUGIOS_IN_CONTAINER:-0}" != "1" ]; then
    echo "ERROR: ejecutalo con tests/run_in_container.sh bash tests/test_vault.sh"
    exit 1
fi

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$TESTS_DIR")"
VAULT_PY="$REPO_DIR/scripts/refugios-vault.py"
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
# C6 - La contrasena debe pedirse dos veces
# ============================================================================
echo "=> C6: verificacion de contrasena al crear la boveda"

# Se toman las opciones reales de luksFormat del script, sin duplicarlas aqui
LUKS_OPTS=$(grep -o 'cryptsetup luksFormat[^\\"]*' "$VAULT_PY" | head -1 | sed 's/cryptsetup luksFormat //')
echo "   opciones de luksFormat en el script: [$LUKS_OPTS]"

grep -q -- "--verify-passphrase" <<<"$LUKS_OPTS"
check $? "C6: el script usa --verify-passphrase"

# Los parametros de derivacion por defecto (argon2id con 1 GiB de memoria) tardan
# minutos por operacion en un contenedor y no tienen nada que ver con lo que se
# esta probando, que es la verificacion de la contrasena. Se abaratan solo aqui.
KDF_TUNING="--pbkdf pbkdf2 --pbkdf-force-iterations 1000"

run_luksformat() {
    # $1 = fichero, $2 = contrasena, $3 = confirmacion. Hace falta un terminal real
    # porque cryptsetup no verifica la contrasena sobre una tuberia.
    python3 "$TESTS_DIR/luks_pty.py" "$1" "$2" "$3" -- \
        $LUKS_OPTS $KDF_TUNING > "$WORK/luks_last.log" 2>&1
}

truncate -s 32M "$WORK/distintas.img"
run_luksformat "$WORK/distintas.img" "clave-correcta" "clave-EQUIVOCADA"
STATUS=$?
[ "$STATUS" -ne 0 ]
check $? "C6: dos contrasenas distintas se rechazan (codigo $STATUS)"

cryptsetup isLuks "$WORK/distintas.img" 2>/dev/null
[ $? -ne 0 ]
check $? "C6: no se crea ninguna boveda cuando las contrasenas no coinciden"

truncate -s 32M "$WORK/iguales.img"
run_luksformat "$WORK/iguales.img" "clave-correcta" "clave-correcta"
check $? "C6: dos contrasenas iguales crean la boveda"

cryptsetup isLuks "$WORK/iguales.img"
check $? "C6: la boveda resultante es un contenedor LUKS valido"

echo "clave-correcta" | cryptsetup open --test-passphrase "$WORK/iguales.img"
check $? "C6: la contrasena elegida abre la boveda"

echo "clave-EQUIVOCADA" | cryptsetup open --test-passphrase "$WORK/iguales.img" 2>/dev/null
[ $? -ne 0 ]
check $? "C6: una contrasena incorrecta no abre la boveda"

# Ciclo completo: abrir, escribir, cerrar, reabrir y comprobar el contenido
MAPPER="vault_test_$$"
echo "clave-correcta" | cryptsetup open "$WORK/iguales.img" "$MAPPER"
if [ $? -eq 0 ]; then
    mkfs.ext4 -q "/dev/mapper/$MAPPER"
    mkdir -p "$WORK/mnt"
    mount "/dev/mapper/$MAPPER" "$WORK/mnt"
    echo "contenido secreto" > "$WORK/mnt/nota.txt"
    umount "$WORK/mnt"
    cryptsetup close "$MAPPER"

    echo "clave-correcta" | cryptsetup open "$WORK/iguales.img" "$MAPPER"
    mount "/dev/mapper/$MAPPER" "$WORK/mnt"
    grep -q "contenido secreto" "$WORK/mnt/nota.txt"
    check $? "C6: los datos persisten tras cerrar y reabrir la boveda"
    umount "$WORK/mnt"
    cryptsetup close "$MAPPER"
else
    check 1 "C6: no se pudo abrir la boveda para el ciclo completo"
fi

# ============================================================================
# C7 - HOME sin definir da un mensaje claro, no una traza
# ============================================================================
echo "=> C7: HOME ausente"

OUT=$(env -u HOME python3 "$VAULT_PY" 2>&1)
STATUS=$?
[ "$STATUS" -ne 0 ]
check $? "C7: sin HOME el script termina con codigo != 0 (codigo $STATUS)"

grep -q "Traceback" <<<"$OUT"
[ $? -ne 0 ]
check $? "C7: no se muestra una traza de Python"

grep -qi "HOME" <<<"$OUT"
check $? "C7: el mensaje menciona HOME (obtenido: $(head -1 <<<"$OUT"))"

echo
if [ "$FAILED" -eq 0 ]; then
    echo "=> test_vault.sh: TODO CORRECTO"
else
    echo "=> test_vault.sh: HAY FALLOS"
fi
exit $FAILED

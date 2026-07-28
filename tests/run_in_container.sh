#!/bin/bash
# Ejecuta un comando dentro del contenedor de pruebas privilegiado.
#
#   tests/run_in_container.sh <comando> [args...]
#
# El repositorio se monta en /repo. Se necesita --privileged para losetup,
# mount y cryptsetup; el usuario pertenece al grupo docker, asi que no hace
# falta sudo en el anfitrion.
set -euo pipefail

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$TESTS_DIR")"
IMAGE_TAG="refugios-test:trixie"

if ! docker image inspect "$IMAGE_TAG" >/dev/null 2>&1; then
    echo "=> Construyendo la imagen de pruebas $IMAGE_TAG..."
    docker build -q -t "$IMAGE_TAG" "$TESTS_DIR/docker" >/dev/null
fi

exec docker run --rm --privileged \
    -v "$REPO_DIR:/repo" \
    -v /dev:/dev \
    -w /repo \
    -e REFUGIOS_IN_CONTAINER=1 \
    "$IMAGE_TAG" "$@"

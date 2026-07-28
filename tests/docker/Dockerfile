# Contenedor de pruebas de refugiOS.
# Da un root real (via `docker run --privileged`) para poder ejercitar debootstrap,
# dispositivos loop y cryptsetup sin depender de sudo en la maquina anfitriona.
FROM debian:trixie-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        debootstrap parted dosfstools e2fsprogs cryptsetup-bin \
        cloud-guest-utils util-linux mount kmod \
        aria2 wget curl ca-certificates \
        python3 python3-dialog dialog \
        shellcheck expect rsync jq file procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /repo

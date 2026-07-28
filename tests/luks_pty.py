#!/usr/bin/env python3
"""
Ejecuta 'cryptsetup luksFormat' sobre un terminal real y responde a sus prompts.

    tests/luks_pty.py FICHERO CONTRASENA CONFIRMACION -- [opciones de cryptsetup...]

Hace falta un pty porque cryptsetup se niega a verificar la contrasena sobre una
tuberia ("Can't do passphrase verification on non-tty inputs"). Devuelve el codigo
de salida de cryptsetup, o 99 si se agota el tiempo.
"""

import os
import pty
import select
import subprocess
import sys
import time

TIMEOUT = 300


def main():
    if "--" not in sys.argv:
        sys.exit(__doc__)
    sep = sys.argv.index("--")
    target, passphrase, verification = sys.argv[1:sep]
    options = sys.argv[sep + 1:]

    master, slave = pty.openpty()
    proc = subprocess.Popen(
        ["cryptsetup", "luksFormat"] + options + [target],
        stdin=slave, stdout=slave, stderr=slave, close_fds=True,
        preexec_fn=os.setsid,
    )
    os.close(slave)

    pending = [passphrase, verification]
    transcript = ""
    deadline = time.time() + TIMEOUT

    while time.time() < deadline:
        ready, _, _ = select.select([master], [], [], 1.0)
        if ready:
            try:
                chunk = os.read(master, 4096).decode(errors="replace")
            except OSError:
                break
            if not chunk:
                break
            transcript += chunk
            sys.stdout.write(chunk)
            sys.stdout.flush()

            lowered = transcript.lower()
            if pending and lowered.rstrip().endswith(":"):
                # cryptsetup vacia la entrada anticipada al desactivar el eco,
                # asi que se espera a que el prompt este completo antes de escribir
                time.sleep(0.3)
                os.write(master, (pending.pop(0) + "\n").encode())
                transcript = ""
        elif proc.poll() is not None:
            break

    try:
        code = proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        print("\nTIMEOUT: cryptsetup no termino", file=sys.stderr)
        return 99

    os.close(master)
    return code


if __name__ == "__main__":
    sys.exit(main())

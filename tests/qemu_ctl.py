#!/usr/bin/env python3
"""
Control interactivo de una VM lanzada por qemu_boot_check.py --keep.

    tests/qemu_ctl.py SOCKET shot NOMBRE      captura la pantalla en un PNG
    tests/qemu_ctl.py SOCKET key K [K...]     envia teclas (sintaxis QMP: ret, tab, spc,
                                              down, up, alt-f2, shift-a, ...)
    tests/qemu_ctl.py SOCKET text "cadena"    teclea una cadena ASCII
"""

import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qemu_boot_check import Qmp  # noqa: E402

SPECIAL = {
    " ": "spc", "\n": "ret", "-": "minus", "=": "equal", "/": "slash",
    ".": "dot", ",": "comma", ";": "semicolon", "'": "apostrophe",
    "[": "bracket_left", "]": "bracket_right", "\\": "backslash",
}
SHIFTED = {
    ":": "semicolon", "_": "minus", "?": "slash", "+": "equal", '"': "apostrophe",
    "~": "grave_accent", "|": "backslash", "(": "9", ")": "0", "!": "1", "@": "2",
    "#": "3", "$": "4", "%": "5", "^": "6", "&": "7", "*": "8",
}


def send_key(qmp, combo):
    keys = []
    for part in combo.split("-"):
        keys.append({"type": "qcode", "data": part})
    qmp.command("send-key", keys=keys)


def send_text(qmp, text):
    for ch in text:
        if ch.isalnum():
            if ch.isupper():
                send_key(qmp, f"shift-{ch.lower()}")
            else:
                send_key(qmp, ch)
        elif ch in SPECIAL:
            send_key(qmp, SPECIAL[ch])
        elif ch in SHIFTED:
            send_key(qmp, f"shift-{SHIFTED[ch]}")
        else:
            raise SystemExit(f"caracter no soportado: {ch!r}")
        time.sleep(0.05)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    sock, action = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    qmp = Qmp(sock, timeout=10)

    if action == "shot":
        name = args[0] if args else f"shot_{int(time.time())}"
        out_dir = os.path.dirname(os.path.abspath(sock))
        ppm = os.path.join(out_dir, name + ".ppm")
        png = os.path.join(out_dir, name + ".png")
        qmp.command("screendump", filename=ppm)
        for _ in range(20):
            if os.path.exists(ppm) and os.path.getsize(ppm) > 0:
                break
            time.sleep(0.25)
        subprocess.run(["convert", ppm, png], check=True)
        os.unlink(ppm)
        print(png)
    elif action in ("click", "dblclick"):
        x, y = int(args[0]), int(args[1])
        # Las coordenadas absolutas se normalizan contra el tamano de la pantalla
        # virtual; se puede indicar otro si la VM no arranco a 1920x1080
        width = int(args[2]) if len(args) > 2 else 1920
        height = int(args[3]) if len(args) > 3 else 1080
        qmp.command("input-send-event", events=[
            {"type": "abs", "data": {"axis": "x", "value": x * 32767 // width}},
            {"type": "abs", "data": {"axis": "y", "value": y * 32767 // height}},
        ])
        time.sleep(0.3)
        for _ in (1, 2) if action == "dblclick" else (1,):
            qmp.command("input-send-event",
                        events=[{"type": "btn", "data": {"down": True, "button": "left"}}])
            qmp.command("input-send-event",
                        events=[{"type": "btn", "data": {"down": False, "button": "left"}}])
            time.sleep(0.08)
        print(f"{action} en ({x}, {y})")
    elif action == "key":
        for combo in args:
            send_key(qmp, combo)
            time.sleep(0.15)
        print(f"enviadas {len(args)} teclas")
    elif action == "text":
        send_text(qmp, " ".join(args))
        print("texto enviado")
    else:
        sys.exit(__doc__)

    qmp.close()


if __name__ == "__main__":
    main()

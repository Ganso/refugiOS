#!/usr/bin/env python3
"""
Arranca una imagen de refugiOS en QEMU sin interfaz grafica y toma capturas de
pantalla en los instantes indicados, para poder verificar el arranque de forma
automatica (GRUB -> LightDM con autologin -> escritorio XFCE).

Uso:
    tests/qemu_boot_check.py IMAGEN [--shots 45,90,150] [--out tests/out]
                             [--net user|none] [--ram 4] [--keep]

Las capturas se guardan como PNG en el directorio de salida. Con --keep la
maquina virtual sigue viva al terminar (util para inspeccionar a mano); el
identificador del proceso se deja en <out>/qemu.pid.
"""

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time

OVMF_CANDIDATES = [
    ("/usr/share/OVMF/OVMF_CODE_4M.fd", "/usr/share/OVMF/OVMF_VARS_4M.fd"),
    ("/usr/share/OVMF/OVMF_CODE.fd", "/usr/share/OVMF/OVMF_VARS.fd"),
    ("/usr/share/edk2/ovmf/OVMF_CODE.fd", "/usr/share/edk2/ovmf/OVMF_VARS.fd"),
]


def find_ovmf():
    for code, varsf in OVMF_CANDIDATES:
        if os.path.isfile(code) and os.path.isfile(varsf):
            return code, varsf
    sys.exit("ERROR: no se encontro el firmware OVMF (paquete 'ovmf').")


class Qmp:
    def __init__(self, path, timeout=60):
        deadline = time.time() + timeout
        while True:
            try:
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(path)
                break
            except OSError:
                if time.time() > deadline:
                    raise
                time.sleep(0.5)
        self.f = self.sock.makefile("rw", encoding="utf-8", newline="\n")
        self.f.readline()  # saludo
        self.command("qmp_capabilities")

    def command(self, name, **args):
        msg = {"execute": name}
        if args:
            msg["arguments"] = args
        self.f.write(json.dumps(msg) + "\n")
        self.f.flush()
        while True:
            line = self.f.readline()
            if not line:
                raise RuntimeError("QMP cerro la conexion")
            resp = json.loads(line)
            if "event" in resp:
                continue
            if "error" in resp:
                raise RuntimeError(f"QMP {name}: {resp['error']}")
            return resp.get("return")

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--shots", default="45,90,150,210")
    ap.add_argument("--out", default="tests/out")
    ap.add_argument("--net", default="user", choices=["user", "none"])
    ap.add_argument("--ram", default="4", help="GiB de RAM para la VM")
    ap.add_argument("--size", default="1920x1080", help="resolucion de la pantalla virtual")
    ap.add_argument("--prefix", default="boot")
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()

    try:
        xres, yres = (int(v) for v in args.size.lower().split("x"))
    except ValueError:
        sys.exit(f"ERROR: resolucion no valida: {args.size} (formato: 1920x1080)")

    if not os.path.isfile(args.image):
        sys.exit(f"ERROR: no existe la imagen {args.image}")

    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    code, vars_template = find_ovmf()
    vars_file = os.path.join(out_dir, f"{args.prefix}_OVMF_VARS.fd")
    shutil.copy(vars_template, vars_file)

    qmp_path = os.path.join(out_dir, f"{args.prefix}_qmp.sock")
    if os.path.exists(qmp_path):
        os.unlink(qmp_path)

    cmd = [
        "qemu-system-x86_64",
        "-m", f"{args.ram}G",
        "-smp", "2",
        "-drive", f"file={os.path.abspath(args.image)},format=raw,index=0,media=disk",
        "-drive", f"if=pflash,format=raw,readonly=on,file={code}",
        "-drive", f"if=pflash,format=raw,file={vars_file}",
        # La resolucion preferida se anuncia por EDID, para que el servidor X del
        # invitado arranque directamente en ella
        "-vga", "none",
        "-device", f"virtio-vga,xres={xres},yres={yres}",
        "-display", "none",
        "-qmp", f"unix:{qmp_path},server,nowait",
    ]
    if os.access("/dev/kvm", os.W_OK):
        cmd += ["-enable-kvm", "-cpu", "host"]
    if args.net == "user":
        cmd += ["-net", "nic", "-net", "user"]
    else:
        cmd += ["-net", "none"]

    print("=> " + " ".join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    shots = sorted(int(s) for s in args.shots.split(",") if s.strip())
    produced = []
    try:
        try:
            qmp = Qmp(qmp_path)
        except OSError:
            if proc.poll() is not None:
                err = proc.stderr.read().decode(errors="replace")
                sys.exit(f"ERROR: QEMU no arranco:\n{err}")
            raise
        start = time.time()
        for when in shots:
            wait = when - (time.time() - start)
            if wait > 0:
                time.sleep(wait)
            if proc.poll() is not None:
                err = proc.stderr.read().decode(errors="replace")
                sys.exit(f"ERROR: QEMU murio antes del segundo {when}:\n{err}")
            ppm = os.path.join(out_dir, f"{args.prefix}_{when:04d}s.ppm")
            png = ppm[:-4] + ".png"
            qmp.command("screendump", filename=ppm)
            for _ in range(20):
                if os.path.exists(ppm) and os.path.getsize(ppm) > 0:
                    break
                time.sleep(0.25)
            subprocess.run(["convert", ppm, png], check=True)
            os.unlink(ppm)
            produced.append(png)
            print(f"   captura t={when}s -> {png}")
        qmp.close()
    finally:
        if args.keep:
            with open(os.path.join(out_dir, f"{args.prefix}_qemu.pid"), "w") as f:
                f.write(str(proc.pid))
            print(f"=> VM viva (pid {proc.pid}); matala con: kill {proc.pid}")
        else:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()

    print("\n".join(produced))


if __name__ == "__main__":
    main()

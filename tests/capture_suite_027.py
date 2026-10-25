#!/usr/bin/env python3
"""
Synchronized capture of 0.27 features inside refugiOS under QEMU at 1920x1080:
1. 10_escritorio.png: Full modern desktop with 9 modules + Biblioteca folder
2. 22_biblioteca.png: "Biblioteca refugiOS" folder open in Thunar with the full catalog
3. 23_comprobacion.png: "Comprobar refugiOS" diagnostic tool in action
4. 24_actualizador.png: "Actualizar refugiOS" update tool
"""

import json
import os
import shutil
import socket
import subprocess
import sys
import time

OVMF_CODE = "/usr/share/OVMF/OVMF_CODE_4M.fd"
OVMF_VARS_TEMPLATE = "/usr/share/OVMF/OVMF_VARS_4M.fd"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_PATH = os.path.join(ROOT_DIR, "tests/out/test_es.qcow2")
VARS_PATH = os.path.join(ROOT_DIR, "tests/out/suite_VARS.fd")
QMP_PATH = os.path.join(ROOT_DIR, "tests/out/suite_qmp.sock")

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
        self.f.readline()
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
                raise RuntimeError("QMP closed connection")
            resp = json.loads(line)
            if "event" in resp:
                continue
            if "error" in resp:
                raise RuntimeError(f"QMP {name}: {resp['error']}")
            return resp.get("return")

    def screendump(self, out_png):
        ppm = out_png + ".ppm"
        self.command("screendump", filename=ppm)
        for _ in range(25):
            if os.path.exists(ppm) and os.path.getsize(ppm) > 0:
                break
            time.sleep(0.2)
        subprocess.run(["convert", ppm, out_png], check=True)
        if os.path.exists(ppm):
            os.unlink(ppm)

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


def main():
    shutil.copy(OVMF_VARS_TEMPLATE, VARS_PATH)
    if os.path.exists(QMP_PATH):
        os.unlink(QMP_PATH)

    # Start TCP sync server on host
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("0.0.0.0", 9999))
    server_sock.listen(5)
    server_sock.settimeout(180)  # max 3 minutes total

    cmd = [
        "qemu-system-x86_64",
        "-enable-kvm", "-cpu", "host",
        "-m", "4G",
        "-smp", "2",
        "-drive", f"file={IMAGE_PATH},format=qcow2,index=0,media=disk",
        "-drive", f"if=pflash,format=raw,readonly=on,file={OVMF_CODE}",
        "-drive", f"if=pflash,format=raw,file={VARS_PATH}",
        "-vga", "none",
        "-device", "virtio-vga,xres=1920,yres=1080",
        "-display", "none",
        "-qmp", f"unix:{QMP_PATH},server,nowait",
        "-net", "nic", "-net", "user",
    ]

    print("=> Starting QEMU...")
    proc = subprocess.Popen(cmd)
    try:
        qmp = Qmp(QMP_PATH)
        print("=> QMP connected. Waiting for guest sync signals...")

        shot1_es = os.path.join(ROOT_DIR, "media/screenshots/es/10_escritorio.png")
        shot1_en = os.path.join(ROOT_DIR, "media/screenshots/en/10_desktop.png")
        shot2_es = os.path.join(ROOT_DIR, "media/screenshots/es/22_biblioteca.png")
        shot2_en = os.path.join(ROOT_DIR, "media/screenshots/en/22_library.png")
        shot3_es = os.path.join(ROOT_DIR, "media/screenshots/es/23_comprobacion.png")
        shot3_en = os.path.join(ROOT_DIR, "media/screenshots/en/23_check.png")
        shot4_es = os.path.join(ROOT_DIR, "media/screenshots/es/24_actualizador.png")
        shot4_en = os.path.join(ROOT_DIR, "media/screenshots/en/24_updater.png")

        captured = set()
        while len(captured) < 4:
            conn, addr = server_sock.accept()
            try:
                data = conn.recv(1024).decode("utf-8").strip()
                print(f"=> Signal from guest: '{data}'")
                if data == "step1_desktop":
                    qmp.screendump(shot1_es)
                    shutil.copy(shot1_es, shot1_en)
                    captured.add(1)
                    print(f"=> [1/4] Desktop captured: {shot1_es}")
                    conn.sendall(b"ok\n")
                elif data == "step2_library":
                    qmp.screendump(shot2_es)
                    shutil.copy(shot2_es, shot2_en)
                    captured.add(2)
                    print(f"=> [2/4] Library captured: {shot2_es}")
                    conn.sendall(b"ok\n")
                elif data == "step3_check":
                    qmp.screendump(shot3_es)
                    shutil.copy(shot3_es, shot3_en)
                    captured.add(3)
                    print(f"=> [3/4] System check captured: {shot3_es}")
                    conn.sendall(b"ok\n")
                elif data == "step4_updater":
                    qmp.screendump(shot4_es)
                    shutil.copy(shot4_es, shot4_en)
                    captured.add(4)
                    print(f"=> [4/4] Updater captured: {shot4_es}")
                    conn.sendall(b"ok\n")
                elif data == "done":
                    conn.sendall(b"ok\n")
                    break
                else:
                    conn.sendall(b"ignored\n")
            finally:
                conn.close()

        qmp.close()
    finally:
        server_sock.close()
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("=> All captures finished!")

if __name__ == "__main__":
    main()

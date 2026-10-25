#!/usr/bin/env python3
"""
Automated capture of LocalTranslate inside refugiOS under QEMU at 1920x1080.
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
VARS_PATH = os.path.join(ROOT_DIR, "tests/out/trans_VARS.fd")
QMP_PATH = os.path.join(ROOT_DIR, "tests/out/trans_qmp.sock")

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

    def send_key(self, combo):
        keys = []
        for part in combo.split("-"):
            keys.append({"type": "qcode", "data": part})
        self.command("send-key", keys=keys)
        time.sleep(0.12)

    def click(self, x, y, width=1920, height=1080):
        self.command("input-send-event", events=[
            {"type": "abs", "data": {"axis": "x", "value": x * 32767 // width}},
            {"type": "abs", "data": {"axis": "y", "value": y * 32767 // height}},
        ])
        time.sleep(0.3)
        self.command("input-send-event", events=[{"type": "btn", "data": {"down": True, "button": "left"}}])
        self.command("input-send-event", events=[{"type": "btn", "data": {"down": False, "button": "left"}}])
        time.sleep(0.2)

    def send_text(self, text):
        special = {
            " ": "spc", "\n": "ret", "-": "minus", "=": "equal", "/": "slash",
            ".": "dot", ",": "comma", ";": "semicolon", "'": "apostrophe",
            "[": "bracket_left", "]": "bracket_right", "\\": "backslash",
        }
        shifted = {
            ":": "semicolon", "_": "minus", "?": "slash", "+": "equal", '"': "apostrophe",
            "~": "grave_accent", "|": "backslash", "(": "9", ")": "0", "!": "1", "@": "2",
            "#": "3", "$": "4", "%": "5", "^": "6", "&": "7", "*": "8",
        }
        for ch in text:
            if ch.isalnum():
                if ch.isupper():
                    self.send_key(f"shift-{ch.lower()}")
                else:
                    self.send_key(ch)
            elif ch in special:
                self.send_key(special[ch])
            elif ch in shifted:
                self.send_key(f"shift-{shifted[ch]}")
            else:
                self.send_key("spc")
            time.sleep(0.04)

    def screendump(self, out_png):
        ppm = out_png + ".ppm"
        self.command("screendump", filename=ppm)
        for _ in range(20):
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
        print("=> QMP connected. Waiting for system boot and auto-start (75s)...")
        for i in range(15):
            time.sleep(5)
            print(f"   booting... {(i+1)*5}s")

        # Focus input area inside LocalTranslate window
        print("=> Clicking input area in LocalTranslate...")
        qmp.click(200, 220)
        time.sleep(1)

        # Type sample translation text
        text = "refugiOS proporciona herramientas criticas y conocimiento offline en emergencias."
        print(f"=> Typing: {text}")
        qmp.send_text(text)
        time.sleep(1)

        # Tab to Translate button and trigger
        print("=> Triggering Translate button...")
        qmp.send_key("tab")
        time.sleep(0.3)
        qmp.send_key("tab")
        time.sleep(0.3)
        qmp.send_key("ret")
        time.sleep(5)

        # Save final screenshots
        final_png = os.path.join(ROOT_DIR, "media/screenshots/es/21_traductor.png")
        qmp.screendump(final_png)
        print(f"=> Final evidence captured: {final_png}")

        en_png = os.path.join(ROOT_DIR, "media/screenshots/en/21_translator.png")
        shutil.copy(final_png, en_png)
        print(f"=> English mirror created: {en_png}")

        qmp.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("=> QEMU finished.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Tests de las funciones de install.py corregidas (C8, C9, C10, C11, C12).

install.py solo ejecuta main() bajo __main__, asi que se puede importar sin
efectos secundarios. Se ejecuta con:

    tests/run_in_container.sh python3 tests/unit_install.py
"""

import hashlib
import http.server
import importlib.util
import io
import os
import socket
import socketserver
import sys
import tempfile
import threading
import time
import unittest

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_DIR)

spec = importlib.util.spec_from_file_location("install", os.path.join(REPO_DIR, "install.py"))
install = importlib.util.module_from_spec(spec)
spec.loader.exec_module(install)


PAYLOAD = os.urandom(3 * 1024 * 1024)
PAYLOAD_SHA = hashlib.sha256(PAYLOAD).hexdigest()


class FlakyHandler(http.server.BaseHTTPRequestHandler):
    """Sirve PAYLOAD; con truncate=True corta la conexion a mitad de envio."""

    truncate = True

    def do_GET(self):
        start = 0
        rng = self.headers.get("Range")
        if rng and rng.startswith("bytes="):
            start = int(rng.split("=")[1].split("-")[0])

        body = PAYLOAD[start:]
        if start:
            self.send_response(206)
            self.send_header("Content-Range",
                             f"bytes {start}-{len(PAYLOAD) - 1}/{len(PAYLOAD)}")
        else:
            self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()

        if type(self).truncate:
            self.wfile.write(body[: len(body) // 3])
            self.wfile.flush()
            self.close_connection = True
            try:
                self.connection.close()
            except OSError:
                pass
        else:
            self.wfile.write(body)

    def log_message(self, *args):
        pass


class BlackHoleServer(threading.Thread):
    """Acepta conexiones TCP y no responde jamas."""

    def __init__(self):
        super().__init__(daemon=True)
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(5)
        self.port = self.sock.getsockname()[1]
        self._accepted = []

    def run(self):
        while True:
            try:
                conn, _ = self.sock.accept()
                self._accepted.append(conn)
            except OSError:
                return


class TestDownloadResume(unittest.TestCase):
    """C8: un fallo de descarga debe conservar el parcial para poder reanudar."""

    def setUp(self):
        FlakyHandler.truncate = True
        self.httpd = socketserver.TCPServer(("127.0.0.1", 0), FlakyHandler)
        self.port = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        self.httpd.shutdown()

    def test_partial_survives_and_resumes(self):
        url = f"http://127.0.0.1:{self.port}/modelo.gguf"
        dest = os.path.join(self.tmp, "modelo.gguf")

        ok = install.download_with_aria2(url, dest, timeout=30, max_tries=1)
        self.assertFalse(ok, "la descarga truncada deberia fallar")
        self.assertTrue(os.path.exists(dest),
                        "C8: el fichero parcial se ha borrado; seria imposible reanudar")
        partial_size = os.path.getsize(dest)
        self.assertGreater(partial_size, 0)
        self.assertLess(partial_size, len(PAYLOAD))

        # Ahora el servidor responde entero: debe reanudar, no empezar de cero
        FlakyHandler.truncate = False
        ok = install.download_with_aria2(url, dest, timeout=60, max_tries=2)
        self.assertTrue(ok, "la segunda descarga deberia completarse")
        with open(dest, "rb") as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), PAYLOAD_SHA)
        self.assertFalse(os.path.exists(dest + ".aria2"),
                         "el fichero de control .aria2 deberia limpiarse al terminar")

    def test_small_files_discard_partial(self):
        """Los ficheros pequenos (scripts) no deben dejar restos truncados."""
        url = f"http://127.0.0.1:{self.port}/refugios-maps.sh"
        dest = os.path.join(self.tmp, "refugios-maps.sh")
        ok = install.download_with_aria2(url, dest, timeout=30, max_tries=1,
                                         keep_partial=False)
        self.assertFalse(ok)
        self.assertFalse(os.path.exists(dest),
                         "un script truncado no debe quedar en disco: se tomaria por valido")


class TestFetchTimeout(unittest.TestCase):
    """C9: fetch_url no puede colgarse contra un servidor que no responde."""

    def test_timeout(self):
        server = BlackHoleServer()
        server.start()
        install.FETCH_TIMEOUT = 5

        outcome = {}

        def call():
            try:
                install.fetch_url(f"http://127.0.0.1:{server.port}/")
                outcome["result"] = "ok"
            except Exception as exc:  # noqa: BLE001 - cualquier fallo vale
                outcome["result"] = type(exc).__name__

        # Vigilante propio: sin timeout en fetch_url el hilo no termina nunca
        worker = threading.Thread(target=call, daemon=True)
        worker.start()
        worker.join(20)

        self.assertFalse(worker.is_alive(),
                         "C9: fetch_url sigue colgado tras 20s contra un servidor mudo")
        self.assertNotEqual(outcome.get("result"), "ok")


class TestVersionOrder(unittest.TestCase):
    """C10: las versiones se comparan numericamente, no como texto."""

    def test_picks_highest_version(self):
        names = [
            "kiwix-desktop_x86_64_2.3.1.appimage",
            "kiwix-desktop_x86_64_2.10.0.appimage",
            "kiwix-desktop_x86_64_2.9.1.appimage",
        ]
        self.assertEqual(sorted(names, key=install.version_key)[-1],
                         "kiwix-desktop_x86_64_2.10.0.appimage")
        # El orden lexicografico antiguo elegia la 2.9.1
        self.assertEqual(sorted(names)[-1], "kiwix-desktop_x86_64_2.9.1.appimage")


class FakeDialog:
    """Doble de dialog.Dialog que valida lo que se le pasa (como hace la libreria real)."""

    OK = "ok"

    def __init__(self, *a, **kw):
        self.seen = []

    def add_persistent_args(self, args):
        pass

    def _record(self, *texts):
        for t in texts:
            if t is None:
                continue
            self.seen.append(t)
            # La libreria dialog codifica en latin-1: esto reproduce el fallo real
            t.encode("latin-1")

    def checklist(self, text, choices=None, title=None, **kw):
        self._record(text, title, *[c[1] for c in choices or []])
        return (self.OK, [])

    def menu(self, text, choices=None, title=None, **kw):
        self._record(text, title, *[c[1] for c in choices or []])
        return (self.OK, "1")

    def yesno(self, text, title=None, **kw):
        self._record(text, title)
        return self.OK

    def msgbox(self, text, title=None, **kw):
        self._record(text, title)
        return self.OK


class TestDialogSanitizing(unittest.TestCase):
    """C11: ningun texto no-latin1 puede llegar a los widgets de dialog."""

    NASTY = "Wikipedia • completa — “todo”… 你好"

    def test_menus_sanitize(self):
        d = FakeDialog()
        options = [{"label": self.NASTY}, {"label": "otra"}]

        install.multi_select_menu(d, self.NASTY, options, [0])
        install.single_select_menu(d, self.NASTY, options, 0)
        install.simple_question(d, self.NASTY, self.NASTY)

        self.assertTrue(d.seen)
        for text in d.seen:
            text.encode("latin-1")  # falla la prueba si algo se colo sin sanear


class TestDeveloperModeScripts(unittest.TestCase):
    """C3 (install.py): con una copia del repositorio, los scripts locales mandan."""

    def test_local_scripts_win(self):
        source = open(os.path.join(REPO_DIR, "install.py"), encoding="utf-8").read()
        body = source.split("def fetch_script(")[1].split("\n    if install_maps")[0]
        local_check = body.index("os.path.exists(local_s)")
        download = body.index("download_with_aria2")
        self.assertLess(local_check, download,
                        "fetch_script descarga antes de mirar la copia local: el "
                        "Developer Mode no llega a los scripts")


class TestTranslationKeys(unittest.TestCase):
    """Ninguna clave usada puede quedar sin traducir: el usuario veria la clave cruda."""

    def test_every_key_is_translated(self):
        import re
        import i18n

        used = set()
        for name in ("install.py", "scripts/refugios-vault.py"):
            with open(os.path.join(REPO_DIR, name), encoding="utf-8") as f:
                used |= set(re.findall(r"i18n\.T\(\s*['\"]([a-zA-Z0-9_]+)['\"]", f.read()))

        english = set(i18n.TRANSLATIONS["en"])
        spanish = set(i18n.TRANSLATIONS["es"])

        self.assertEqual(sorted(used - english), [],
                         "claves sin traduccion en ingles")
        self.assertEqual(sorted(used - spanish), [],
                         "claves sin traduccion en espanol")


class TestExitCode(unittest.TestCase):
    """C12: si algun modulo fallo, el instalador debe salir con codigo != 0."""

    def test_failed_items_exit_nonzero(self):
        source = open(os.path.join(REPO_DIR, "install.py"), encoding="utf-8").read()
        self.assertIn("sys.exit(1)", source.split("if FAILED_ITEMS:")[1][:400],
                      "el bloque de errores finales no propaga un codigo de salida")


if __name__ == "__main__":
    unittest.main(verbosity=2)

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

    checklist_all = False

    def checklist(self, text, choices=None, title=None, **kw):
        self._record(text, title, *[c[1] for c in choices or []])
        return (self.OK, [c[0] for c in choices or []] if type(self).checklist_all else [])

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


class TestSourceDir(unittest.TestCase):
    """install.sh ejecuta una copia de install.py: la ruta del repositorio llega por entorno."""

    def test_env_wins_when_it_is_a_checkout(self):
        saved = os.environ.get("REFUGIOS_SRC_DIR")
        try:
            os.environ["REFUGIOS_SRC_DIR"] = REPO_DIR
            self.assertEqual(install.source_dir(), REPO_DIR)
            os.environ["REFUGIOS_SRC_DIR"] = tempfile.mkdtemp()
            self.assertEqual(install.source_dir(), os.path.dirname(os.path.realpath(install.__file__)))
        finally:
            if saved is None:
                os.environ.pop("REFUGIOS_SRC_DIR", None)
            else:
                os.environ["REFUGIOS_SRC_DIR"] = saved

    def test_fetch_script_uses_it(self):
        source = open(os.path.join(REPO_DIR, "install.py"), encoding="utf-8").read()
        body = source.split("def fetch_script(")[1].split("\n    if install_maps")[0]
        self.assertIn("source_dir()", body)


class TestTranslationKeys(unittest.TestCase):
    """Ninguna clave usada puede quedar sin traducir: el usuario veria la clave cruda."""

    def test_every_key_is_translated(self):
        import re
        import i18n

        used = set()
        for name in ("install.py", "scripts/refugios-vault.py", "scripts/refugios-check.py"):
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


class RoutedHandler(http.server.BaseHTTPRequestHandler):
    """Sirve un diccionario ruta -> (codigo, cabeceras, cuerpo). Lo demas es 404."""

    routes = {}

    def _answer(self, with_body):
        code, headers, body = type(self).routes.get(self.path.split("?")[0], (404, {}, b""))
        self.send_response(code)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if with_body:
            self.wfile.write(body)

    def do_GET(self):
        self._answer(True)

    def do_HEAD(self):
        self._answer(False)

    def log_message(self, *args):
        pass


class RoutedServerCase(unittest.TestCase):
    def setUp(self):
        RoutedHandler.routes = {}
        self.httpd = socketserver.TCPServer(("127.0.0.1", 0), RoutedHandler)
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.tmp = tempfile.mkdtemp()
        install._LISTING_CACHE.clear()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()


class TestCatalog(unittest.TestCase):
    """El catalogo es datos: cualquier error en una entrada rompe el instalador en marcha."""

    def test_entries_are_complete_and_translated(self):
        import i18n
        groups = {g['id'] for g in install.LIBRARY_GROUPS}
        ids = set()
        for e in install.WIKIPEDIA_CONFIG + install.LIBRARY_CATALOG:
            self.assertNotIn(e['id'], ids, f"id repetido: {e['id']}")
            ids.add(e['id'])
            self.assertTrue(e['urls'] and all(u.endswith('/') for u in e['urls']), e['id'])
            keys = [e['label_key']] + ([e['title_key']] if 'title_key' in e else [])
            for k in keys:
                for lang in ('en', 'es'):
                    self.assertIn(k, i18n.TRANSLATIONS[lang], f"{k} sin traducir en {lang}")
            for lang in ('en', 'es'):
                self.assertGreater(install.entry_size_mb(e, lang), 0, e['id'])
        for e in install.LIBRARY_CATALOG:
            self.assertIn(e['group'], groups, e['id'])
            self.assertTrue(set(e.get('presets', [])) <= {"lite", "standard", "rich"}, e['id'])
        for g in install.LIBRARY_GROUPS:
            for lang in ('en', 'es'):
                self.assertIn(g['title_key'], i18n.TRANSLATIONS[lang])
        for p in install.MAP_PRESETS:
            for lang in ('en', 'es'):
                self.assertIn(p['label_key'], i18n.TRANSLATIONS[lang])

    def test_labels_survive_dialog(self):
        for lang in ('en', 'es'):
            for e in install.WIKIPEDIA_CONFIG + install.visible_catalog(lang):
                install.sanitize_for_dialog(install.catalog_label(e, lang)).encode("latin-1")

    def test_language_fallback(self):
        entry = {"stem": "wikipedia_{lang}_top_mini"}
        self.assertEqual(install.zim_stems(entry, "es"),
                         ["wikipedia_es_top_mini", "wikipedia_en_top_mini"])
        self.assertEqual(install.zim_stems(entry, "en"), ["wikipedia_en_top_mini"])
        self.assertEqual(install.zim_stems({"stem": "zimgit-water_en"}, "es"), ["zimgit-water_en"])

    def test_spanish_only_books_hidden_in_english(self):
        en_ids = {e['id'] for e in install.visible_catalog('en')}
        es_ids = {e['id'] for e in install.visible_catalog('es')}
        self.assertNotIn('gutenberg', en_ids)
        self.assertIn('gutenberg', es_ids)

    def test_default_wiki_fits_the_disk(self):
        # Un pendrive de 16 GB deja unos 10 GB libres: nunca la Wikipedia completa
        idx = install.default_wiki_index(10000, 'es')
        self.assertLessEqual(install.entry_size_mb(install.WIKIPEDIA_CONFIG[idx - 1], 'es'), 3500)
        # La inglesa completa pesa >100 GB: con 100 GB libres no se preselecciona
        idx = install.default_wiki_index(100000, 'en')
        self.assertNotEqual(install.WIKIPEDIA_CONFIG[idx - 1]['id'], 'wiki_total')
        self.assertEqual(install.default_wiki_index(100, 'es'), 1)


class TestLocalDetection(unittest.TestCase):
    """Una descarga interrumpida no puede contar como instalada."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def touch(self, name):
        open(os.path.join(self.dir, name), "w").close()

    def test_partial_and_sidecar_files_ignored(self):
        entry = {"stem": "wikivoyage_{lang}_all_maxi"}
        self.touch("wikivoyage_es_all_maxi_2026-01.zim")
        self.touch("wikivoyage_es_all_maxi_2026-01.zim.sha256")
        self.touch("wikivoyage_es_all_maxi_2026-09.zim")
        self.touch("wikivoyage_es_all_maxi_2026-09.zim.aria2")
        self.assertEqual(install.find_local_zim(self.dir, entry, "es"),
                         "wikivoyage_es_all_maxi_2026-01.zim")

    def test_english_fallback_found(self):
        self.touch("wikem_en_all_maxi_2026-10.zim")
        self.assertEqual(install.find_local_zim(self.dir, {"stem": "wikem_en_all_maxi"}, "es"),
                         "wikem_en_all_maxi_2026-10.zim")

    def test_ai_symlink_never_points_to_partial(self):
        base = tempfile.mkdtemp()
        env = install.TargetEnv(base, os.path.join(base, "Desktop"))
        install.ensure_dirs(env)
        m = install.AI_MODEL_CONFIG[0]
        path = os.path.join(env.ai_dir, m['filename'])
        open(path, "w").close()
        open(path + ".aria2", "w").close()
        open(path + ".sha256", "w").close()
        open(os.path.join(env.know_dir, "x"), "w").close()

        class Info:
            lang = "es"
        install.sync_resources(env, Info(), "kiwix-desktop")
        link = os.path.join(base, "AI", m['symlink'])
        self.assertFalse(os.path.lexists(link), "enlace a un modelo a medio descargar")
        os.remove(path + ".aria2")
        install.sync_resources(env, Info(), "kiwix-desktop")
        self.assertEqual(os.path.realpath(link), os.path.realpath(path))


class TestLibraryLaunchers(unittest.TestCase):
    """Los libros principales van al escritorio; el resto, a la carpeta de biblioteca."""

    def test_desktop_and_library_folder(self):
        import i18n
        base = tempfile.mkdtemp()
        env = install.TargetEnv(base, os.path.join(base, "Desktop"))
        install.ensure_dirs(env)
        for name in ("wikipedia_es_top_mini_2026-10.zim", "wikipedia_es_medicine_maxi_2026-10.zim",
                     "zimgit-water_en_2024-08.zim"):
            open(os.path.join(env.know_dir, name), "w").close()

        class Info:
            lang = "es"
        install.sync_resources(env, Info(), "kiwix-desktop")
        library = os.path.join(env.desktop, i18n.T('library_folder'))
        self.assertTrue(os.path.isfile(os.path.join(env.desktop, "Knowledge_wikipedia.desktop")))
        self.assertTrue(os.path.isfile(os.path.join(env.desktop, "Knowledge_wikimed.desktop")))
        self.assertTrue(os.path.isfile(os.path.join(library, "Knowledge_water.desktop")))
        self.assertEqual(os.path.realpath(os.path.join(base, "Knowledge", "water.zim")),
                         os.path.realpath(os.path.join(env.know_dir, "zimgit-water_en_2024-08.zim")))

        # Si el recurso desaparece, su icono y la carpeta vacia tambien
        os.remove(os.path.join(env.know_dir, "zimgit-water_en_2024-08.zim"))
        install.sync_resources(env, Info(), "kiwix-desktop")
        self.assertFalse(os.path.exists(library))


class TestRemoteResolution(RoutedServerCase):
    def test_newest_file_and_mirrors(self):
        listing = ('<a href="phet_es_all_2026-01.zim">x</a> <a href="phet_es_all_2026-08.zim">x</a>'
                   '<a href="phet_en_all_2026-09.zim">x</a>').encode()
        RoutedHandler.routes = {
            "/a/": (200, {}, listing),
            "/b/": (200, {}, b'<a href="phet_es_all_2026-08.zim">x</a>'),
        }
        entry = {"id": "phet", "stem": "phet_{lang}_all", "urls": [self.base + "/a/", self.base + "/b/"]}
        name, mirrors = install.find_remote_zim(entry, "es")
        self.assertEqual(name, "phet_es_all_2026-08.zim")
        self.assertEqual(mirrors, [self.base + "/a/", self.base + "/b/"])

    def test_falls_back_to_english(self):
        RoutedHandler.routes = {"/a/": (200, {}, b'<a href="phet_en_all_2026-09.zim">x</a>')}
        entry = {"id": "phet", "stem": "phet_{lang}_all", "urls": [self.base + "/a/"]}
        self.assertEqual(install.find_remote_zim(entry, "es")[0], "phet_en_all_2026-09.zim")


class TestVerifiedZimDownload(RoutedServerCase):
    """Sin metalink, la descarga directa se contrasta con el .sha256 publicado."""

    NAME = "zimgit-water_en_2024-08.zim"

    def routes(self, published_sha):
        RoutedHandler.routes = {
            f"/zim/{self.NAME}": (200, {"Accept-Ranges": "bytes"}, PAYLOAD),
            f"/zim/{self.NAME}.sha256": (200, {}, f"{published_sha}  {self.NAME}\n".encode()),
        }

    def test_good_download_is_kept_with_checksum(self):
        self.routes(PAYLOAD_SHA)
        ok = install.download_zim(self.tmp, self.NAME, [self.base + "/zim/"])
        self.assertTrue(ok)
        dest = os.path.join(self.tmp, self.NAME)
        self.assertEqual(install.sha256_of(dest), PAYLOAD_SHA)
        with open(dest + ".sha256") as f:
            self.assertEqual(f.read().split()[0], PAYLOAD_SHA)

    def test_corrupt_download_is_discarded(self):
        self.routes("0" * 64)
        ok = install.download_zim(self.tmp, self.NAME, [self.base + "/zim/"])
        self.assertFalse(ok, "un ZIM que no casa con su SHA-256 se dio por bueno")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, self.NAME)))


class TestHuggingFaceChecksum(RoutedServerCase):
    def test_reads_linked_etag_without_following_redirect(self):
        sha = "ac2d97712095a558e31573f62f466a3f9d93990898b0ec79d7c974c1780d524a"
        RoutedHandler.routes = {"/m.gguf": (302, {"Location": "/cdn", "X-Linked-Etag": f'"{sha}"'}, b"")}
        self.assertEqual(install.fetch_hf_sha256(self.base + "/m.gguf"), sha)

    def test_missing_header_means_unknown(self):
        RoutedHandler.routes = {"/m.gguf": (200, {}, b"")}
        self.assertIsNone(install.fetch_hf_sha256(self.base + "/m.gguf"))


class TestMapRegions(RoutedServerCase):
    TREE = {"v": 260527, "id": "Countries", "g": [
        {"id": "Chile", "g": [{"id": "Chile_North", "s": 1}, {"id": "Campo de Hielo Sur", "s": 1}]},
        {"id": "Argentina", "g": [{"id": "Argentina_Buenos Aires", "s": 1}, {"id": "Campo de Hielo Sur", "s": 1}]},
        {"id": "Andorra", "s": 1},
    ]}

    def test_shared_regions_downloaded_once(self):
        presets = [{"countries": ["Chile"]}, {"countries": ["Argentina", "Atlantis"]}]
        ids = sorted(r['id'] for r in install.map_regions_for(presets, self.TREE))
        self.assertEqual(ids, ["Argentina_Buenos Aires", "Campo de Hielo Sur", "Chile_North"])

    def test_regions_land_where_the_app_reads_them(self):
        import base64
        body = b"mwm-bytes" * 1000
        sha1 = base64.b64encode(hashlib.sha1(body).digest()).decode()
        tree = {"v": 260527, "id": "Countries", "g": [
            {"id": "Andorra", "s": len(body), "sha1_base64": sha1},
            {"id": "Bad Region", "s": len(body), "sha1_base64": "AAAA"},
        ]}
        RoutedHandler.routes = {
            "/maps/260527/Andorra.mwm": (200, {}, body),
            "/maps/260527/Bad%20Region.mwm": (200, {}, body),
        }
        home = tempfile.mkdtemp()
        old_home = os.environ.get("HOME")
        os.environ["HOME"] = home
        saved = (install.organic_maps_countries, install.organic_maps_servers)
        install.organic_maps_countries = lambda: tree
        install.organic_maps_servers = lambda: [self.base + "/"]
        failed_before = len(install.FAILED_ITEMS)
        try:
            ok = install.install_map_regions([{"countries": ["Andorra", "Bad Region"]}])
        finally:
            install.organic_maps_countries, install.organic_maps_servers = saved
            os.environ["HOME"] = old_home
        maps = os.path.join(home, ".var", "app", install.ORGANIC_MAPS_ID, "data", "OMaps", "260527")
        self.assertTrue(os.path.isfile(os.path.join(maps, "Andorra.mwm")))
        self.assertFalse(os.path.exists(os.path.join(maps, "Bad Region.mwm")),
                         "una region que no casa con su SHA-1 se quedo en disco")
        self.assertFalse(ok)
        self.assertEqual(len(install.FAILED_ITEMS), failed_before + 1)
        del install.FAILED_ITEMS[failed_before:]


class TestSelfCheck(unittest.TestCase):
    """refugios-check.py: detecta descargas cortadas, ficheros danados y enlaces rotos sin conexion."""

    def run_check(self, home, *args):
        import subprocess
        env = dict(os.environ, HOME=home, PATH="/usr/bin:/bin")
        with open(os.path.join(home, ".refugios_lang"), "w") as f:
            f.write("es")
        return subprocess.run([sys.executable, os.path.join(REPO_DIR, "scripts", "refugios-check.py"),
                               "--no-dialog", *args], env=env, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL)

    def make_home(self):
        home = tempfile.mkdtemp()
        know = os.path.join(home, "refugiOS", "Knowledge", "versions")
        os.makedirs(know)
        os.makedirs(os.path.join(home, "refugiOS", "Apps"))
        open(os.path.join(home, "refugiOS", "Apps", "kiwix-desktop_x86_64_2.5.1.appimage"), "w").close()
        good = os.path.join(know, "zimgit-water_en_2024-08.zim")
        with open(good, "wb") as f:
            f.write(PAYLOAD)
        install.write_checksum_file(good, PAYLOAD_SHA)
        return home, know

    def test_healthy_device_passes(self):
        home, know = self.make_home()
        r = self.run_check(home, "--full")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("verificado", r.stdout)
        self.assertTrue(os.path.isfile(os.path.join(home, "refugiOS", "check-report.txt")))

    def test_damage_is_reported(self):
        home, know = self.make_home()
        # Descarga interrumpida
        cut = os.path.join(know, "phet_es_all_2026-08.zim")
        open(cut, "w").write("x")
        open(cut + ".aria2", "w").close()
        # Fichero alterado tras la descarga
        with open(os.path.join(know, "zimgit-water_en_2024-08.zim"), "r+b") as f:
            f.write(b"\0" * 16)
        # Enlace estable huerfano
        os.symlink(os.path.join(know, "no-existe.zim"), os.path.join(home, "refugiOS", "Knowledge", "wikimed.zim"))
        # Boveda que no es un contenedor LUKS
        os.makedirs(os.path.join(home, "refugiOS", "Vaults"))
        open(os.path.join(home, "refugiOS", "Vaults", "papeles.img"), "wb").write(b"\0" * 4096)

        quick = self.run_check(home, "--quick")
        self.assertNotEqual(quick.returncode, 0)
        self.assertIn("incompleto", quick.stdout)
        self.assertIn("wikimed.zim", quick.stdout)
        self.assertIn("papeles", quick.stdout)
        self.assertNotIn("dañado (no coincide", quick.stdout, "la rapida no debe leer ficheros enteros")

        full = self.run_check(home, "--full")
        self.assertIn("zimgit-water_en_2024-08.zim: el fichero está dañado", full.stdout)

    def test_luks_vault_recognised(self):
        home, _ = self.make_home()
        os.makedirs(os.path.join(home, "refugiOS", "Vaults"))
        with open(os.path.join(home, "refugiOS", "Vaults", "fotos.img"), "wb") as f:
            f.write(b"LUKS\xba\xbe" + b"\0" * 4090)
        r = self.run_check(home, "--quick")
        self.assertIn("'fotos': contenedor cifrado intacto", r.stdout)


class TestAutologinScreenLock(unittest.TestCase):
    """Con autologin y sin contrasena, el bloqueo de pantalla deja al usuario fuera."""

    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.saved = (os.environ.get("HOME"), os.environ.get("USER"), install.is_autologin_user, install.run_cmd)
        os.environ["HOME"] = self.home
        os.environ["USER"] = "refugios"
        install.run_cmd = lambda *a, **k: True

    def tearDown(self):
        home, user, install.is_autologin_user, install.run_cmd = self.saved
        os.environ["HOME"] = home
        if user is None:
            os.environ.pop("USER", None)
        else:
            os.environ["USER"] = user

    def test_autologin_user_gets_lock_disabled(self):
        install.is_autologin_user = lambda: True
        install.disable_autologin_screen_lock()
        path = os.path.join(self.home, ".config", "autostart", "light-locker.desktop")
        self.assertIn("Hidden=true", open(path).read())

    def test_password_users_keep_their_lock(self):
        install.is_autologin_user = lambda: False
        install.disable_autologin_screen_lock()
        self.assertFalse(os.path.exists(os.path.join(self.home, ".config", "autostart")))


class UpdaterCase(RoutedServerCase):
    """Base: un refugiOS falso en un HOME temporal y los origenes remotos neutralizados."""

    def setUp(self):
        super().setUp()
        self.home = tempfile.mkdtemp()
        self.env = install.TargetEnv(os.path.join(self.home, "refugiOS"), os.path.join(self.home, "Desktop"))
        install.ensure_dirs(self.env)
        self.saved = {n: getattr(install, n) for n in (
            "WIKIPEDIA_CONFIG", "LIBRARY_CATALOG", "latest_kiwix_appimage", "latest_llamafile",
            "flatpak_updates", "map_version_dirs", "organic_maps_countries", "AI_MODEL_CONFIG")}
        install.WIKIPEDIA_CONFIG = []
        install.LIBRARY_CATALOG = []
        install.AI_MODEL_CONFIG = []
        install.latest_kiwix_appimage = lambda: (None, None)
        install.latest_llamafile = lambda: None
        install.flatpak_updates = lambda: {}
        install.map_version_dirs = lambda: {}
        install.organic_maps_countries = lambda: None
        self.failed_before = len(install.FAILED_ITEMS)

    def tearDown(self):
        for n, v in self.saved.items():
            setattr(install, n, v)
        del install.FAILED_ITEMS[self.failed_before:]
        super().tearDown()

    def put(self, name, data=b"old"):
        path = os.path.join(self.env.know_dir, name)
        with open(path, "wb") as f:
            f.write(data)
        return path


class TestOldVersionCleanup(UpdaterCase):
    def test_only_other_editions_of_the_same_book_go(self):
        self.put("phet_es_all_2026-01.zim")
        self.put("phet_es_all_2026-01.zim.sha256", b"x")
        self.put("phet_es_all_2026-08.zim")
        self.put("phet_en_all_2026-01.zim")
        self.put("wikivoyage_es_all_maxi_2026-01.zim")
        install.remove_older_zims(self.env.know_dir, "phet_es_all_2026-08.zim")
        self.assertEqual(sorted(os.listdir(self.env.know_dir)),
                         ["phet_en_all_2026-01.zim", "phet_es_all_2026-08.zim",
                          "wikivoyage_es_all_maxi_2026-01.zim"])


class TestBookUpdates(UpdaterCase):
    NEW = "phet_es_all_2026-08.zim"

    def serve(self, sha):
        listing = b'<a href="phet_es_all_2026-01.zim">x</a><a href="phet_es_all_2026-08.zim">x</a>'
        RoutedHandler.routes = {
            "/zim/": (200, {}, listing),
            f"/zim/{self.NEW}": (200, {"Accept-Ranges": "bytes"}, PAYLOAD),
            f"/zim/{self.NEW}.sha256": (200, {}, f"{sha}  {self.NEW}\n".encode()),
        }
        install.LIBRARY_CATALOG = [{"id": "phet", "label_key": "lib_phet", "title_key": "lib_phet_title",
                                    "stem": "phet_{lang}_all", "urls": [self.base + "/zim/"], "size_mb": 110}]

    def test_newer_edition_is_offered_with_its_real_size(self):
        self.serve(PAYLOAD_SHA)
        self.put("phet_es_all_2026-01.zim")
        updates = install.collect_updates(self.env, "es")
        self.assertEqual(len(updates), 1)
        self.assertIn("2026-01 -> 2026-08", updates[0]['label'])
        self.assertEqual(updates[0]['size_mb'], install.size_mb(len(PAYLOAD)))

    def test_up_to_date_book_is_not_offered(self):
        self.serve(PAYLOAD_SHA)
        self.put(self.NEW)
        self.assertEqual(install.collect_updates(self.env, "es"), [])

    def test_book_in_the_users_language_replaces_the_english_fallback(self):
        self.serve(PAYLOAD_SHA)
        self.put("phet_en_all_2026-09.zim")
        updates = install.collect_updates(self.env, "es")
        self.assertEqual(len(updates), 1)
        self.assertTrue(updates[0]['apply']())
        self.assertEqual(os.listdir(self.env.know_dir).count("phet_en_all_2026-09.zim"), 0)
        self.assertIn(self.NEW, os.listdir(self.env.know_dir))

    def test_verified_update_replaces_the_old_edition(self):
        self.serve(PAYLOAD_SHA)
        self.put("phet_es_all_2026-01.zim")
        self.assertTrue(install.collect_updates(self.env, "es")[0]['apply']())
        files = os.listdir(self.env.know_dir)
        self.assertIn(self.NEW, files)
        self.assertNotIn("phet_es_all_2026-01.zim", files)

    def test_failed_update_keeps_the_old_edition(self):
        self.serve("0" * 64)
        old = self.put("phet_es_all_2026-01.zim", b"contenido antiguo")
        self.assertFalse(install.collect_updates(self.env, "es")[0]['apply']())
        with open(old, "rb") as f:
            self.assertEqual(f.read(), b"contenido antiguo", "se borro la edicion que funcionaba")
        self.assertNotIn(self.NEW, os.listdir(self.env.know_dir))


class TestEngineAndModelUpdates(UpdaterCase):
    def test_model_with_new_revision(self):
        model = {"filename": "m.gguf", "url": self.base + "/m.gguf", "size_mb": 3}
        install.AI_MODEL_CONFIG = [model]
        path = os.path.join(self.env.ai_dir, "m.gguf")
        with open(path, "wb") as f:
            f.write(b"revision vieja")
        install.write_checksum_file(path, "1" * 64)
        RoutedHandler.routes = {"/m.gguf": (302, {"Location": "/cdn/m.gguf", "X-Linked-Etag": f'"{PAYLOAD_SHA}"',
                                                  "X-Linked-Size": str(len(PAYLOAD))}, b""),
                                "/cdn/m.gguf": (200, {}, PAYLOAD)}
        updates = install.collect_updates(self.env, "es")
        self.assertEqual(len(updates), 1)
        self.assertTrue(updates[0]['apply']())
        self.assertEqual(install.sha256_of(path), PAYLOAD_SHA)
        self.assertEqual(install.saved_sha256(path), PAYLOAD_SHA)
        self.assertFalse(os.path.exists(path + ".new"))

    def test_model_failing_verification_keeps_the_old_one(self):
        model = {"filename": "m.gguf", "url": self.base + "/m.gguf"}
        path = os.path.join(self.env.ai_dir, "m.gguf")
        with open(path, "wb") as f:
            f.write(b"revision vieja")
        RoutedHandler.routes = {"/m.gguf": (200, {}, PAYLOAD)}
        self.assertFalse(install.update_model(self.env, model, "2" * 64))
        with open(path, "rb") as f:
            self.assertEqual(f.read(), b"revision vieja")
        self.assertFalse(os.path.exists(path + ".new"))

    def test_engine_update_is_verified_and_relinked(self):
        old = os.path.join(self.env.ai_dir, "llamafile-0.10.5")
        open(old, "w").close()
        os.symlink(old, os.path.join(self.env.base, "AI", "llamafile"))
        RoutedHandler.routes = {"/llamafile-0.10.6": (200, {}, PAYLOAD)}
        install.latest_llamafile = lambda: {"name": "llamafile-0.10.6", "url": self.base + "/llamafile-0.10.6",
                                            "size": len(PAYLOAD), "sha256": PAYLOAD_SHA}
        updates = install.collect_updates(self.env, "es")
        self.assertEqual(len(updates), 1)
        self.assertTrue(updates[0]['apply']())
        link = os.path.join(self.env.base, "AI", "llamafile")
        self.assertEqual(os.path.basename(os.path.realpath(link)), "llamafile-0.10.6")
        self.assertFalse(os.path.exists(old))

    def test_engine_with_bad_checksum_is_rejected(self):
        RoutedHandler.routes = {"/llamafile-0.10.6": (200, {}, PAYLOAD)}
        info = {"name": "llamafile-0.10.6", "url": self.base + "/llamafile-0.10.6", "size": 1, "sha256": "3" * 64}
        self.assertFalse(install.install_llamafile(self.env, info))
        self.assertFalse(os.path.exists(os.path.join(self.env.ai_dir, "llamafile-0.10.6")))

    def test_kiwix_appimage_checked_against_md5(self):
        import hashlib as h
        old = os.path.join(self.env.apps_dir, "kiwix-desktop_x86_64_2.4.1.appimage")
        open(old, "w").close()
        name = "kiwix-desktop_x86_64_2.5.1.appimage"
        RoutedHandler.routes = {f"/{name}": (200, {}, PAYLOAD),
                                f"/{name}.md5": (200, {}, (h.md5(b"otra cosa").hexdigest() + f"  {name}\n").encode())}
        self.assertFalse(install.update_kiwix_appimage(self.env, name, f"{self.base}/{name}"))
        self.assertTrue(os.path.exists(old), "el AppImage que funcionaba se borro")
        RoutedHandler.routes[f"/{name}.md5"] = (200, {}, (h.md5(PAYLOAD).hexdigest() + f"  {name}\n").encode())
        self.assertTrue(install.update_kiwix_appimage(self.env, name, f"{self.base}/{name}"))
        self.assertFalse(os.path.exists(old))
        self.assertTrue(os.access(os.path.join(self.env.apps_dir, name), os.X_OK))


class TestMapAndFlatpakUpdates(UpdaterCase):
    TREE = {"v": 260527, "g": [{"id": "Spain", "g": [{"id": "Spain_Madrid", "s": 1}, {"id": "Spain_Galicia", "s": 1}]},
                               {"id": "Andorra", "s": 1}]}

    def test_regions_of_old_data_versions_are_migrated(self):
        on_disk = {"260101": ["Andorra", "Spain_Madrid", "Gone_Region"], "260527": ["Andorra"]}
        ids = [r['id'] for r in install.map_regions_to_migrate(self.TREE, on_disk)]
        self.assertEqual(ids, ["Spain_Madrid"])

    def test_old_map_folders_only_go_when_the_new_ones_are_complete(self):
        maps = os.path.join(self.home, ".var", "app", install.ORGANIC_MAPS_ID, "data", "OMaps")
        old = os.path.join(maps, "260101")
        os.makedirs(old)
        open(os.path.join(old, "Spain_Madrid.mwm"), "w").close()
        saved_home = os.environ["HOME"]
        saved_dl = install.download_map_regions
        os.environ["HOME"] = self.home
        install.map_version_dirs = self.saved["map_version_dirs"]
        install.organic_maps_countries = lambda: self.TREE
        try:
            install.download_map_regions = lambda tree, regions: False
            self.assertFalse(install.update_map_regions())
            self.assertTrue(os.path.isdir(old), "se borraron mapas que funcionaban sin tener los nuevos")
            install.download_map_regions = lambda tree, regions: True
            self.assertTrue(install.update_map_regions())
            self.assertFalse(os.path.isdir(old))
        finally:
            os.environ["HOME"] = saved_home
            install.download_map_regions = saved_dl

    def test_flatpak_update_sizes_are_parsed(self):
        saved = install.get_cmd_output
        install.get_cmd_output = lambda cmd: "app.organicmaps.desktop\t169,2 MB\norg.kiwix.desktop\t1.5 GB\n"
        try:
            self.assertEqual(self.saved["flatpak_updates"](), {"app.organicmaps.desktop": 169, "org.kiwix.desktop": 1536})
        finally:
            install.get_cmd_output = saved


class TestRunUpdate(UpdaterCase):
    """El flujo completo: lo que falla o no cabe se omite, el resto se aplica y se informa."""

    def run_with(self, updates, free_mb):
        saved = (install.collect_updates, install.fetch_url, install.shutil.disk_usage, install.sync_resources)
        install.collect_updates = lambda env, lang: updates
        install.fetch_url = lambda url: ""
        install.shutil.disk_usage = lambda p: type("U", (), {"free": free_mb * 1024 * 1024})()
        install.sync_resources = lambda *a: None
        os.environ["HOME"] = self.home
        try:
            class Info:
                lang = "es"
            return install.run_update(FakeDialog(), Info())
        finally:
            install.collect_updates, install.fetch_url, install.shutil.disk_usage, install.sync_resources = saved

    def test_failures_and_missing_space_are_reported(self):
        done = []
        updates = [
            {"label": "bien", "size_mb": 10, "old_mb": 5, "apply": lambda: done.append("bien") or True},
            {"label": "falla", "size_mb": 10, "old_mb": 5, "apply": lambda: False},
            {"label": "enorme", "size_mb": 999999, "old_mb": 0, "apply": lambda: done.append("enorme") or True},
        ]
        FakeDialog.checklist_all = True
        self.assertEqual(self.run_with(updates, 5000), 1)
        self.assertEqual(done, ["bien"], "se intento aplicar una actualizacion que no cabia")

    def test_nothing_to_update(self):
        self.assertEqual(self.run_with([], 5000), 0)


class TestSpaceEstimates(UpdaterCase):
    """Las estimaciones descuentan lo que ya esta en disco."""

    def test_maps_already_downloaded_are_not_counted_again(self):
        tree = {"v": 260527, "g": [{"id": "Andorra", "s": 5 * 1024 * 1024}, {"id": "Spain", "g": [
            {"id": "Spain_Madrid", "s": 100 * 1024 * 1024}]}]}
        install.organic_maps_countries = lambda: tree
        saved_home = os.environ["HOME"]
        os.environ["HOME"] = self.home
        try:
            presets = [{"countries": ["Andorra", "Spain"], "size_mb": 999}]
            self.assertEqual(install.pending_map_mb(presets), 105)
            d = os.path.join(install.organic_maps_data_dir(), "260527")
            os.makedirs(d)
            with open(os.path.join(d, "Andorra.mwm"), "wb") as f:
                f.write(b"\0" * 5 * 1024 * 1024)
            self.assertEqual(install.pending_map_mb(presets), 100)
            install.organic_maps_countries = lambda: None
            self.assertEqual(install.pending_map_mb(presets), 999, "sin Organic Maps se usa la estimacion del preset")
        finally:
            os.environ["HOME"] = saved_home

    def test_installed_kiwix_is_detected(self):
        saved = install.flatpak_app_installed
        install.flatpak_app_installed = lambda app: False
        try:
            self.assertFalse(install.kiwix_installed(self.env))
            open(os.path.join(self.env.apps_dir, "kiwix-desktop_x86_64_2.5.1.appimage"), "w").close()
            self.assertTrue(install.kiwix_installed(self.env))
        finally:
            install.flatpak_app_installed = saved

    def test_update_titles_are_short(self):
        entry = {"label_key": "wiki_lite_label"}
        self.assertNotIn("[", install.entry_title(entry))


if __name__ == "__main__":
    unittest.main(verbosity=2)

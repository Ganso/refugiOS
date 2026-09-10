#!/usr/bin/env python3
"""
publish_images.py — Publishes refugiOS base images and SHA256SUMS.txt to the download server via SFTP.

Reads connection credentials and destination path from '.sftp' in the repository root:
  Line 1: user@host
  Line 2: password
  Line 3: remote destination directory (e.g. /path/to/web/refugios)

Follows the publishing protocol defined in AGENTS.md:
  1. Verifies local checksums before upload.
  2. Uploads to temporary files (<file>.tmp) with progress.
  3. Verifies remote file size matches local file size.
  4. Rotates atomically (<file> -> <file>.old, <file>.tmp -> <file>, delete <file>.old).
  5. Uploads SHA256SUMS.txt last to ensure consistency.
  6. Executes remote checksum verification via SSH.
"""

import os
import sys
import re
import time
import subprocess

try:
    import paramiko
except ImportError:
    print("ERROR: paramiko is required for SFTP uploads. Run: pip install paramiko or sudo apt-get install python3-paramiko")
    sys.exit(1)

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFTP_FILE = os.path.join(REPO_DIR, ".sftp")

def update_landing_page_html(es_zip_path, en_zip_path):
    index_path = os.path.join(REPO_DIR, "web", "index.html")
    if not os.path.isfile(index_path):
        return None

    es_gb = os.path.getsize(es_zip_path) / (1024**3)
    en_gb = os.path.getsize(en_zip_path) / (1024**3)

    es_str = f"{es_gb:.1f} GB"
    en_str = f"{en_gb:.1f} GB"

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(r'Imagen en Español \([0-9\.]+ GB\)', f'Imagen en Español ({es_str})', content)
    content = re.sub(r'English Image \([0-9\.]+ GB\)', f'English Image ({en_str})', content)
    content = re.sub(r'Al ser ficheros grandes \(~[0-9\.]+ GB\)', f'Al ser ficheros grandes (~{es_str})', content)
    content = re.sub(r'As these are large images \(~[0-9\.]+ GB\)', f'As these are large images (~{en_str})', content)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"   [OK] web/index.html actualizado con tamaños: ES={es_str}, EN={en_str}")
    return index_path

def format_size(bytes_num):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.2f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.2f} TB"

def upload_file(sftp, local_path, remote_path):
    local_size = os.path.getsize(local_path)
    remote_tmp = remote_path + ".tmp"
    remote_old = remote_path + ".old"
    filename = os.path.basename(local_path)

    print(f"\n=> Subiendo {filename} ({format_size(local_size)})...")
    print(f"   Destino temporal: {remote_tmp}")

    last_print = [time.time(), 0]
    start_time = time.time()

    def progress(transferred, total):
        now = time.time()
        if now - last_print[0] >= 2.0 or transferred == total:
            elapsed = now - start_time
            speed = transferred / elapsed if elapsed > 0 else 0
            pct = (transferred / total) * 100 if total > 0 else 100
            print(f"   [{pct:5.1f}%] {format_size(transferred)} / {format_size(total)} "
                  f"({format_size(speed)}/s, transcurrido: {int(elapsed)}s)", flush=True)
            last_print[0] = now
            last_print[1] = transferred

    # Upload to .tmp
    sftp.put(local_path, remote_tmp, callback=progress)

    # Verify size
    remote_stat = sftp.stat(remote_tmp)
    if remote_stat.st_size != local_size:
        raise RuntimeError(f"Error de tamaño en {remote_tmp}: local {local_size} vs remoto {remote_stat.st_size}")
    print(f"   [OK] Tamaño verificado: {remote_stat.st_size} bytes")

    # Atomic rotation
    try:
        sftp.remove(remote_old)
    except IOError:
        pass

    try:
        sftp.rename(remote_path, remote_old)
        print(f"   [OK] Versión anterior respaldada como {os.path.basename(remote_old)}")
    except IOError:
        pass

    sftp.rename(remote_tmp, remote_path)
    print(f"   [OK] Publicado como {os.path.basename(remote_path)}")

    try:
        sftp.remove(remote_old)
        print(f"   [OK] Respaldo temporal anterior limpiado")
    except IOError:
        pass

def main():
    if not os.path.isfile(SFTP_FILE):
        print(f"ERROR: No se encontró el fichero de credenciales: {SFTP_FILE}")
        print("El fichero .sftp debe contener:")
        print("  Línea 1: usuario@servidor")
        print("  Línea 2: contraseña")
        print("  Línea 3: directorio_remoto")
        sys.exit(1)

    with open(SFTP_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    if len(lines) < 3:
        print("ERROR: Formato de .sftp inválido (se requieren 3 líneas: user@host, password y remote_dir).")
        sys.exit(1)

    if "@" not in lines[0]:
        print("ERROR: La primera línea de .sftp debe tener el formato usuario@servidor.")
        sys.exit(1)

    user, host = lines[0].split("@", 1)
    pwd = lines[1]
    remote_dir = lines[2]

    es_zip = os.path.join(REPO_DIR, "refugios-base-16G-es.img.zip")
    en_zip = os.path.join(REPO_DIR, "refugios-base-16G-en.img.zip")
    sums_file = os.path.join(REPO_DIR, "SHA256SUMS.txt")

    # 1. Validar que los ficheros locales existan
    print("=> Comprobando ficheros locales a publicar...")
    for fpath in [es_zip, en_zip, sums_file]:
        if not os.path.isfile(fpath):
            print(f"ERROR: Falta el archivo local requerido: {fpath}")
            sys.exit(1)
        print(f"   [OK] {os.path.basename(fpath)} ({format_size(os.path.getsize(fpath))})")

    # 2. Comprobar checksums locales
    print("=> Verificando integridad local antes de subir...")
    res = subprocess.run(["sha256sum", "-c", "SHA256SUMS.txt"], cwd=REPO_DIR)
    if res.returncode != 0:
        print("ERROR: Los checksums locales no coinciden con SHA256SUMS.txt!")
        sys.exit(1)
    print("   [OK] Integridad local verificada.")

    # 3. Actualizar tamaños reales en web/index.html
    print("=> Sincronizando tamaños reales en web/index.html...")
    index_file = update_landing_page_html(es_zip, en_zip)

    # 4. Conectar al servidor
    print(f"\n=> Conectando a {user}@{host} vía SFTP...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=pwd, timeout=20)
    sftp = client.open_sftp()
    print("=> Conexión establecida.")

    # 5. Validar directorio remoto
    print(f"=> Verificando directorio remoto: {remote_dir}")
    try:
        remote_files = [f.filename for f in sftp.listdir_attr(remote_dir)]
    except Exception as e:
        print(f"ERROR al listar directorio remoto {remote_dir}: {e}")
        sftp.close()
        client.close()
        sys.exit(1)

    if "index.html" not in remote_files:
        print(f"ERROR: El directorio {remote_dir} no contiene index.html. Abortando para evitar publicar en ruta equivocada.")
        sftp.close()
        client.close()
        sys.exit(1)
    print(f"   [OK] Directorio remoto verificado ({len(remote_files)} archivos encontrados).")

    # 6. Subir archivos en orden estricto:
    #    a) Imágenes base (.zip)
    #    b) index.html (landing page con los tamaños actualizados)
    #    c) SHA256SUMS.txt (siempre al final como señal de publicación completa)
    upload_file(sftp, es_zip, f"{remote_dir}/refugios-base-16G-es.img.zip")
    upload_file(sftp, en_zip, f"{remote_dir}/refugios-base-16G-en.img.zip")
    if index_file and os.path.isfile(index_file):
        upload_file(sftp, index_file, f"{remote_dir}/index.html")
    upload_file(sftp, sums_file, f"{remote_dir}/SHA256SUMS.txt")

    # 7. Verificación remota
    print("\n=======================================================")
    print("=> Verificando checksums en el servidor remoto vía SSH...")
    stdin, stdout, stderr = client.exec_command(f"cd {remote_dir} && sha256sum -c SHA256SUMS.txt")
    check_out = stdout.read().decode()
    check_err = stderr.read().decode()
    print(check_out)
    if check_err:
        print("Avisos remotos:", check_err)

    sftp.close()
    client.close()
    print("=> ¡Publicación completada y verificada con éxito!")

if __name__ == "__main__":
    main()

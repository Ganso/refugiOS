# refugiOS Automated Test Suite

This guide describes the project's automated checks: what they cover, how to run them, and how to extend them. It is meant for people **developing or modifying refugiOS**; if you only intend to use the system, you need none of this.

The suite lives in the [`tests/`](https://github.com/Ganso/refugiOS/tree/main/tests) folder of the repository and covers the three distinct moments of the system: **building** the image, **installing** modules, and **running** on the user's device.

Two ideas guide the whole design:

1. **Nothing requires `sudo` on your machine.** Whatever genuinely needs root (`debootstrap`, loop devices, `cryptsetup`) runs inside a privileged Debian container.
2. **A test that does not fail without the fix is worthless.** Every check was also validated against the code from before the fix, in a separate copy of the repository.

> [!NOTE]
> The project has **no continuous integration**: nothing runs the suite automatically. Run it yourself before proposing a change.

---

## 1. Quick use

```bash
bash tests/run_all.sh
```

Runs the whole suite (about 3-4 minutes, a bit more the first time because it builds the Docker image). Returns exit code 0 if everything is correct.

If you do not want to use Docker or just need an immediate check:

```bash
bash tests/run_all.sh --quick
```

Runs only what executes on your machine: syntax checks and the Bash script tests.

---

## 2. Requirements

| Tool | What for | Required |
| :--- | :--- | :--- |
| `docker` (with your user in the `docker` group) | Privileged container for whatever needs root | Yes, except with `--quick` |
| `qemu-system-x86_64` + `/dev/kvm` | Booting built images | Only for the boot tests |
| `ovmf` package | UEFI firmware for QEMU | Only for the boot tests |
| `imagemagick` (`convert`) | Converting QEMU captures to PNG | Only for the boot tests |
| Internet connection | One case in `test_install_sh.sh` and the `debootstrap` in `test_build.sh` | Recommended |

Quick check that you have what you need:

```bash
docker info >/dev/null && test -w /dev/kvm && ls /usr/share/OVMF/OVMF_CODE*.fd && command -v convert
```

---

## 3. What each file does

### 3.1. Running

| File | What it does |
| :--- | :--- |
| `run_all.sh` | Runs the full suite. With `--quick`, only what does not need the container. |
| `run_in_container.sh` | Wrapper: runs a command inside the privileged container with the repository mounted at `/repo`. |
| `docker/Dockerfile` | Debian Trixie container with `debootstrap`, `cryptsetup`, `parted`, `aria2`, `shellcheck`… |

### 3.2. Checks

| File | What it checks | Needs container |
| :--- | :--- | :--- |
| `lint.sh` | Syntax of the 8 Bash scripts (`bash -n`) and the 3 Python ones (`py_compile`). With `shellcheck` available, reports the number of warnings per file (non-blocking). | No |
| `unit_bash.sh` | Language precedence in `i18n.sh`, version selection in `refugios-kiwix.sh`, the full cycle of `refugios-ai-selector.sh`, and argument handling plus RAM calculation in `test_boot.sh`. | No |
| `unit_install.py` | Internals of `install.py`: download resumption, timeouts, version ordering, text sanitizing for `dialog`, exit code, precedence of local scripts, and untranslated keys. | Yes (uses `aria2c`) |
| `test_install_sh.sh` | The `install.sh` bootstrapper: that Developer Mode takes effect, that normal mode downloads from GitHub, and the validations for `i18n.py` and a missing terminal. | Yes |
| `test_vault.sh` | Real LUKS vault creation: mismatched passwords rejected, matching passwords accepted, and the open → write → close → reopen cycle. | Yes (real root) |
| `test_build.sh` | A real image build, deliberately aborted right after entering the chroot: that the failure stops the build, that the previous image is discarded, and that no stacked mounts remain. | Yes (real root) |

### 3.3. Utilities

| File | What for |
| :--- | :--- |
| `luks_pty.py` | Runs `cryptsetup luksFormat` over a real terminal and answers its prompts. Needed because cryptsetup refuses to verify the password when the input is a pipe. |
| `qemu_boot_check.py` | Boots an image headless and takes screenshots at the moments you specify. |
| `qemu_ctl.py` | Controls an already running virtual machine: screenshots, keys, text, and mouse clicks. |
| `verify_image.sh` | Verifies a built image **before publishing it**: filesystem integrity, presence of the thirteen artefacts it must contain and, with `--expand`, that the partition really grows to the size of the device. |
| `prepare_e2e_image.sh` | Prepares a copy of a built image to test the installer end to end: injects the local repository and launches the installer at login. |

---

## 4. Running individual checks

Every test works on its own. The ones needing root go through the wrapper:

```bash
bash tests/lint.sh
```

```bash
bash tests/unit_bash.sh
```

```bash
bash tests/run_in_container.sh python3 -W ignore tests/unit_install.py
```

```bash
bash tests/run_in_container.sh bash tests/test_install_sh.sh
```

```bash
bash tests/run_in_container.sh bash tests/test_vault.sh
```

```bash
bash tests/run_in_container.sh bash tests/test_build.sh
```

For a single case of the Python tests:

```bash
bash tests/run_in_container.sh python3 -W ignore tests/unit_install.py TestDownloadResume
```

And to open a shell inside the container and poke around by hand:

```bash
bash tests/run_in_container.sh bash
```

---

## 5. Image and boot tests

These are not part of `run_all.sh` because they take 20 to 40 minutes.

### 5.1. Building an image without using sudo

```bash
mkdir -p ~/refugios-builds && docker run --rm --privileged -v "$PWD:/repo" -v ~/refugios-builds:/out -v /dev:/dev -w /out refugios-test:trixie /repo/scripts/build_refugios.sh -s 12G -l en
```

The image ends up owned by `root`; to boot it with QEMU, hand it back to your user:

```bash
docker run --rm -v ~/refugios-builds:/out refugios-test:trixie chown -R 1000:1000 /out
```

### 5.2. Verifying the image before publishing it

```bash
bash tests/verify_image.sh ~/refugios-builds/refugios-base-16G-en.img --expand
```

It checks the **artefact**, not the build: that the filesystem is clean, that the thirteen
items the image must contain are inside it (auto-expansion service and script with its
symlink, installer wrapper, launchers, `fstab`, `grub.cfg`…) and, with `--expand`, that
dropping it onto a 128 GB disk really grows the root partition. Without `--expand` it
takes seconds; with it, about five minutes.

> [!IMPORTANT]
> Do not skip `--expand`. Version 0.23 was published without the auto-expansion service
> enabled and every signal said it was fine: the build exited 0, its log recorded the
> symlink as created, and the screenshot showed a correct desktop. None of them looks
> inside the image, and on a disk the same size as the image the expansion has nothing to
> do. Watch out for the welcome popup too: it reports the size of the **disk**, not of the
> partition, so it says "114 GB" whether or not the expansion worked.

### 5.3. Verifying that it boots

```bash
python3 tests/qemu_boot_check.py ~/refugios-builds/refugios-base-12G-en.img --shots 25,60,100 --out tests/out --prefix my_image
```

It leaves the PNGs in `tests/out/`. Open them and check the expected sequence: GRUB, automatic login, XFCE desktop, and the welcome message with the real disk size.

Useful options:

- `--net none` boots with no network — this is the proof that the system works offline.
- `--ram 4` sets the virtual machine memory in GiB.
- `--size 1920x1080` sets the virtual screen resolution.
- `--keep` leaves the machine alive at the end so you can drive it (see below).

### 5.4. Testing the installer end to end

Prepare a copy of the image with the local repository injected, so the installer uses **your code** and not the one published on GitHub:

```bash
docker run --rm --privileged -v "$PWD:/repo" -v ~/refugios-builds:/out -v /dev:/dev -w /repo -e REFUGIOS_IN_CONTAINER=1 refugios-test:trixie bash tests/prepare_e2e_image.sh /out/refugios-base-12G-en.img /out/e2e.img
```

Boot the copy and leave it alive:

```bash
python3 tests/qemu_boot_check.py ~/refugios-builds/e2e.img --shots 60 --out tests/out --prefix e2e --keep
```

The installer opens by itself at login. From there it is driven with `qemu_ctl.py`, which talks to the machine through the socket left at `tests/out/e2e_qmp.sock`:

```bash
python3 tests/qemu_ctl.py tests/out/e2e_qmp.sock shot step1
```

```bash
python3 tests/qemu_ctl.py tests/out/e2e_qmp.sock key ret
```

```bash
python3 tests/qemu_ctl.py tests/out/e2e_qmp.sock key down spc ret
```

```bash
python3 tests/qemu_ctl.py tests/out/e2e_qmp.sock text "my_vault"
```

```bash
python3 tests/qemu_ctl.py tests/out/e2e_qmp.sock dblclick 65 490
```

Key names: `ret`, `tab`, `spc`, `esc`, `up`, `down`, `left`, `right`, `backspace`, and hyphenated combinations (`ctrl-c`, `alt-f4`, `shift-a`).

To stop the machine when you are done:

```bash
kill $(cat tests/out/e2e_qemu.pid)
```

> [!WARNING]
> **Keyboard warning:** the Spanish image uses the `es` layout, so when using `text` the characters `-`, `;` and `=` come out as `'`, `ñ` and `¡`. Write commands using only letters, digits and spaces, or send those symbols with `key`.

---

## 6. Adding a new test

1. Decide where it belongs: behaviour of a Bash script → `unit_bash.sh`; an internal function of `install.py` → `unit_install.py`; anything needing real root → a `test_*.sh` launched with `run_in_container.sh`.
2. Bash tests use the `check` function, which takes an exit code and a description: `check $? "description of what should happen"`.
3. For scripts that call external programs, create doubles in a temporary directory and put it first in `PATH` — that is how `unit_bash.sh` handles `dialog`, `curl`, `llamafile` and `qemu-system-x86_64`.
4. **Check that the test fails without the fix.** Dump the previous version of the file into a separate directory and run the test against it:

```bash
mkdir -p /tmp/orig/scripts && git show main:scripts/refugios-kiwix.sh > /tmp/orig/scripts/refugios-kiwix.sh
```

---

## 7. When something looks stuck

- **`cryptsetup` takes forever.** With the default parameters (argon2id, 1 GiB of memory) each operation takes minutes inside a container. `test_vault.sh` cheapens the KDF *for the test only*, leaving untouched the options being tested.
- **An orphaned container from a previous run** blocks `cryptsetup` and the loop devices. Check `docker ps` before investigating anything else.
- **`expect`.** It was tried and dropped: with the block form and with `expect_before timeout` it stopped matching the prompts and the test hung with no explanation. That is why terminal control lives in `luks_pty.py`, which is explicit and can be read in full.
- **QEMU refuses to boot the image** with "Permission denied": the image belongs to `root` because the container built it. Hand it back to your user with the `chown` above.

---

## 8. What these tests do not cover

There is no automated check for a full installation of the large modules (complete Wikipedia, maps), nor for behaviour on Raspberry Pi, nor for booting on real hardware through legacy BIOS. All of that is still manual.

---

## Related links

- **[System Image Build Guide](System-Image-Build-EN.md)** — how the image these tests verify is generated.
- **[Virtualization Guide](Virtualization-Guide-EN.md)** — booting images in QEMU or VirtualBox manually.
- **[System Architecture](System-Architecture-EN.md)** — what each script in the project does.

# ESPD Kits

Curated **board definitions**, **CI-built firmware**, and a **browser flasher** for [ESPD](https://github.com/ben-wes/espd) (Pure Data on ESP32).

Upstream firmware and Pd core live in the **`espd/`** git submodule. This repo owns kit YAMLs, release binaries, and the web UI — so board presets can evolve without bloating the core tree.

## Layout

| Path | Role |
|------|------|
| [`espd/`](espd/) | ESPD firmware submodule (pinned per release tag on this repo) |
| [`boards/`](boards/) | Board plugin YAMLs (source of truth; `ESPD_BOARDS_DIR` at build time) |
| [`config/boards/`](config/boards/) | Per-board `.select` → copied to `espd/sdkconfig.defaults.local` at build time |
| [`presets/`](presets/) | Example `config.txt` / patch bundles per use case (optional) |
| [`flasher/`](flasher/) | Static Web Serial flasher (GitHub Pages) |
| [`manifests/`](manifests/) | Generated `releases.json` for the flasher |
| [`scripts/`](scripts/) | `prepare_espd.sh`, `build-board.sh`, `generate-manifest.py` |

## Quick start (local build)

```bash
git clone --recursive https://github.com/ben-wes/espd-kits.git
cd espd-kits
. $HOME/.espressif/v6.0.1/esp-idf/export.sh   # ESP-IDF v6.0.1

./scripts/build-board.sh waveshare_s3
# artifacts in dist/waveshare_s3/
```

## Custom config (menuconfig)

`build-board.sh` builds with the kit's defaults and no prompts. To customize the
config (sample rate, WiFi, dev sync, extra GPIO, …) run menuconfig in the `espd/`
submodule, starting from the kit baseline:

```bash
. $HOME/.espressif/v6.0.1/esp-idf/export.sh
export ESPD_BOARDS_DIR=$PWD/boards                       # kit boards discoverable
cp config/boards/waveshare_s3.select espd/sdkconfig.defaults.local   # pre-select the board
cd espd
idf.py set-target esp32s3
idf.py menuconfig                  # ESPD Configuration → … (board already selected)
idf.py build flash monitor
```

`grep CONFIG_ESPD_BOARD_ espd/sdkconfig` should show your kit. Note: re-running
`build-board.sh` overwrites `espd/sdkconfig.defaults.local` and re-runs
`set-target`, resetting to kit defaults — so keep menuconfig tweaks tracked
(a branch, or a committed `.select`/profile change).

## Adding a custom board

Firmware stays board-agnostic in `espd/`; a board is just two files here:

1. **`boards/<id>.yaml`** — board definition: the esp-bsp package (`bsp:`), enabled
   ESPD features (`features.imply`), flash size (`flash:`), IDF tuning (`profile:`),
   and button map (`io:`). Full schema:
   [espd/docs/ADDING_A_BOARD.md](espd/docs/ADDING_A_BOARD.md).
2. **`config/boards/<id>.select`** — one line, `CONFIG_ESPD_BOARD_<ID>=y`, copied to
   `espd/sdkconfig.defaults.local` at build time.

Then `./scripts/build-board.sh <id>` (or the menuconfig flow above).

**Custom components / BSP:** hardware drivers live in the **esp-bsp package** the
YAML points at (`bsp.git` / `bsp.registry`), *not* in `espd`. Point `bsp:` at your
fork or a registry component; extra Component Manager deps go in that package's
`idf_component.yml`. For an in-tree BSP, use `bsp.path: local` and drop the
component in `espd/local_components/` (see ADDING_A_BOARD.md). The generator emits
`espd/components/espd_board_<id>/` (a thin plugin → your BSP) on every configure.

## Submodule policy

- **Development:** `espd` tracks a branch (e.g. `bsp`) or commit on `main`.
- **Releases:** tag `espd-kits` and record the submodule SHA in release notes; CI builds from that SHA.
- Board YAMLs stay **here**; consider upstreaming stable kits to `ben-wes/espd` later if they belong in core docs.

## Web flasher

GitHub Pages serves [`flasher/`](flasher/) — a Web Serial UI for the **Waveshare ESP32-S3-AUDIO** kit. Firmware binaries come from this repo’s **GitHub Releases** (built by CI on tags). Board metadata: [`manifests/releases.json`](manifests/releases.json).

## Docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — design, CI, manifest schema, follow-ups in `espd`
- [boards/README.md](boards/README.md) — YAML schema pointer

## Status

CI writes `espd/sdkconfig.defaults.local` before the Docker build (see `build.yml`).
The **`espd` submodule** must include `sdkconfig.defaults.local` support in `CMakeLists.txt`
(`espd` `bsp` with neutral chip defaults + local overlay).

If the build log shows `/app/ben-wes/espd` (not `…/espd-kits/espd`), the workflow is on the wrong repo.

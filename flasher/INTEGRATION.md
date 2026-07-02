# Web flasher integration

## Status

Multi-board ready UI in `index.html` + `app.js`.

| Piece | Source |
|-------|--------|
| Release list | GitHub Releases API |
| Board picker + firmware files | `manifests/releases/{tag}.json` + `firmware/{tag}/` on Pages (mirrored from GitHub Releases; browser cannot fetch release assets cross-origin) |
| Firmware binaries | `{board_id}-bootloader.bin`, `{board_id}-espd.bin`, … per release |
| Deploy | `.github/workflows/pages.yml` → GitHub Pages |

## Release manifest

**`manifest.json`** is attached to each GitHub Release tag and drives the board list. Generated from `boards/<id>.yaml` on tag:

```yaml
id: waveshare_s3
name: Waveshare ESP32-S3-AUDIO   # flasher title
note: USB Serial JTAG sync       # optional subtitle
```

Board photo: `flasher/assets/boards/<id>.jpg` (included in the manifest only when the file exists).

`help` is for menuconfig / integrators — not shown in the flasher.

Example:

```json
{
  "version": "v0.1.0",
  "boards": [
    {
      "id": "waveshare_s3",
      "target": "esp32s3",
      "chip": "ESP32-S3",
      "title": "Waveshare ESP32-S3-AUDIO",
      "note": "USB Serial JTAG sync",
      "image": "assets/boards/waveshare_s3.jpg",
      "files": {
        "bootloader": { "url": "…/waveshare_s3-bootloader.bin", "offset": 0 },
        "partition_table": { "url": "…/waveshare_s3-partition-table.bin", "offset": 32768 },
        "app": { "url": "…/waveshare_s3-espd.bin", "offset": 65536 }
      }
    }
  ]
}
```

Generate locally:

```bash
python3 scripts/generate-manifest.py --version v0.1.0 \
  --base-url "https://github.com/ben-wes/espd-kits/releases/download/v0.1.0" \
  -o /tmp/manifest.json
```

## Patch sync (browser)

`sync.js` implements the same CDC protocol as [`espd/scripts/espd_sync.py`](../espd/scripts/espd_sync.py):

- `STATUS`, `PUT`, `RELOAD`, `RESET`
- Prepares SD (`/sdcard`); if the internal flash is in host-drive mode, `RESET` reboots into Pd mode (`/storage`)
- After reboot, reconnects via `navigator.serial.getPorts()` (port must stay authorized)

**Browser limits:**

- Folder pick: `showDirectoryPicker()` (Chrome / Edge)
- Auto-watch: `FileSystemObserver` when available; otherwise **Sync now**
- If reconnect after reboot fails, user must pick the USB port again

See [espd/docs/DEV_SYNC.md](../espd/docs/DEV_SYNC.md) for protocol and storage rules.

## SoftAP device console

Boards with `ESPD_WIFI_AP_SYNC` (e.g. `waveshare_s3_ap`) serve a web UI after you join the SoftAP:

- **https://192.168.4.1/** — monitor, patch sync, live folder watch (self-signed cert; accept browser warning once)

- Static UI embedded in firmware (`espd/main/device_console/`)
- **WebSocket `/ws`** — same line protocol as USB/TCP (monitor log + patch sync)
- **TCP :4499** — still available for [`espd_sync.py`](../espd/scripts/espd_sync.py)

The GitHub Pages flasher cannot talk to the device over Wi‑Fi (browser security); use the on-device console or the Python script instead.

## Adding a board

1. Add `boards/<id>.yaml`

CI, `build-board.sh`, and release manifests discover boards from that directory automatically.

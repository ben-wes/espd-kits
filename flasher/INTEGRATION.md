# Web flasher integration

## Current public site

[https://flasher.michaelkramer.at/](https://flasher.michaelkramer.at/) — **ESPD Web Flasher** (German UI, Web Serial, serial monitor, erase).

### What we could find

- **No separate public GitHub repo** under `ben-wes`, `mkalten`, or `michaelkramer` for this UI.
- The site is a **single large HTML document** (~230 KB) with **inline CSS/JS** (includes [pako](https://github.com/nodeca/pako) for compression).
- Firmware list today is wired to **`ben-wes/espd` GitHub Releases**; board metadata is **hardcoded in JS** (e.g. `waveshare_s3`, `korvo2`, `xiao_s3`).
- Footer links: `ben-wes/espd`, Pure Data, tamlab.kunstuni-linz.at.

So integration means **vendoring that HTML/JS** (with the author’s permission) or getting the **source repo** from Michael Kramer / the institute.

## Target for espd-kits

| Piece | Change |
|-------|--------|
| Release URL | `https://github.com/ben-wes/espd-kits/releases` (or your fork) |
| Board list | Load from `manifests/releases.json` (+ optional images under `flasher/boards/`) |
| Chip filter | Derive from manifest `target` field |
| Stub in this repo | `index.html` placeholder until vendored UI lands |

## Suggested steps

1. **Get source** — ask for the git repo or a zip of the flasher tree (preferred over scraping production HTML).
2. **Add as submodule or `flasher/vendor/espd-web-flasher/`** with LICENSE noted in README.
3. **Patch** release fetcher to use `manifests/releases.json` from the same tag as firmware assets.
4. **CI (`pages.yml`)** — copy `manifests/releases.json` → `flasher/manifests/`; deploy `flasher/`.
5. **Custom domain** (optional) — CNAME to GitHub Pages or keep `flasher.michaelkramer.at` pointing at the new host.

## Manifest contract (kits)

`scripts/generate-manifest.py` emits:

```json
{
  "version": "v0.1.0",
  "boards": [
    {
      "id": "waveshare_s3",
      "name": "Waveshare ESP32-S3-AUDIO",
      "target": "esp32s3",
      "files": {
        "bootloader": { "url": "…/bootloader.bin", "offset": 0 },
        "partition_table": { "url": "…/partition-table.bin", "offset": 32768 },
        "app": { "url": "…/espd.bin", "offset": 65536 }
      }
    }
  ]
}
```

Offsets must match `espd/build/flash_args` per board (manifest generator may read `flash_args` in a later revision).

## If you provide the source

Place it at `flasher/vendor/` or send the repo URL; we can wire submodule + Pages + release URL in one pass.

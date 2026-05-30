# Web flasher

Deployed to **GitHub Pages** from this directory.

- **Integration plan:** [INTEGRATION.md](INTEGRATION.md)
- **Reference UI:** [flasher.michaelkramer.at](https://flasher.michaelkramer.at/) (source repo not public — provide tree to vendor here)
- **Manifest:** `manifests/releases.json` (copied here on release by CI)

## Local preview

```bash
mkdir -p flasher/manifests && cp manifests/releases.json flasher/manifests/
python3 -m http.server 8080 --directory flasher
```

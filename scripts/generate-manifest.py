#!/usr/bin/env python3
"""Kit helpers: board discovery, CI matrix, release manifest.json for the flasher."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def board_kconfig_choice(board_id: str) -> str:
    """menuconfig board choice line for sdkconfig.defaults.local."""
    return f"CONFIG_ESPD_BOARD_{board_id.upper()}=y"


def board_select_for_path(yaml_path: Path) -> str:
    if yaml is None:
        raise SystemExit("PyYAML required: pip install pyyaml")
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"{yaml_path}: expected mapping at top level")
    board_id = data.get("id") or yaml_path.stem
    return board_kconfig_choice(board_id)


def discover_boards(root: Path) -> list[dict]:
    """All kit boards: one entry per boards/<id>.yaml."""
    if yaml is None:
        raise SystemExit("PyYAML required: pip install pyyaml")
    boards_dir = root / "boards"
    entries: list[dict] = []
    for path in sorted(boards_dir.glob("*.yaml")):
        if path.name == "index.yaml":
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise SystemExit(f"{path}: expected mapping at top level")
        board_id = data.get("id") or path.stem
        entries.append(
            {
                "id": board_id,
                "name": data.get("name") or board_id,
                "target": data.get("target") or "",
                "data": data,
            }
        )
    return entries


def chip_label(target: str) -> str:
    if target.startswith("esp32s3"):
        return "ESP32-S3"
    if target.startswith("esp32c3"):
        return "ESP32-C3"
    if target.startswith("esp32c6"):
        return "ESP32-C6"
    if target.startswith("esp32p4"):
        return "ESP32-P4"
    if target == "esp32":
        return "ESP32"
    return target.upper()


def board_description(data: dict) -> str:
    help_text = data.get("help") or ""
    if isinstance(help_text, str):
        line = help_text.strip().split("\n")[0].strip()
        if " (" in line:
            line = line.split(" (")[0].strip()
        return line
    return ""


def release_board_entry(board: dict) -> dict:
    data = board["data"]
    entry = {
        "id": board["id"],
        "name": board["name"],
        "target": board["target"],
        "chip": chip_label(board["target"]),
        "description": board_description(data),
    }
    flasher = data.get("flasher") or {}
    if isinstance(flasher, dict) and flasher.get("image"):
        entry["image"] = flasher["image"]
    return entry


def boards_by_id(root: Path) -> dict[str, dict]:
    return {b["id"]: b for b in discover_boards(root)}


def bootloader_offset(target: str) -> int:
    """Flash offset of the bootloader, which is target-dependent.

    Classic ESP32 and S2 reserve 0x0..0x1000 (and place the bootloader at
    0x1000); P4 uses 0x2000; newer chips (S3, C2/C3/C6, H2) start at 0x0.
    Flashing at the wrong offset bricks the boot — esp32_dac (esp32) needs 0x1000.
    """
    if target in ("esp32", "esp32s2"):
        return 0x1000
    if target == "esp32p4":
        return 0x2000
    return 0


def release_files(base: str, board_id: str, target: str) -> dict:
    prefix = base.rstrip("/")
    return {
        "bootloader": {
            "url": f"{prefix}/{board_id}-bootloader.bin",
            "offset": bootloader_offset(target),
        },
        "partition_table": {
            "url": f"{prefix}/{board_id}-partition-table.bin",
            "offset": 32768,
        },
        "app": {"url": f"{prefix}/{board_id}-espd.bin", "offset": 65536},
    }


def write_release_manifest(
    root: Path, out_path: Path, version: str, base_url: str
) -> None:
    base = base_url.rstrip("/")
    out_boards = []
    for board in discover_boards(root):
        entry = release_board_entry(board)
        if base:
            entry["files"] = release_files(base, board["id"], board["target"])
        out_boards.append(entry)
    manifest = {"version": version, "boards": out_boards}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")


def board_matrix_json(root: Path) -> str:
    boards = discover_boards(root)
    return json.dumps({"board": [b["id"] for b in boards]})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--matrix-json",
        action="store_true",
        help="print GitHub Actions matrix JSON for board ids",
    )
    ap.add_argument(
        "--select",
        metavar="BOARD",
        help="print CONFIG_ESPD_BOARD_*=y for boards/BOARD.yaml",
    )
    ap.add_argument("--version", default="dev", help="release tag, e.g. v0.1.0")
    ap.add_argument(
        "--base-url",
        default="",
        help="URL prefix for assets, e.g. https://github.com/ben-wes/espd-kits/releases/download/v0.1.0",
    )
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("-o", "--output", type=Path, default=None)
    args = ap.parse_args()

    root = args.root
    if args.select:
        yaml_path = root / "boards" / f"{args.select}.yaml"
        if not yaml_path.is_file():
            raise SystemExit(f"missing {yaml_path}")
        print(board_select_for_path(yaml_path))
        return 0
    if args.matrix_json:
        print(board_matrix_json(root))
        return 0

    if not args.base_url:
        raise SystemExit("--base-url is required for release manifest generation")
    out_path = args.output or (root / "manifest.json")
    write_release_manifest(root, out_path, args.version, args.base_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

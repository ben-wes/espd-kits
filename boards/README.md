# Board definitions

YAML files here are the **only** source of truth for kit boards — one file per board (`<id>.yaml`). CI and `generate-manifest.py` discover them automatically.

Builds point **`ESPD_BOARDS_DIR`** at this directory (the `espd` submodule is not modified and board YAMLs are not copied into it).

Schema and authoring guide: **[espd/docs/ADDING_A_BOARD.md](../espd/docs/ADDING_A_BOARD.md)** (in submodule).

`build-board.sh` and CI write **`CONFIG_ESPD_BOARD_<ID>=y`** to **`espd/sdkconfig.defaults.local`** from the YAML `id`.

## Adding a board

1. Add `boards/<id>.yaml`
2. Tag a release — CI builds firmware and attaches `manifest.json`; Pages mirrors `flasher/manifests/releases/{tag}.json`

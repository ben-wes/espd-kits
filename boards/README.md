# Board definitions

YAML files here are the **source of truth** for kit builds. Builds set **`ESPD_BOARDS_DIR`** to this directory (the `espd` submodule is not modified).

Schema and authoring guide: **[espd/docs/ADDING_A_BOARD.md](../espd/docs/ADDING_A_BOARD.md)** (in submodule).

Each board needs **`config/boards/<id>.select`**, merged into **`espd/sdkconfig.defaults.local`** for builds.

An optional copy of a kit YAML may also exist under **`espd/boards/`** as a reference for firmware-only workflows.

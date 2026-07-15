# Raw Datasets Directory (`datasets/raw/`)

This directory is a storage target for raw game footage, uncompressed screenshots, and full gameplay recordings captured directly from Android emulators.

---

## Directory Guidelines

- **Formats**: Save captured frames as lossless `.png` (for calibration) or `.jpg` buffers (for training footage).
- **Git Rules**: This directory is ignored by Git, except for this `README.md` file. Do not commit heavy video/image assets.
- **Naming Structure**: File names should follow `run_<timestamp>_fps<fps>_cookie_<type>_<index>.png` structure.

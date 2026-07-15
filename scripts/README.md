# Scripts Directory (`scripts/`)

This directory houses infrastructure, pipeline utilities, evaluation execution, and automation helper scripts.

---

## Script Guidelines

All scripts must comply with the following standards:
- **Executable**: Scripts must be designed to run standalone.
- **Argument Parsing**: Use standard Python `argparse` to parse inputs, providing detailed help texts.
- **Config First**: Avoid hardcoded constants inside script logic; read system thresholds and parameters from the `configs/` folder.
- **Linter & Typing**: All scripts must be fully type-hinted and format-compliant (checked by Ruff).

---

## Directory Index (Planned Scripts)

1.  **`calibrate_display.py`**: Assist the developer in verifying emulator dimensions and cropping bounding coordinates.
2.  **`collect_raw_dataset.py`**: Loop through gameplay capture frames and export images into raw dataset folders.
3.  **`train_detector.py`**: Model training routine that loads processed folders and outputs weight checkpoints to `models/`.

# Configurations Directory (`configs/`)

This directory contains configuration files defining structural inputs, calibration offsets, system paths, emulator profiles, and vision thresholds.

---

## Architecture Guidelines

- **Config-First**: Hardcoding magic numbers or environmental parameters inside python modules is strictly prohibited.
- **Formating Standard**: Use structured formats like `json` or `yaml`.
- **Environment Exclusions**: Specific connection configurations (e.g., local emulator ADB IP, token/port strings) should use prefixes like `local_` and must be ignored in `.gitignore`.

---

## Directory Index (Future Files)

1.  **`system.yaml`**: Emulator resolution settings, crop region coordinates, ADB target TCP address.
2.  **`vision_thresholds.yaml`**: Classification confidence margins, overlapping boundary ratios (IoU thresholds), color masks.
3.  **`policy_heuristics.yaml`**: Jump velocity thresholds, slide length buffers, fever gauge limits.

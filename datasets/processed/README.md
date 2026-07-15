# Processed Datasets Directory (`datasets/processed/`)

This directory holds preprocessed training samples, augmented images, label annotations, and normalized model input tensors.

---

## Directory Guidelines

- **Standard Annotation Formats**: Store object labels in YOLO text files (`.txt`) corresponding to each frame, using standard normalized coordinates: `<object-class> <x_center> <y_center> <width> <height>`.
- **Classification Categories**:
  - Class `0`: Cookie
  - Class `1`: Ground Obstacle
  - Class `2`: High Obstacle
  - Class `3`: Jelly
  - Class `4`: Coin
  - Class `5`: Potion
- **Split Standard**: Organize directories into distinct `train/`, `val/`, and `test/` splits.
- **Git Rules**: Processed datasets are ignored by Git, except for this `README.md` file.

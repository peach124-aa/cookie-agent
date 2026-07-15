# Serialized Models Directory (`models/`)

This directory houses trained neural network weights, optimized graphs, and inference parameters.

---

## Directory Guidelines

- **Supported Formats**:
  - PyTorch standard weights: `.pt` or `.pth`.
  - Optimized deployment graphs: `.onnx`.
- **Naming Conventions**: Use `detector_<arch>_<version>_<resolution>_mAP<val>.onnx` (e.g. `detector_yolov8n_v1.0_1280x720_mAP92.onnx`).
- **Git Rules**: Model binary files are excluded by Git via `.gitignore`, except for this `README.md` file. Do not commit heavy model checkpoints to Git.

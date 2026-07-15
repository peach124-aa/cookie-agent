# Replay Logs Directory (`datasets/replay/`)

This directory stores serialized execution trace files mapping simulated controller inputs to corresponding game timeline states.

---

## Directory Guidelines

- **Purpose**: Facilitate behavior cloning and evaluation checks.
- **Formats**: Use standard `.jsonl` or `.csv` files mapping timestamp markers to user action matrices: `[Timestamp, FrameID, Action(Jump/DoubleJump/Slide), Score, HP]`.
- **Git Rules**: This directory is ignored by Git, except for this `README.md` file. Do not commit local gameplay session files.

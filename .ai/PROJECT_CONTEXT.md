# Project Context - Cookie Run Classic

This document provides context regarding the target game, platform boundaries, and operational constraints for the **Cookie Agent** project.

---

## 1. The Target Game: CookieRun Classic (쿠키런 for Kakao)

### Game Description
CookieRun Classic is an auto-running side-scrolling platformer. The player controls a cookie running from left to right. The screen scrolls dynamically, speed increases over time, and obstacles appear in various heights and configurations.

### Control System
The controls are extremely simple:
1. **Jump**: Pressing the left side of the screen initiates a jump. Pressing it again in mid-air initiates a double jump.
2. **Slide**: Pressing and holding the right side of the screen makes the cookie slide underneath high obstacles.

### Core Mechanics
- **Health (HP)**: The cookie has a decaying health bar. Colliding with obstacles inflicts damage, while collecting potions restores health.
- **Jellies**: Various jellies (basic, yellow, pink, bear jellies) populate the screen, acting as scoring indicators and guiding the path.
- **Fever Mode**: Collecting special jellies or filling a gauge sends the player into Fever Mode, where they run in a safe, jelly-rich environment.
- **Obstacles**:
  - Ground Obstacles: Require jumping.
  - Floating Obstacles: Require sliding or double-jumping.
  - Dynamic Obstacles: Fall or emerge suddenly.

---

## 2. Infrastructure & Operating Environment (Future Phases)

To guide future runtime engineers and vision models, the operating ecosystem will be structured as follows:

### Platform Boundaries
- **Runtime Host**: Windows PC.
- **Android Emulator**: LDPlayer, BlueStacks, or Nox Player running a stable instance of the game.
- **Connection Interface**: Android Debug Bridge (ADB) via TCP/IP or localhost socket connections.

### Capturing Display Output
- **Methodology**: High-speed screen acquisition using OS-level graphic buffers (e.g., Desktop Duplication API, Scrcpy frame buffers, or Win32 GDI).
- **Target Resolution**: Usually scaled to a standard aspect ratio (e.g., `1280x720` or `1920x1080` at 60 FPS).
- **Latency Requirement**: Acquisition and preprocessing must run under **16.6ms** (1 frame at 60Hz).

### Simulating Touch Events
- **Methodology**: Tap and touch drag actions sent to `/dev/input/event*` via ADB shell command interfaces, or direct click simulations through Win32 API to the emulator window.
- **Timing Constraint**: Action latency must be minimal to execute jumps exactly before obstacle collisions.

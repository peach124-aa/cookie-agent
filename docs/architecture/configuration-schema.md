# Configuration Schema Specification

This document defines the architectural contract and validation schema for the configuration files inside the **Cookie Agent** system.

---

## 1. Configuration Principles

The system strictly adheres to the following core architectural rules:

1.  **Config-First Architecture**: Components must be initialized using configuration blocks. Code files must only implement logic structures, leaving all parameter attributes externally defined.
2.  **No Magic Numbers**: Pixel offsets, threshold scores, connection timeouts, and frame rates must reside exclusively in configuration files.
3.  **No Hardcoded Paths**: Model directories, logs targets, and cache buffers must be configurable dynamically.
4.  **No Runtime Constants**: Variables affecting agent behavior must never be declared as final compile-time constants in modules.
5.  **Environment Override Priority**: Values loaded from storage are overridden by system environment variables matching the configuration node path (e.g. `COOKIE_DETECTOR_DEVICE=cuda` overrides settings in `detector.yaml`).

---

## 2. Configuration Layout and Directory Structure

The configuration files reside under the `configs/` folder structured as follows:

```
configs/
├── defaults/          # Version-controlled baseline defaults
│   ├── app.yaml
│   ├── device.yaml
│   ├── capture.yaml
│   ├── detector.yaml
│   ├── planner.yaml
│   ├── reward.yaml
│   ├── character.yaml
│   ├── training.yaml
│   └── logging.yaml
└── local/             # Git-ignored local developer overrides
    └── (developer override files)
```

-   **`configs/defaults/`**: Standard default values. This directory is checked into Git version control to establish baseline properties.
-   **`configs/local/`**: Local configuration file overrides. This directory is excluded in `.gitignore`. Local properties are merged on top of defaults at startup.
-   **Runtime Merging Order**:
    $$\text{Default Settings} \longrightarrow \text{Local Settings (Overrides)} \longrightarrow \text{Environment Variables (Highest Priority)}$$

---

## 3. Configuration File Specifications

Every configuration file must declare the top-level property `schema_version` at the start of the document.

### 3.1. `app.yaml`
Governs core properties of the python process.

#### YAML Example
```yaml
schema_version: 1
app:
  project_name: "cookie_agent"
  version: "1.0.0"
  debug: false
  log_level: "INFO"
```

#### Schema Validation Properties
| Parameter | Type | Required | Default | Constraint / Range |
| :--- | :--- | :---: | :---: | :--- |
| `schema_version` | Integer | Yes | N/A | Must be `>= 1` |
| `app.project_name`| String | Yes | N/A | Must equal `"cookie_agent"` |
| `app.version` | String | Yes | N/A | Semantic versioning format |
| `app.debug` | Boolean | No | `false` | True or False |
| `app.log_level` | String | No | `"INFO"` | `["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]` |

---

### 3.2. `device.yaml`
Establishes resolution limits and connection parameters for the Android emulator.

#### YAML Example
```yaml
schema_version: 1
device:
  adb_serial: "127.0.0.1:5555"
  emulator_name: "MuMuPlayer"
  resolution:
    width: 1280
    height: 720
  orientation: "landscape"
  capture_backend: "DXGI"
```

#### Schema Validation Properties
| Parameter | Type | Required | Default | Constraint / Range |
| :--- | :--- | :---: | :---: | :--- |
| `schema_version` | Integer | Yes | N/A | Must be `>= 1` |
| `device.adb_serial`| String | Yes | N/A | Format: `<ip>:<port>` or serial hash |
| `device.emulator_name`| String | Yes | N/A | Non-empty alphanumeric string |
| `device.resolution.width`| Integer| Yes | `1280` | `[640, 3840]` (supports scaling in future stages) |
| `device.resolution.height`|Integer| Yes | `720` | `[360, 2160]` (supports scaling in future stages) |
| `device.orientation`| String | No | `"landscape"` | `["landscape", "portrait"]` |
| `device.capture_backend`| String| No | `"DXGI"` | `["GDI", "DXGI", "ADB"]` |

---

### 3.3. `capture.yaml`
Configures the graphics pipeline thread responsible for capturing emulator frames.

#### YAML Example
```yaml
schema_version: 1
capture:
  backend: "DXGI"
  target_fps: 60
  queue_size: 3
  retry_policy:
    max_retries: 5
    backoff_ms: 100
```

#### Schema Validation Properties
| Parameter | Type | Required | Default | Constraint / Range |
| :--- | :--- | :---: | :---: | :--- |
| `schema_version` | Integer | Yes | N/A | Must be `>= 1` |
| `capture.backend` | String | Yes | `"DXGI"` | `["GDI", "DXGI", "ADB"]` |
| `capture.target_fps`| Integer | No | `60` | `[1, 120]` (defines target capture rate) |
| `capture.queue_size`| Integer | No | `3` | `[1, 10]` |
| `capture.retry_policy.max_retries`|Integer| No | `5` | `[0, 100]` |
| `capture.retry_policy.backoff_ms`| Integer| No | `100` | `[10, 10000]` |

---

### 3.4. `detector.yaml`
Configures the visual target detector.

#### YAML Example
```yaml
schema_version: 1
detector:
  detector_type: "yolov8n"
  model_path: "models/detector_yolov8n_v1.0.onnx"
  confidence_threshold: 0.75
  iou_threshold: 0.45
  device: "auto"
  half_precision: true
```

#### Schema Validation Properties
| Parameter | Type | Required | Default | Constraint / Range |
| :--- | :--- | :---: | :---: | :--- |
| `schema_version` | Integer | Yes | N/A | Must be `>= 1` |
| `detector.detector_type`| String | Yes | N/A | `["yolov8n", "yolonas", "custom_cnn"]` |
| `detector.model_path` | String | Yes | N/A | Path must exist under the workspace directory |
| `detector.confidence_threshold`|Float| No | `0.70` | `[0.0, 1.0]` |
| `detector.iou_threshold`| Float | No | `0.45` | `[0.0, 1.0]` |
| `detector.device` | String | No | `"auto"` | `["auto", "cpu", "cuda"]` |
| `detector.half_precision`| Boolean| No | `true` | True or False |

#### Design Notes
- **`device`**: Set to `"auto"` to enable GPU execution (CUDA) if available, falling back to CPU.
- **`half_precision`**: Setting this parameter to `true` enables FP16 execution modes, which reduces latency on supported architectures (such as CUDA cores or future TensorRT/ONNX optimizations).

---

### 3.5. `planner.yaml`
Configures input tap variations and action schedules.

#### YAML Example
```yaml
schema_version: 1
planner:
  tap_variance:
    max_offset_x: 10
    max_offset_y: 10
  hold_variance:
    max_jitter_ms: 10
  timing_variance:
    max_delay_jitter_ms: 15
  cooldown_rules:
    jump_cooldown_ms: 200
    slide_cooldown_ms: 100
```

#### Schema Validation Properties
| Parameter | Type | Required | Default | Constraint / Range |
| :--- | :--- | :---: | :---: | :--- |
| `schema_version` | Integer | Yes | N/A | Must be `>= 1` |
| `planner.tap_variance.max_offset_x`| Integer| No | `5` | `[0, 50]` pixels (random touch target noise) |
| `planner.tap_variance.max_offset_y`| Integer| No | `5` | `[0, 50]` pixels (random touch target noise) |
| `planner.hold_variance.max_jitter_ms`|Integer| No | `5` | `[0, 100]` milliseconds (press duration noise) |
| `planner.timing_variance.max_delay_jitter_ms`|Integer| No | `10` | `[0, 200]` milliseconds (action interval noise) |
| `planner.cooldown_rules.jump_cooldown_ms`|Integer| No | `200` | `[50, 1000]` milliseconds |
| `planner.cooldown_rules.slide_cooldown_ms`|Integer| No | `100` | `[50, 1000]` milliseconds |

---

### 3.6. `reward.yaml`
Specifies scoring models.

#### YAML Example
```yaml
schema_version: 1
reward:
  strategy: "survival"
  survival:
    points_per_distance_pixel: 1.0
    points_per_jelly: 0.1
    damage_penalty: -100.0
    collision_penalty: -500.0
  coin_farming:
    points_per_distance_pixel: 0.1
    points_per_jelly: 0.05
    points_per_coin: 5.0
    damage_penalty: -50.0
    collision_penalty: -500.0
  score_farming:
    points_per_distance_pixel: 0.5
    points_per_jelly: 2.0
    points_per_coin: 0.1
    damage_penalty: -200.0
    collision_penalty: -800.0
```

#### Schema Validation Properties
| Parameter | Type | Required | Default | Constraint / Range |
| :--- | :--- | :---: | :---: | :--- |
| `schema_version` | Integer | Yes | N/A | Must be `>= 1` |
| `reward.strategy` | String | Yes | `"survival"` | Must match one of `["survival", "coin_farming", "score_farming"]` |
| `reward.survival.points_per_distance_pixel`|Float|Yes|`1.0`| `>= 0.0` |
| `reward.survival.points_per_jelly`|Float|Yes|`0.1`| `>= 0.0` |
| `reward.survival.damage_penalty`|Float|Yes|`-100.0`| `<= 0.0` |
| `reward.survival.collision_penalty`|Float|Yes|`-500.0`| `<= 0.0` |

---

### 3.7. `character.yaml`
Encapsulates features representing selected runners.

#### YAML Example
```yaml
schema_version: 1
character:
  active_id: "brave_cookie"
  roster:
    brave_cookie:
      name: "GingerBrave"
      abilities: []
      cooldowns: {}
      movement:
        base_speed: 1.0
        jump_height_pixels: 240
      detectors:
        - "models/brave_cookie_bounds.onnx"
    zombie_cookie:
      name: "Zombie Cookie"
      abilities:
        - name: "revive"
          hp_restore: 30
          max_activations: 1
      cooldowns:
        revive_cooldown_ms: 0
      movement:
        base_speed: 1.0
        jump_height_pixels: 240
      detectors:
        - "models/zombie_cookie_bounds.onnx"
```

#### Design Notes
- Avoids hardcoded movement paths. Jump height boundaries, revive metrics, and custom model networks are defined on a per-character basis.
- **`abilities`** and **`detectors`** allow easy expansion to multi-character setups.

---

### 3.8. `training.yaml`
Hyperparameters for policy training (Schema Only).

#### YAML Example
```yaml
schema_version: 1
training:
  algorithm: "PPO"
  seed: 42
  batch_size: 64
  learning_rate: 0.0003
  checkpoint_dir: "models/checkpoints/"
  resume: false
  device: "cuda"
  num_workers: 4
  replay_buffer:
    capacity: 100000
    burn_in_steps: 1000
```

#### Schema Validation Properties
| Parameter | Type | Required | Default | Constraint / Range |
| :--- | :--- | :---: | :---: | :--- |
| `schema_version` | Integer | Yes | N/A | Must be `>= 1` |
| `training.algorithm` | String | Yes | `"PPO"` | `["PPO", "DQN", "SAC"]` |
| `training.seed` | Integer | No | `42` | `[0, 2147483647]` |
| `training.batch_size` | Integer | Yes | `64` | `[8, 4096]` |
| `training.learning_rate`| Float | Yes | `0.0003` | `[1e-6, 1e-1]` |
| `training.checkpoint_dir`|String | Yes | `"models/checkpoints/"` | Directory path must exist inside workspace |
| `training.resume` | Boolean | No | `false` | True or False |
| `training.device` | String | No | `"cuda"` | `["cpu", "cuda", "auto"]` |
| `training.num_workers` | Integer | No | `4` | `[0, 64]` |

---

### 3.9. `logging.yaml`
Determines log and diagnostic screenshot behavior.

#### YAML Example
```yaml
schema_version: 1
logging:
  log_directory: "logs/"
  log_rotation:
    max_bytes: 10485760
    backup_count: 5
  save_frames: false
  save_replay: true
  save_detector_output: false
  save_tracker_output: false
```

#### Schema Validation Properties
| Parameter | Type | Required | Default | Constraint / Range |
| :--- | :--- | :---: | :---: | :--- |
| `schema_version` | Integer | Yes | N/A | Must be `>= 1` |
| `logging.log_directory`| String | Yes | `"logs/"` | Must point inside the workspace directory |
| `logging.save_frames` | Boolean | Yes | `false` | Save raw graphical frames to `datasets/raw/` |
| `logging.save_replay` | Boolean | Yes | `true` | Log execution inputs to `datasets/replay/` |
| `logging.save_detector_output`|Boolean|No| `false` | Export bounding box predictions for diagnostic review |
| `logging.save_tracker_output`|Boolean|No| `false` | Export tracking lines and velocity lists |

#### Debugging Workflow
By configuring these booleans, the developer can toggle precise diagnostic hooks:
- During active play validation, setting `save_detector_output: true` allows inspecting overlay boxes to locate model inference mismatches.
- Disabling `save_frames` during training runs avoids saturating storage paths.

---

## 4. Versioning and Migrations

### 4.1. Versioning
We use an integer schema version mapping: `schema_version: X`.
- Increments denote breaking configuration schema structure mutations.

### 4.2. Migration Strategy
If a configuration's layout changes:
- Loader functions must write migration scripts mapping legacy keys to modern nodes.
- Attempting to parse files with legacy version indexes triggers a migration script conversion before parsing values into variables.

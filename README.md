# JetsonEyes

A practical guide and example code for setting up dual MIPI CSI cameras on NVIDIA Jetson devices.

This work is part of the [ArcheryEdge](https://github.com/zebraoptics/ArcheryEdge) project, where the dual-camera setup serves as the stereo vision system for arrow tracking and trajectory analysis.

---

## Overview

Getting CSI cameras running on Jetson is non-trivial — the NVIDIA Argus stack requires GStreamer, and the commonly used `opencv-python` package from PyPI is compiled without it. This repository documents the correct environment setup and provides a ready-to-use dual-camera streaming library.

**What's included:**

| File | Description |
|------|-------------|
| `jetson_csi_camera.py` | Dual CSI camera library — threaded capture, FPS tracking, context manager |
| `main.py` | Live dual-camera preview with snapshot support |
| `SETUP.md` | Full hardware and environment setup guide |

---

## Quick Start

See [`SETUP.md`](SETUP.md) for the full hardware wiring and `jetson-io` configuration steps.

### Environment

```bash
# Use the system Python 3.10 (required for NVIDIA OpenCV with GStreamer)
/usr/bin/python3.10 -m venv .venv --system-site-packages
.venv/bin/pip install "numpy<2"
```

### Run

```bash
.venv/bin/python main.py
```

| Key | Action |
|-----|--------|
| `q` | Quit |
| `s` | Save snapshot pair |

---

## Library Usage

```python
from jetson_csi_camera import DualCSICamera, DualCameraConfig, CameraConfig

config = DualCameraConfig(
    cam0=CameraConfig(sensor_id=0, width=1920, height=1080, framerate=30),
    cam1=CameraConfig(sensor_id=1, width=1920, height=1080, framerate=30),
)

with DualCSICamera(config) as cams:
    while True:
        left, right = cams.read()
        if left is not None and right is not None:
            # process stereo frames
            pass
```

---

## Key Findings

- **Do not use `opencv-python` from PyPI** on Jetson for CSI cameras — it has no GStreamer support and fails silently.
- Use the **NVIDIA-provided OpenCV** (`/usr/lib/python3.10/dist-packages/cv2/`) via a `--system-site-packages` venv.
- Use **`/usr/bin/python3.10`** to create the venv, not `/usr/local/bin/python3.10` (a separate custom build that cannot find the NVIDIA packages).
- **NumPy must be pinned to `<2`** — the NVIDIA OpenCV binary is linked against the NumPy 1.x ABI.
- Only use sensor modes supported by the hardware. For IMX219: `1920×1080 @ 30fps`, `3280×2464 @ 21fps`, etc. See `SETUP.md` for the full table.

---

## Tested On

- Jetson Orin Nano Super
- JetPack / GStreamer 1.20.3
- OpenCV 4.8.0 (NVIDIA build)
- Raspberry Pi Camera Module v2 / Arducam (IMX219 sensor)

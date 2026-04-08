# JetsonEyes — MIPI CSI Camera Environment Setup on Jetson

## Requirements

- NVIDIA Jetson (tested on Jetson Orin Nano Super)
- JetPack with GStreamer and `nvarguscamerasrc` plugin
- Two MIPI CSI cameras (e.g. Raspberry Pi Camera Module v2 / Arducam) 
- Two 22-pin MIPI cabels
- Python 3.10 system installation (`/usr/bin/python3.10`)*

*Other versions should work as well.

---

## Hardware Setup

### 1. Connect the cameras

Install both CSI cameras via MIPI flat cables into the 22-pin CSI connector on the Jetson.
Make sure the cable orientation is not flipped (metal contacts facing the correct direction).

### 2. Configure the CSI connector with `jetson-io`

```bash
cd /opt/nvidia/jetson-io/
sudo python jetson-io.py
```

**Step 1** — Select `Configure Jetson 22pin CSI Connector`:

```
=================== Jetson Expansion Header Tool ===================
|                                                                    |
|                    Select one of the following:                    |
|                                                                    |
|                   Configure Jetson 40pin Header                    |
|                Configure Jetson 22pin CSI Connector                |
|                  Configure Jetson M.2 Key E Slot                   |
|                                Exit                                |
|====================================================================|
```

**Step 2** — Select `Configure for compatible hardware`:

```
=================== Jetson Expansion Header Tool ===================
|                                                                    |
|                      3.3V (  1) .. (  2) i2c3                      |
|                      i2c3 (  3) .. (  4) GND                       |
|                       GND (  7) .. (  8) NA                        |
|                        NA (  9) .. ( 10) GND                       |
|                       GND ( 13) .. ( 14) NA                        |
|                        NA ( 15) .. ( 16) GND                       |
|                       GND ( 19) .. ( 20) NA                        |
|                        NA ( 21) .. ( 22) GND                       |
|                                                                    |
|                    Jetson 22pin CSI Connector:                     |
|                                                                    |
|                 Configure for compatible hardware                  |
|                                Back                                |
|====================================================================|
```

**Step 3** — Choose your camera model. For two IMX219 cameras select `Camera IMX219 Dual`:

```
=================== Jetson Expansion Header Tool ===================
|                                                                    |
|                Select one of the following options:                |
|                                                                    |
|                         Camera IMX219 Dual                         |
|                          Camera IMX219-A                           |
|                    Camera IMX219-A and IMX477-C                    |
|                          Camera IMX219-C                           |
|                         Camera IMX477 Dual                         |
|                          Camera IMX477-A                           |
|                    Camera IMX477-A and IMX219-C                    |
|                          Camera IMX477-C                           |
|                                Back                                |
|====================================================================|
```

Save and exit.

### 3. Verify the cameras are detected

```bash
ls /dev/video*
```

Expected output:
```
/dev/video0  /dev/video1
```

---

## Environment Setup

### Why not `opencv-python` from PyPI?

CSI cameras on Jetson use the NVIDIA Argus stack via GStreamer (`nvarguscamerasrc`).
OpenCV must be compiled with GStreamer support to open these pipelines.

`opencv-python` from PyPI is compiled **without** GStreamer and will silently fail.
The correct OpenCV is the NVIDIA-provided build at `/usr/lib/python3.10/dist-packages/cv2/`,
installed via JetPack/apt with GStreamer support included.

> **Important:** Use `/usr/bin/python3.10` (the system Python). The custom Python build
> at `/usr/local/bin/python3.10` does not include `/usr/lib` in its path and cannot see
> the NVIDIA OpenCV.

### 1. Create the virtual environment

```bash
/usr/bin/python3.10 -m venv .venv --system-site-packages
```

`--system-site-packages` gives the venv access to the NVIDIA OpenCV at
`/usr/lib/python3.10/dist-packages/`.

### 2. Pin NumPy to < 2

The NVIDIA OpenCV binary was compiled against NumPy 1.x. NumPy 2.x breaks the ABI.

```bash
.venv/bin/pip install "numpy<2"
```

### 3. Verify GStreamer support

```bash
.venv/bin/python -c "import cv2; [print(l) for l in cv2.getBuildInformation().split('\n') if 'gstreamer' in l.lower()]"
```

Expected output:
```
    GStreamer:                   YES (1.20.3)
```

---

## Running

```bash
.venv/bin/python main.py
```

| Key | Action |
|-----|--------|
| `q` | Quit |
| `s` | Save a snapshot pair (`snap_cam0_<ts>.jpg` / `snap_cam1_<ts>.jpg`) |

---

## Supported Camera Sensor Modes

The table below lists valid resolution/framerate combinations for the IMX219 sensor.
Use only these values in `main.py` — mismatched values will cause pipeline negotiation failure.

| Resolution  | Max Framerate |
|-------------|---------------|
| 3280 x 2464 | 21 fps        |
| 3280 x 1848 | 28 fps        |
| 1920 x 1080 | 30 fps        |
| 1640 x 1232 | 30 fps        |
| 1280 x 720  | 60 fps        |

Configure in `main.py`:

```python
config = DualCameraConfig(
    cam0=CameraConfig(sensor_id=0, width=1920, height=1080, framerate=30),
    cam1=CameraConfig(sensor_id=1, width=1920, height=1080, framerate=30),
)
```

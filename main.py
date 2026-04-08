import os
import cv2
from jetson_csi_camera import DualCSICamera, DualCameraConfig, CameraConfig

# Optional: customise resolution / framerate per camera
config = DualCameraConfig(
    cam0=CameraConfig(sensor_id=0, width=1920, height=1080, framerate=10),
    cam1=CameraConfig(sensor_id=1, width=1920, height=1080, framerate=10),
)

with DualCSICamera(config) as cams:
    print(f"Streaming — press 'q' to quit, 's' to save a snapshot pair.")
    while True:
        left, right = cams.read()

        if left is None or right is None:
            continue

        # Downscale for display only
        disp_left  = cv2.resize(left,  (640, 360))
        disp_right = cv2.resize(right, (640, 360))

        # Overlay FPS
        for img, cam in [(disp_left, cams.cam0), (disp_right, cams.cam1)]:
            cv2.putText(img, f"cam{cam.sensor_id}  {cam.fps:.1f} fps",
                        (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        combined = cv2.hconcat([disp_left, disp_right])
        cv2.imshow("JetsonEyes — Dual CSI", combined)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('s'):
            tag = f"{int(__import__('time').time())}"
            cv2.imwrite(f"snap_cam0_{tag}.jpg", left)
            cv2.imwrite(f"snap_cam1_{tag}.jpg", right)
            print(f"Saved snapshot pair: snap_cam*_{tag}.jpg")

cv2.destroyAllWindows()

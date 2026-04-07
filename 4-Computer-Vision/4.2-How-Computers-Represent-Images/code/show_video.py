import cv2
from pathlib import Path

# Build a path relative to this script file, so the video can be loaded
# even when the script is run from a different working directory.
video_path = Path(__file__).resolve().parent / "sources" / "cv_world.mp4"

cap = cv2.VideoCapture(str(video_path))
if not cap.isOpened():
    raise FileNotFoundError(f"Unable to open video: {video_path}")

while True:
    ret, img = cap.read()
    if not ret:
        break
    img = cv2.resize(img,None,fx=0.5,fy=0.5)
    cv2.imshow("video", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
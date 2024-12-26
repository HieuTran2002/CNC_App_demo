# webcam_manager.py
import cv2
import numpy as np
from typing import Optional

class WebcamManager:
    def __init__(self):
        self.camera: Optional[cv2.VideoCapture] = None
        self.is_running: bool = False

    def initialize_camera(self, camera_id: int = 0) -> bool:
        """Initialize the webcam"""
        try:
            self.camera = cv2.VideoCapture(camera_id)
            if not self.camera.isOpened():
                return False
            self.is_running = True
            return True
        except Exception:
            return False

    def release_camera(self) -> None:
        """Release the webcam resources"""
        if self.camera:
            self.is_running = False
            self.camera.release()
            self.camera = None

    def get_frame(self) -> Optional[np.ndarray]:
        if not self.camera or not self.is_running:
            if not self.initialize_camera():
                return None
        
        success, frame = self.camera.read()
        if not success:
            return None
        
        return frame

    def create_test_image(self, text: str = 'Hello from OpenCV!') -> np.ndarray:
        height, width = 1080, 1920
        img = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.putText(img, text, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 3, (40, 42, 52), 5, cv2.LINE_AA)
        return img


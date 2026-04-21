"""
Pengurus kamera untuk menangkap aliran video USB webcam.
Menyokong pelbagai indeks kamera dan resolusi.
"""

import cv2
import numpy as np


class CameraManager:
    """
    Pengurus kamera yang mengendalikan sambungan, pembacaan bingkai,
    dan pelepasan sumber kamera.
    """

    def __init__(self, camera_index=0, width=640, height=480, fps=30):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None
        self._is_open = False

    def open(self):
        """
        Buka sambungan kamera. Kembalikan True jika berjaya.
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        # Kurangkan buffer untuk kurangkan latensi
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self._is_open = True
        return True

    def read_frame(self):
        """
        Baca satu bingkai dari kamera.
        Kembalikan (success, frame_bgr).
        """
        if not self._is_open or self.cap is None:
            return False, None
        ret, frame = self.cap.read()
        if not ret:
            return False, None
        # Cermin bingkai (mirror) supaya lebih natural untuk pengguna
        frame = cv2.flip(frame, 1)
        return True, frame

    def get_actual_resolution(self):
        """
        Dapatkan resolusi sebenar yang dikonfigurasikan oleh kamera.
        """
        if self.cap is None:
            return (self.width, self.height)
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (w, h)

    def get_actual_fps(self):
        if self.cap is None:
            return self.fps
        return self.cap.get(cv2.CAP_PROP_FPS)

    def release(self):
        """Lepaskan sumber kamera."""
        if self.cap is not None:
            self.cap.release()
        self._is_open = False
        self.cap = None

    def is_open(self):
        return self._is_open

    @staticmethod
    def bgr_to_rgb(frame_bgr):
        """Tukar format BGR (OpenCV) kepada RGB (Streamlit/Pillow)."""
        return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    @staticmethod
    def list_available_cameras(max_check=5):
        """
        Senaraikan indeks kamera yang tersedia pada sistem.
        """
        available = []
        for i in range(max_check):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available

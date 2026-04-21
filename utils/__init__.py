"""
Modul pengenalan isyarat tangan menggunakan MediaPipe.
Mengesan 21 titik landmark dan mengklasifikasikan isyarat.
"""

import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class GestureRecognizer:
    """
    Kelas utama untuk mengesan dan mengenali isyarat tangan.
    """

    GESTURE_LABELS = {
        "thumbs_up":    "Ibu Jari Atas",
        "thumbs_down":  "Ibu Jari Bawah",
        "open_hand":    "Tapak Tangan Terbuka",
        "fist":         "Penumbuk",
        "peace":        "Dua Jari (Peace)",
        "pointing":     "Tunjuk",
        "ok":           "OK",
        "none":         "Tiada Isyarat",
    }

    GESTURE_ACTIONS = {
        "thumbs_up":    "Play Media",
        "thumbs_down":  "Stop Media",
        "open_hand":    "Pause / Berhenti",
        "fist":         "Kunci Skrin",
        "peace":        "Tukar Tetingkap",
        "pointing":     "Gerakkan Kursor",
        "ok":           "Sahkan / OK",
        "none":         "-",
    }

    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.5):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    def process(self, frame_rgb):
        """
        Proses bingkai dan kembalikan keputusan MediaPipe.
        frame_rgb: numpy array dalam format RGB
        """
        return self.hands.process(frame_rgb)

    def get_landmarks(self, results, frame_shape):
        """
        Ekstrak koordinat 21 landmark tangan.
        Kembalikan senarai dict {x, y, z} dinormalisasi.
        """
        if not results.multi_hand_landmarks:
            return None
        h, w = frame_shape[:2]
        lm_list = []
        for lm in results.multi_hand_landmarks[0].landmark:
            lm_list.append({
                "x": lm.x,
                "y": lm.y,
                "z": lm.z,
                "px": int(lm.x * w),
                "py": int(lm.y * h),
            })
        return lm_list

    def recognize_gesture(self, landmarks):
        """
        Klasifikasikan isyarat berdasarkan kedudukan landmark.
        Menggunakan logik geometri jari.
        """
        if landmarks is None:
            return "none"

        # Indeks landmark MediaPipe:
        # 4=ibu jari hujung, 8=telunjuk hujung, 12=tengah hujung
        # 16=manis hujung, 20=kelingking hujung
        # 3=ibu jari sendi, 6=telunjuk knuckle, 10=tengah knuckle
        # 14=manis knuckle, 18=kelingking knuckle

        fingers_up = self._count_fingers_up(landmarks)
        thumb_up = self._is_thumb_up(landmarks)
        thumb_down = self._is_thumb_down(landmarks)

        total_up = sum(fingers_up[1:])  # telunjuk hingga kelingking

        # Logik pengenalan
        if thumb_up and total_up == 0:
            return "thumbs_up"

        if thumb_down and total_up == 0:
            return "thumbs_down"

        if all(f == 1 for f in fingers_up[1:]) and total_up == 4:
            return "open_hand"

        if total_up == 0 and not thumb_up:
            return "fist"

        if fingers_up[1] == 1 and fingers_up[2] == 1 and total_up == 2:
            return "peace"

        if fingers_up[1] == 1 and total_up == 1:
            return "pointing"

        if self._is_ok_gesture(landmarks):
            return "ok"

        return "none"

    def _count_fingers_up(self, lm):
        """
        Semak sama ada setiap jari (telunjuk-kelingking) tegak.
        Kembalikan senarai [ibu_jari, telunjuk, tengah, manis, kelingking].
        """
        tips = [4, 8, 12, 16, 20]
        pips = [3, 6, 10, 14, 18]
        fingers = []

        # Ibu jari: bandingkan x (lateral)
        fingers.append(1 if lm[tips[0]]["x"] < lm[pips[0]]["x"] else 0)

        # Jari lain: bandingkan y (atas/bawah)
        for i in range(1, 5):
            fingers.append(1 if lm[tips[i]]["y"] < lm[pips[i]]["y"] else 0)

        return fingers

    def _is_thumb_up(self, lm):
        """Ibu jari hujung lebih tinggi dari pangkal."""
        return lm[4]["y"] < lm[2]["y"] - 0.05

    def _is_thumb_down(self, lm):
        """Ibu jari hujung lebih rendah dari pangkal."""
        return lm[4]["y"] > lm[2]["y"] + 0.05

    def _is_ok_gesture(self, lm):
        """
        Isyarat OK: hujung ibu jari dan telunjuk berdekatan,
        jari lain tegak.
        """
        thumb_tip = np.array([lm[4]["x"], lm[4]["y"]])
        index_tip = np.array([lm[8]["x"], lm[8]["y"]])
        dist = np.linalg.norm(thumb_tip - index_tip)
        fingers_up = self._count_fingers_up(lm)
        other_fingers_up = sum(fingers_up[2:])
        return dist < 0.06 and other_fingers_up >= 2

    def draw_landmarks(self, frame_bgr, results):
        """
        Lukis landmark dan sambungan tangan pada bingkai BGR.
        """
        if results.multi_hand_landmarks:
            for hand_lm in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame_bgr,
                    hand_lm,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style(),
                )
        return frame_bgr

    def get_hand_bbox(self, landmarks, frame_shape):
        """
        Dapatkan kotak sempadan (bounding box) tangan.
        Kembalikan (x_min, y_min, x_max, y_max) dalam piksel.
        """
        if landmarks is None:
            return None
        h, w = frame_shape[:2]
        xs = [lm["px"] for lm in landmarks]
        ys = [lm["py"] for lm in landmarks]
        pad = 20
        return (
            max(0, min(xs) - pad),
            max(0, min(ys) - pad),
            min(w, max(xs) + pad),
            min(h, max(ys) + pad),
        )

    def close(self):
        self.hands.close()

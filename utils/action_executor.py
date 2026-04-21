"""
Pelaksana tindakan sistem berdasarkan isyarat tangan yang dikenali.
Setiap isyarat dipetakan kepada tindakan kawalan komputer.
"""

import subprocess
import platform
import time


class ActionExecutor:
    """
    Melaksanakan tindakan sistem sebenar berdasarkan isyarat.
    Menyokong Linux (untuk Jetson) dengan fallback untuk OS lain.
    """

    def __init__(self, cooldown_seconds=1.5):
        """
        cooldown_seconds: masa minimum antara tindakan berulang
        untuk mengelakkan pencetus yang tidak sengaja.
        """
        self.cooldown = cooldown_seconds
        self._last_action_time = {}
        self._last_gesture = None
        self.os_type = platform.system()
        self.action_log = []

    def execute(self, gesture):
        """
        Jalankan tindakan berpadanan dengan isyarat.
        Kembalikan nama tindakan yang dilaksanakan atau None.
        """
        if gesture == "none" or gesture == self._last_gesture:
            self._last_gesture = gesture
            return None

        now = time.time()
        last = self._last_action_time.get(gesture, 0)
        if now - last < self.cooldown:
            return None

        action_map = {
            "thumbs_up":    self._action_play,
            "thumbs_down":  self._action_stop,
            "open_hand":    self._action_pause,
            "fist":         self._action_lock,
            "peace":        self._action_switch_window,
            "pointing":     self._action_move_cursor,
            "ok":           self._action_confirm,
        }

        fn = action_map.get(gesture)
        if fn:
            result = fn()
            self._last_action_time[gesture] = now
            self._last_gesture = gesture
            if result:
                self.action_log.append({
                    "time": time.strftime("%H:%M:%S"),
                    "gesture": gesture,
                    "action": result,
                })
                # Simpan hanya 20 rekod terkini
                self.action_log = self.action_log[-20:]
            return result

        self._last_gesture = gesture
        return None

    def reset_last_gesture(self):
        """Reset supaya isyarat sama boleh dicetuskan semula."""
        self._last_gesture = None

    # ----------------------------------------------------------
    # Tindakan individual
    # ----------------------------------------------------------

    def _action_play(self):
        """Hantar kekunci Space untuk play/pause media player."""
        self._send_key("space")
        return "Play Media (Space)"

    def _action_stop(self):
        """Hentikan media — hantar kekunci S."""
        self._send_key("s")
        return "Stop Media (S)"

    def _action_pause(self):
        """Pause — hantar kekunci Space."""
        self._send_key("space")
        return "Pause/Resume (Space)"

    def _action_lock(self):
        """Kunci skrin."""
        if self.os_type == "Linux":
            self._run_cmd(["loginctl", "lock-session"])
        return "Kunci Skrin"

    def _action_switch_window(self):
        """Alt+Tab untuk tukar tetingkap."""
        self._send_key_combo(["alt", "Tab"])
        return "Tukar Tetingkap (Alt+Tab)"

    def _action_move_cursor(self):
        """Placeholder — kawalan kursor memerlukan koordinat landmark."""
        return "Mod Kawalan Kursor Aktif"

    def _action_confirm(self):
        """Tekan Enter sebagai pengesahan."""
        self._send_key("Return")
        return "Sahkan (Enter)"

    # ----------------------------------------------------------
    # Pembantu menghantar kekunci
    # ----------------------------------------------------------

    def _send_key(self, key):
        """Hantar satu kekunci menggunakan xdotool (Linux)."""
        if self.os_type == "Linux":
            self._run_cmd(["xdotool", "key", key])

    def _send_key_combo(self, keys):
        """Hantar kombinasi kekunci seperti Alt+Tab."""
        if self.os_type == "Linux":
            self._run_cmd(["xdotool", "key", "+".join(keys)])

    def _run_cmd(self, cmd):
        """Jalankan arahan sistem secara senyap."""
        try:
            subprocess.run(cmd, capture_output=True, timeout=2)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # xdotool mungkin tidak dipasang — abaikan

    def get_log(self):
        """Kembalikan log tindakan terkini."""
        return list(reversed(self.action_log))

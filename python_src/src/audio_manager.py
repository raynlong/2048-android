"""Audio manager for 2048 — generates synth sound effects via WAV files.

Works on both desktop (kivy.core.audio) and Android (GStreamer backend).
Generates short sine-wave WAVs in temp files on first use.
"""

import struct
import math
import os
import tempfile

from kivy.core.audio import SoundLoader

PREF_FILE = "2048_audio_pref.txt"


class AudioManager:
    """Manages sound effects for the 2048 game.

    Generates short synthesized WAV files for move (slide) and merge sounds.
    Uses Kivy's SoundLoader which works across platforms.
    """

    def __init__(self):
        self.enabled = True
        self._sounds = {}
        self._loaded = False
        self._load_preference()

    # ── Public API ──────────────────────────────────────────────────

    def play_move(self):
        """Play the sliding sound effect (triggered on every valid swipe)."""
        if not self.enabled:
            return
        self._ensure_loaded()
        s = self._sounds.get("move")
        if s:
            s.stop()
            s.play()

    def play_merge(self, value):
        """Play the merge sound effect, frequency increases with tile value."""
        if not self.enabled:
            return
        self._ensure_loaded()
        key = f"merge_{value}"
        s = self._sounds.get(key)
        if s:
            s.stop()
            s.play()
        else:
            # Fallback: highest available pitched merge sound
            for v in [2048, 1024, 512, 256, 128, 64]:
                s = self._sounds.get(f"merge_{v}")
                if s:
                    s.stop()
                    s.play()
                    return

    def toggle(self):
        """Toggle sound on/off. Returns new state."""
        self.enabled = not self.enabled
        self._save_preference()
        return self.enabled

    # ── Internal ────────────────────────────────────────────────────

    def _ensure_loaded(self):
        """Lazy-init: generate and load sound files on first use."""
        if self._loaded:
            return
        self._loaded = True

        base_dir = tempfile.gettempdir()
        move_data = self._make_wav([(180, 0.02), (280, 0.04), (120, 0.04)])
        self._sounds["move"] = self._load_wav(base_dir, "move", move_data)

        # Merge sounds: frequency scales with log2(value)
        for v in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]:
            freq = int(220 + math.log2(v) * 55)
            data = self._make_wav([(freq, 0.06), (freq * 1.25, 0.08)])
            self._sounds[f"merge_{v}"] = self._load_wav(base_dir, f"merge_{v}", data)

    def _make_wav(self, tones, sample_rate=22050):
        """Generate WAV bytes from a list of (frequency, duration) tones.

        Each tone uses a sine wave with quick fade envelope.
        """
        total_duration = sum(d for _, d in tones)
        n_samples = int(sample_rate * total_duration)
        samples = []
        t = 0.0

        for freq, duration in tones:
            n_tone = int(sample_rate * duration)
            for i in range(n_tone):
                envelope = max(0, 1.0 - (i / n_tone))
                value = int(32767 * 0.35 * envelope * math.sin(2 * math.pi * freq * (t + i / sample_rate)))
                samples.append(max(-32768, min(32767, value)))
            t += duration

        # WAV header (PCM 16-bit mono)
        data_size = n_samples * 2
        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF', 36 + data_size,
            b'WAVE', b'fmt ', 16,
            1, 1, sample_rate, sample_rate * 2, 2, 16,
            b'data', data_size,
        )
        return header + struct.pack('<' + 'h' * n_samples, *samples)

    def _load_wav(self, base_dir, name, data):
        """Write WAV data to temp file and load via SoundLoader."""
        path = os.path.join(base_dir, f"2048_{name}.wav")
        try:
            with open(path, "wb") as f:
                f.write(data)
            return SoundLoader.load(path)
        except OSError:
            return None

    def _load_preference(self):
        """Read sound enabled state from persistent storage."""
        try:
            path = os.path.join(tempfile.gettempdir(), PREF_FILE)
            if os.path.exists(path):
                with open(path, "r") as f:
                    self.enabled = f.read().strip() != "0"
        except OSError:
            self.enabled = True

    def _save_preference(self):
        """Persist sound enabled state."""
        try:
            path = os.path.join(tempfile.gettempdir(), PREF_FILE)
            with open(path, "w") as f:
                f.write("1" if self.enabled else "0")
        except OSError:
            pass

from __future__ import annotations

import math
from array import array
from dataclasses import dataclass
from dataclasses import field

import pygame


@dataclass
class Audio:
    enabled: bool
    events: dict[str, str]
    _cache: dict[str, pygame.mixer.Sound] = field(default_factory=dict)
    _music_channel: pygame.mixer.Channel | None = None
    _music_sound: pygame.mixer.Sound | None = None

    def init(self) -> None:
        if not self.enabled:
            return
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
        except pygame.error:
            self.enabled = False

    def play(self, event: str) -> None:
        if not self.enabled:
            return
        path = self.events.get(event, "")
        if not path:
            return
        sound = self._load_sound(path)
        if sound is None:
            return
        sound.play()

    def start_music(self) -> None:
        if not self.enabled:
            return
        path = self.events.get("theme_music", "")
        if not path:
            return
        sound = self._load_sound(path)
        if sound is None:
            return
        if self._music_sound is sound and self._music_channel is not None and self._music_channel.get_busy():
            return
        self.stop_music()
        self._music_sound = sound
        self._music_channel = sound.play(loops=-1)

    def stop_music(self) -> None:
        if self._music_channel is not None:
            try:
                self._music_channel.stop()
            except pygame.error:
                pass
        self._music_channel = None
        self._music_sound = None

    def _load_sound(self, spec: str) -> pygame.mixer.Sound | None:
        if spec in self._cache:
            return self._cache[spec]

        if spec.startswith("synth:"):
            sound = self._synth_sound(spec)
            if sound is None:
                return None
            self._cache[spec] = sound
            return sound

        try:
            sound = pygame.mixer.Sound(spec)
        except pygame.error:
            return None
        self._cache[spec] = sound
        return sound

    def _synth_sound(self, spec: str) -> pygame.mixer.Sound | None:
        if spec == "synth:theme_v1":
            samples = _synth_theme_v1(sample_rate=22050)
        elif spec == "synth:pellet":
            samples = _synth_blip(sample_rate=22050, freq_hz=1046.5, duration_s=0.045, volume=0.10)
        elif spec == "synth:power":
            samples = _synth_blip(sample_rate=22050, freq_hz=659.25, duration_s=0.10, volume=0.14)
        elif spec == "synth:ghost":
            samples = _synth_blip(sample_rate=22050, freq_hz=523.25, duration_s=0.08, volume=0.16)
        elif spec == "synth:fruit":
            samples = _synth_chord(sample_rate=22050, freqs_hz=[880.0, 1174.66], duration_s=0.12, volume=0.14)
        elif spec == "synth:death":
            samples = _synth_sweep(sample_rate=22050, start_hz=440.0, end_hz=110.0, duration_s=0.40, volume=0.18)
        elif spec == "synth:win":
            samples = _synth_chord(sample_rate=22050, freqs_hz=[523.25, 659.25, 783.99], duration_s=0.35, volume=0.16)
        elif spec == "synth:lose":
            samples = _synth_chord(sample_rate=22050, freqs_hz=[392.0, 311.13, 233.08], duration_s=0.35, volume=0.16)
        else:
            return None

        try:
            return pygame.mixer.Sound(buffer=samples.tobytes())
        except pygame.error:
            return None


def _synth_theme_v1(*, sample_rate: int) -> array:
    def note(name: str) -> float:
        table = {
            "C4": 261.63,
            "D4": 293.66,
            "E4": 329.63,
            "F4": 349.23,
            "G4": 392.00,
            "A4": 440.00,
            "B4": 493.88,
            "C5": 523.25,
            "D5": 587.33,
            "E5": 659.25,
            "G5": 783.99,
        }
        return table[name]

    seq: list[tuple[float, float, float]] = [
        (note("E4"), 0.18, 0.18),
        (note("G4"), 0.18, 0.18),
        (note("C5"), 0.22, 0.22),
        (note("G4"), 0.12, 0.16),
        (note("A4"), 0.18, 0.18),
        (note("E5"), 0.22, 0.22),
        (note("D5"), 0.18, 0.18),
        (note("C5"), 0.22, 0.22),
        (note("G4"), 0.18, 0.18),
        (note("E4"), 0.18, 0.18),
        (0.0, 0.10, 0.0),
        (note("F4"), 0.18, 0.18),
        (note("A4"), 0.18, 0.18),
        (note("D5"), 0.22, 0.22),
        (note("A4"), 0.12, 0.16),
        (note("B4"), 0.18, 0.18),
        (note("G5"), 0.22, 0.22),
        (note("E5"), 0.18, 0.18),
        (note("D5"), 0.18, 0.18),
        (note("C5"), 0.22, 0.22),
        (0.0, 0.20, 0.0),
    ]

    out = array("h")
    for freq_hz, duration_s, volume in seq:
        out.extend(_render_note(sample_rate=sample_rate, freq_hz=freq_hz, duration_s=duration_s, volume=volume))
    return out


def _synth_blip(*, sample_rate: int, freq_hz: float, duration_s: float, volume: float) -> array:
    return _render_note(sample_rate=sample_rate, freq_hz=freq_hz, duration_s=duration_s, volume=volume)


def _synth_sweep(*, sample_rate: int, start_hz: float, end_hz: float, duration_s: float, volume: float) -> array:
    total = max(1, int(sample_rate * duration_s))
    out = array("h", [0]) * total
    if volume <= 0.0:
        return out

    fade = min(int(sample_rate * 0.01), total // 2)
    base_amp = int(32767 * min(max(volume, 0.0), 1.0))

    phase = 0.0
    for i in range(total):
        t = i / max(1, total - 1)
        freq_hz = start_hz + (end_hz - start_hz) * t
        phase_step = (2.0 * math.pi * max(freq_hz, 1.0)) / sample_rate
        if phase >= 2.0 * math.pi:
            phase -= 2.0 * math.pi

        raw = 1.0 if math.sin(phase) >= 0.0 else -1.0

        env = 1.0
        if i < fade:
            env = i / fade
        elif i >= total - fade:
            env = (total - 1 - i) / fade

        out[i] = int(base_amp * raw * env)
        phase += phase_step

    return out


def _synth_chord(*, sample_rate: int, freqs_hz: list[float], duration_s: float, volume: float) -> array:
    total = max(1, int(sample_rate * duration_s))
    out = array("h", [0]) * total
    if not freqs_hz or volume <= 0.0:
        return out

    fade = min(int(sample_rate * 0.01), total // 2)
    base_amp = int(32767 * min(max(volume, 0.0), 1.0))

    phases = [0.0 for _ in freqs_hz]
    steps = [(2.0 * math.pi * max(f, 1.0)) / sample_rate for f in freqs_hz]

    for i in range(total):
        mixed = 0.0
        for idx in range(len(freqs_hz)):
            if phases[idx] >= 2.0 * math.pi:
                phases[idx] -= 2.0 * math.pi
            mixed += 1.0 if math.sin(phases[idx]) >= 0.0 else -1.0
            phases[idx] += steps[idx]
        mixed /= len(freqs_hz)

        env = 1.0
        if i < fade:
            env = i / fade
        elif i >= total - fade:
            env = (total - 1 - i) / fade

        out[i] = int(base_amp * mixed * env)

    return out


def _render_note(*, sample_rate: int, freq_hz: float, duration_s: float, volume: float) -> array:
    total = max(1, int(sample_rate * duration_s))
    fade = min(int(sample_rate * 0.01), total // 2)
    out = array("h", [0]) * total

    if freq_hz <= 0.0 or volume <= 0.0:
        return out

    phase = 0.0
    phase_step = (2.0 * math.pi * freq_hz) / sample_rate
    base_amp = int(32767 * min(max(volume, 0.0), 1.0))

    for i in range(total):
        if phase >= 2.0 * math.pi:
            phase -= 2.0 * math.pi
        raw = 1.0 if math.sin(phase) >= 0.0 else -1.0

        env = 1.0
        if i < fade:
            env = i / fade
        elif i >= total - fade:
            env = (total - 1 - i) / fade

        out[i] = int(base_amp * raw * env)
        phase += phase_step

    return out

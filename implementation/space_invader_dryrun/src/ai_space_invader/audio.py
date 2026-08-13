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
        spec = self.events.get(event, '')
        if not spec:
            return
        sound = self._load_sound(spec)
        if sound is not None:
            sound.play()

    def start_music(self) -> None:
        if not self.enabled:
            return
        spec = self.events.get('theme_music', '')
        if not spec:
            return
        sound = self._load_sound(spec)
        if sound is None:
            return
        if self._music_channel is not None and self._music_channel.get_busy():
            return
        self.stop_music()
        self._music_channel = sound.play(loops=-1)

    def stop_music(self) -> None:
        if self._music_channel is not None:
            try:
                self._music_channel.stop()
            except pygame.error:
                pass
        self._music_channel = None

    def _load_sound(self, spec: str) -> pygame.mixer.Sound | None:
        if spec in self._cache:
            return self._cache[spec]
        if not spec.startswith('synth:'):
            return None
        samples = _synth(spec)
        if samples is None:
            return None
        try:
            sound = pygame.mixer.Sound(buffer=samples.tobytes())
        except pygame.error:
            return None
        self._cache[spec] = sound
        return sound


def _synth(spec: str) -> array | None:
    sample_rate = 22050
    if spec == 'synth:shoot':
        return _note(sample_rate, 880.0, 0.06, 0.13)
    if spec == 'synth:alien_hit':
        return _chord(sample_rate, [440.0, 660.0], 0.08, 0.12)
    if spec == 'synth:enemy_shoot':
        return _note(sample_rate, 220.0, 0.06, 0.11)
    if spec == 'synth:bunker_hit':
        return _noise(sample_rate, 0.05, 0.08)
    if spec == 'synth:ufo_hit':
        return _sweep(sample_rate, 320.0, 920.0, 0.18, 0.16)
    if spec == 'synth:player_hit':
        return _sweep(sample_rate, 520.0, 140.0, 0.24, 0.16)
    if spec == 'synth:wave_clear':
        return _chord(sample_rate, [523.25, 659.25, 783.99], 0.22, 0.14)
    if spec == 'synth:game_over':
        return _chord(sample_rate, [392.0, 311.13, 233.08], 0.30, 0.16)
    if spec == 'synth:space_pulse':
        return _theme(sample_rate)
    return None


def _theme(sample_rate: int) -> array:
    sequence = [
        (220.0, 0.08, 0.11),
        (246.94, 0.08, 0.11),
        (293.66, 0.08, 0.11),
        (329.63, 0.08, 0.11),
        (0.0, 0.04, 0.0),
        (329.63, 0.08, 0.11),
        (293.66, 0.08, 0.11),
        (246.94, 0.08, 0.11),
        (220.0, 0.08, 0.11),
        (0.0, 0.04, 0.0),
    ]
    out = array('h')
    for freq, duration, volume in sequence:
        out.extend(_note(sample_rate, freq, duration, volume))
    return out


def _note(sample_rate: int, freq_hz: float, duration_s: float, volume: float) -> array:
    total = max(1, int(sample_rate * duration_s))
    out = array('h', [0]) * total
    if freq_hz <= 0.0 or volume <= 0.0:
        return out
    fade = min(int(sample_rate * 0.01), total // 2)
    phase = 0.0
    step = (2.0 * math.pi * freq_hz) / sample_rate
    amplitude = int(32767 * min(max(volume, 0.0), 1.0))
    for idx in range(total):
        if phase >= 2.0 * math.pi:
            phase -= 2.0 * math.pi
        env = 1.0
        if idx < fade:
            env = idx / fade
        elif idx >= total - fade:
            env = (total - 1 - idx) / fade
        raw = 1.0 if math.sin(phase) >= 0.0 else -1.0
        out[idx] = int(amplitude * raw * env)
        phase += step
    return out


def _chord(sample_rate: int, freqs_hz: list[float], duration_s: float, volume: float) -> array:
    total = max(1, int(sample_rate * duration_s))
    out = array('h', [0]) * total
    if not freqs_hz:
        return out
    fade = min(int(sample_rate * 0.01), total // 2)
    amplitude = int(32767 * min(max(volume, 0.0), 1.0))
    phases = [0.0 for _ in freqs_hz]
    steps = [(2.0 * math.pi * freq) / sample_rate for freq in freqs_hz]
    for idx in range(total):
        mixed = 0.0
        for pos in range(len(freqs_hz)):
            if phases[pos] >= 2.0 * math.pi:
                phases[pos] -= 2.0 * math.pi
            mixed += 1.0 if math.sin(phases[pos]) >= 0.0 else -1.0
            phases[pos] += steps[pos]
        mixed /= len(freqs_hz)
        env = 1.0
        if idx < fade:
            env = idx / fade
        elif idx >= total - fade:
            env = (total - 1 - idx) / fade
        out[idx] = int(amplitude * mixed * env)
    return out


def _noise(sample_rate: int, duration_s: float, volume: float) -> array:
    total = max(1, int(sample_rate * duration_s))
    out = array('h', [0]) * total
    amplitude = int(32767 * min(max(volume, 0.0), 1.0))
    seed = 0x1234
    for idx in range(total):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        value = ((seed % 2000) / 1000.0) - 1.0
        out[idx] = int(amplitude * value)
    return out


def _sweep(sample_rate: int, start_hz: float, end_hz: float, duration_s: float, volume: float) -> array:
    total = max(1, int(sample_rate * duration_s))
    out = array('h', [0]) * total
    fade = min(int(sample_rate * 0.01), total // 2)
    amplitude = int(32767 * min(max(volume, 0.0), 1.0))
    phase = 0.0
    for idx in range(total):
        t = idx / max(1, total - 1)
        freq = start_hz + (end_hz - start_hz) * t
        phase += (2.0 * math.pi * max(freq, 1.0)) / sample_rate
        if phase >= 2.0 * math.pi:
            phase -= 2.0 * math.pi
        env = 1.0
        if idx < fade:
            env = idx / fade
        elif idx >= total - fade:
            env = (total - 1 - idx) / fade
        raw = 1.0 if math.sin(phase) >= 0.0 else -1.0
        out[idx] = int(amplitude * raw * env)
    return out

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass
class GameState:
    score: int
    lives: int
    mode: str
    frightened_until_s: float
    difficulty: str
    countdown_end_s: float
    ghosts_eaten_in_fright: int
    paused_from_mode: str
    level: int
    level_start_pellet_count: int
    fruit_active: bool
    fruit_row: int
    fruit_col: int
    fruit_name: str
    fruit_score: int
    fruit_expires_s: float
    fruit_spawned_at_pellets_eaten: set[int] = field(default_factory=set)

    def frightened_active(self, now_s: float) -> bool:
        return now_s < self.frightened_until_s

    def countdown_active(self, now_s: float) -> bool:
        return self.mode == "countdown" and now_s < self.countdown_end_s

from __future__ import annotations

from dataclasses import dataclass

from ai_space_invader.bunker import Bunker
from ai_space_invader.formation import AlienFormation
from ai_space_invader.player import Player
from ai_space_invader.projectile import Projectile
from ai_space_invader.ufo import UFO


@dataclass
class GameState:
    score: int
    lives: int
    level: int
    mode: str
    difficulty: str
    countdown_end_s: float
    shots_fired: int
    extra_life_awarded: bool
    attract_mode: bool = False
    idle_started_s: float = 0.0
    paused_from_mode: str = 'playing'
    high_score_checked: bool = False
    high_score_saved: bool = False

    def extra_life_available(self, threshold: int) -> bool:
        return (not self.extra_life_awarded) and self.score >= threshold


@dataclass
class World:
    player: Player
    formation: AlienFormation
    bunkers: list[Bunker]
    ufo: UFO
    player_shot: Projectile | None
    enemy_shots: list[Projectile]

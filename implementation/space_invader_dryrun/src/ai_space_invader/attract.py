from __future__ import annotations

from dataclasses import dataclass

from ai_space_invader.formation import AlienFormation
from ai_space_invader.player import Player
from ai_space_invader.ufo import UFO


@dataclass(frozen=True)
class AttractAction:
    move_direction: int
    should_fire: bool


def idle_timeout_reached(*, enabled: bool, idle_started_s: float, now_s: float, timeout_s: float) -> bool:
    if not enabled or timeout_s <= 0.0:
        return False
    return now_s - idle_started_s >= timeout_s


def choose_action(
    *,
    player: Player,
    formation: AlienFormation,
    ufo: UFO,
    player_shot_active: bool,
    fire_tolerance_px: float = 10.0,
) -> AttractAction:
    player_center = player.x + player.width / 2.0
    target_center = _target_center_x(player_center=player_center, formation=formation, ufo=ufo)
    delta = target_center - player_center

    if abs(delta) <= fire_tolerance_px:
        return AttractAction(move_direction=0, should_fire=not player_shot_active)
    return AttractAction(move_direction=1 if delta > 0.0 else -1, should_fire=False)


def _target_center_x(*, player_center: float, formation: AlienFormation, ufo: UFO) -> float:
    if ufo.active:
        return ufo.x + ufo.width / 2.0

    alive_aliens = formation.alive_aliens()
    if not alive_aliens:
        return player_center

    target = min(
        alive_aliens,
        key=lambda alien: (
            abs((alien.x + alien.width / 2.0) - player_center),
            -alien.y,
            alien.col,
            alien.row,
        ),
    )
    return target.x + target.width / 2.0

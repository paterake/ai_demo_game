from __future__ import annotations

from ai_space_invader.alien import Alien
from ai_space_invader.attract import choose_action
from ai_space_invader.attract import idle_timeout_reached
from ai_space_invader.formation import AlienFormation
from ai_space_invader.player import Player
from ai_space_invader.ufo import UFO


def test_idle_timeout_reached_only_after_threshold_when_enabled() -> None:
    assert not idle_timeout_reached(enabled=False, idle_started_s=10.0, now_s=25.0, timeout_s=8.0)
    assert not idle_timeout_reached(enabled=True, idle_started_s=10.0, now_s=17.5, timeout_s=8.0)
    assert idle_timeout_reached(enabled=True, idle_started_s=10.0, now_s=18.0, timeout_s=8.0)


def test_choose_action_targets_active_ufo_and_fires_when_aligned() -> None:
    player = Player(x=88.0, y=620.0, width=24, height=16, speed_px_per_s=320.0, shot_cooldown_s=0.35, baseline_x=88.0)
    formation = AlienFormation(
        aliens=[],
        total_aliens=0,
        direction=1,
        last_step_s=0.0,
        base_interval_s=1.0,
        min_interval_s=0.2,
        step_px=12,
        step_down_px=10,
    )
    ufo = UFO(
        width=24,
        height=12,
        speed_px_per_s=120.0,
        spawn_interval_s=20.0,
        respawn_delay_s=8.0,
        y_px=64,
        score_cycle=[100],
        active=True,
        x=88.0,
    )

    action = choose_action(player=player, formation=formation, ufo=ufo, player_shot_active=False, fire_tolerance_px=10.0)

    assert action.move_direction == 0
    assert action.should_fire


def test_choose_action_moves_towards_nearest_alien_column() -> None:
    player = Player(x=90.0, y=620.0, width=24, height=16, speed_px_per_s=320.0, shot_cooldown_s=0.35, baseline_x=90.0)
    formation = AlienFormation(
        aliens=[
            Alien(row=0, col=0, kind='squid', score=30, x=20.0, y=80.0, width=24, height=16),
            Alien(row=2, col=3, kind='crab', score=20, x=140.0, y=132.0, width=24, height=16),
        ],
        total_aliens=2,
        direction=1,
        last_step_s=0.0,
        base_interval_s=1.0,
        min_interval_s=0.2,
        step_px=12,
        step_down_px=10,
    )
    ufo = UFO(
        width=24,
        height=12,
        speed_px_per_s=120.0,
        spawn_interval_s=20.0,
        respawn_delay_s=8.0,
        y_px=64,
        score_cycle=[100],
    )

    action = choose_action(player=player, formation=formation, ufo=ufo, player_shot_active=False, fire_tolerance_px=10.0)

    assert action.move_direction == 1
    assert not action.should_fire

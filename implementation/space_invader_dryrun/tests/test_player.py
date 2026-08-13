from ai_space_invader.player import Player


def test_player_respects_horizontal_bounds() -> None:
    player = Player(x=10.0, y=100.0, width=20, height=10, speed_px_per_s=100.0, shot_cooldown_s=0.3, baseline_x=10.0)
    player.move(-1, 1.0, min_x=0.0, max_x=120.0)
    assert player.x == 0.0
    player.move(1, 5.0, min_x=0.0, max_x=120.0)
    assert player.x == 100.0


def test_player_fire_respects_cooldown() -> None:
    player = Player(x=30.0, y=90.0, width=20, height=10, speed_px_per_s=100.0, shot_cooldown_s=0.5, baseline_x=30.0)
    shot = player.fire(now_s=1.0, projectile_width=4, projectile_height=8, projectile_speed_px_per_s=-300.0)
    assert shot is not None
    assert player.can_fire(now_s=1.2, active_player_shot=False) is False
    assert player.can_fire(now_s=1.6, active_player_shot=False) is True

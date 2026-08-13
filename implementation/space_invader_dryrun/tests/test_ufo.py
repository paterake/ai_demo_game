from ai_space_invader.projectile import Projectile
from ai_space_invader.ufo import UFO


def test_ufo_score_cycle_follows_shot_count() -> None:
    ufo = UFO(width=40, height=18, speed_px_per_s=100.0, spawn_interval_s=10.0, respawn_delay_s=5.0, y_px=20, score_cycle=[50, 100, 300])
    assert ufo.current_score(1) == 50
    assert ufo.current_score(2) == 100
    assert ufo.current_score(3) == 300
    assert ufo.current_score(4) == 50


def test_ufo_try_hit_returns_score_and_deactivates() -> None:
    ufo = UFO(width=40, height=18, speed_px_per_s=100.0, spawn_interval_s=10.0, respawn_delay_s=5.0, y_px=20, score_cycle=[50, 100, 300], active=True, x=50.0)
    shot = Projectile(x=55.0, y=22.0, width=4, height=12, velocity_px_per_s=-200.0, owner='player')
    score = ufo.try_hit(shot, shots_fired=3, now_s=12.0)
    assert score == 300
    assert ufo.active is False
    assert ufo.next_spawn_s == 17.0

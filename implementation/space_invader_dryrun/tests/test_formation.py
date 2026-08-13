from random import Random

from ai_space_invader.formation import AlienFormation


def _sample_config() -> dict:
    return {
        'fleet': {
            'rows': 2,
            'cols': 2,
            'start_x_px': 10,
            'start_y_px': 10,
            'alien_width_px': 20,
            'alien_height_px': 10,
            'h_spacing_px': 5,
            'v_spacing_px': 5,
            'step_px': 8,
            'step_down_px': 6,
            'base_interval_s': 1.0,
            'min_interval_s': 0.2,
            'row_types': [
                {'kind': 'squid', 'score': 30},
                {'kind': 'octopus', 'score': 10},
            ],
        }
    }


def test_formation_descends_and_reverses_at_edge() -> None:
    formation = AlienFormation.from_config(_sample_config(), interval_multiplier=1.0, now_s=0.0)
    descended = formation.update(1.1, arena_left_px=0.0, arena_right_px=48.0)
    assert descended is True
    assert formation.direction == -1
    assert min(alien.y for alien in formation.alive_aliens()) == 16.0


def test_formation_accelerates_as_invaders_die() -> None:
    formation = AlienFormation.from_config(_sample_config(), interval_multiplier=1.0, now_s=0.0)
    start_interval = formation.current_interval_s()
    formation.aliens[0].alive = False
    formation.aliens[1].alive = False
    assert formation.current_interval_s() < start_interval


def test_choose_shooter_returns_bottom_alien_in_column() -> None:
    formation = AlienFormation.from_config(_sample_config(), interval_multiplier=1.0, now_s=0.0)
    for alien in formation.aliens:
        alien.alive = False
    formation.aliens[0].alive = True
    formation.aliens[2].alive = True
    shooter = formation.choose_shooter(Random(0))
    assert shooter is not None
    assert shooter.row == 1

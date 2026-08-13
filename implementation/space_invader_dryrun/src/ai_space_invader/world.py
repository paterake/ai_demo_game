from __future__ import annotations

from ai_space_invader.bunker import Bunker
from ai_space_invader.formation import AlienFormation
from ai_space_invader.player import Player
from ai_space_invader.state import World
from ai_space_invader.ufo import UFO


def build_world(
    *,
    game_config: dict,
    formation_config: dict,
    difficulty_profile: dict,
    level: int,
    now_s: float,
) -> World:
    window = game_config['window']
    ui_cfg = game_config['ui']
    player_cfg = game_config['player']
    progression = game_config['progression']
    ufo_cfg = game_config['ufo']

    window_width = int(window['width_px'])
    window_height = int(window['height_px'])
    arena_bottom_margin = int(ui_cfg['arena_bottom_margin_px'])
    player_width = int(player_cfg['width_px'])
    player_height = int(player_cfg['height_px'])
    baseline_x = (window_width - player_width) / 2.0
    baseline_y = float(window_height - arena_bottom_margin - player_height)
    player_speed = float(player_cfg['speed_px_per_s']) * float(difficulty_profile.get('player_speed_multiplier', 1.0))

    player = Player(
        x=baseline_x,
        y=baseline_y,
        width=player_width,
        height=player_height,
        speed_px_per_s=player_speed,
        shot_cooldown_s=float(player_cfg['shot_cooldown_s']),
        baseline_x=baseline_x,
    )

    decay = float(progression.get('formation_interval_decay_per_level', 0.08))
    min_multiplier = float(progression.get('min_formation_interval_multiplier', 0.55))
    level_multiplier = max(min_multiplier, 1.0 - decay * max(0, level - 1))
    interval_multiplier = float(difficulty_profile.get('formation_interval_multiplier', 1.0)) * level_multiplier
    formation = AlienFormation.from_config(
        formation_config,
        interval_multiplier=interval_multiplier,
        now_s=now_s,
    )

    bunker_cfg = formation_config['bunkers']
    pattern = list(bunker_cfg['pattern'])
    cell_size = int(bunker_cfg['cell_size_px'])
    bunker_y = int(bunker_cfg['top_y_px'])
    bunkers = [
        Bunker.from_pattern(pattern, x=int(origin_x), y=bunker_y, cell_size=cell_size)
        for origin_x in bunker_cfg['origins_x_px']
    ]

    ufo = UFO(
        width=int(ufo_cfg['width_px']),
        height=int(ufo_cfg['height_px']),
        speed_px_per_s=float(ufo_cfg['speed_px_per_s']),
        spawn_interval_s=float(ufo_cfg['spawn_interval_s']),
        respawn_delay_s=float(ufo_cfg['respawn_delay_s']),
        y_px=int(ufo_cfg['y_px']),
        score_cycle=[int(score) for score in ufo_cfg.get('score_cycle', [])],
        next_spawn_s=now_s + float(ufo_cfg['spawn_interval_s']),
    )
    return World(player=player, formation=formation, bunkers=bunkers, ufo=ufo, player_shot=None, enemy_shots=[])


def reset_player_after_hit(world: World) -> None:
    world.player.reset_position()
    world.player_shot = None
    world.enemy_shots.clear()

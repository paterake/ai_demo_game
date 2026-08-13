from __future__ import annotations

import random
import time

import pygame

from ai_space_invader.attract import choose_action
from ai_space_invader.attract import idle_timeout_reached
from ai_space_invader.audio import Audio
from ai_space_invader.config_loader import load_all
from ai_space_invader.config_loader import module_root
from ai_space_invader.high_scores import HighScoreEntry
from ai_space_invader.high_scores import load_high_scores
from ai_space_invader.high_scores import qualifies_for_high_score
from ai_space_invader.high_scores import record_high_score
from ai_space_invader.high_scores import save_high_scores
from ai_space_invader.projectile import Projectile
from ai_space_invader.projectile import rects_overlap
from ai_space_invader.renderer import Renderer
from ai_space_invader.state import GameState
from ai_space_invader.ui import UI
from ai_space_invader.world import build_world
from ai_space_invader.world import reset_player_after_hit


def main() -> None:
    configs = load_all()
    base_dir = module_root()
    game_config = configs['game']
    formation_config = configs['formation']
    difficulty_profiles = dict(configs['difficulty']['profiles'])
    visuals_config = configs['visuals']
    sounds_config = configs['sounds']
    high_score_config = dict(game_config['high_scores'])
    high_score_limit = int(high_score_config.get('max_entries', 5))
    high_score_name = str(high_score_config.get('default_name', 'PLAYER'))
    high_score_path = str(high_score_config['file'])
    high_scores = load_high_scores(high_score_path, limit=high_score_limit, base_dir=base_dir)

    difficulty_names = sorted(str(name) for name in difficulty_profiles)
    selected_index = difficulty_names.index('normal') if 'normal' in difficulty_names else 0
    fps = int(game_config['timing']['fps'])
    window_width = int(game_config['window']['width_px'])
    window_height = int(game_config['window']['height_px'])
    ui_cfg = game_config['ui']
    hud_height = int(ui_cfg['hud_height_px'])
    arena_top = int(ui_cfg['arena_top_px'])
    invade_line_y = window_height - int(ui_cfg['invade_line_margin_px'])
    projectile_cfg = game_config['projectiles']
    attract_config = dict(game_config.get('attract_mode', {}))
    attract_enabled = bool(attract_config.get('enabled', False))
    attract_idle_timeout_s = float(attract_config.get('idle_timeout_s', 0.0))
    attract_restart_delay_s = float(attract_config.get('restart_delay_s', game_config['timing']['wave_clear_delay_s']))
    attract_fire_tolerance_px = float(attract_config.get('fire_tolerance_px', 10.0))

    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption('Space Invaders (workshop demo)')
    clock = pygame.time.Clock()

    renderer = Renderer(
        screen=screen,
        colours=visuals_config['colours'],
        stars_config=visuals_config['stars'],
        hud_height_px=hud_height,
        arena_top_px=arena_top,
    )
    ui = UI(
        screen=screen,
        font_size_px=int(ui_cfg['font_size_px']),
        colours=visuals_config['colours'],
        hud_height_px=hud_height,
    )
    audio = Audio(enabled=bool(sounds_config.get('enabled', False)), events=dict(sounds_config.get('events', {})))
    audio.init()
    state, world, next_enemy_fire_s, rng = _new_run(
        game_config=game_config,
        formation_config=formation_config,
        difficulty_profiles=difficulty_profiles,
        difficulty=difficulty_names[selected_index],
        now_s=time.monotonic(),
    )

    running = True
    while running:
        dt_s = clock.tick(fps) / 1000.0
        now_s = time.monotonic()
        move_dir = 0
        keys = pygame.key.get_pressed()
        if not state.attract_mode:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move_dir -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move_dir += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                audio.stop_music()
            elif event.type == pygame.KEYDOWN:
                if state.attract_mode:
                    audio.stop_music()
                    state, world, next_enemy_fire_s, rng = _new_run(
                        game_config=game_config,
                        formation_config=formation_config,
                        difficulty_profiles=difficulty_profiles,
                        difficulty=difficulty_names[selected_index],
                        now_s=now_s,
                    )
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    audio.stop_music()
                elif event.key == pygame.K_p and state.mode in {'playing', 'paused'}:
                    if state.mode == 'playing':
                        state.paused_from_mode = 'playing'
                        state.mode = 'paused'
                    else:
                        state.mode = state.paused_from_mode
                elif event.key == pygame.K_r and state.mode in {'game_over', 'victory'}:
                    audio.stop_music()
                    state, world, next_enemy_fire_s, rng = _new_run(
                        game_config=game_config,
                        formation_config=formation_config,
                        difficulty_profiles=difficulty_profiles,
                        difficulty=difficulty_names[selected_index],
                        now_s=now_s,
                    )
                elif state.mode == 'start':
                    state.idle_started_s = now_s
                    if event.key in {pygame.K_UP, pygame.K_w}:
                        selected_index = (selected_index - 1) % len(difficulty_names)
                        state.difficulty = difficulty_names[selected_index]
                    elif event.key in {pygame.K_DOWN, pygame.K_s}:
                        selected_index = (selected_index + 1) % len(difficulty_names)
                        state.difficulty = difficulty_names[selected_index]
                    elif event.key in {pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE}:
                        state.mode = 'countdown'
                        state.countdown_end_s = now_s + float(game_config['timing']['start_countdown_s'])
                        audio.start_music()
                elif state.mode == 'playing' and event.key == pygame.K_SPACE:
                    if world.player_shot is None and world.player.can_fire(now_s=now_s, active_player_shot=False):
                        world.player_shot = world.player.fire(
                            now_s=now_s,
                            projectile_width=int(projectile_cfg['width_px']),
                            projectile_height=int(projectile_cfg['height_px']),
                            projectile_speed_px_per_s=float(projectile_cfg['player_speed_px_per_s']),
                        )
                        if world.player_shot is not None:
                            state.shots_fired += 1
                            audio.play('player_shoot')

        if state.mode == 'start' and idle_timeout_reached(
            enabled=attract_enabled,
            idle_started_s=state.idle_started_s,
            now_s=now_s,
            timeout_s=attract_idle_timeout_s,
        ):
            state, world, next_enemy_fire_s, rng = _new_attract_run(
                game_config=game_config,
                formation_config=formation_config,
                difficulty_profiles=difficulty_profiles,
                difficulty=difficulty_names[selected_index],
                now_s=now_s,
            )
            audio.start_music()
        elif state.mode == 'countdown' and now_s >= state.countdown_end_s:
            state.mode = 'playing'
        elif state.mode == 'wave_clear' and now_s >= state.countdown_end_s:
            state.level += 1
            if state.level > int(game_config['rules']['max_level']):
                state.mode = 'victory'
                audio.stop_music()
                if state.attract_mode:
                    state.countdown_end_s = now_s + attract_restart_delay_s
            else:
                world = build_world(
                    game_config=game_config,
                    formation_config=formation_config,
                    difficulty_profile=difficulty_profiles[state.difficulty],
                    level=state.level,
                    now_s=now_s,
                )
                state.mode = 'countdown'
                state.countdown_end_s = now_s + float(game_config['timing']['start_countdown_s'])
                next_enemy_fire_s = now_s + _enemy_fire_interval(game_config, difficulty_profiles[state.difficulty], state.level)
        elif state.attract_mode and state.mode in {'game_over', 'victory'} and now_s >= state.countdown_end_s:
            audio.stop_music()
            state, world, next_enemy_fire_s, rng = _new_attract_run(
                game_config=game_config,
                formation_config=formation_config,
                difficulty_profiles=difficulty_profiles,
                difficulty=difficulty_names[selected_index],
                now_s=now_s,
            )
            audio.start_music()

        if state.mode == 'playing':
            if state.attract_mode:
                action = choose_action(
                    player=world.player,
                    formation=world.formation,
                    ufo=world.ufo,
                    player_shot_active=world.player_shot is not None,
                    fire_tolerance_px=attract_fire_tolerance_px,
                )
                move_dir = action.move_direction
                if action.should_fire and world.player_shot is None and world.player.can_fire(now_s=now_s, active_player_shot=False):
                    world.player_shot = world.player.fire(
                        now_s=now_s,
                        projectile_width=int(projectile_cfg['width_px']),
                        projectile_height=int(projectile_cfg['height_px']),
                        projectile_speed_px_per_s=float(projectile_cfg['player_speed_px_per_s']),
                    )
                    if world.player_shot is not None:
                        state.shots_fired += 1
                        audio.play('player_shoot')
            world.player.move(move_dir, dt_s, min_x=20.0, max_x=window_width - 20.0)
            _update_projectiles(world, dt_s, window_height)
            world.formation.update(now_s, arena_left_px=20.0, arena_right_px=window_width - 20.0)
            world.ufo.update(dt_s, now_s, arena_left_px=20.0, arena_right_px=window_width - 20.0)
            _handle_bunker_collisions(world, audio)
            if world.player_shot is not None:
                alien = world.formation.hit(world.player_shot)
                if alien is not None:
                    state.score += alien.score
                    world.player_shot = None
                    audio.play('alien_hit')
            if world.player_shot is not None:
                ufo_score = world.ufo.try_hit(world.player_shot, shots_fired=state.shots_fired, now_s=now_s)
                if ufo_score is not None:
                    state.score += ufo_score
                    world.player_shot = None
                    audio.play('ufo_hit')
            if now_s >= next_enemy_fire_s and len(world.enemy_shots) < _max_enemy_projectiles(difficulty_profiles[state.difficulty]):
                shot = _spawn_enemy_shot(world, projectile_cfg, difficulty_profiles[state.difficulty], rng)
                if shot is not None:
                    world.enemy_shots.append(shot)
                    audio.play('enemy_shoot')
                next_enemy_fire_s = now_s + _enemy_fire_interval(game_config, difficulty_profiles[state.difficulty], state.level)
            if _enemy_hit_player(world):
                state.lives -= 1
                audio.play('player_hit')
                if state.lives <= 0:
                    state.mode = 'game_over'
                    audio.stop_music()
                    audio.play('game_over')
                    if state.attract_mode:
                        state.countdown_end_s = now_s + attract_restart_delay_s
                else:
                    reset_player_after_hit(world)
                    state.mode = 'countdown'
                    state.countdown_end_s = now_s + float(game_config['timing']['respawn_countdown_s'])
            elif world.formation.invasion_reached(invade_line_y):
                state.mode = 'game_over'
                audio.stop_music()
                audio.play('game_over')
                if state.attract_mode:
                    state.countdown_end_s = now_s + attract_restart_delay_s
            elif world.formation.alive_count() == 0:
                state.mode = 'wave_clear'
                state.countdown_end_s = now_s + float(game_config['timing']['wave_clear_delay_s'])
                audio.play('wave_clear')
            if state.extra_life_available(int(game_config['rules']['extra_life_score'])):
                state.extra_life_awarded = True
                state.lives += 1

        if (not state.attract_mode) and state.mode in {'game_over', 'victory'} and not state.high_score_checked:
            high_scores, state.high_score_saved = _maybe_save_high_score(
                state=state,
                high_scores=high_scores,
                high_score_name=high_score_name,
                high_score_path=high_score_path,
                high_score_limit=high_score_limit,
                game_config=game_config,
                base_dir=base_dir,
            )
            state.high_score_checked = True

        renderer.draw_world(
            player=world.player,
            formation=world.formation,
            bunkers=world.bunkers,
            player_shot=world.player_shot,
            enemy_shots=world.enemy_shots,
            ufo=world.ufo,
            invade_line_y=invade_line_y,
        )
        ui.draw_hud(score=state.score, lives=state.lives, level=state.level, difficulty=state.difficulty)
        if state.mode == 'start':
            ui.draw_start_screen(
                difficulty_names=difficulty_names,
                selected_index=selected_index,
                high_scores=high_scores,
                attract_hint=_start_screen_attract_hint(
                    enabled=attract_enabled,
                    idle_started_s=state.idle_started_s,
                    now_s=now_s,
                    timeout_s=attract_idle_timeout_s,
                ),
            )
        elif state.mode == 'countdown':
            ui.draw_countdown(remaining_s=max(0.0, state.countdown_end_s - now_s))
        else:
            ui.draw_overlay(
                mode=state.mode,
                high_scores=high_scores,
                high_score_saved=state.high_score_saved,
                attract_mode=state.attract_mode,
            )
        pygame.display.flip()

    pygame.quit()


def _new_run(*, game_config: dict, formation_config: dict, difficulty_profiles: dict, difficulty: str, now_s: float):
    return _build_session(
        game_config=game_config,
        formation_config=formation_config,
        difficulty_profiles=difficulty_profiles,
        difficulty=difficulty,
        now_s=now_s,
        mode='start',
        attract_mode=False,
        countdown_end_s=0.0,
        rng_seed=7,
    )


def _new_attract_run(*, game_config: dict, formation_config: dict, difficulty_profiles: dict, difficulty: str, now_s: float):
    return _build_session(
        game_config=game_config,
        formation_config=formation_config,
        difficulty_profiles=difficulty_profiles,
        difficulty=difficulty,
        now_s=now_s,
        mode='countdown',
        attract_mode=True,
        countdown_end_s=now_s + float(game_config['timing']['start_countdown_s']),
        rng_seed=17,
    )


def _build_session(
    *,
    game_config: dict,
    formation_config: dict,
    difficulty_profiles: dict,
    difficulty: str,
    now_s: float,
    mode: str,
    attract_mode: bool,
    countdown_end_s: float,
    rng_seed: int,
):
    state = GameState(
        score=0,
        lives=int(game_config['rules']['starting_lives']),
        level=1,
        mode=mode,
        difficulty=difficulty,
        countdown_end_s=countdown_end_s,
        shots_fired=0,
        extra_life_awarded=False,
        attract_mode=attract_mode,
        idle_started_s=now_s if mode == 'start' else 0.0,
    )
    world = build_world(
        game_config=game_config,
        formation_config=formation_config,
        difficulty_profile=difficulty_profiles[difficulty],
        level=state.level,
        now_s=now_s,
    )
    next_enemy_fire_s = now_s + _enemy_fire_interval(game_config, difficulty_profiles[difficulty], state.level)
    return state, world, next_enemy_fire_s, random.Random(rng_seed)


def _start_screen_attract_hint(*, enabled: bool, idle_started_s: float, now_s: float, timeout_s: float) -> str | None:
    if not enabled or timeout_s <= 0.0:
        return None
    remaining_s = max(0.0, timeout_s - (now_s - idle_started_s))
    return f'Demo starts after {remaining_s:.1f}s of idle time'


def _enemy_fire_interval(game_config: dict, difficulty_profile: dict, level: int) -> float:
    base = float(difficulty_profile.get('enemy_fire_interval_s', 1.0))
    decay = float(game_config['progression'].get('enemy_fire_interval_decay_per_level', 0.06))
    return max(0.22, base * max(0.45, 1.0 - decay * max(0, level - 1)))


def _max_enemy_projectiles(difficulty_profile: dict) -> int:
    return int(difficulty_profile.get('max_enemy_projectiles', 3))


def _spawn_enemy_shot(world, projectile_cfg: dict, difficulty_profile: dict, rng: random.Random) -> Projectile | None:
    shooter = world.formation.choose_shooter(rng)
    if shooter is None:
        return None
    speed = float(projectile_cfg['enemy_speed_px_per_s']) * float(difficulty_profile.get('enemy_shot_speed_multiplier', 1.0))
    width = int(projectile_cfg['width_px'])
    height = int(projectile_cfg['height_px'])
    return Projectile(
        x=shooter.x + (shooter.width - width) / 2.0,
        y=shooter.y + shooter.height,
        width=width,
        height=height,
        velocity_px_per_s=speed,
        owner='enemy',
    )


def _update_projectiles(world, dt_s: float, max_y: int) -> None:
    if world.player_shot is not None:
        world.player_shot.update(dt_s)
        if world.player_shot.offscreen(min_y=0.0, max_y=float(max_y)):
            world.player_shot = None
    alive_enemy_shots: list[Projectile] = []
    for shot in world.enemy_shots:
        shot.update(dt_s)
        if not shot.offscreen(min_y=0.0, max_y=float(max_y)):
            alive_enemy_shots.append(shot)
    world.enemy_shots = alive_enemy_shots


def _handle_bunker_collisions(world, audio: Audio) -> None:
    if world.player_shot is not None:
        px, py = world.player_shot.tip()
        for bunker in world.bunkers:
            if bunker.damage_point(px, py):
                world.player_shot = None
                audio.play('bunker_hit')
                break
    surviving_enemy_shots: list[Projectile] = []
    for shot in world.enemy_shots:
        px, py = shot.tip()
        hit = False
        for bunker in world.bunkers:
            if bunker.damage_point(px, py):
                audio.play('bunker_hit')
                hit = True
                break
        if not hit:
            surviving_enemy_shots.append(shot)
    world.enemy_shots = surviving_enemy_shots


def _enemy_hit_player(world) -> bool:
    player_bounds = world.player.bounds()
    remaining: list[Projectile] = []
    hit = False
    for shot in world.enemy_shots:
        if rects_overlap(player_bounds, shot.bounds()):
            hit = True
        else:
            remaining.append(shot)
    world.enemy_shots = remaining
    return hit


def _maybe_save_high_score(
    *,
    state: GameState,
    high_scores: list[HighScoreEntry],
    high_score_name: str,
    high_score_path: str,
    high_score_limit: int,
    game_config: dict,
    base_dir,
) -> tuple[list[HighScoreEntry], bool]:
    if not qualifies_for_high_score(high_scores, score=state.score, limit=high_score_limit):
        return high_scores, False
    level_reached = min(state.level, int(game_config['rules']['max_level']))
    updated_scores = record_high_score(
        high_scores,
        name=high_score_name,
        score=state.score,
        difficulty=state.difficulty,
        level=level_reached,
        limit=high_score_limit,
    )
    save_high_scores(high_score_path, updated_scores, limit=high_score_limit, base_dir=base_dir)
    return updated_scores, True


if __name__ == '__main__':
    main()

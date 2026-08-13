from __future__ import annotations

import random
import time
from pathlib import Path

import pygame
import yaml

from ai_pacman.audio import Audio
from ai_pacman.ghost import Ghost
from ai_pacman.maze import Maze
from ai_pacman.pacman import PacMan
from ai_pacman.renderer import Renderer
from ai_pacman.state import GameState
from ai_pacman.ui import UI


def main() -> None:
    game_config = _load_yaml("game.yaml")
    visuals_config = _load_yaml("visuals.yaml")
    maze_config = _load_yaml("maze.yaml")
    sounds_config = _load_yaml("sounds.yaml")
    difficulty_config = _load_yaml("difficulty.yaml")

    window_width_px = int(game_config["window"]["width_px"])
    window_height_px = int(game_config["window"]["height_px"])
    fps = int(game_config["timing"]["fps"])
    base_frightened_duration_s = float(game_config["timing"]["frightened_duration_s"])

    starting_lives = int(game_config["rules"]["starting_lives"])
    pellet_score = int(game_config["rules"]["pellet_score"])
    power_pellet_score = int(game_config["rules"]["power_pellet_score"])
    ghost_eat_score = int(game_config["rules"]["ghost_eat_score"])
    fruit_config = dict(game_config.get("fruit", {}))

    base_pacman_speed = float(game_config["movement"]["pacman_speed_tiles_per_s"])
    base_ghost_speed = float(game_config["movement"]["ghost_speed_tiles_per_s"])
    frightened_speed_multiplier = float(game_config["movement"]["ghost_frightened_speed_multiplier"])

    hud_height_px = int(game_config["ui"]["hud_height_px"])
    font_size_px = int(game_config["ui"]["font_size_px"])

    colours = visuals_config["colours"]
    sizes = visuals_config["sizes"]
    animation = visuals_config["animation"]
    mouth_speed_hz = float(animation["pacman_mouth_speed_hz"])

    maze = Maze.from_config(maze_config)

    pygame.init()
    screen = pygame.display.set_mode((window_width_px, window_height_px))
    pygame.display.set_caption("Pac-Man (workshop demo)")
    clock = pygame.time.Clock()

    renderer = Renderer(
        screen=screen,
        window_width_px=window_width_px,
        window_height_px=window_height_px,
        hud_height_px=hud_height_px,
        colours=colours,
        sizes=sizes,
        animation=animation,
    )
    renderer.configure_for_maze(maze)

    ui = UI(screen=screen, hud_height_px=hud_height_px, font_size_px=font_size_px, colours=colours)

    audio = Audio(enabled=bool(sounds_config.get("enabled", False)), events=dict(sounds_config.get("events", {})))
    audio.init()

    rng = random.Random(0)
    difficulty_profiles = difficulty_config.get("profiles", {})
    if not isinstance(difficulty_profiles, dict) or not difficulty_profiles:
        raise ValueError("difficulty.yaml must contain profiles: <mapping>")
    difficulty_names = sorted(str(k) for k in difficulty_profiles.keys())
    selected_difficulty_index = 0

    pacman, ghosts, state, maze = _new_game(
        maze_config=maze_config,
        starting_lives=starting_lives,
        pacman_speed=base_pacman_speed,
        ghost_speed=base_ghost_speed,
        difficulty=difficulty_names[selected_difficulty_index],
    )

    def apply_level_speeds() -> None:
        profile = difficulty_profiles.get(state.difficulty, {})
        pac_mul = float(profile.get("pacman_speed_multiplier", 1.0))
        ghost_mul = float(profile.get("ghost_speed_multiplier", 1.0))
        level_mul = 1.0 + 0.06 * max(0, state.level - 1)
        pacman.speed_tiles_per_s = base_pacman_speed * pac_mul
        for ghost in ghosts:
            ghost.speed_tiles_per_s = base_ghost_speed * ghost_mul * level_mul

    running = True
    while running:
        dt_s = clock.tick(fps) / 1000.0
        now_s = time.monotonic()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                audio.stop_music()
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    audio.stop_music()
                    running = False
                elif event.key == pygame.K_p and state.mode in {"playing", "paused"}:
                    if state.mode == "playing":
                        state.paused_from_mode = "playing"
                        state.mode = "paused"
                    else:
                        state.mode = state.paused_from_mode or "playing"
                elif event.key == pygame.K_r and state.mode in {"game_over", "victory", "level_complete"}:
                    audio.stop_music()
                    pacman, ghosts, state, maze = _new_game(
                        maze_config=maze_config,
                        starting_lives=starting_lives,
                        pacman_speed=base_pacman_speed,
                        ghost_speed=base_ghost_speed,
                        difficulty=difficulty_names[selected_difficulty_index],
                    )
                    renderer.configure_for_maze(maze)
                else:
                    if state.mode == "start":
                        if event.key in {pygame.K_UP, pygame.K_w}:
                            selected_difficulty_index = (selected_difficulty_index - 1) % len(difficulty_names)
                            state.difficulty = difficulty_names[selected_difficulty_index]
                        elif event.key in {pygame.K_DOWN, pygame.K_s}:
                            selected_difficulty_index = (selected_difficulty_index + 1) % len(difficulty_names)
                            state.difficulty = difficulty_names[selected_difficulty_index]
                        elif event.key in {pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE}:
                            state.mode = "countdown"
                            state.countdown_end_s = now_s + 3.0
                            audio.start_music()
                            apply_level_speeds()
                    elif state.mode in {"countdown", "playing"}:
                        direction = _key_to_direction(event.key)
                        if direction is not None:
                            pacman.queue_direction(direction)

        if state.mode == "countdown":
            if now_s >= state.countdown_end_s:
                state.mode = "playing"
                state.frightened_until_s = 0.0
        elif state.mode == "level_complete":
            if now_s >= state.countdown_end_s:
                state.level += 1
                maze = Maze.from_config(maze_config)
                pacman.reset(*maze.pacman_spawn)
                for ghost in ghosts:
                    ghost.reset_to_spawn()
                renderer.configure_for_maze(maze)
                state.frightened_until_s = 0.0
                state.ghosts_eaten_in_fright = 0
                state.level_start_pellet_count = maze.pellet_count()
                state.fruit_active = False
                state.fruit_expires_s = 0.0
                state.fruit_score = 0
                state.fruit_name = ""
                state.fruit_spawned_at_pellets_eaten.clear()
                state.mode = "countdown"
                state.countdown_end_s = now_s + 3.0
                apply_level_speeds()
        elif state.mode == "playing":
            profile = difficulty_profiles.get(state.difficulty, {})
            frightened_duration_s = base_frightened_duration_s * float(profile.get("frightened_duration_multiplier", 1.0))

            pacman.update(dt_s, maze, mouth_speed_hz=mouth_speed_hz)

            maze, pellet_kind = maze.eat_pellet(pacman.row, pacman.col)
            if pellet_kind == "normal":
                state.score += pellet_score
                audio.play("pellet_eat")
            elif pellet_kind == "power":
                state.score += power_pellet_score
                state.frightened_until_s = now_s + frightened_duration_s
                state.ghosts_eaten_in_fright = 0
                audio.play("power_pellet")

            next_fruit_name, next_fruit_score = _fruit_for_level(fruit_config, level=state.level)
            if state.fruit_active:
                if now_s >= state.fruit_expires_s:
                    state.fruit_active = False
                    state.fruit_name = ""
                    state.fruit_score = 0
                elif pacman.row == state.fruit_row and pacman.col == state.fruit_col:
                    state.score += int(state.fruit_score)
                    state.fruit_active = False
                    state.fruit_name = ""
                    state.fruit_score = 0
                    audio.play("fruit_eat")

            pellets_eaten = state.level_start_pellet_count - maze.pellet_count()
            spawn_counts = fruit_config.get("spawn_pellets_eaten", [70, 170])
            if not isinstance(spawn_counts, list):
                spawn_counts = [70, 170]
            spawn_counts = [int(x) for x in spawn_counts if isinstance(x, (int, float))]
            spawn_counts.sort()

            if not state.fruit_active:
                for target_eaten in spawn_counts:
                    if pellets_eaten >= target_eaten and target_eaten not in state.fruit_spawned_at_pellets_eaten:
                        positions = fruit_config.get("spawn_positions", [{"row": 17, "col": 13}])
                        if not isinstance(positions, list) or not positions:
                            positions = [{"row": 17, "col": 13}]
                        pos = rng.choice([p for p in positions if isinstance(p, dict)] or [{"row": 17, "col": 13}])
                        row = int(pos.get("row", 17))
                        col = int(pos.get("col", 13))
                        if not maze.is_wall(row, col):
                            state.fruit_row = row
                            state.fruit_col = col
                            state.fruit_name = str(next_fruit_name)
                            state.fruit_score = int(next_fruit_score)
                            ttl_min_s = float(fruit_config.get("ttl_min_s", fruit_config.get("ttl_s", 9.0)))
                            ttl_max_s = float(fruit_config.get("ttl_max_s", fruit_config.get("ttl_s", 9.0)))
                            ttl_low = min(ttl_min_s, ttl_max_s)
                            ttl_high = max(ttl_min_s, ttl_max_s)
                            ttl_s = ttl_low + (ttl_high - ttl_low) * rng.random()
                            state.fruit_expires_s = now_s + max(0.5, ttl_s)
                            state.fruit_active = True
                            state.fruit_spawned_at_pellets_eaten.add(target_eaten)
                            break

            frightened_active = state.frightened_active(now_s)
            frightened_remaining_s = max(0.0, state.frightened_until_s - now_s) if frightened_active else 0.0
            for ghost in ghosts:
                ghost.update(
                    dt_s,
                    maze,
                    now_s=now_s,
                    pacman_row=pacman.row,
                    pacman_col=pacman.col,
                    frightened_active=frightened_active,
                    frightened_remaining_s=frightened_remaining_s,
                    frightened_speed_multiplier=frightened_speed_multiplier,
                    rng=rng,
                )

            for ghost in ghosts:
                if ghost.row == pacman.row and ghost.col == pacman.col:
                    if frightened_active and ghost.mode not in {"eyes", "regenerating"}:
                        state.score += ghost_eat_score * (2 ** state.ghosts_eaten_in_fright)
                        state.ghosts_eaten_in_fright = min(state.ghosts_eaten_in_fright + 1, 3)
                        ghost.become_eyes()
                        audio.play("ghost_eat")
                    elif ghost.mode not in {"eyes", "regenerating"}:
                        state.lives -= 1
                        audio.play("pacman_death")
                        if state.lives <= 0:
                            state.mode = "game_over"
                            audio.stop_music()
                            audio.play("game_over")
                        else:
                            pacman.reset(*maze.pacman_spawn)
                            for g in ghosts:
                                g.reset_to_spawn()
                            state.frightened_until_s = 0.0
                            state.ghosts_eaten_in_fright = 0
                            state.fruit_active = False
                            state.fruit_name = ""
                            state.fruit_score = 0
                            state.fruit_expires_s = 0.0
                            state.mode = "countdown"
                            state.countdown_end_s = now_s + 3.7
                    break

            if state.mode == "playing" and maze.pellet_count() == 0:
                state.mode = "level_complete"
                state.countdown_end_s = now_s + 2.0
                audio.play("victory")

        fruit = (state.fruit_row, state.fruit_col, state.fruit_name) if state.fruit_active else None
        renderer.draw_world(maze, pacman, ghosts, now_s=now_s, fruit=fruit)
        next_fruit_name, next_fruit_score = _fruit_for_level(fruit_config, level=state.level)
        pellets_eaten = state.level_start_pellet_count - maze.pellet_count()
        fruit_label = f"Next: {next_fruit_name} ({next_fruit_score})  Dots: {pellets_eaten}"
        if state.fruit_active:
            fruit_label = f"{fruit_label}  Fruit: {state.fruit_name} {max(0.0, state.fruit_expires_s - now_s):.1f}s"
        ui.draw_hud(score=state.score, lives=state.lives, level=state.level, fruit_label=fruit_label)
        if state.mode == "start":
            ui.draw_start_screen(difficulty_names=difficulty_names, selected_index=selected_difficulty_index)
        elif state.mode == "countdown":
            ui.draw_countdown(remaining_s=max(0.0, state.countdown_end_s - now_s))
        ui.draw_overlay(mode=state.mode)
        pygame.display.flip()

    pygame.quit()


def _new_game(
    *,
    maze_config: dict,
    starting_lives: int,
    pacman_speed: float,
    ghost_speed: float,
    difficulty: str,
) -> tuple[PacMan, list[Ghost], GameState, Maze]:
    maze = Maze.from_config(maze_config)
    pacman = PacMan(
        row=maze.pacman_spawn[0],
        col=maze.pacman_spawn[1],
        direction="none",
        queued_direction=None,
        speed_tiles_per_s=pacman_speed,
    )

    ghosts: list[Ghost] = []
    for name in ["blinky", "pinky", "inky", "clyde"]:
        row, col = maze.ghost_spawns[name]
        ghosts.append(
            Ghost(
                name=name,
                row=row,
                col=col,
                direction="left",
                speed_tiles_per_s=ghost_speed,
                spawn_row=row,
                spawn_col=col,
            )
        )

    state = GameState(
        score=0,
        lives=starting_lives,
        mode="start",
        frightened_until_s=0.0,
        difficulty=difficulty,
        countdown_end_s=0.0,
        ghosts_eaten_in_fright=0,
        paused_from_mode="playing",
        level=1,
        level_start_pellet_count=maze.pellet_count(),
        fruit_active=False,
        fruit_row=0,
        fruit_col=0,
        fruit_name="",
        fruit_score=0,
        fruit_expires_s=0.0,
    )
    return pacman, ghosts, state, maze


def _fruit_for_level(fruit_config: dict, *, level: int) -> tuple[str, int]:
    table = fruit_config.get("table", [])
    if isinstance(table, list):
        for entry in table:
            if not isinstance(entry, dict):
                continue
            min_level = int(entry.get("min_level", 1))
            max_level = int(entry.get("max_level", 999))
            if min_level <= level <= max_level:
                name = str(entry.get("name", "fruit"))
                score = int(entry.get("score", 500))
                return name, score
    return "fruit", 500


def _key_to_direction(key: int) -> str | None:
    if key in {pygame.K_UP, pygame.K_w}:
        return "up"
    if key in {pygame.K_DOWN, pygame.K_s}:
        return "down"
    if key in {pygame.K_LEFT, pygame.K_a}:
        return "left"
    if key in {pygame.K_RIGHT, pygame.K_d}:
        return "right"
    return None


def _load_yaml(filename: str) -> dict:
    config_dir = Path(__file__).resolve().parents[2] / "config"
    path = config_dir / filename
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{filename} must parse to a mapping")
    return data


if __name__ == "__main__":
    main()

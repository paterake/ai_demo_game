from __future__ import annotations

from pathlib import Path

import yaml


def module_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_yaml(filename: str) -> dict:
    path = module_root() / 'config' / filename
    with path.open('r', encoding='utf-8') as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f'{filename} must parse to a mapping')
    return data


def load_all() -> dict[str, dict]:
    return {
        'game': load_yaml('game.yaml'),
        'formation': load_yaml('formation.yaml'),
        'difficulty': load_yaml('difficulty.yaml'),
        'visuals': load_yaml('visuals.yaml'),
        'sounds': load_yaml('sounds.yaml'),
    }

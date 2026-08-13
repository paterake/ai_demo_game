from __future__ import annotations

import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class HighScoreEntry:
    name: str
    score: int
    difficulty: str
    level: int
    date: str

    @classmethod
    def from_dict(cls, payload: dict) -> HighScoreEntry:
        return cls(
            name=str(payload['name']).strip(),
            score=int(payload['score']),
            difficulty=str(payload['difficulty']).strip(),
            level=int(payload['level']),
            date=str(payload['date']).strip(),
        )


def resolve_storage_path(path_value: str | Path, *, base_dir: Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return base_dir / path


def load_high_scores(path_value: str | Path, *, limit: int, base_dir: Path) -> list[HighScoreEntry]:
    path = resolve_storage_path(path_value, base_dir=base_dir)
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(payload, list):
        return []
    entries: list[HighScoreEntry] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        try:
            entries.append(HighScoreEntry.from_dict(item))
        except (KeyError, TypeError, ValueError):
            continue
    return _rank_entries(entries, limit=limit)


def save_high_scores(path_value: str | Path, entries: Iterable[HighScoreEntry], *, limit: int, base_dir: Path) -> None:
    path = resolve_storage_path(path_value, base_dir=base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(entry) for entry in _rank_entries(entries, limit=limit)]
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def qualifies_for_high_score(entries: list[HighScoreEntry], *, score: int, limit: int) -> bool:
    if limit <= 0:
        return False
    if len(entries) < limit:
        return True
    return score > entries[-1].score


def record_high_score(
    entries: list[HighScoreEntry],
    *,
    name: str,
    score: int,
    difficulty: str,
    level: int,
    when: date | None = None,
    limit: int,
) -> list[HighScoreEntry]:
    entry = HighScoreEntry(
        name=(name.strip() or 'PLAYER'),
        score=score,
        difficulty=difficulty,
        level=level,
        date=(when or date.today()).isoformat(),
    )
    return _rank_entries([*entries, entry], limit=limit)


def _rank_entries(entries: Iterable[HighScoreEntry], *, limit: int) -> list[HighScoreEntry]:
    ranked = sorted(
        entries,
        key=lambda entry: (-entry.score, -entry.level, entry.date, entry.name),
    )
    return ranked[: max(0, limit)]

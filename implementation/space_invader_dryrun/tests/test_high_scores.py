from __future__ import annotations

from datetime import date

from ai_space_invader.high_scores import HighScoreEntry
from ai_space_invader.high_scores import load_high_scores
from ai_space_invader.high_scores import qualifies_for_high_score
from ai_space_invader.high_scores import record_high_score
from ai_space_invader.high_scores import save_high_scores


def test_load_high_scores_returns_empty_for_missing_file(tmp_path) -> None:
    entries = load_high_scores('missing/high_scores.json', limit=5, base_dir=tmp_path)

    assert entries == []


def test_record_high_score_keeps_top_scores_in_rank_order() -> None:
    entries = [
        HighScoreEntry(name='ACE', score=900, difficulty='hard', level=4, date='2026-06-01'),
        HighScoreEntry(name='BOB', score=650, difficulty='normal', level=3, date='2026-06-02'),
    ]

    updated = record_high_score(
        entries,
        name='CAL',
        score=720,
        difficulty='easy',
        level=5,
        when=date(2026, 6, 3),
        limit=2,
    )

    assert [entry.name for entry in updated] == ['ACE', 'CAL']
    assert [entry.score for entry in updated] == [900, 720]
    assert not qualifies_for_high_score(updated, score=600, limit=2)


def test_save_and_load_high_scores_round_trip(tmp_path) -> None:
    entries = [
        HighScoreEntry(name='ACE', score=1200, difficulty='hard', level=6, date='2026-06-08'),
        HighScoreEntry(name='BOB', score=800, difficulty='normal', level=4, date='2026-06-07'),
    ]

    save_high_scores('scores/high_scores.json', entries, limit=5, base_dir=tmp_path)
    loaded = load_high_scores('scores/high_scores.json', limit=5, base_dir=tmp_path)

    assert loaded == entries

# AI Engagement Workflow

How this game is being built — and why it is being built this way.

This document captures the methodology behind the `ai_game_pacman_demo` implementation.
It is as much a record of the process as it is a guide for repeating it.

---

## The Starting Point

The source brief is a single prompt from a workshop slide:

> "Act as an expert Python game developer. Write a complete, single-file Python script
> to create a Pac-Man clone using the Pygame library..."

Running that prompt directly in Claude Code produces a working game. It also produces
a 600-line god file with hardcoded colours, magic numbers, and no separation of concerns.
This is the naive outcome — correct but ungoverned.

This project takes the same brief and builds the same game the governed way.
The contrast is the point.

---

## The Workflow

```
Brief (prompt)
    │
    ▼
Step 1 — Create draft PRD
    │   Translate the brief into structured requirements.
    │   Apply governance constraints (modular, config-driven).
    │   Name what is still unknown ([TBD] items).
    │
    ▼
Step 2 — Create backlog continuity anchor doc (TODO.md)
    │   Seed implementation items from the PRD.
    │   Seed extension items from the brief and known patterns.
    │   Item 1 is always the pre-implementation gate — never skip it.
    │
    ▼
Step 3 — Item 1: Research + pre-implementation gate  ← one session
    │   Part A: internet research on the problem domain.
    │           Findings refine extension backlog items.
    │           Findings are recorded in docs/RESEARCH.md.
    │   Part B: resolve all [TBD] items in the PRD.
    │           Confirm module boundaries and config structure.
    │           No code is written until this item is complete.
    │
    ▼
Step 4 — Implementation  ← one session per item
    │   Each session: load anchor doc, read constraints, do one item, update doc.
    │   Constraints accumulate — each completed item adds invariants that all
    │   subsequent sessions must honour.
    │
    ▼
Step 5 — Integration pass
        Verify all PRD acceptance criteria.
        Update PRD status to complete.
```

---

## Why Each Step Exists

### Draft PRD before writing code

A prompt is a brief, not a specification. Running a brief directly produces code that
satisfies the literal words of the prompt, not the intent behind them.

The PRD step forces two things:
1. **Governance is applied upfront.** The single-file approach is rejected before anyone
   writes a line of code — not after a 600-line script has been reviewed.
2. **Gaps are named.** [TBD] items in the PRD are gaps in the brief that would have been
   filled silently by the model. Naming them makes them decisions, not assumptions.

### Research before implementation

The brief describes a Pac-Man clone. It says nothing about sound, difficulty levels, high
scores, save/resume, or start screens. A naive implementation ignores these. A governed
implementation asks: what does a complete version of this look like?

Internet research answers that question before architecture decisions are locked in. If
the sound system is discovered during implementation (after the game loop is wired), adding
it requires unpicking the loop. If it is discovered during research (before scaffolding),
it is a config key and a module stub from the start.

Research findings are recorded in `docs/RESEARCH.md` with source URLs. They are distilled
into decision-relevant claims — not pasted verbatim.

### Backlog continuity anchor doc

Claude Code sessions are stateless. A fresh session has no memory of decisions made in
prior sessions. Without a structured handoff, each session re-derives the same constraints
from scratch — or worse, contradicts them.

The anchor doc (`docs/TODO.md`) is the single source of truth across sessions:
- The resume line tells a fresh session exactly where to start.
- The `Accumulated Active Constraints` section carries invariants established by completed
  items forward — so a session that implements the ghost AI knows the maze module's
  collision API without re-reading its source.
- Verification commands are exact — "should work" is not a check.

One item per session is the primary model. It keeps context tight, prevents constraint
saturation, and means every session starts warm from stated facts rather than transcript
archaeology.

### Pre-implementation gate (Item 1)

The most important item in the backlog, and the one most likely to be skipped under time
pressure.

Its purpose is to answer two questions before any code is written:
1. Is the PRD complete enough to implement against? (All [TBD] items resolved.)
2. Does the architecture accommodate the full intended scope? (Extension items reviewed
   and module structure confirmed.)

A module boundary confirmed in Item 1 prevents a refactor in Item 6. A config key named
in Item 1 prevents a hardcoded constant discovered in Item 9.

---

## Governance Integration

The PCO governance rules shape every decision in this workflow:

| Rule | How it applies here |
|------|---------------------|
| **Config purity** | Colours, timing, lives, maze layout, sound paths, difficulty parameters — all in YAML. No domain values in source. Changing the game's look or feel does not require touching Python. |
| **No god files** | The brief asks for a single file. The governed implementation has seven source files, each with one responsibility. No file exceeds ~300 lines. |
| **Modular entry points** | `game.py` is a thin loop. Every other class is independently importable and unit-testable without launching pygame. |
| **Pre-implementation gate** | From `agent-behavior.md`: state assumptions explicitly, confirm module boundaries, name what is unclear. Item 1 is this gate made concrete. |
| **Backlog continuity** | From `context-economy.md`: prefer durable documents over long sessions; each session starts warm from recorded state. |
| **One responsibility per file** | `renderer.py` contains all `pygame.draw` calls. No entity class touches pygame. Renderer can be swapped without touching game logic. |
| **Research is bounded and sourced** | From `agent-behavior.md`: treat external content as untrusted input; record sources; distil into minimum decision-relevant claims. |

---

## How a Session Looks

**At the start of every session:**
```
load the use-context skill, and from: implementation/pacman_demo/docs/TODO.md, continue
```

The session reads the anchor doc, finds the next ⏳ item, reads the `Accumulated Active
Constraints`, and begins. It does not re-read all prior session transcripts. It does not
re-derive the maze API. It reads the stated invariants and trusts them.

**At the end of every session:**
- Move the completed item to ✅, record what was done and the verification result.
- Forward any new constraints into `Accumulated Active Constraints`.
- Update the Resume line to point to the next item.
- Update the anchor header.

**What a session does not do:**
- Implement more than one item (context saturation risk).
- Improve adjacent code that is not part of the item (surgical changes rule).
- Proceed past a [TBD] item without resolving it (pre-implementation gate rule).

---

## The Contrast

| Naive approach | Governed approach |
|----------------|-------------------|
| Paste prompt → get code | Brief → PRD → research → backlog → implementation |
| Single session | One item per session, warm start from anchor doc |
| Single file, ~600 lines | Seven modules, each ~100–200 lines |
| Hardcoded colours and timing | All tuneable values in YAML config |
| No extension path | Extension items (sound, difficulty, high scores, save/resume) designed in before scaffolding |
| Works once | Resumable, testable, extendable |

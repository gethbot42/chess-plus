# Implementation Plan: Lichess Puzzle

**Branch**: `001-lichess-puzzle` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-lichess-puzzle/spec.md`

## Summary

A single `Puzzle` class that parses one Lichess puzzle CSV row (text line or header-keyed
mapping), validates it eagerly, and lets callers step through the moves in either direction
and read the moves in SAN. Board state, legality and SAN all come from python-chess; the class
only parses fields and keeps a step index.

## Technical Context

**Language/Version**: Python 3.10+ (python-chess 1.11 requires >= 3.8; 3.10 chosen for `X | None` syntax)

**Primary Dependencies**: `chess` (python-chess) only; stdlib `csv`, `datetime`, `dataclasses`

**Storage**: N/A (no I/O; caller supplies the row)

**Testing**: pytest; mypy on the package

**Target Platform**: Any platform running CPython

**Project Type**: library

**Performance Goals**: None specific; one puzzle is ~2-20 moves, so per-step board replay is trivial

**Constraints**: No I/O or global state (constitution); immutable puzzle data, mutable step only

**Scale/Scope**: One class, one module, one test file

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Build on python-chess | PASS | `chess.Board` for FEN/legality/position, `chess.Move` for moves, `Board.variation_san` for SAN. Nothing re-implemented. |
| II. Test-First | PASS | tasks.md will order `tests/test_puzzle.py` cases before each implementation step. |
| III. Simplicity / YAGNI | PASS | One class, no base classes/protocols/factories. No CSV-file reader or filtering (out of scope per spec). No new runtime deps. |
| IV. Stable, Typed Public API | PASS | `chess_plus.__init__` exports only `Puzzle`; all public methods typed + docstrings. Version starts at 0.1.0. |
| Tech constraints | PASS | `pyproject.toml` only, pytest, mypy, no I/O. |

Post-design re-check: PASS (design adds nothing beyond the above).

## Project Structure

### Documentation (this feature)

```text
specs/001-lichess-puzzle/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── puzzle-api.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
pyproject.toml
src/
└── chess_plus/
    ├── __init__.py      # exports Puzzle
    ├── py.typed
    └── puzzle.py        # Puzzle class
tests/
└── test_puzzle.py
CHANGELOG.md
```

**Structure Decision**: Single library package in `src/` layout. One module, one test file;
split only when a second feature needs it.

## Complexity Tracking

No violations.

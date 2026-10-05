---

description: "Task list for the Lichess Puzzle feature"
---

# Tasks: Lichess Puzzle

**Input**: Design documents from `/specs/001-lichess-puzzle/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/puzzle-api.md, quickstart.md

**Tests**: REQUIRED. The constitution (Principle II, Test-First, NON-NEGOTIABLE) says every test
task comes before the implementation it covers, and the tests must fail before the implementation
is written.

**Organization**: Tasks are grouped by user story. All code lives in one module
(`src/chess_plus/puzzle.py`) and one test file (`tests/test_puzzle.py`), per plan.md. Because of
this, most tasks inside a story touch the same file and run in sequence.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story the task belongs to (US1, US2, US3)

## Shared test fixtures (used across tasks)

- `SAMPLE_ROW` = `00sO1,1k1r4/pp3pp1/2p1p3/4b3/P3n1P1/8/KPP2PN1/3rBR1R b - - 2 31,b8c7 e1a5 b7b6 f1d1,998,85,94,293,advantage discoveredAttack master middlegame short,https://lichess.org/vsfFkG0s/black#62,,`
- `SAMPLE_FEN` = `1k1r4/pp3pp1/2p1p3/4b3/P3n1P1/8/KPP2PN1/3rBR1R b - - 2 31`
- `HEADER` = `PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningTags,DailyDate`
- `TAGGED_ROW` = `SAMPLE_ROW` with OpeningTags = `Sicilian_Defense Sicilian_Defense_Najdorf` and DailyDate = `2024-01-15`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create an installable, type-checked, empty package.

- [X] T001 Create `pyproject.toml` at repo root: build backend `setuptools>=61` with `[tool.setuptools.packages.find] where = ["src"]`, project name `chess-plus`, version `0.1.0`, `requires-python = ">=3.10"`, `dependencies = ["chess>=1.11"]`, optional dependency group `dev = ["pytest", "mypy"]`, `[tool.pytest.ini_options] testpaths = ["tests"]`, `[tool.mypy] strict = true`. No `setup.py`.
- [X] T002 [P] Create `src/chess_plus/__init__.py` with a module docstring and an empty `__all__: list[str] = []`, plus an empty marker file `src/chess_plus/py.typed` (PEP 561).
- [X] T003 [P] Create `tests/test_puzzle.py` holding only the shared fixture constants `SAMPLE_ROW`, `SAMPLE_FEN`, `HEADER` and `TAGGED_ROW` (values listed above) and `import chess`, `import datetime`, `import pytest`.
- [X] T004 Install with `pip install -e ".[dev]"`, then confirm `pytest` runs (0 tests collected is fine) and `mypy src` passes.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: An empty `Puzzle` class that is exported, so tests can import it.

- [X] T005 Create `src/chess_plus/puzzle.py` with `class Puzzle:` (docstring only: "One Lichess puzzle row with step-by-step navigation."). In `src/chess_plus/__init__.py`, add `from chess_plus.puzzle import Puzzle` and set `__all__ = ["Puzzle"]`. `Puzzle` is the only public export (contract).

**Checkpoint**: `from chess_plus import Puzzle` works. User story work can begin.

---

## Phase 3: User Story 1 - Load a puzzle from a Lichess row (Priority: P1) 🎯 MVP

**Goal**: Turn one Lichess CSV row (text or header-keyed mapping) into a validated, immutable `Puzzle`.

**Independent Test**: `pytest tests/test_puzzle.py -k load` passes. The sample row loads and every field matches the row; every invalid row raises a `ValueError` that names the bad field.

### Tests for User Story 1 (write FIRST, confirm they FAIL) ⚠️

- [X] T006 [US1] In `tests/test_puzzle.py`, add `test_load_sample_row_fields`: `Puzzle.from_csv_row(SAMPLE_ROW)` has `puzzle_id == "00sO1"`, `fen == SAMPLE_FEN`, `moves == tuple(chess.Move.from_uci(m) for m in ["b8c7", "e1a5", "b7b6", "f1d1"])`, `rating == 998`, `rating_deviation == 85`, `popularity == 94`, `nb_plays == 293`, `themes == ("advantage", "discoveredAttack", "master", "middlegame", "short")`, `game_url == "https://lichess.org/vsfFkG0s/black#62"`, `opening_tags == ()`, `daily_date is None` (US1-1, US1-2, US1-3, SC-001).
- [X] T007 [US1] In `tests/test_puzzle.py`, add `test_load_solver_color`: the sample puzzle has `solver_color == chess.WHITE` (US1-5, FR-007).
- [X] T008 [US1] In `tests/test_puzzle.py`, add `test_load_tagged_row`: `Puzzle.from_csv_row(TAGGED_ROW)` has `opening_tags == ("Sicilian_Defense", "Sicilian_Defense_Najdorf")` and `daily_date == datetime.date(2024, 1, 15)` (US1-4, FR-004, FR-005).
- [X] T009 [US1] In `tests/test_puzzle.py`, add `test_load_from_dict`: build the mapping with `dict(zip(HEADER.split(","), next(csv.reader([SAMPLE_ROW]))))`. `Puzzle.from_dict(mapping)` gives the same field values as `from_csv_row(SAMPLE_ROW)`. Also check that a mapping with the `Rating` key removed raises `ValueError` whose message contains `Rating` (FR-001, contract).
- [X] T010 [US1] In `tests/test_puzzle.py`, add `test_load_whitespace_tags`: a row whose Themes is `"  advantage   short "` gives `themes == ("advantage", "short")`, and whose Themes is blank gives `themes == ()` (Edge Cases, FR-004).
- [X] T011 [US1] In `tests/test_puzzle.py`, add `test_load_invalid_rows` with `@pytest.mark.parametrize` over `(row, field_name)` pairs. Each one asserts `pytest.raises(ValueError, match=field_name)` on `Puzzle.from_csv_row(row)`. All rows are derived from `SAMPLE_ROW` (SC-005, FR-013):
  - 10 fields (drop the last comma) → `"row"`
  - 12 fields (add a trailing comma) → `"row"`
  - empty PuzzleId → `"PuzzleId"`
  - FEN `"not a fen"` → `"FEN"`
  - Moves `""` → `"Moves"`
  - Moves `"b8c7"` (only 1 move; at least 2 required) → `"Moves"`
  - Moves `"b8c7 zzzz"` (not UCI) → `"Moves"`
  - Moves `"b8c7 a1a8"` (illegal in position) → `"Moves"`
  - Rating `"abc"` → `"Rating"`; RatingDeviation `"1.5"` → `"RatingDeviation"`; Popularity `"x"` → `"Popularity"`; NbPlays `""` → `"NbPlays"`
  - DailyDate `"2024-13-45"` → `"DailyDate"`
  - `HEADER` itself → `ValueError` (any field name)
- [X] T012 [US1] In `tests/test_puzzle.py`, add `test_load_negative_popularity`: a row with Popularity `-42` loads and has `popularity == -42` (Edge Cases).
- [X] T013 [US1] Run `pytest tests/test_puzzle.py`. Confirm that T006–T012 FAIL because `from_csv_row`/`from_dict` do not exist yet.

### Implementation for User Story 1

- [X] T014 [US1] In `src/chess_plus/puzzle.py`, add a module-level private constant `_HEADER: tuple[str, ...] = ("PuzzleId", "FEN", "Moves", "Rating", "RatingDeviation", "Popularity", "NbPlays", "Themes", "GameUrl", "OpeningTags", "DailyDate")` and a private helper `_int(row, key) -> int` that raises `ValueError(f"{key}: expected an integer, got {value!r}")` when the value does not parse.
- [X] T015 [US1] In `src/chess_plus/puzzle.py`, implement `Puzzle.from_dict(cls, row: Mapping[str, str]) -> Puzzle` (classmethod, typed, docstring). It raises `ValueError(f"{key}: missing")` for any absent header key. It then parses and validates in this order:
  - `puzzle_id`: "non-empty", otherwise `ValueError("PuzzleId: empty")`
  - `fen`: "must parse as `chess.Board(fen)`"; wrap the python-chess `ValueError` as `ValueError(f"FEN: {err}")`
  - `moves`: "UCI, whitespace-split, ≥ 2, each legal in sequence". Split with `str.split()`, require `len >= 2`, parse each with `chess.Move.from_uci`, and replay on a fresh `chess.Board(fen)`, checking `move in board.legal_moves`. Compute `board.san(move)` before each `push` to build `san_moves` in the same pass (research R4/R5). Any failure → `ValueError(f"Moves: ...")` naming the bad move.
  - `rating`, `rating_deviation`, `popularity` ("may be negative"), `nb_plays` via `_int`
  - `themes`, `opening_tags`: "whitespace-split; blank → `()`" via `tuple(value.split())`
  - `game_url`: as-is
  - `daily_date`: "ISO date; blank → `None`" via `datetime.date.fromisoformat`; failure → `ValueError(f"DailyDate: ...")`
  - `solver_color = not chess.Board(fen).turn`
  Never return a partly built object.
- [X] T016 [US1] In `src/chess_plus/puzzle.py`, store all data fields from data-model.md as read-only attributes (private `_`-prefixed slots exposed via `@property`, each typed and docstringed): `puzzle_id: str`, `fen: str`, `moves: tuple[chess.Move, ...]`, `rating: int`, `rating_deviation: int`, `popularity: int`, `nb_plays: int`, `themes: tuple[str, ...]`, `game_url: str`, `opening_tags: tuple[str, ...]`, `daily_date: datetime.date | None`, `solver_color: chess.Color`, `san_moves: tuple[str, ...]`. Use tuples so stored data is immutable.
- [X] T017 [US1] In `src/chess_plus/puzzle.py`, implement `Puzzle.from_csv_row(cls, line: str) -> Puzzle` (classmethod, typed, docstring). Parse with `next(csv.reader([line]))` (research R1). If the field count is not 11, raise `ValueError(f"row: expected 11 fields, got {n}")`. Otherwise delegate to `from_dict(dict(zip(_HEADER, fields)))`.
- [X] T018 [US1] Run `pytest tests/test_puzzle.py` (T006–T012 green) and `mypy src` (clean).

**Checkpoint**: User Story 1 works and can be tested on its own (MVP).

---

## Phase 4: User Story 2 - Step through the puzzle's moves in either direction (Priority: P2)

**Goal**: Move forward and backward through the moves and read the board at each step.

**Independent Test**: `pytest tests/test_puzzle.py -k nav` passes. Forward through all 4 sample moves and back to the start gives `board.fen() == SAMPLE_FEN`.

### Tests for User Story 2 (write FIRST, confirm they FAIL) ⚠️

- [X] T019 [US2] In `tests/test_puzzle.py`, add `test_nav_initial_state`: a newly loaded sample puzzle has `step == 0`, `board.fen() == SAMPLE_FEN`, `previous_move is None`, and `next_move == chess.Move.from_uci("b8c7")` (US2-1, FR-008, FR-012).
- [X] T020 [US2] In `tests/test_puzzle.py`, add `test_nav_forward_once`: `forward()` returns `True`, `step == 1`, `board.turn == chess.WHITE`, and `board.fen()` equals the FEN of `chess.Board(SAMPLE_FEN)` after pushing `b8c7`. `previous_move == b8c7` and `next_move == e1a5` (US2-2, FR-012).
- [X] T021 [US2] In `tests/test_puzzle.py`, add `test_nav_round_trip`: call `forward()` 4 times (each returns `True`), then `back()` 4 times (each returns `True`). Afterward `board.fen() == SAMPLE_FEN` exactly, including side to move, castling, en passant and counters (US2-3, SC-002).
- [X] T022 [US2] In `tests/test_puzzle.py`, add `test_nav_bounds`: at step 0, `back()` returns `False` and the FEN is unchanged. After `go_to_end()`, `forward()` returns `False`, the FEN is unchanged, and `next_move is None` (US2-4, US2-5, FR-009, FR-012).
- [X] T023 [US2] In `tests/test_puzzle.py`, add `test_nav_go_to_matches_stepping`: for each `i` in `0..4`, `go_to(i)` (starting from any prior step, e.g. after `go_to_end()`) gives the same `board.fen()` and `step` as calling `forward()` `i` times on a fresh puzzle. `go_to_start()`, `go_to_solver_start()` and `go_to_end()` match `go_to(0)`, `go_to(1)` and `go_to(4)`. `go_to(-1)` and `go_to(5)` raise `ValueError` (US2-6, FR-010).
- [X] T024 [US2] In `tests/test_puzzle.py`, add `test_nav_board_is_copy`: pushing a move onto the board returned by `puzzle.board` does not change `puzzle.board.fen()` or `puzzle.step`. Navigating never changes `puzzle.moves` or `puzzle.fen` (Edge Cases, research R3).
- [X] T025 [US2] Run `pytest tests/test_puzzle.py -k nav` and confirm that T019–T024 FAIL.

### Implementation for User Story 2

- [X] T026 [US2] In `src/chess_plus/puzzle.py`, add private navigation state set at the end of construction: `self._board = chess.Board(fen)` (the step is `len(self._board.move_stack)`; no separate counter needed). Add typed, docstringed properties: `step -> int`, `board -> chess.Board` (returns `self._board.copy()`), `next_move -> chess.Move | None` (`moves[step]` if `step < N` else `None`), `previous_move -> chess.Move | None` (`moves[step-1]` if `step > 0` else `None`).
- [X] T027 [US2] In `src/chess_plus/puzzle.py`, implement `forward() -> bool` (push `next_move` if there is one, return whether a move was played) and `back() -> bool` (`self._board.pop()` if `step > 0`, return whether a move was undone). Both are typed and docstringed (FR-009, research R2).
- [X] T028 [US2] In `src/chess_plus/puzzle.py`, implement `go_to(step: int) -> None`: raise `ValueError(f"step: must be in 0..{N}, got {step}")` when outside `0..N`, otherwise call `back()`/`forward()` until it reaches the target. Add `go_to_start()`, `go_to_solver_start()` and `go_to_end()` as one-line wrappers for `go_to(0)`, `go_to(1)` and `go_to(N)`. All typed and docstringed (FR-010).
- [X] T029 [US2] Run `pytest tests/test_puzzle.py` (all green) and `mypy src` (clean).

**Checkpoint**: User Stories 1 and 2 both work.

---

## Phase 5: User Story 3 - Get the moves in SAN (Priority: P3)

**Goal**: Read the puzzle's moves in SAN, independent of the current step.

**Independent Test**: `pytest tests/test_puzzle.py -k san` passes.

### Tests for User Story 3 (write FIRST) ⚠️

- [X] T030 [US3] In `tests/test_puzzle.py`, add `test_san_sample`: `Puzzle.from_csv_row(SAMPLE_ROW).san_moves == ("Kc7", "Ba5+", "b6", "Rxd1")` (US3-1, SC-003).
- [X] T031 [US3] In `tests/test_puzzle.py`, add `test_san_independent_of_step`: for each `i` in `0..4`, `go_to(i)` leaves `san_moves == ("Kc7", "Ba5+", "b6", "Rxd1")` (US3-2, FR-011).
- [X] T032 [US3] Run `pytest tests/test_puzzle.py -k san`. Note: `san_moves` was already computed at load in T015/T016 (research R5), so these tests may pass right away. If they do, confirm they would catch a regression by temporarily breaking the SAN pass in `src/chess_plus/puzzle.py` (e.g. returning UCI strings), seeing them fail, and reverting.

### Implementation for User Story 3

- [X] T033 [US3] (Not needed: T030/T031 passed.) Only if T030/T031 fail: fix the SAN pass in `Puzzle.from_dict` in `src/chess_plus/puzzle.py` so `board.san(move)` is computed before each `push` on a fresh `chess.Board(fen)`, stored as `tuple[str, ...]`. Then rerun `pytest` and `mypy src`.

**Checkpoint**: All user stories work.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T034 [P] Create `CHANGELOG.md` at repo root with a `## 0.1.0 - 2026-10-03` entry: "Added `Puzzle`: load a Lichess puzzle CSV row, step through its moves, and get them in SAN." (Constitution IV).
- [X] T035 [P] Check that every public member of `Puzzle` in `src/chess_plus/puzzle.py` has type hints and a docstring, and that `chess_plus.__all__ == ["Puzzle"]` (Constitution IV).
- [X] T036 Run the quickstart.md validation: `pytest` and `mypy src` both pass, and the 4-line manual check in `specs/001-lichess-puzzle/quickstart.md` prints `('Kc7', 'Ba5+', 'b6', 'Rxd1')` followed by 4 FENs (SC-004).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies. T002 and T003 can run in parallel after T001. T004 comes last.
- **Foundational (Phase 2)**: depends on Setup. Blocks all stories.
- **US1 (Phase 3)**: depends on Foundational.
- **US2 (Phase 4)**: depends on US1. Navigation needs a loaded puzzle (`moves`, `fen`), and the stories share one module and one test file.
- **US3 (Phase 5)**: depends on US1 (SAN is computed at load). T031 also uses `go_to` from US2.
- **Polish (Phase 6)**: depends on all stories.

### Within Each User Story

- Tests are written first and must FAIL before implementation (Constitution II).
- Tests and implementation each live in a single file, so tasks run in sequence within a story.

### Parallel Opportunities

- T002 ∥ T003 (different files)
- T034 ∥ T035 (different files)
- Otherwise none. One module and one test file (by plan design, Principle III) mean the stories can't be worked on in parallel without merge conflicts.

---

## Parallel Example: Setup

```text
Task: "Create src/chess_plus/__init__.py and src/chess_plus/py.typed"   (T002)
Task: "Create tests/test_puzzle.py with shared fixture constants"       (T003)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup → Phase 2 Foundational
2. Phase 3 (US1): tests red → implement → green
3. **STOP and VALIDATE**: the sample row loads and invalid rows raise errors

### Incremental Delivery

1. US1: load and validate (MVP)
2. US2: navigation
3. US3: SAN (mostly already done by US1's load pass; adds tests that lock it in)
4. Polish: changelog, API audit, quickstart check

---

## Notes

- Error format everywhere: `ValueError("<FieldName>: <reason>")` (research R6). No custom exception class.
- No CSV-file reading, filtering, or solution checking (out of scope per spec).
- Commit after each green checkpoint.

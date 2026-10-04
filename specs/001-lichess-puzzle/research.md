# Research: Lichess Puzzle

No NEEDS CLARIFICATION items remained in Technical Context. Decisions below record the
non-obvious choices.

## R1. Parsing a CSV line

- **Decision**: `next(csv.reader([line]))` for text input; mapping input read by header name.
- **Rationale**: stdlib handles quoting; Lichess rows have trailing empty fields (`,,`) that
  `str.split` would also handle, but `csv` is correct if a field is ever quoted.
- **Alternatives**: `str.split(",")` (breaks on quoted fields); pandas (new dependency, rejected).

## R2. Board state at each step

- **Decision**: Keep one `chess.Board` and use `push()` / `pop()` for forward/back; for
  `go_to(i)`, pop or push the difference.
- **Rationale**: python-chess's move stack restores exact state, including castling, en passant
  and counters (SC-002). No re-implementation.
- **Alternatives**: store a FEN per step (extra state, no benefit); rebuild from FEN each step
  (fine but needless).

## R3. Exposing the position

- **Decision**: `board` property returns `self._board.copy()`.
- **Rationale**: Callers mutating the returned board must not corrupt navigation (spec: navigation
  never changes stored data).

## R4. Legality check at load

- **Decision**: Replay all moves on a fresh board at load; raise `ValueError` naming `Moves` on
  the first illegal move. Malformed FEN → `ValueError` naming `FEN`.
- **Rationale**: fail fast, never return a half-built puzzle (FR-006, FR-013).

## R5. SAN

- **Decision**: compute per move with `board.san(move)` then `push`, on a fresh board from the
  FEN, once at load (same pass as the legality check in R4).
- **Rationale**: `variation_san` adds move numbers; per-move `san()` gives the plain list
  `["Kc7", "Ba5+", "b6", "Rxd1"]`. Computing once at load makes it step-independent (FR-011).

## R6. Errors

- **Decision**: plain `ValueError` with message `"<FieldName>: <reason>"`.
- **Rationale**: one caller-visible error type is enough; a custom exception class has no second
  use case yet (Principle III).

## R7. Minimum move count

- **Decision**: require at least 2 moves (setup + one solver move).
- **Rationale**: spec Edge Cases. A header row fails naturally (`Rating` isn't an int, `FEN` is
  invalid).

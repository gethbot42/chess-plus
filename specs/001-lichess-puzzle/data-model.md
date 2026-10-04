# Data Model: Lichess Puzzle

## Puzzle

| Field | Type | Source column | Rule |
|-------|------|---------------|------|
| `puzzle_id` | `str` | PuzzleId | non-empty |
| `fen` | `str` | FEN | must parse as `chess.Board(fen)` |
| `moves` | `tuple[chess.Move, ...]` | Moves | UCI, whitespace-split, ≥ 2, each legal in sequence |
| `rating` | `int` | Rating | int |
| `rating_deviation` | `int` | RatingDeviation | int |
| `popularity` | `int` | Popularity | int (may be negative) |
| `nb_plays` | `int` | NbPlays | int |
| `themes` | `tuple[str, ...]` | Themes | whitespace-split; blank → `()` |
| `game_url` | `str` | GameUrl | as-is |
| `opening_tags` | `tuple[str, ...]` | OpeningTags | whitespace-split; blank → `()` |
| `daily_date` | `datetime.date \| None` | DailyDate | ISO date; blank → `None` |

Tuples instead of lists so the stored data is immutable (spec: navigation never changes data).

### Derived (computed once at load)

- `solver_color: chess.Color` — `not chess.Board(fen).turn`
- `san_moves: tuple[str, ...]` — SAN of each move from the FEN

### Navigation state

- `step: int` in `0..len(moves)`; 0 = row FEN, starts at 0
- private `_board: chess.Board` kept in sync with `step` via `push`/`pop`

### State transitions

```text
step k --forward()--> k+1   (if k < N, returns True; else False, no change)
step k --back()-----> k-1   (if k > 0, returns True; else False, no change)
step k --go_to(i)---> i     (0 <= i <= N, else ValueError)
```

`next_move` = `moves[step]` if `step < N` else `None`;
`previous_move` = `moves[step-1]` if `step > 0` else `None`.

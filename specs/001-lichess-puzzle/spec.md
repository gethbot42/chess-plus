# Feature Specification: Lichess Puzzle

**Feature Branch**: `001-lichess-puzzle`

**Created**: 2026-10-03

**Status**: Draft

**Input**: User description: "I want a Puzzle class. The puzzle class should be able to contain the
data within a Lichess puzzle row. The Lichess puzzle comes in a csv format with the following
header: PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningTags,DailyDate.
Sample: `00sO1,1k1r4/pp3pp1/2p1p3/4b3/P3n1P1/8/KPP2PN1/3rBR1R b - - 2 31,b8c7 e1a5 b7b6 f1d1,998,85,94,293,advantage discoveredAttack master middlegame short,https://lichess.org/vsfFkG0s/black#62,,`.
With puzzles, we should be able to trace through moves in either direction, and convert the
syntax of the moves to san."

## User Scenarios & Testing *(mandatory)*

The users are developers who use the library to work with puzzles from the Lichess puzzle
database.

**Lichess convention**: the row's FEN is the position *before* the opponent's move. The first
move in `Moves` is that opponent's move, which sets up the puzzle. The solver's moves start with
the second move and alternate with the opponent's replies.

### User Story 1 - Load a puzzle from a Lichess row (Priority: P1)

A developer passes one row from the Lichess puzzle CSV to the library and gets back a puzzle
whose fields hold the row's data as meaningful values: numbers as numbers, themes as a list,
moves as a sequence of moves, and blank fields as absent.

**Why this priority**: every other capability depends on having the puzzle data loaded.

**Independent Test**: load the sample row and check every field against the values in the row.

**Acceptance Scenarios**:

1. **Given** the sample row, **When** it is loaded, **Then** the puzzle has ID `00sO1`, rating
   998, rating deviation 85, popularity 94, play count 293, game URL
   `https://lichess.org/vsfFkG0s/black#62`, and the starting position from the FEN.
2. **Given** the sample row, **When** it is loaded, **Then** its themes are `advantage`,
   `discoveredAttack`, `master`, `middlegame` and `short`, in that order, and its moves are
   `b8c7`, `e1a5`, `b7b6` and `f1d1`, in that order.
3. **Given** the sample row, whose OpeningTags and DailyDate are blank, **When** it is loaded,
   **Then** the opening tags are empty and the daily date is absent.
4. **Given** a row with opening tags and a daily date, **When** it is loaded, **Then** the
   opening tags are a list and the daily date is a calendar date.
5. **Given** the sample puzzle, **When** the side to solve is requested, **Then** it is White,
   because Black plays the setup move.

---

### User Story 2 - Step through the puzzle's moves in either direction (Priority: P2)

A developer moves forward and backward through the puzzle's moves one at a time and can read
the board position at every step. This lets them replay or display the puzzle.

**Why this priority**: tracing moves in both directions is the main behavior requested beyond
holding data.

**Independent Test**: load the sample puzzle, step forward through all four moves, then back to
the start, and compare the position at each step with the expected FEN.

**Acceptance Scenarios**:

1. **Given** a newly loaded puzzle, **When** the current position is requested, **Then** it is
   the row's FEN and no moves have been played.
2. **Given** the puzzle at the start, **When** it steps forward once, **Then** the setup move
   `b8c7` has been played and the position is the one the solver must answer.
3. **Given** the puzzle after N forward steps, **When** it steps back N times, **Then** the
   position matches the row's FEN exactly.
4. **Given** the puzzle after its last move, **When** it steps forward, **Then** the position
   does not change and the caller is told no move was made.
5. **Given** the puzzle at the start, **When** it steps back, **Then** the position does not
   change and the caller is told no move was made.
6. **Given** any puzzle, **When** it jumps directly to a step (start, the solver's first turn,
   the end, or a specific index), **Then** the position matches the one reached by stepping
   there one move at a time.

---

### User Story 3 - Get the moves in SAN (Priority: P3)

A developer gets the puzzle's moves in Standard Algebraic Notation (SAN) instead of UCI so
people can read them.

**Why this priority**: it's useful for display, but it builds on stories 1 and 2.

**Independent Test**: load the sample puzzle and compare its moves in SAN with the expected
list.

**Acceptance Scenarios**:

1. **Given** the sample puzzle, **When** its moves are requested in SAN, **Then** the result is
   `Kc7`, `Ba5+`, `b6`, `Rxd1`.
2. **Given** a puzzle at any step, **When** its moves are requested in SAN, **Then** the result
   is the same as at any other step.

---

### Edge Cases

- If a row has the wrong number of fields, a malformed FEN, or a move that is illegal in its
  position, loading fails with an error naming the bad field. Loading never returns a partly
  loaded puzzle.
- If a numeric field (Rating, RatingDeviation, Popularity, NbPlays) isn't an integer, loading
  fails with an error. Popularity can be negative; Lichess's range is -100 to 100.
- If Moves is empty, loading fails, because a puzzle needs at least the setup move and one
  solver move.
- If the row has the CSV header itself, loading fails; headers are not puzzles.
- Themes and OpeningTags fields may contain any amount of whitespace between items. Blank
  fields produce an empty list.
- Navigation never changes the puzzle's stored data. Only the current step changes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The library MUST create a puzzle from one Lichess puzzle CSV row, given either as
  a line of CSV text or as a mapping from header names to values.
- **FR-002**: A puzzle MUST expose every column in the header: PuzzleId, FEN, Moves, Rating,
  RatingDeviation, Popularity, NbPlays, Themes, GameUrl, OpeningTags and DailyDate.
- **FR-003**: Rating, RatingDeviation, Popularity and NbPlays MUST be exposed as integers.
- **FR-004**: Themes and OpeningTags MUST be exposed as ordered lists of tags split on
  whitespace. A blank field MUST give an empty list.
- **FR-005**: DailyDate MUST be exposed as a calendar date when present and as absent when
  blank.
- **FR-006**: Moves MUST be exposed as an ordered sequence of moves. Every move MUST be checked
  for legality in sequence from the FEN when the puzzle is loaded.
- **FR-007**: A puzzle MUST report which side solves it, meaning the side that does not play the
  first move.
- **FR-008**: A puzzle MUST track a current step from 0, the row's FEN, to N, after every move,
  and MUST expose the position at that step.
- **FR-009**: A puzzle MUST support stepping forward and backward by one move. A step past
  either end MUST leave the position unchanged and tell the caller that no move was made.
- **FR-010**: A puzzle MUST support jumping directly to the start, to the solver's first turn
  (step 1), to the end, or to any valid step index. An index outside 0..N MUST raise an error.
- **FR-011**: A puzzle MUST expose its full move list in SAN, computed from the FEN regardless
  of the current step.
- **FR-012**: A puzzle MUST expose the move that the next forward step would play and the move
  that the next backward step would undo. When there is no such move, it MUST report none.
- **FR-013**: Loading MUST fail with a descriptive error that names the bad field when the data
  is invalid. See the Edge Cases section.

### Key Entities

- **Puzzle**: one Lichess puzzle. It holds the identifier, starting position, move sequence,
  rating data (rating, deviation, popularity, play count), themes, source game URL, opening
  tags and optional daily date, plus a current step used for navigation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The sample row loads, and 100% of its fields match the values shown in the row.
- **SC-002**: For any valid puzzle, stepping forward N times and then back N times returns a
  position identical to the original FEN, including side to move, castling rights, en passant
  square and move counters.
- **SC-003**: The sample puzzle's SAN output is exactly `Kc7 Ba5+ b6 Rxd1`.
- **SC-004**: A developer who knows the Lichess CSV format can load a puzzle and step through
  it in 5 lines of code or fewer.
- **SC-005**: 100% of the invalid-row cases in Edge Cases give an error instead of a puzzle.

## Assumptions

- The scope is one row per puzzle. Reading or streaming the whole Lichess CSV file and
  filtering puzzles (for example by theme or rating) are out of scope. They can be added in a
  later feature.
- The header order is the one given above, including DailyDate. A mapping input uses the header
  names as keys.
- DailyDate uses ISO format (YYYY-MM-DD) when present.
- Checking whether a user's attempted move solves the puzzle is out of scope. This feature
  covers replay and display only.
- Following the constitution, board state, move legality and SAN conversion come from
  python-chess. They are not re-implemented.

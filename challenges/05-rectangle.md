# Challenge 5: Rectangle

**Difficulty:** intermediate
**Theme:** nested loops / art

## Problem

Print a solid rectangle: 3 rows of 5 `#` characters, each row on its own line.

## Contract

- Input: none.
- Output (exactly):
  ```
  #####
  #####
  #####
  ```
  Each of the three lines ends with a newline (eighteen bytes total: three rows of
  five `#` plus three newlines).

## Constraints

- Use nested loops — an outer loop for the 3 rows, an inner loop for the 5 `#`.
- `#` is ASCII 35; newline is ASCII 10.

## Hints

- Keep two constant cells: one holding `#` (35) and one holding newline (10), like
  [`programs/art/box.bf`](../programs/art/box.bf) does with its star and newline.
- The outer counter is 3; each pass prints 5 `#` then one newline.
- Printing five `#` is itself a tiny inner loop: a counter of 5 that prints the
  `#` cell and counts down. See [tutorials/06-art-and-zen.md](../tutorials/06-art-and-zen.md).
- Check yourself:
  ```bash
  python interpreters/bf_interpreter.py mine.bf
  ```

## Stretch

Make it a hollow rectangle (border only), like a wider version of `box.bf`, or
read a digit and print that many rows.

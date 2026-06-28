# Challenge 1: Initials

**Difficulty:** beginner
**Theme:** fixed output, no input

## Problem

Print the two letters `BF` followed by a newline.

## Contract

- Input: none.
- Output (exactly):
  ```
  BF
  ```
  That is the characters `B`, `F`, newline — three bytes total
  (`66`, `70`, `10`).

## Constraints

- Output exactly those three bytes, nothing more.

## Hints

- `B` is ASCII 66, `F` is 70, newline is 10.
- Build one cell up to 66 and print, then adjust the same cell to 70 and print —
  you do not need a separate cell per character.
- A multiplication loop (`<count>[>...<-]`) reaches 66 with far fewer instructions
  than 66 plus signs. See [tutorials/03-loops.md](../tutorials/03-loops.md).
- Check yourself:
  ```bash
  python interpreters/bf_interpreter.py mine.bf
  ```
- Then golf it with `python interpreters/bf_optimizer.py mine.bf --stats`.

## Stretch

Print your own initials instead, then the whole repository name, `BF`.

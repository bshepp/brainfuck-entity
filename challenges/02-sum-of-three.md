# Challenge 2: Sum of Three

**Difficulty:** beginner
**Theme:** input + arithmetic

## Problem

Read three single ASCII digits and print their sum as one digit.

## Contract

- Input: three digit characters, e.g. `234`.
- Output: one digit character. For input `234`, print `9` (2 + 3 + 4).
  For input `123`, print `6`.

## Constraints

- Assume the three digits sum to 9 or less (single-digit result).
- Print only the result digit — no newline unless you want one (the examples have
  none).

## Hints

- Each typed digit arrives offset by 48. Three of them carry an extra `3 * 48`.
- The move pattern `[->+<]` (or `[<+>-]`) pours one cell into another; use it to
  gather all three onto one cell. See [tutorials/04-input.md](../tutorials/04-input.md).
- To print the answer as a character, the result cell must hold `sum + 48`, so
  remove the right amount of the accumulated offset first.
- Check yourself:
  ```bash
  python interpreters/bf_interpreter.py mine.bf "234"   # expect 9
  python interpreters/bf_interpreter.py mine.bf "123"   # expect 6
  ```

## Stretch

Extend it to add four digits, or handle a two-digit result (much harder — it needs
printing a number bigger than 9).

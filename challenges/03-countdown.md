# Challenge 3: Countdown

**Difficulty:** intermediate
**Theme:** loops

## Problem

Print the digits from `9` down to `0`, then a newline.

## Contract

- Input: none.
- Output (exactly):
  ```
  9876543210
  ```
  followed by a newline (eleven bytes total).

## Constraints

- Produce the ten digits in descending order plus one trailing newline.
- Use a loop — a hand-typed run of ten print statements is the thing to avoid.

## Hints

- This is [`programs/hello-world/digits.bf`](../programs/hello-world/digits.bf)
  turned around: start the character cell at `9` (ASCII 57) and step **down** each
  pass instead of up.
- A counter cell of 10 drives the loop; the character cell starts at 57.
- The newline (ASCII 10) is a separate print after the loop ends.
- Check yourself:
  ```bash
  python interpreters/bf_interpreter.py mine.bf
  ```
- Profile the loop with `python tools/bf_profiler.py mine.bf` — the hottest loop
  should run ten times.

## Stretch

Print `0` up to `9` and then `9` down to `0` on two lines.

# Brainfuck Challenges

Self-directed exercises. Each challenge states an exact output to produce; your
job is to write a `.bf` program that produces it. No solutions are committed here —
the point is to earn them.

Work through the [tutorials](../tutorials/) first if any command is unfamiliar.

## How to attempt a challenge

1. Write your program, e.g. `mine.bf`.
2. Check the brackets and structure:
   ```bash
   python tools/bf_validator.py mine.bf
   ```
3. Run it (with input where the challenge calls for it):
   ```bash
   python interpreters/bf_interpreter.py mine.bf
   python interpreters/bf_interpreter.py mine.bf "234"
   ```
   Add `--max-steps 100000` while experimenting so a stray infinite loop aborts
   instead of hanging.
4. Compare your output to the challenge's stated expected output, exactly —
   including spaces and the trailing newline.
5. Golf it: try to beat your own instruction count.
   ```bash
   python tools/bf_profiler.py mine.bf      # total steps, hot loops
   python interpreters/bf_optimizer.py mine.bf --stats   # source size before/after
   ```

## Conventions

- Where a challenge reads digits, inputs are single ASCII digits and results stay
  in the single-digit range unless stated otherwise.
- "Print X" means produce exactly X on standard output — no extra characters.
- A trailing newline is the ASCII 10 byte; include it only when the expected
  output shows one.

## The challenges

| # | Title | Theme | Difficulty |
|---|---|---|---|
| 1 | [Initials](01-initials.md) | fixed output | beginner |
| 2 | [Sum of Three](02-sum-of-three.md) | input + arithmetic | beginner |
| 3 | [Countdown](03-countdown.md) | loops | intermediate |
| 4 | [Shout](04-shout.md) | input loop + ASCII | intermediate |
| 5 | [Rectangle](05-rectangle.md) | nested loops / art | intermediate |

A good order is top to bottom, but each stands alone.

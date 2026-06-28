# Brainfuck Tutorials

A progressive path from "what is a tape?" to writing your own loops, input
handling, and ASCII art — taught entirely through programs that already live in
this repository and pass the test suite.

## How to run any example

```bash
python interpreters/bf_interpreter.py programs/hello-world/hello.bf
# with input:
python interpreters/bf_interpreter.py programs/mathematical/add_two_numbers.bf "35"
# watch it step (first 100 steps):
python interpreters/bf_interpreter.py programs/hello-world/hello.bf --debug
# guard against runaway loops while you experiment:
python interpreters/bf_interpreter.py myprogram.bf --max-steps 100000
```

You can also paste snippets straight into the REPL, where state persists between
lines:

```bash
python interpreters/bf_interpreter.py --repl
```

## The learning path

1. [The Tape](01-the-tape.md) — memory, the pointer, and the eight commands.
2. [Output](02-output.md) — `+ - .`, ASCII, and printing your first character.
3. [Loops](03-loops.md) — `[ ]`, the clear loop, and the multiplication loop.
4. [Input](04-input.md) — `,`, the echo loop, and single-digit arithmetic.
5. [Conditionals](05-conditionals.md) — using loops as if/else and flags.
6. [Art and Zen](06-art-and-zen.md) — nested loops, ASCII art, and fixed text.

When you are ready to build your own, head to the [challenges](../challenges/).

## The eight commands at a glance

| Command | Meaning |
|---|---|
| `>` | move the pointer right |
| `<` | move the pointer left |
| `+` | increment the byte under the pointer |
| `-` | decrement the byte under the pointer |
| `.` | output the byte under the pointer |
| `,` | read one byte of input under the pointer |
| `[` | if the byte is zero, jump past the matching `]` |
| `]` | if the byte is nonzero, jump back to the matching `[` |

Everything else in a `.bf` file is a comment — the interpreter ignores any
character that is not one of these eight.

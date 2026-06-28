# 3. Loops

A loop is a pair of brackets:

- `[` — if the current cell is **zero**, jump forward past the matching `]`.
- `]` — if the current cell is **nonzero**, jump back to the matching `[`.

In plain words: *"while the current cell is not zero, repeat what is between the
brackets."* The cell the brackets test is whichever one the pointer is on when
control reaches the bracket.

## The clear loop

The most common idiom in all of brainfuck:

```text
[-]
```

"While the cell is nonzero, subtract one." It runs the cell straight down to 0 —
a reliable way to reset a cell no matter what it held.

```bash
python interpreters/bf_interpreter.py --repl
bf> +++++[-]
bf> .memory
```

The cell ends at 0.

## The multiplication loop

Loops let one cell drive changes to another. This is how you build large values
without huge runs of `+`:

```text
++++++++[>++++++++<-]
```

Read it as a multiplication: cell 0 starts at 8 (the outer count). Each pass adds
8 to cell 1 and subtracts 1 from cell 0. After 8 passes, cell 0 is 0 (the loop
ends) and cell 1 holds `8 * 8 = 64`. The shape is:

```text
<count>[ >  <add to neighbor>  <  - ]
```

You saw this in the previous lesson to reach 65 for `A`.

## Loops that print as they go

Combine a counter with output and you can print a whole sequence from a tiny
program. [`programs/hello-world/digits.bf`](../programs/hello-world/digits.bf)
prints `0123456789` with a single ten-step loop, and
[`programs/hello-world/alphabet.bf`](../programs/hello-world/alphabet.bf) prints
`A` through `Z` the same way:

```bash
python interpreters/bf_interpreter.py programs/hello-world/digits.bf
python interpreters/bf_interpreter.py programs/hello-world/alphabet.bf
```

Open `digits.bf` and find the loop `[>.+<-]`: print the character cell, step it up
by one, return, and count down. Ten passes, ten digits.

The classic [`programs/hello-world/hello.bf`](../programs/hello-world/hello.bf)
uses one setup loop to seed several cells at once before printing — read its
comments to see the tape plan.

## Checklist

- `[` and `]` mean "repeat while the current cell is nonzero."
- `[-]` clears a cell to zero.
- `<count>[>...<-]` multiplies/seeds a neighbor cell — the workhorse pattern.

Next: [Input](04-input.md) — letting the outside world into the tape.

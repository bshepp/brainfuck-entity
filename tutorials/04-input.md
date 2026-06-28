# 4. Input

One command brings the outside world onto the tape:

- `,` reads one byte of input and stores it in the current cell.

The byte is whatever character was typed or piped in — again as its ASCII number.
Typing `5` stores 53 (the ASCII code for the digit five), not 5. That distinction
is the source of most early confusion, so keep it in mind.

In this interpreter, when there is no more input, `,` stores 0. That gives loops a
natural way to stop at end of input.

## The echo loop

The smallest interesting input program copies input to output:

```text
,[.,]
```

Read it: read one byte; while it is nonzero, print it and read the next. Save
`,[.,]` as `echo.bf` and pass input as the second argument:

```bash
python interpreters/bf_interpreter.py echo.bf "Hi there"
```

It echoes the characters until the input runs out (when `,` reads 0 and the loop
ends). With no input argument the interpreter reads from standard input instead,
so `echo "Hi there" | python interpreters/bf_interpreter.py echo.bf` works too.

## From ASCII digits to numbers

To do arithmetic on a typed digit, remember it arrives offset by 48 (`0` is 48).
Two typed digits both carry that offset, so when you add them you must remove the
extra 48 before printing the answer as a character.

[`programs/mathematical/add_two_numbers.bf`](../programs/mathematical/add_two_numbers.bf)
reads two digits, adds them, and prints the sum (for sums of 9 or less):

```bash
python interpreters/bf_interpreter.py programs/mathematical/add_two_numbers.bf "35"
```

It prints `8`. The new library programs
[`multiply.bf`](../programs/mathematical/multiply.bf) and
[`subtract.bf`](../programs/mathematical/subtract.bf) use the same idea — strip
the offset, do the arithmetic, add 48 back to print a single-digit result:

```bash
python interpreters/bf_interpreter.py programs/mathematical/multiply.bf "23"
python interpreters/bf_interpreter.py programs/mathematical/subtract.bf "73"
```

## A useful trick: moving a value

The pattern `[->+<]` empties the current cell into its right neighbor (add to the
neighbor, subtract here, until here is zero). `add_two_numbers.bf` uses exactly
this to pour the second digit onto the first. Moving and copying values between
cells is the heart of every larger program.

## Checklist

- `,` reads one byte into the current cell; at end of input it stores 0.
- Typed digits are offset by 48 — subtract it to compute, add it back to print.
- `,[.,]` echoes input; `[->+<]` moves a value to the next cell.

Next: [Conditionals](05-conditionals.md) — making decisions with loops.

# 5. Conditionals

Brainfuck has no `if` keyword. It does not need one — a loop that runs at most
once *is* an if.

## The "if nonzero" pattern

```text
<cell>[ <body> <cell>[-] ]
```

If the cell is zero, the body is skipped entirely. If it is nonzero, the body
runs; clearing the cell with `[-]` before the `]` guarantees the loop does not
repeat. So the body runs **once when the cell is nonzero, never when it is zero** —
that is an `if`.

## The if/else pattern with a flag

Real branching needs both arms. The trick is a second cell used as an "else flag":

1. Set an else-flag cell to 1.
2. In the "if" branch (the value was nonzero), do the work *and* clear the flag.
3. Then test the flag: if it is still 1, the value was zero, so run the "else"
   branch.

This is precisely how
[`programs/games/guess_the_number.bf`](../programs/games/guess_the_number.bf)
decides between "wrong" and "right", and how the new
[`programs/games/secret_knock.bf`](../programs/games/secret_knock.bf) chooses
between printing a dot (wrong) and a bang (correct):

```bash
python interpreters/bf_interpreter.py programs/games/secret_knock.bf "147"
```

It prints `..!` — two wrong knocks, then the match. Open the file and follow the
two bracketed branches around the `difference` and `branch flag` cells.

## Testing a property: even or odd

Sometimes the decision is about a number's property rather than equality.
[`programs/games/even_or_odd.bf`](../programs/games/even_or_odd.bf) reads a digit
and flips a flag once per unit; whichever flag survives says even or odd:

```bash
python interpreters/bf_interpreter.py programs/games/even_or_odd.bf "7"
```

It prints `O`. Try `4` and you get `E`.

## Comparing two values

Equality is easy: subtract one from the other and test for zero (the games above).
Full "is A greater than B" comparisons are possible but fiddly in raw brainfuck —
a good thing to attempt once you are comfortable, and a reason the library leans on
equality-based games.

## Checklist

- A loop that clears its own cell runs at most once — that is an `if`.
- if/else uses a separate flag cell: clear it in the "if" arm, then test it.
- Equality is "subtract and test for zero"; ordering comparisons are advanced.

Next: [Art and Zen](06-art-and-zen.md) — nesting loops to make shapes and text.

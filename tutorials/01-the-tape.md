# 1. The Tape

Brainfuck has exactly one data structure: a long row of memory cells called the
**tape**. In this interpreter the tape has 30,000 cells, each holding one byte
(a number from 0 to 255). Every cell starts at 0.

A single **pointer** marks the "current" cell. You can only ever read or change
the cell the pointer is on. To work with another cell, you move the pointer.

```
cells:  [ 0 ][ 0 ][ 0 ][ 0 ] ...
pointer:  ^
```

## Moving the pointer

- `>` moves the pointer one cell to the right.
- `<` moves the pointer one cell to the left.

So `>>>` lands you on cell 3, and `<` steps back to cell 2.

```
>>>      pointer now on cell 3
[ 0 ][ 0 ][ 0 ][ 0 ]
                ^
```

Nothing is printed yet — moving the pointer changes *where* you are, not what
the world sees. Computation in brainfuck is the quiet rearrangement of state;
output is a separate act (the next lesson).

## See it for yourself

The interpreter can show you the tape around the pointer. Try the debug view on
any program and read the final memory state it prints:

```bash
python interpreters/bf_interpreter.py programs/hello-world/hello.bf --debug
```

You will see the address row, the value row, and a `^^` marker under the current
cell — exactly the mental model above.

## Mental model checklist

- One tape, many cells, all starting at 0.
- One pointer; you act only on the cell it sits on.
- `>` and `<` move; they never change a cell's value.

Next: [Output](02-output.md) — turning numbers in cells into characters on screen.

# 2. Output

A cell holds a number. The screen wants characters. The bridge between them is
**ASCII**: every character has a number. `A` is 65, `a` is 97, a space is 32, and
a newline is 10.

Two commands change a cell's value, and one prints it:

- `+` adds 1 to the current cell.
- `-` subtracts 1 from the current cell.
- `.` outputs the current cell as a character (it does not change the cell).

## Your first character

To print `A`, the current cell needs to hold 65, then we print it. The blunt way
is sixty-five plus signs followed by a dot. The interpreter does not care how you
arrive at 65 — only what the cell holds when `.` runs.

A tidier way uses a helper cell and a loop (you will learn loops fully in the
next lesson, but here is the shape):

```text
++++++++[>++++++++<-]>+.
```

Run it:

```bash
python interpreters/bf_interpreter.py --repl
bf> ++++++++[>++++++++<-]>+.
```

It prints `A`. The pattern set cell 1 to `8 * 8 = 64`, then `>+` nudged it to 65,
then `.` printed it.

## Printing more than one character

After printing, the cell still holds its value. Adjust and print again:

```text
++++++++[>++++++++<-]>+.+.
```

This prints `AB` — `.` shows `A` (65), `+` makes it 66, `.` shows `B`.

## A real program

Open [`programs/hello-world/simple_hello.bf`](../programs/hello-world/simple_hello.bf).
It builds each letter of `Hello World!` and prints it. Watch it run:

```bash
python interpreters/bf_interpreter.py programs/hello-world/simple_hello.bf
```

Notice the rhythm: set a value, print, adjust to the next character, print. That
is all output ever is.

## Checklist

- Characters are numbers (ASCII): `A`=65, space=32, newline=10.
- `+`/`-` change the current cell; `.` prints it without changing it.
- Print several characters by adjusting the same cell between dots.

Next: [Loops](03-loops.md) — so you never have to type sixty-five plus signs.

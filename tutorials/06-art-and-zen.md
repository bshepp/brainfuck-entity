# 6. Art and Zen

With the tape, output, loops, input, and conditionals in hand, you can make
brainfuck draw and speak. This final lesson is about composition — putting loops
inside loops and planning the tape.

## Nested loops draw shapes

A loop inside a loop gives you rows and columns. The outer loop counts rows; the
inner loop prints a row. [`programs/art/triangle.bf`](../programs/art/triangle.bf)
grows the inner count each pass to make a staircase of stars:

```bash
python interpreters/bf_interpreter.py programs/art/triangle.bf
```

```
*
**
***
****
*****
```

[`programs/art/box.bf`](../programs/art/box.bf) keeps three constant cells — a
star, a space, and a newline — and just prints them in the right order to draw a
bordered box. Sometimes the elegant move is *not* a clever loop but a clean tape
layout:

```bash
python interpreters/bf_interpreter.py programs/art/box.bf
```

The older [`programs/art/mandala.bf`](../programs/art/mandala.bf) repeats a
patterned row with a single outer loop — study how it clears its scratch cells
between symbols so each row starts clean.

## Fixed text without endless plus signs

Printing a fixed sentence efficiently is its own small art. Instead of building
each letter from zero, seed one cell near the middle of the alphabet's codes and
nudge up or down to the next letter. The two koans do exactly this:
[`less_is_more.bf`](../programs/philosophy/less_is_more.bf) and
[`empty_is_full.bf`](../programs/philosophy/empty_is_full.bf) use one setup loop
to put roughly 100 in a "letters" cell and roughly 30 in a "space and newline"
cell, then walk between characters with short adjustments:

```bash
python interpreters/bf_interpreter.py programs/philosophy/less_is_more.bf
python interpreters/bf_interpreter.py programs/philosophy/empty_is_full.bf
```

Two cells, two ranges, small steps — far fewer instructions than building every
letter from zero.

## Tools that help you compose

- Validate structure before running: `python tools/bf_validator.py myprogram.bf`
- Profile hot loops and instruction counts: `python tools/bf_profiler.py myprogram.bf`
- Shrink your code: `python interpreters/bf_optimizer.py myprogram.bf --stats`

## Where to go next

You now know every command and every core pattern: the tape, output, loops,
input, conditionals, and composition. The [challenges](../challenges/) put them to
work — each one names an exact output to aim for, and the tools above will tell you
whether you hit it and how tightly.

> *In the reduction of all computation to eight operations, we find not limitation
> but liberation.*

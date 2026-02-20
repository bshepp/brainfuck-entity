Guess the secret digit (the answer is 5)
Reads one digit at a time until correct
Prints N for wrong and Y for correct

cell 0: play flag
cell 1: multiplication temp
cell 2: target ASCII value (53)
cell 3: user input then difference
cell 4: if else flag
cell 5 and 6: character generation scratch

Start game
+
[
    Clear play flag
    -

    Set target to ASCII 53 (the digit five)
    >+++++[>++++++++++<-]>+++

    Read a digit
    >,

    Subtract target from input
    <[->-<]

    Move to difference cell
    >

    Set if else flag
    >[-]+
    <

    Wrong guess branch (difference was nonzero)
    [
        [-]
        >-
        >++++++++[>++++++++++<-]>--.
        [-]<[-]
        >++++++++++.
        [-]
        <<<<<<
        +
        >>>
    ]

    Correct guess branch (difference was zero so flag is still set)
    >[
        -
        >+++++++++[>++++++++++<-]>-.
        [-]<[-]
        >++++++++++.
        [-]
        <<<<<<
        >>>>
    ]

    Return to cell 0
    <<<<
]

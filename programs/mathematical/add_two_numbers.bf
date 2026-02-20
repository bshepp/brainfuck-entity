Read two single ASCII digits and print their sum
Only works for results 0 through 9

,                           read first digit (ASCII)
>,[<+>-]                    read second digit and add to first
<                           back to result cell
------------------------------------------------.   subtract 48 to undo double ASCII offset then print

# Cleaning decisions

After the audit I looked at the odd rows and decided what to do with each type. I apply
these rules in order with `python -m src.clean`, and the counts are in
`cleaning_summary.json`.

| Rule | Rows affected | What I did and why |
|---|---:|---|
| Same person at the same meet more than once | 659 | Removed all of them, because I can't tell which entry is right |
| Third attempt over 450 kg | 2 | Removed, because 500 kg at 92.5 kg bodyweight and a 550 kg women's attempt are far beyond any raw record |
| Age under 10 | 344 | Kept, because nearly all are real youth lifters in youth divisions with light bodyweights |
| Bodyweight under 30 kg or over 250 kg | 113 | Kept, because the light ones are children (most are in the 30 kg class) and the one 260 kg lifter in the 120+ class is plausible |

That leaves **461,828 lifts**, and 60.96% of third attempts are still successful, the same
as before cleaning to two decimal places.

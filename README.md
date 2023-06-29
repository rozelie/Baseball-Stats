# COBP

This project calculates Conditional On-Base Percentage (COBP) for MLB
players based on [retrosheet.org](retrosheet.org) event data.

Data is dynamically downloaded based on user's input of a team and a year.

Interface is built with the `streamlit` library.

# Usage
```shell
make setup
make run
```

# Definitions 
## OBP
`On-Base % (OBP)` = how frequently batter reaches base per plate appearance

- Includes: hits (H), walks (BB), and hit by pitches (HBP) in the numerator
- Does not include: errors, fielder’s choice, or dropped third strike
- Sacrifice bunts (SB) are removed from the numerator but sacrifice flies (SF) are
included in the denominator.
- Denominator equals: `At-Bats (AB) + Walks (BB) + Hit by Pitches (HBP) + Sacrifice
Flies (SF)`
- `OBP = (H + BB + HBP) / (AB + BB + HBP + SF)`

## COBP
`Conditional On-Base % (COBP)` = the OBP when any batter(s) reach(es) base in the
same inning.
- Includes same factors as OBP but requires other batter(s) (or the current batter) to reach base in the same inning.
- If no one gets on base in a specific inning, those At-Bats are not included in the COBP calculation.

# Data
- [Retrosheet Play-by-Play Data Files (Event Files)](https://www.retrosheet.org/game.htm)
  - `.evl` files: event files ([file format description](https://www.retrosheet.org/eventfile.htm))
    - download for 2022 data: https://www.retrosheet.org/events/2022eve.zip
  - [data/2022CHN.EVN](data/2022CHN.EVN)
    - Cub's 2022 data

# Todo
- test seasonal calculations
- test aggregated team stats
- test OPS
- test COPS
- calculate correlations
  - test COBPs player correlations
  - correlate COBPs with runs scored
    - tests
  - correlate COBPs with wins
    - tests
  - calculate SOPS: SOBP + OPS
  - add list of sorted correlations to correlations display
- track where each player batted in the line-up when they got on base
- if available from a different data source, correlate each player’s COBP with their respective WAR values (Wins Above Replacement)


### Credits
- Project skeleton generated via `cookiecutter https://github.com/rozelie/Python-Project-Cookiecutter`
# Baseball OBP and COBP

This project calculates On-Base Percentage (OBP) and Conditional On-Base Percentage (COBP) for MLB
players based on [retrosheet.org](retrosheet.org) event data.

Interface is built with the `streamlit` library - current usage only works for a single, local data set.

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
- Includes same factors as OBP but requires other batter(s) to reach base in the same
inning (either before or after the current batter).
- If no one gets on base in a specific inning, those At-Bats are not included in the
COBP calculation.

# Data
- [Retrosheet Play-by-Play Data Files (Event Files)](https://www.retrosheet.org/game.htm)
  - `.evl` files: event files ([file format description](https://www.retrosheet.org/eventfile.htm))
    - download for 2022 data: https://www.retrosheet.org/events/2022eve.zip
  - [data/2022CHN.EVN](data/2022CHN.EVN)
    - Cub's 2022 data

# Todo
- calculate on-base percentages (OBP) conditional on-base percentage (COBP) for one team, for one season
    - ✅ data retrieval, retrosheet.org suggested
    - ✅ calculate per-game OBP
    - calculate seasonal OBP
    - calculate per-game COBP
    - calculate seasonal COBP
    - calculate correlations
- future work
    - track where each player batted in the line-up when they got on base
    - if available from a different data source, correlate each player’s COBP with their respective WAR values (Wins Above Replacement)
    - provide user-friendly interface, allowing selection of a particular team over specified seasons

### Credits
- Project skeleton generated via `cookiecutter https://github.com/rozelie/Python-Project-Cookiecutter`
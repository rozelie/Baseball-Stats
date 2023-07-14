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
- stats
  - per team per season
    - mean, median, min, max, std. dev of all other stats
    - win percentage
    - efficiency: `R / H + BB + HBP`
  - Wins Above Replacement (WAR)
    - can find from other sources
  - LOOP
    - OBP when lead-off an inning
    - only considered when another player gets an on-base in the same inning
  - runs (R)
  - RBI
  - runs created (RC)
    - SB: stolen bases
    - CS: caught stealing
    - SP = `TB / AB`, TB = `AB * SP`
    - RC: `((0.55 * SB) + TB) * (BB - CS + H) / AB + BB`

  
- correlations
  - correlate COBPs with runs scored
  - correlate COBPs with wins
  - calculate SOPS: SOBP + OPS
  - add list of sorted correlations to correlations display
  - calculate correlation matrix between all other stats at the player and team level for a season

- deployment
  - publish yearly data to S3 to be able to be retrieved in deployed instance
  - build out Terraform infrastructure

- testing
  - seasonal calculations
  - aggregated team stats
  - OPS
  - COPS
  - COBPs player correlations

### Credits
- Project skeleton generated via `cookiecutter https://github.com/rozelie/Python-Project-Cookiecutter`
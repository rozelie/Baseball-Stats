# Baseball Stats

# Data
- [Retrosheet Play-by-Play Data Files (Event Files)](https://www.retrosheet.org/game.htm)
  - `.evl` files: event files ([file format description](https://www.retrosheet.org/eventfile.htm))
    - download for 2022 data: https://www.retrosheet.org/events/2022eve.zip
  - [data/2022CHN.EVN](data/2022CHN.EVN)
    - Cub's 2022 data
- [Team Abbreviation Lookup](https://www.retrosheet.org/TEAMABR.TXT)

# Todo
- calculate on-base percentages (OBP) conditional on-base percentage (COBP) for one team, for one season
    - data retrieval, retrosheet.org suggested
    - calculate OBP
    - calculate COBP
    - calculate correlations
- future work
    - track where each player batted in the line-up when they got on base
    - If available from a different data source, correlate each player’s COBP with their respective WAR values (Wins Above Replacement)

### Credits
- Project skeleton generated via `cookiecutter https://github.com/rozelie/Python-Project-Cookiecutter`
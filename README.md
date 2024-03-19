# COBP
Calculates Conditional On-Base Percentage (COBP) and other custom statistics for MLB
teams and players based on [retrosheet.org](retrosheet.org) event data.

Through correlating these custom statistics, a more optimal batting lineup can be achieved.

# Stats
- `sp`: Slugging Percentage
- `ba`: Batting Average
- `runs`: Runs
- `rbis`: Runs Batted In

- On-Base Percentages
- `obp`: On-Base Percentage

- `cobp`: Conditional On-Base Percentage
  - include only plays where there is another on-base in the inning
  - `csp`: Conditional Slugging Percentage
  - `cops`: `cobp` + `csp`

- `sobp`: Sequential On-Base Percentage
  - include only plays where there is another on-base before the play in the inning, excluding leadoff plays
  - `ssp`: Sequential Slugging Percentage
  - `sops`: `sobp` + `ssp`

- `loop`: Leadoff On-Base Percentage
  - include only leadoff plays that have another on-base in the inning
  - `lsp`: Leadoff Slugging Percentage
  - `loops`: `loop` + `lsp`

# Technologies
- Languages: Python 3.11
- UI: [Streamlit](https://streamlit.io/)
- Build/Deployment: Docker, Github Actions, AWS, Terraform (WIP)
- Testing: pytest, pytest-mock
- Formatting: black, isort
- Linting: mypy, ruff

# Usage
```shell
make setup  # creates virtualenv and installs required packages
make run    # runs Streamlit application
```

# Data
- [Retrosheet Play-by-Play Data Files (Event Files)](https://www.retrosheet.org/game.htm)
  - `.evl` files: event files ([file format description](https://www.retrosheet.org/eventfile.htm))

# Development
- testing: `make test`
- formatting: `make format`
- linting: `make lint`

# Todo

## For MVP
- Add baseball-reference link to results
  - single game URL format: https://www.baseball-reference.com/boxes/KCA/KCA202207250.shtml
  - season URL format: https://www.baseball-reference.com/teams/CHC/2022.shtml
- fix csv numerical values

## Later
- documentation
  - define and describe statistics in class docstrings
    - dynamically update README.md with statistics defintions

- stats
  - per team per season
    - win percentage
    - efficiency: `R / H + BB + HBP`
  - Wins Above Replacement (WAR)
    - can find from other sources
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

- testing
  - seasonal calculations
  - aggregated team stats
  - OPS
  - COPS
  - COBPs player correlations

- cosmetic
  - update red/green correlation colors to be the cell background with white text

# Credits
- Project skeleton generated via `cookiecutter https://github.com/rozelie/Python-Project-Cookiecutter`

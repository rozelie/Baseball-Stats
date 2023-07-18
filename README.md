# COBP
Calculates Conditional On-Base Percentage (COBP) and other custom statistics for MLB
teams and players based on [retrosheet.org](retrosheet.org) event data.

Through correlating these custom statistics, a more optimal batting lineup can be achieved.

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
- documentation
  - define and describe statistics in class docstrings
    - dynamically update README.md with statistics defintions

- stats
  - per team per season
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

# Credits
- Project skeleton generated via `cookiecutter https://github.com/rozelie/Python-Project-Cookiecutter`

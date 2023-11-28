from collections import defaultdict
from pathlib import Path
import pandas as pd


discrepancy_dir = Path("/tmp/retrosheet/discrepancies")
year_to_df = defaultdict(pd.DataFrame)

for path in discrepancy_dir.iterdir():
    if path.is_file():
        year = path.name[0:4]
        year_to_df[year] = pd.concat([year_to_df[year], pd.read_csv(path)])

for year in sorted(year_to_df, reverse=True):
    df = year_to_df[year]
    print(f"{year}: {len(df)}")
from dataclasses import dataclass, field

import requests
from requests import Session


@dataclass
class BaseballReferenceClient:
    base_url: str = "https://www.baseball-reference.com"
    _session: Session = field(init=False)

    def __post_init__(self):
        self._session = Session()

    def get_box_score_html(self, game_id: str) -> str:
        team_id = "".join([c for c in game_id if c.isalpha()])
        response = requests.get(f"{self.base_url}/boxes/{team_id}/{game_id}.shtml")
        response.raise_for_status()
        return response.text

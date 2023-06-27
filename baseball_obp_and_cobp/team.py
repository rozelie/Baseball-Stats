"""Team data."""
from enum import Enum


class TeamLocation(Enum):
    """Team location, as defined in Retrosheet spec."""

    VISITING = 0
    HOME = 1


class Team(Enum):
    """Team identifiers, as defined in Retrosheet spec.

    https://www.retrosheet.org/TEAMABR.TXT
    """

    ANAHEIM_ANGELS = "ANA"
    ARIZONA_DIAMONDBACKS = "ARI"
    ATLANTA_BRAVES = "ATL"
    BALTIMORE_ORIOLES = "BAL"
    BOSTON_RED_SOX = "BOS"
    CHICAGO_CUBS = "CHN"
    CHICAGO_WHITE_SOX = "CHA"
    CINCINNATI_REDS = "CIN"
    CLEVELAND_INDIANS = "CLE"
    COLORADO_ROCKIES = "COL"
    DETROIT_TIGERS = "DET"
    HOUSTON_ASTROS = "HOU"
    KANSAS_CITY_ROYALS = "KCA"
    LOS_ANGELES_DODGERS = "LAN"
    MIAMI_MARLINS = "MIA"
    MILWAUKEE_BREWERS = "MIL"
    MINNESOTA_TWINS = "MIN"
    NEW_YORK_METS = "NYN"
    NEW_YORK_YANKEES = "NYA"
    OAKLAND_ATHLETICS = "OAK"
    PHILADELPHIA_PHILLIES = "PHI"
    PITTSBURGH_PIRATES = "PIT"
    SAN_DIEGO_PADRES = "SDN"
    SAN_FRANCISCO_GIANTS = "SFN"
    SEATTLE_MARINERS = "SEA"
    ST_LOUIS_CARDINALS = "SLN"
    TAMPA_BAY_DEVIL_RAYS = "TBA"
    TEXAS_RANGERS = "TEX"
    TORONTO_BLUE_JAYS = "TOR"
    WASHINGTON_NATIONALS = "WAS"

    @property
    def pretty_name(self) -> str:
        words = [word.title() for word in self.name.split("_")]
        return " ".join(words)

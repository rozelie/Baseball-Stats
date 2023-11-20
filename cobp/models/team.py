"""Team data."""
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TeamLocation(Enum):
    """Team location, as defined in Retrosheet spec."""

    VISITING = 0
    HOME = 1


@dataclass
class Team:
    """Team information as defined in Retrosheet spec."""

    retrosheet_id: str
    location: str
    name: str
    start_year: int
    end_year: int

    def is_active_in_year(self, year: int) -> bool:
        active_range = list(range(self.start_year, self.end_year + 1))
        return year in active_range

    @property
    def pretty_name(self) -> str:
        return f"{self.location} {self.name}"


TEAMS = [
    Team("ALT", "Altoona", "Mountain Citys", 1884, 1884),
    Team("ANA", "Anaheim", "Angels", 1997, 2022),
    Team("ARI", "Arizona", "Diamondbacks", 1998, 2022),
    Team("ATL", "Atlanta", "Braves", 1966, 2022),
    Team("BAL", "Baltimore", "Orioles", 1954, 2022),
    Team("BFN", "Buffalo", "Bisons", 1879, 1885),
    Team("BFP", "Buffalo", "Bisons", 1890, 1890),
    Team("BL1", "Baltimore", "Lord Baltimores", 1872, 1874),
    Team("BL2", "Baltimore", "Orioles", 1882, 1889),
    Team("BL3", "Baltimore", "Orioles", 1890, 1891),
    Team("BL4", "Baltimore", "Marylands", 1873, 1873),
    Team("BLA", "Baltimore", "Orioles", 1901, 1902),
    Team("BLF", "Baltimore", "Terrapins", 1914, 1915),
    Team("BLN", "Baltimore", "Orioles", 1892, 1899),
    Team("BLU", "Baltimore", "Monumentals", 1884, 1884),
    Team("BOS", "Boston", "Red Sox", 1901, 2022),
    Team("BR1", "Brooklyn", "Eckfords", 1872, 1872),
    Team("BR2", "Brooklyn", "Atlantics", 1872, 1875),
    Team("BR3", "Brooklyn", "Dodgers", 1884, 1889),
    Team("BR4", "Brooklyn", "Gladiators", 1890, 1890),
    Team("BRF", "Brooklyn", "Tip-Tops", 1914, 1915),
    Team("BRO", "Brooklyn", "Dodgers", 1890, 1957),
    Team("BRP", "Brooklyn", "Wonders", 1890, 1890),
    Team("BS1", "Boston", "Braves", 1871, 1875),
    Team("BS2", "Boston", "Reds", 1891, 1891),
    Team("BSN", "Boston", "Braves", 1876, 1952),
    Team("BSP", "Boston", "Reds", 1890, 1890),
    Team("BSU", "Boston", "Reds", 1884, 1884),
    Team("BUF", "Buffalo", "Blues", 1914, 1915),
    Team("CAL", "California", "Angels", 1965, 1996),
    Team("CH1", "Chicago", "White Stockings", 1871, 1871),
    Team("CH2", "Chicago", "White Stockings", 1874, 1875),
    Team("CHA", "Chicago", "White Sox", 1901, 2022),
    Team("CHF", "Chicago", "Whales", 1914, 1915),
    Team("CHN", "Chicago", "Cubs", 1876, 2022),
    Team("CHP", "Chicago", "Pirates", 1890, 1890),
    Team("CHU", "Chicago-Pittsburgh", "Browns", 1884, 1884),
    Team("CIN", "Cincinnati", "Reds", 1890, 2022),
    Team("CL1", "Cleveland", "Forest Cities", 1871, 1872),
    Team("CL2", "Cleveland", "Spiders", 1879, 1884),
    Team("CL3", "Cleveland", "Spiders", 1887, 1888),
    Team("CL4", "Cleveland", "Spiders", 1889, 1899),
    Team("CL5", "Columbus", "Colts", 1883, 1884),
    Team("CL6", "Columbus", "Colts", 1889, 1891),
    Team("CLE", "Cleveland", "Indians", 1901, 2022),
    Team("CLP", "Cleveland", "Infants", 1890, 1890),
    Team("CN1", "Cincinnati", "Reds", 1876, 1880),
    Team("CN2", "Cincinnati", "Reds", 1882, 1889),
    Team("CN3", "Cincinnati", "Kelly's Killers", 1891, 1891),
    Team("CN4", "Cincinnati", "Stars", 1880, 1880),
    Team("CNU", "Cincinnati", "Outlaw Reds", 1884, 1884),
    Team("COL", "Colorado", "Rockies", 1993, 2022),
    Team("DET", "Detroit", "Tigers", 1901, 2022),
    Team("DTN", "Detroit", "Wolverines", 1881, 1888),
    Team("ELI", "Elizabeth", "Resolutes", 1873, 1873),
    Team("FLO", "Florida", "Marlins", 1993, 2011),
    Team("FW1", "Ft. Wayne", "Kekiongas", 1871, 1871),
    Team("HAR", "Hartford", "Dark Blues", 1876, 1877),
    Team("HOU", "Houston", "Astros", 2013, 2022),
    Team("HOU", "Houston", "Colts", 1962, 2012),
    Team("HR1", "Hartford", "Dark Blues", 1874, 1875),
    Team("IN1", "Indianapolis", "Blues", 1878, 1878),
    Team("IN2", "Indianapolis", "Blues", 1884, 1884),
    Team("IN3", "Indianapolis", "Hoosiers", 1887, 1889),
    Team("IND", "Indianapolis", "Hoosiers", 1914, 1914),
    Team("KC1", "Kansas City", "Athletics", 1955, 1967),
    Team("KC2", "Kansas City", "Cowboys", 1888, 1889),
    Team("KCA", "Kansas City", "Royals", 1969, 2022),
    Team("KCF", "Kansas City", "Packers", 1914, 1915),
    Team("KCN", "Kansas City", "Cowboys", 1886, 1886),
    Team("KCU", "Kansas City", "Cowboys", 1884, 1884),
    Team("KEO", "Keokuk", "Westerns", 1875, 1875),
    Team("LAA", "Los Angeles", "Angels", 1961, 1964),
    Team("LAN", "Los Angeles", "Dodgers", 1958, 2022),
    Team("LS1", "Louisville", "Grays", 1876, 1877),
    Team("LS2", "Louisville", "Colonels", 1882, 1891),
    Team("LS3", "Louisville", "Colonels", 1892, 1899),
    Team("MIA", "Miami", "Marlins", 2012, 2022),
    Team("MID", "Middletown", "Mansfields", 1872, 1872),
    Team("MIL", "Milwaukee", "Brewers", 1970, 1997),
    Team("MIL", "Milwaukee", "Brewers", 1998, 2022),
    Team("MIN", "Minnesota", "Twins", 1961, 2022),
    Team("ML2", "Milwaukee", "Cream Citys", 1878, 1878),
    Team("ML3", "Milwaukee", "Brewers", 1891, 1891),
    Team("MLA", "Milwaukee", "Brewers", 1901, 1901),
    Team("MLN", "Milwaukee", "Braves", 1953, 1965),
    Team("MLU", "Milwaukee", "Brewers", 1884, 1884),
    Team("MON", "Montreal", "Expos", 1969, 2004),
    Team("NEW", "Newark", "Peppers", 1915, 1915),
    Team("NH1", "New Haven", "New Havens", 1875, 1875),
    Team("NY1", "New York", "Giants", 1883, 1957),
    Team("NY2", "New York", "Mutuals", 1871, 1875),
    Team("NY3", "New York", "Mutuals", 1876, 1876),
    Team("NY4", "New York", "Metropolitans", 1883, 1887),
    Team("NYA", "New York", "Yankees", 1903, 2022),
    Team("NYN", "New York", "Mets", 1962, 2022),
    Team("NYP", "New York", "Giants", 1890, 1890),
    Team("OAK", "Oakland", "Athletics", 1968, 2022),
    Team("PH1", "Philadelphia", "Athletics", 1871, 1875),
    Team("PH2", "Philadelphia", "White Stockings", 1873, 1875),
    Team("PH3", "Philadelphia", "Centennials", 1875, 1875),
    Team("PH4", "Philadelphia", "Athletics", 1882, 1891),
    Team("PHA", "Philadelphia", "Athletics", 1901, 1954),
    Team("PHI", "Philadelphia", "Phillies", 1883, 2022),
    Team("PHN", "Philadelphia", "Athletics", 1876, 1876),
    Team("PHP", "Philadelphia", "Quakers", 1890, 1890),
    Team("PHU", "Philadelphia", "Keystones", 1884, 1884),
    Team("PIT", "Pittsburgh", "Pirates", 1887, 2022),
    Team("PRO", "Providence", "Grays", 1878, 1885),
    Team("PT1", "Pittsburgh", "Pirates", 1882, 1886),
    Team("PTF", "Pittsburgh", "Rebels", 1914, 1915),
    Team("PTP", "Pittsburgh", "Burghers", 1890, 1890),
    Team("RC1", "Rockford", "Forest Citys", 1871, 1871),
    Team("RC2", "Rochester", "Hop Bitters", 1890, 1890),
    Team("RIC", "Richmond", "Virginias", 1884, 1884),
    Team("SDN", "San Diego", "Padres", 1969, 2022),
    Team("SE1", "Seattle", "Pilots", 1969, 1969),
    Team("SEA", "Seattle", "Mariners", 1977, 2022),
    Team("SFN", "San Francisco", "Giants", 1958, 2022),
    Team("SL1", "St. Louis", "Red Stockings", 1875, 1875),
    Team("SL2", "St. Louis", "Brown Stockings", 1875, 1875),
    Team("SL3", "St. Louis", "Brown Stockings", 1876, 1877),
    Team("SL4", "St. Louis", "Cardinals", 1882, 1891),
    Team("SL5", "St. Louis", "Maroons", 1885, 1886),
    Team("SLA", "St.Louis", "Browns", 1902, 1953),
    Team("SLF", "St.Louis", "Terriers", 1914, 1915),
    Team("SLN", "St. Louis", "Cardinals", 1892, 2022),
    Team("SLU", "St. Louis", "Maroons", 1884, 1884),
    Team("SPU", "St. Paul", "Saints", 1884, 1884),
    Team("SR1", "Syracuse", "Stars", 1879, 1879),
    Team("SR2", "Syracuse", "Stars", 1890, 1890),
    Team("TBA", "Tampa Bay", "Devil Rays", 1998, 2022),
    Team("TEX", "Texas", "Rangers", 1972, 2022),
    Team("TL1", "Toledo", "Blue Stockings", 1884, 1884),
    Team("TL2", "Toledo", "Maumees", 1890, 1890),
    Team("TOR", "Toronto", "Blue Jays", 1977, 2022),
    Team("TRN", "Troy", "Trojans", 1879, 1882),
    Team("TRO", "Troy", "Haymakers", 1871, 1872),
    Team("WAS", "Washington", "Nationals", 2005, 2022),
    Team("WIL", "Wilmington", "Quicksteps", 1884, 1884),
    Team("WOR", "Worcester", "Ruby Legs", 1880, 1882),
    Team("WS1", "Washington", "Senators", 1901, 1960),
    Team("WS2", "Washington", "Senators", 1961, 1971),
    Team("WS3", "Washington", "Olympics", 1871, 1872),
    Team("WS4", "Washington", "Nationals", 1872, 1872),
    Team("WS5", "Washington", "Nationals", 1873, 1873),
    Team("WS6", "Washington", "Olympics", 1875, 1875),
    Team("WS7", "Washington", "Nationals", 1884, 1884),
    Team("WS8", "Washington", "Senators", 1886, 1889),
    Team("WS9", "Washington", "Senators", 1891, 1891),
    Team("WSN", "Washington", "Senators", 1892, 1899),
    Team("WSU", "Washington", "Nationals", 1884, 1884),
]
TEAM_RETROSHEET_ID_TO_TEAM = {team.retrosheet_id: team for team in TEAMS}


def get_teams_for_year(year: int) -> list[Team]:
    return [team for team in TEAMS if team.is_active_in_year(year)]


def get_team_for_year(team: str, year: int) -> Team:
    for team_ in get_teams_for_year(year):
        if team == team_.retrosheet_id:
            return team_

    raise ValueError(f"Unable to find team for year: {team=} | {year=}")

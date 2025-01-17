"""Generate team definitions from Retrosheet data (https://www.retrosheet.org/TEAMABR.TXT)."""
data = """\
"BS1","NA","Boston","Braves","1871","1875"
"CH1","NA","Chicago","White Stockings","1871","1871"
"CL1","NA","Cleveland","Forest Cities","1871","1872"
"FW1","NA","Ft. Wayne","Kekiongas","1871","1871"
"NY2","NA","New York","Mutuals","1871","1875"
"PH1","NA","Philadelphia","Athletics","1871","1875"
"RC1","NA","Rockford","Forest Citys","1871","1871"
"TRO","NA","Troy","Haymakers","1871","1872"
"WS3","NA","Washington","Olympics","1871","1872"
"BL1","NA","Baltimore","Lord Baltimores","1872","1874"
"BR1","NA","Brooklyn","Eckfords","1872","1872"
"BR2","NA","Brooklyn","Atlantics","1872","1875"
"MID","NA","Middletown","Mansfields","1872","1872"
"WS4","NA","Washington","Nationals","1872","1872"
"BL4","NA","Baltimore","Marylands","1873","1873"
"ELI","NA","Elizabeth","Resolutes","1873","1873"
"PH2","NA","Philadelphia","White Stockings","1873","1875"
"WS5","NA","Washington","Nationals","1873","1873"
"CH2","NA","Chicago","White Stockings","1874","1875"
"HR1","NA","Hartford","Dark Blues","1874","1875"
"KEO","NA","Keokuk","Westerns","1875","1875"
"NH1","NA","New Haven","New Havens","1875","1875"
"PH3","NA","Philadelphia","Centennials","1875","1875"
"SL1","NA","St. Louis","Red Stockings","1875","1875"
"SL2","NA","St. Louis","Brown Stockings","1875","1875"
"WS6","NA","Washington","Olympics","1875","1875"
"BSN","NL","Boston","Braves","1876","1952"
"CN1","NL","Cincinnati","Reds","1876","1880"
"CN4","NL","Cincinnati","Stars","1880","1880"
"HAR","NL","Hartford","Dark Blues","1876","1877"
"LS1","NL","Louisville","Grays","1876","1877"
"NY3","NL","New York","Mutuals","1876","1876"
"PHN","NL","Philadelphia","Athletics","1876","1876"
"SL3","NL","St. Louis","Brown Stockings","1876","1877"
"IN1","NL","Indianapolis","Blues","1878","1878"
"ML2","NL","Milwaukee","Cream Citys","1878","1878"
"PRO","NL","Providence","Grays","1878","1885"
"BFN","NL","Buffalo","Bisons","1879","1885"
"CL2","NL","Cleveland","Spiders","1879","1884"
"SR1","NL","Syracuse","Stars","1879","1879"
"TRN","NL","Troy","Trojans","1879","1882"
"WOR","NL","Worcester","Ruby Legs","1880","1882"
"DTN","NL","Detroit","Wolverines","1881","1888"
"BL2","AA","Baltimore","Orioles","1882","1889"
"CN2","AA","Cincinnati","Reds","1882","1889"
"LS2","AA","Louisville","Colonels","1882","1891"
"PH4","AA","Philadelphia","Athletics","1882","1891"
"PT1","AA","Pittsburgh","Pirates","1882","1886"
"SL4","AA","St. Louis","Cardinals","1882","1891"
"CL5","AA","Columbus","Colts","1883","1884"
"NY4","AA","New York","Metropolitans","1883","1887"
"NY1","NL","New York","Giants","1883","1957"
"BR3","AA","Brooklyn","Dodgers","1884","1889"
"IN2","AA","Indianapolis","Blues","1884","1884"
"RIC","AA","Richmond","Virginias","1884","1884"
"TL1","AA","Toledo","Blue Stockings","1884","1884"
"WS7","AA","Washington","Nationals","1884","1884"
"ALT","UA","Altoona","Mountain Citys","1884","1884"
"BLU","UA","Baltimore","Monumentals","1884","1884"
"BSU","UA","Boston","Reds","1884","1884"
"CHU","UA","Chicago-Pittsburgh","Browns","1884","1884"
"CNU","UA","Cincinnati","Outlaw Reds","1884","1884"
"KCU","UA","Kansas City","Cowboys","1884","1884"
"MLU","UA","Milwaukee","Brewers","1884","1884"
"PHU","UA","Philadelphia","Keystones","1884","1884"
"SLU","UA","St. Louis","Maroons","1884","1884"
"SPU","UA","St. Paul","Saints","1884","1884"
"WSU","UA","Washington","Nationals","1884","1884"
"WIL","UA","Wilmington","Quicksteps","1884","1884"
"SL5","NL","St. Louis","Maroons","1885","1886"
"KCN","NL","Kansas City","Cowboys","1886","1886"
"WS8","NL","Washington","Senators","1886","1889"
"CL3","AA","Cleveland","Spiders","1887","1888"
"IN3","NL","Indianapolis","Hoosiers","1887","1889"
"KC2","AA","Kansas City","Cowboys","1888","1889"
"CL6","AA","Columbus","Colts","1889","1891"
"CL4","NL","Cleveland","Spiders","1889","1899"
"BL3","AA","Baltimore","Orioles","1890","1891"
"BR4","AA","Brooklyn","Gladiators","1890","1890"
"RC2","AA","Rochester","Hop Bitters","1890","1890"
"SR2","AA","Syracuse","Stars","1890","1890"
"TL2","AA","Toledo","Maumees","1890","1890"
"BRO","NL","Brooklyn","Dodgers","1890","1957"
"BSP","PL","Boston","Reds","1890","1890"
"BRP","PL","Brooklyn","Wonders","1890","1890"
"BFP","PL","Buffalo","Bisons","1890","1890"
"CHP","PL","Chicago","Pirates","1890","1890"
"CLP","PL","Cleveland","Infants","1890","1890"
"NYP","PL","New York","Giants","1890","1890"
"PHP","PL","Philadelphia","Quakers","1890","1890"
"PTP","PL","Pittsburgh","Burghers","1890","1890"
"BS2","AA","Boston","Reds","1891","1891"
"CN3","AA","Cincinnati","Kelly's Killers","1891","1891"
"ML3","AA","Milwaukee","Brewers","1891","1891"
"WS9","AA","Washington","Senators","1891","1891"
"BLN","NL","Baltimore","Orioles","1892","1899"
"LS3","NL","Louisville","Colonels","1892","1899"
"WSN","NL","Washington","Senators","1892","1899"
"BLA","AL","Baltimore","Orioles","1901","1902"
"MLA","AL","Milwaukee","Brewers","1901","1901"
"PHA","AL","Philadelphia","Athletics","1901","1954"
"WS1","AL","Washington","Senators","1901","1960"
"SLA","AL","St.Louis","Browns","1902","1953"
"BLF","FL","Baltimore","Terrapins","1914","1915"
"BRF","FL","Brooklyn","Tip-Tops","1914","1915"
"BUF","FL","Buffalo","Blues","1914","1915"
"CHF","FL","Chicago","Whales","1914","1915"
"IND","FL","Indianapolis","Hoosiers","1914","1914"
"KCF","FL","Kansas City","Packers","1914","1915"
"PTF","FL","Pittsburgh","Rebels","1914","1915"
"SLF","FL","St.Louis","Terriers","1914","1915"
"NEW","FL","Newark","Peppers","1915","1915"
"MLN","NL","Milwaukee","Braves","1953","1965"
"FLO","NL","Florida","Marlins","1993","2011"
"KC1","AL","Kansas City","Athletics","1955","1967"
"LAA","AL","Los Angeles","Angels","1961","1964"
"CAL","AL","California","Angels","1965","1996"
"SE1","AL","Seattle","Pilots","1969","1969"
"MON","NL","Montreal","Expos","1969","2004"
"WS2","AL","Washington","Senators","1961","1971"
"MIL","AL","Milwaukee","Brewers","1970","1997"
"HOU","NL","Houston","Colts","1962","2012"
"ANA","AL","Anaheim","Angels","1997","2021"
"BAL","AL","Baltimore","Orioles","1954","2021"
"BOS","AL","Boston","Red Sox","1901","2021"
"CHA","AL","Chicago","White Sox","1901","2021"
"CLE","AL","Cleveland","Indians","1901","2021"
"DET","AL","Detroit","Tigers","1901","2021"
"HOU","AL","Houston","Astros","2013","2021"
"KCA","AL","Kansas City","Royals","1969","2021"
"MIN","AL","Minnesota","Twins","1961","2021"
"NYA","AL","New York","Yankees","1903","2021"
"OAK","AL","Oakland","Athletics","1968","2021"
"SEA","AL","Seattle","Mariners","1977","2021"
"TBA","AL","Tampa Bay","Devil Rays","1998","2021"
"TEX","AL","Texas","Rangers","1972","2021"
"TOR","AL","Toronto","Blue Jays","1977","2021"
"ARI","NL","Arizona","Diamondbacks","1998","2021"
"ATL","NL","Atlanta","Braves","1966","2021"
"CHN","NL","Chicago","Cubs","1876","2021"
"CIN","NL","Cincinnati","Reds","1890","2021"
"COL","NL","Colorado","Rockies","1993","2021"
"LAN","NL","Los Angeles","Dodgers","1958","2021"
"SDN","NL","San Diego","Padres","1969","2021"
"MIA","NL","Miami","Marlins","2012","2021"
"MIL","NL","Milwaukee","Brewers","1998","2021"
"NYN","NL","New York","Mets","1962","2021"
"PHI","NL","Philadelphia","Phillies","1883","2021"
"PIT","NL","Pittsburgh","Pirates","1887","2021"
"SFN","NL","San Francisco","Giants","1958","2021"
"SLN","NL","St. Louis","Cardinals","1892","2021"
"WAS","NL","Washington","Nationals","2005","2021"
"""
team_definitions = []
for line in data.splitlines():
    if not line:
        continue
    retrosheet_id, _, location, name, start_year, end_year = [part.replace('"', "") for part in line.split(",")]
    # at the time of writing, 2022 yearly teams are not defined
    # so we assume if they were a team in 2021, they are a 2022 team as well
    if end_year == 2021:
        end_year = 2022
    team_definitions.append(
        f'Team("{retrosheet_id}", "{location}", "{name}", {start_year}, {end_year}),'
    )

for team in sorted(team_definitions):
    print(team)

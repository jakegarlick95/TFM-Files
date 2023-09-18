import pandas as pd
from pprint import pprint
import math
import json

data = pd.read_csv("LaLiga/20_21.csv")

ordered_fixtures = {}

for i, row in data.iterrows():

    home = row.HomeTeam
    away = row.AwayTeam

    if home not in ordered_fixtures:
        ordered_fixtures[home] = {}
    if away not in ordered_fixtures:
        ordered_fixtures[away] = {}

    if ordered_fixtures[home] == {}:
        ordered_fixtures[home][1] = {"Match": home + "-" + away}
    else:
        fixture_number = max(ordered_fixtures[home].keys()) + 1
        ordered_fixtures[home][fixture_number] = {"Match": home + "-" + away}

    if ordered_fixtures[away] == {}:
        ordered_fixtures[away][1] = {"Match": home + "-" + away}
    else:
        fixture_number = max(ordered_fixtures[away].keys()) + 1
        ordered_fixtures[away][fixture_number] = {"Match": home + "-" + away}

out_file = open("ordered_fixtures.json", "w")

json.dump(ordered_fixtures, out_file)

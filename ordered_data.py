import pandas as pd
from pprint import pprint
import math

data = pd.read_csv("2022_RMdSG_la_liga.csv", sep = ";")

#Drop rows containing team averages for the season
data = data.drop(labels = [39 * i + 38 for i in range(20)] + [780], axis = 0)

data = data.reset_index(drop=True)

data["MatchIndex"] = [0]*760
data["HomeIndex"] = [0]*760
data["AwayIndex"] = [0]*760

team_orders = {"ALV": 1, "ATH": 2,  "BAR": 3, "CAD": 4, "CEL": 5,
               "ECF": 6, "EIB": 7, "GRA": 8, "GTF": 9, "HUE": 10,
               "LUD": 11, "OSA": 12, "RBB": 13, "RMA": 14,
               "RSO": 15, "SFC": 16, "VCF": 17, "VIL": 18,
               "VLL": 19, "ATM": 20}

team_count = {team: 1 for team in team_orders}

data2 = pd.read_csv("20_21.csv")

for i, row in data2.iterrows():
    print(i)
    home = row.HomeTeam
    away = row.AwayTeam
    match = home + "-" + away

    data.loc[38 * team_orders[home] - team_count[home], "MatchIndex"] = i + 1
    data.loc[38 * team_orders[away] - team_count[away], "MatchIndex"] = i + 1

    data.loc[38 * team_orders[home] - team_count[home], "HomeIndex"] = team_count[home]
    data.loc[38 * team_orders[away] - team_count[away], "HomeIndex"] = team_count[home]

    data.loc[38 * team_orders[home] - team_count[home], "AwayIndex"] = team_count[away]
    data.loc[38 * team_orders[away] - team_count[away], "AwayIndex"] = team_count[away]

    team_count[home] += 1
    team_count[away] += 1

data = data.sort_values(by = ["MatchIndex"])
data = data.reset_index(drop=True)

data.to_csv("ordered_data.csv", index = False)

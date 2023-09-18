import pandas as pd
from pprint import pprint
import math
import json

data_21 = pd.read_csv("LaLiga/20_21.csv")
data_20 = pd.read_csv("LaLiga/19_20.csv")
data_19 = pd.read_csv("LaLiga/18_19.csv")

model_data = pd.DataFrame(columns=['Goals', 'HomeTeam', 'ShotsFor','ShotsAgainst','ShotsOnTargetFor','ShotsOnTargetAgainst',
                                   'FoulsFor','FoulsAgainst','CornersFor', "CornersAgainst", "YellowsFor", "YellowsAgainst",
                                   "RedsFor", "RedsAgainst"])

home_adv = 0
home_shots_on_target_adv = 0
home_shots_adv = 0
home_corners_adv = 0
home_y_adv = 0
home_f_adv = 0
home_r_adv = 0

new_home_adv = 0
new_home_adv_squ = 0
new_home_shots_target = 0
new_home_shots_target_squ = 0
new_home_corners = 0
new_home_corners_squ = 0
new_home_shots = 0
new_home_shots_squ = 0

for i, row in data_20.iterrows():
    if i < 270:
        home_row = [row.FTHG, 1, row.HS, row.AS, row.HST, row.AST, row.HF, row.AF, row.HC, row.AC, row.HY, row.AY, row.HR, row.AR]
        away_row = [row.FTAG, 0, row.AS, row.HS, row.AST, row.HST, row.AF, row.HF, row.AC, row.HC, row.AY, row.HY, row.AR, row.HR]
        model_data.loc[len(model_data)] = home_row
        model_data.loc[len(model_data)] = away_row

        home_adv += row.FTHG - row.FTAG
        home_shots_on_target_adv += row.HST - row.AST
        home_corners_adv += row.HC - row.AC
        home_y_adv += row.HY - row.AY
        home_f_adv += row.HF - row.AF
        home_r_adv += row.HR - row.AR
        home_shots_adv += row.HS - row.AS
    else:
        new_home_adv += row.FTHG - row.FTAG
        new_home_shots_target += row.HST - row.AST
        new_home_corners += row.HC - row.AC
        new_home_shots += row.HS - row.AS
        new_home_adv_squ += math.pow(row.FTHG - row.FTAG, 2)
        new_home_shots_target_squ += math.pow(row.HST - row.AST, 2)
        new_home_shots_squ += math.pow(row.HS - row.AS, 2)
        new_home_corners_squ += math.pow(row.HC - row.AC, 2)

for i, row in data_19.iterrows():
    home_row = [row.FTHG, 1, row.HS, row.AS, row.HST, row.AST, row.HF, row.AF, row.HC, row.AC, row.HY, row.AY, row.HR, row.AR]
    away_row = [row.FTAG, 0, row.AS, row.HS, row.AST, row.HST, row.AF, row.HF, row.AC, row.HC, row.AY, row.HY, row.AR, row.HR]
    model_data.loc[len(model_data)] = home_row
    model_data.loc[len(model_data)] = away_row
    home_adv += row.FTHG - row.FTAG
    home_shots_on_target_adv += row.HST - row.AST
    home_corners_adv += row.HC - row.AC
    home_y_adv += row.HY - row.AY
    home_f_adv += row.HF - row.AF
    home_r_adv += row.HR - row.AR
    home_shots_adv += row.HS - row.AS

for i, row in data_21.iterrows():
    if i <= 42:
        new_home_adv += row.FTHG - row.FTAG
        new_home_shots_target += row.HST - row.AST
        new_home_corners += row.HC - row.AC
        new_home_shots += row.HS - row.AS
        new_home_adv_squ += math.pow(row.FTHG - row.FTAG, 2)
        new_home_shots_target_squ += math.pow(row.HST - row.AST, 2)
        new_home_shots_squ += math.pow(row.HS - row.AS, 2)
        new_home_corners_squ += math.pow(row.HC - row.AC, 2)

# model_data.to_csv("training_set.csv", index = True)

#print("Old")
#print("Goals", home_adv / 650)
#print("SOT", home_shots_on_target_adv / 650)
#print("Shots", home_shots_adv / 650)
#print("Corners", home_corners_adv / 650)
#print("Yellows", home_y_adv / 650)
#print("Fouls", home_f_adv / 650)
#print("Reds", home_r_adv / 650)

# print("New")
# print("Goals", new_home_adv / 152)
# print("SOT", new_home_shots_target / 152)
# print("Corners", new_home_corners / 152)
# print("Shots", new_home_shots / 152)
# print("Goals Sigma Squared", (new_home_adv_squ / 152) - math.pow(new_home_adv / 152, 2))
# print("SOT Sigma Squared", (new_home_shots_target_squ / 152) - math.pow(new_home_shots_target / 152, 2))
# print("Corners Sigma Squared", (new_home_corners_squ / 152) - math.pow(new_home_corners / 152, 2))
# print("Shots Squared", (new_home_shots_squ / 152) - math.pow(new_home_shots / 152, 2))

home_adv_dict = {"Goals": {"Sum": new_home_adv, "Squared Sum": new_home_adv_squ},
                 "SOT": {"Sum": new_home_shots_target, "Squared Sum": new_home_shots_target_squ},
                 "Corners": {"Sum": new_home_corners, "Squared Sum": new_home_corners_squ},
                 "Shots": {"Sum": new_home_shots, "Squared Sum": new_home_shots_squ}}

out_file = open("home_advantage_dict.json", "w")

#json.dump(home_adv_dict, out_file)

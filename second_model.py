import numpy as np
import pandas as pd
import json
from pprint import pprint
import datetime
import math
from grids import create_goals_grid, points_grid_generator, calc_asian_handicap, result_asian_handicap, calc_1X2
import matplotlib.pyplot as plt

f = open("ordered_fixtures.json")
ordered_fixtures = json.load(f)

np.random.seed(123456)

#Poisson regression coefficients
coeffs = {"Intercept": -0.655728, "XG": 0.102013, "Shots_Prop": 2.933390, "D.P_w_Shot": 0.053745,
          "SOT_Box": 0.109590, "SOT_Saved_Against": -0.012709}

fixtures = pd.read_csv("LaLiga/20_21.csv")

fixtures2 = pd.read_csv("ordered_data.csv")

#Adds relevant statistics to ordered fixtures dict.
#Use convention if a team has 0 shots on target that save percentage is 100 not 0
for i, row in fixtures2.iterrows():
    match = row.match
    home = match.split("-")[0]
    away = match.split("-")[1]
    team = row.Team
    for match_number in ordered_fixtures[home]:
        if ordered_fixtures[home][match_number]["Match"] == match:
            home_match = match_number
    for match_number in ordered_fixtures[away]:
        if ordered_fixtures[away][match_number]["Match"] == match:
            away_match = match_number
    if team == home:
        ordered_fixtures[home][home_match]["XG"] = row["Expected goals"]
        ordered_fixtures[away][away_match]["XG_Against"] = row["Expected goals"]
        ordered_fixtures[home][home_match]["Shots_Prop"] = row["Goals proportion among shots"]
        ordered_fixtures[away][away_match]["Shots_Prop_Against"] = row["Goals proportion among shots"]
        ordered_fixtures[home][home_match]["D.P_w_Shot"] = row["Dangerous possessions with shot"]
        ordered_fixtures[away][away_match]["D.P_w_Shot_Against"] = row["Dangerous possessions with shot"]
        ordered_fixtures[home][home_match]["SOT_Box"] = row["Shots on target from the box"]
        ordered_fixtures[away][away_match]["SOT_Box_Against"] = row["Shots on target from the box"]
        if row["Shots on target received"] != 0:
            ordered_fixtures[away][away_match]["SOT_Saved_Against"] = row["Shots on target saved proportion"]
            ordered_fixtures[home][home_match]["SOT_Saved"] = row["Shots on target saved proportion"]
        else:
            ordered_fixtures[away][away_match]["SOT_Saved_Against"] = 100
            ordered_fixtures[home][home_match]["SOT_Saved"] = 100
    elif team == away:
        ordered_fixtures[away][away_match]["XG"] = row["Expected goals"]
        ordered_fixtures[home][home_match]["XG_Against"] = row["Expected goals"]
        ordered_fixtures[away][away_match]["Shots_Prop"] = row["Goals proportion among shots"]
        ordered_fixtures[home][home_match]["Shots_Prop_Against"] = row["Goals proportion among shots"]
        ordered_fixtures[away][away_match]["D.P_w_Shot"] = row["Dangerous possessions with shot"]
        ordered_fixtures[home][home_match]["D.P_w_Shot_Against"] = row["Dangerous possessions with shot"]
        ordered_fixtures[away][away_match]["SOT_Box"] = row["Shots on target from the box"]
        ordered_fixtures[home][home_match]["SOT_Box_Against"] = row["Shots on target from the box"]
        if row["Shots on target received"] != 0:
            ordered_fixtures[home][home_match]["SOT_Saved_Against"] = row["Shots on target saved proportion"]
            ordered_fixtures[away][away_match]["SOT_Saved"] = row["Shots on target saved proportion"]
        else:
            ordered_fixtures[home][home_match]["SOT_Saved_Against"] = 100
            ordered_fixtures[away][away_match]["SOT_Saved"] = 100

#Start from 3rd December
start_date = "03/12/2020"
start_date_time = datetime.datetime.strptime(start_date, '%d/%m/%Y')
week = 1
profit_1x2 = 0

betting_log_2 = {}

while week < 26:
    print(week)
    for i, row in fixtures.iterrows():
        match_date = row.Date
        match_date_time = datetime.datetime.strptime(match_date, '%d/%m/%Y')
        end_date_time = start_date_time + datetime.timedelta(days = 7)

        if start_date_time < match_date_time < end_date_time:
            home = row.HomeTeam
            away = row.AwayTeam
            match = home + "-" + away
            for match_number in ordered_fixtures[home]:
                if ordered_fixtures[home][match_number]["Match"] == match:
                    home_index = int(match_number)
            for match_number in ordered_fixtures[away]:
                if ordered_fixtures[away][match_number]["Match"] == match:
                    away_index = int(match_number)

            home_xg_for = 0
            home_xg_against = 0
            home_shots_prop_for = 0
            home_shots_prop_against = 0
            home_dp_w_shot_for = 0
            home_dp_w_shot_against = 0
            home_sot_box_for = 0
            home_sot_box_against = 0
            home_sot_saved_for = 0
            home_sot_saved_against = 0

            away_xg_for = 0
            away_xg_against = 0
            away_shots_prop_for = 0
            away_shots_prop_against = 0
            away_dp_w_shot_for = 0
            away_dp_w_shot_against = 0
            away_sot_box_for = 0
            away_sot_box_against = 0
            away_sot_saved_for = 0
            away_sot_saved_against = 0

            if home_index <= 11:
                for i in range(1, home_index):
                    home_xg_for += (ordered_fixtures[home][str(i)]["XG"] * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])
                    home_xg_against += (ordered_fixtures[home][str(i)]["XG_Against"] * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])
                    home_shots_prop_for += (ordered_fixtures[home][str(i)]["Shots_Prop"] * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])
                    home_shots_prop_against += (ordered_fixtures[home][str(i)]["Shots_Prop_Against"] * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])
                    home_dp_w_shot_for += (ordered_fixtures[home][str(i)]["D.P_w_Shot"] * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])
                    home_dp_w_shot_against += (ordered_fixtures[home][str(i)]["D.P_w_Shot_Against"] * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])
                    home_sot_box_for += (ordered_fixtures[home][str(i)]["SOT_Box"] * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])
                    home_sot_box_against += (ordered_fixtures[home][str(i)]["SOT_Box_Against"] * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])
                    home_sot_box_against += (ordered_fixtures[home][str(i)]["SOT_Box_Against"] * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])
                    home_sot_saved_for += (ordered_fixtures[home][str(i)]["SOT_Saved"] * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])
                    home_sot_saved_against += (ordered_fixtures[home][str(i)]["SOT_Saved_Against"] * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])

            elif home_index >= 12:
                for i in range(home_index - 10, home_index):
                    home_xg_for += (ordered_fixtures[home][str(i)]["XG"] * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    home_xg_against += (ordered_fixtures[home][str(i)]["XG_Against"] * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    home_shots_prop_for += (ordered_fixtures[home][str(i)]["Shots_Prop"] * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    home_shots_prop_against += (ordered_fixtures[home][str(i)]["Shots_Prop_Against"] * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    home_dp_w_shot_for += (ordered_fixtures[home][str(i)]["D.P_w_Shot"] * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    home_dp_w_shot_against += (ordered_fixtures[home][str(i)]["D.P_w_Shot_Against"] * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    home_sot_box_for += (ordered_fixtures[home][str(i)]["SOT_Box"] * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    home_sot_box_against += (ordered_fixtures[home][str(i)]["SOT_Box_Against"] * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    home_sot_box_against += (ordered_fixtures[home][str(i)]["SOT_Box_Against"] * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    home_sot_saved_for += (ordered_fixtures[home][str(i)]["SOT_Saved"] * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    home_sot_saved_against += (ordered_fixtures[home][str(i)]["SOT_Saved_Against"] * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

            if away_index <= 11:
                for i in range(1, away_index):
                    away_xg_for += (ordered_fixtures[away][str(i)]["XG"] * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_xg_against += (ordered_fixtures[away][str(i)]["XG_Against"] * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_shots_prop_for += (ordered_fixtures[away][str(i)]["Shots_Prop"] * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_shots_prop_against += (ordered_fixtures[away][str(i)]["Shots_Prop_Against"] * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_dp_w_shot_for += (ordered_fixtures[away][str(i)]["D.P_w_Shot"] * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_dp_w_shot_against += (ordered_fixtures[away][str(i)]["D.P_w_Shot_Against"] * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_sot_box_for += (ordered_fixtures[away][str(i)]["SOT_Box"] * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_sot_box_against += (ordered_fixtures[away][str(i)]["SOT_Box_Against"] * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_sot_box_against += (ordered_fixtures[away][str(i)]["SOT_Box_Against"] * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_sot_saved_for += (ordered_fixtures[away][str(i)]["SOT_Saved"] * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_sot_saved_against += (ordered_fixtures[away][str(i)]["SOT_Saved_Against"] * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])

            elif away_index >= 12:
                for i in range(away_index - 10, away_index):
                    away_xg_for += (ordered_fixtures[away][str(i)]["XG"] * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    away_xg_against += (ordered_fixtures[away][str(i)]["XG_Against"] * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    away_shots_prop_for += (ordered_fixtures[away][str(i)]["Shots_Prop"] * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    away_shots_prop_against += (ordered_fixtures[away][str(i)]["Shots_Prop_Against"] * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    away_dp_w_shot_for += (ordered_fixtures[away][str(i)]["D.P_w_Shot"] * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    away_dp_w_shot_against += (ordered_fixtures[away][str(i)]["D.P_w_Shot_Against"] * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    away_sot_box_for += (ordered_fixtures[away][str(i)]["SOT_Box"] * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    away_sot_box_against += (ordered_fixtures[away][str(i)]["SOT_Box_Against"] * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    away_sot_box_against += (ordered_fixtures[away][str(i)]["SOT_Box_Against"] * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    away_sot_saved_for += (ordered_fixtures[away][str(i)]["SOT_Saved"] * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    away_sot_saved_against += (ordered_fixtures[away][str(i)]["SOT_Saved_Against"] * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

            home_xg_param = (home_xg_for + away_xg_against) / 2
            away_xg_param = (away_xg_for + home_xg_against) / 2
            home_shots_prop_param = (home_shots_prop_for + away_shots_prop_against) / 2
            away_shots_prop_param = (away_shots_prop_for + home_shots_prop_against) / 2
            home_dp_w_shot_param = (home_dp_w_shot_for + away_dp_w_shot_against) / 2
            away_dp_w_shot_param = (away_dp_w_shot_for + home_dp_w_shot_against) / 2
            home_sot_box_param = (home_sot_box_for + away_sot_box_against) / 2
            away_sot_box_param = (away_sot_box_for + home_sot_box_against) / 2
            home_sot_saved_param = (away_sot_saved_for + home_sot_saved_against) / 2
            away_sot_saved_param = (home_sot_saved_for + away_sot_saved_against) / 2

            home_goals_param = math.exp(coeffs["Intercept"]
                                        + coeffs["XG"] * home_xg_param
                                        + coeffs["Shots_Prop"] * home_shots_prop_param
                                        + coeffs["D.P_w_Shot"] * home_dp_w_shot_param
                                        + coeffs["SOT_Box"] * home_sot_box_param
                                        + coeffs["SOT_Saved_Against"] * home_sot_saved_param
                                        ) + 0.1 #Home advantage is being applied

            away_goals_param = math.exp(coeffs["Intercept"]
                                        + coeffs["XG"] * away_xg_param
                                        + coeffs["Shots_Prop"] * away_shots_prop_param
                                        + coeffs["D.P_w_Shot"] * away_dp_w_shot_param
                                        + coeffs["SOT_Box"] * away_sot_box_param
                                        + coeffs["SOT_Saved_Against"] * away_sot_saved_param
                                        ) - 0.1

            supremacy = home_goals_param - away_goals_param
            draw_factor = -0.04549851 * supremacy**2 + 0.02775876 * abs(supremacy) + 1.10795869
            goals_grid = create_goals_grid(home_goals_param, away_goals_param, draw_factor)
            generator = points_grid_generator(goals_grid)

            asian_handicap_line = row.AHh
            our_asian_handicap = calc_asian_handicap(goals_grid, generator, asian_handicap_line)
            our_1x2 = calc_1X2(goals_grid, generator)

            market_home = row.MaxAHH
            market_away = row.MaxAHA

            market_home_1x2 = row.MaxH
            market_away_1x2 = row.MaxA

            market_implied_prob_home = 1 / market_home
            market_implied_prob_away = 1 / market_away

            market_implied_prob_home_1x2 = 1 / market_home_1x2
            market_implied_prob_away_1x2 = 1 / market_away_1x2

            bet_home = False
            bet_away = False

            bet_home_1x2 = False
            bet_away_1x2 = False

            if our_asian_handicap[0] > market_implied_prob_home + 0.05:
                bet_home = True
            if our_asian_handicap[1] > market_implied_prob_away + 0.05:
                bet_away = True

            if our_1x2[0] > market_implied_prob_home_1x2 + 0.02:
                bet_home_1x2 = True
            if our_1x2[2] > market_implied_prob_away_1x2 + 0.02:
                bet_away_1x2 = True

            if bet_home or bet_away:
                result = result_asian_handicap(row.FTHG - row.FTAG, asian_handicap_line)
                if week not in betting_log_2:
                    betting_log_2[week] = {}
                if bet_home:
                    betting_log_2[week][match] = {"Selection": "home", "Line": asian_handicap_line,
                                                "Price": market_home, "Result": result, "Score": (row.FTHG, row.FTAG),
                                                "Params": (float(home_goals_param), float(away_goals_param))}
                elif bet_away:
                    betting_log_2[week][match] = {"Selection": "away", "Line": asian_handicap_line,
                                                "Price": market_home, "Result": result, "Score": (row.FTHG, row.FTAG),
                                                "Params": (float(home_goals_param), float(away_goals_param))}

            if bet_home_1x2:
                if week not in betting_log_2:
                    betting_log_2[week] = {}
                stake = 1 / (market_home_1x2 - 1)
                if row.FTHG > row.FTAG:
                    profit_1x2 += (market_home_1x2 - 1)
                    result_1x2 = "home"
                else:
                    profit_1x2 -= 1
                    if row.FTHG == row.FTAG:
                        result_1x2 = "draw"
                    else:
                        result_1x2 = "away"

                if match not in betting_log_2[week]:
                    betting_log_2[week][match] = {"Selection1X2": "home",
                                                "Price1X2": market_home_1x2, "Result1X2": result_1x2, "Score": (row.FTHG, row.FTAG),
                                                "Params": (float(home_goals_param), float(away_goals_param))}
                else:
                    betting_log_2[week][match]["Selection1X2"] = "home"
                    betting_log_2[week][match]["Price1X2"] = market_home_1x2
                    betting_log_2[week][match]["Result1X2"] = result_1x2

            if bet_away_1x2:
                if week not in betting_log_2:
                    betting_log_2[week] = {}
                stake = 1 / (market_away_1x2 - 1)
                if row.FTHG < row.FTAG:
                    profit_1x2 += (market_away_1x2 - 1)
                    result_1x2 = "away"
                else:
                    profit_1x2 -= 1
                    if row.FTHG == row.FTAG:
                        result_1x2 = "draw"
                    else:
                        result_1x2 = "home"
                if match not in betting_log_2[week]:
                    betting_log_2[week][match] = {"Selection1X2": "away",
                                                "Price1X2": market_away_1x2, "Result1X2": result_1x2, "Score": (row.FTHG, row.FTAG),
                                                "Params": (float(home_goals_param), float(away_goals_param))}
                else:
                    betting_log_2[week][match]["Selection1X2"] = "away"
                    betting_log_2[week][match]["Price1X2"] = market_away_1x2
                    betting_log_2[week][match]["Result1X2"] = result_1x2

        elif match_date_time < start_date_time:
            pass
        elif match_date_time > start_date_time:
            break

    week += 1
    start_date_time = end_date_time

for week in betting_log_2:
    betting_log_2[week]["Profit"] = 0
    betting_log_2[week]["Stake"] = 0
    for bet in betting_log_2[week]:
        if bet not in ["Profit", "Stake"]:
            if "Result" in betting_log_2[week][bet]:
                betting_log_2[week]["Stake"] += 1
                if (betting_log_2[week][bet]["Result"] == betting_log_2[week][bet]["Selection"]):
                    betting_log_2[week]["Profit"] += betting_log_2[week][bet]["Price"] - 1
                elif (betting_log_2[week][bet]["Result"] == "win_void"):
                    if betting_log_2[week][bet]["Selection"] == "home":
                        betting_log_2[week]["Profit"] += (betting_log_2[week][bet]["Price"] - 1) * 0.5
                    elif betting_log_2[week][bet]["Selection"] == "away":
                        betting_log_2[week]["Profit"] += -0.5
                elif (betting_log_2[week][bet]["Result"] == "lose_void"):
                    if betting_log_2[week][bet]["Selection"] == "home":
                        betting_log_2[week]["Profit"] += -0.5
                    elif betting_log_2[week][bet]["Selection"] == "away":
                        betting_log_2[week]["Profit"] += (betting_log_2[week][bet]["Price"] - 1) * 0.5
                else:
                    betting_log_2[week]["Profit"] += -1

for week in betting_log_2:
    betting_log_2[week]["Profit1X2"] = 0
    betting_log_2[week]["Stake1X2"] = 0
    for bet in betting_log_2[week]:
        if bet not in ["Profit", "Stake", "Profit1X2", "Stake1X2"]:
            if "Result1X2" in betting_log_2[week][bet]:
                betting_log_2[week]["Stake1X2"] += 1
                if (betting_log_2[week][bet]["Result1X2"] == betting_log_2[week][bet]["Selection1X2"]):
                    betting_log_2[week]["Profit1X2"] += betting_log_2[week][bet]["Price1X2"] - 1
                else:
                    betting_log_2[week]["Profit1X2"] += -1

# pprint(betting_log_2)
print(sum(betting_log_2[week]["Profit"] for week in betting_log_2))
print(sum(betting_log_2[week]["Profit"] for week in betting_log_2) / sum(betting_log_2[week]["Stake"] for week in betting_log_2))

print(profit_1x2)
print(sum(betting_log_2[week]["Profit1X2"] for week in betting_log_2) / sum(betting_log_2[week]["Stake1X2"] for week in betting_log_2))

lines = []
for week in betting_log_2:
    for key in betting_log_2[week]:
        if key not in ["Profit", "Profit1X2", "Stake", "Stake1X2"]:
            if "Line" in betting_log_2[week][key]:
                line = float(betting_log_2[week][key]["Line"])
                selection = betting_log_2[week][key]["Selection"]
                if selection == "away":
                    line = -line
                lines.append(line)

ordered_lines = sorted(set(lines))

plt.figure()
plt.bar(ordered_lines, [lines.count(line) for line in ordered_lines], width = 0.1)
plt.xlabel("Line")
plt.ylabel("Frequency")

weeks = []
profit = []
profit_1x2 = []
for week in betting_log_2:
    weeks.append(week)
    profit.append(betting_log_2[week]["Profit"])
    profit_1x2.append(betting_log_2[week]["Profit1X2"])


plt.figure()
plt.bar(weeks, profit)
plt.xlabel("Week")
plt.ylabel("Total Units Profit")

plt.figure()
plt.bar(weeks, profit_1x2)
plt.xlabel("Week")
plt.ylabel("Total Units Profit")
#plt.show()

with open("betting_log_2.json", "w+") as outfile:
    json.dump(betting_log_2, outfile)

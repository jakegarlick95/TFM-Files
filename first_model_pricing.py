import numpy as np
import pandas as pd
import json
from pprint import pprint
import datetime
import math
from grids import create_goals_grid, points_grid_generator, calc_asian_handicap, result_asian_handicap, calc_1X2
import matplotlib.pyplot as plt

#Load in ordered fixtures
f = open("ordered_fixtures.json")
ordered_fixtures = json.load(f)

np.random.seed(123456)

#Coefficients from our Poisson regression
coeffs = {"Intercept": 0.460875, "SOT": 0.133871, "Shots": -0.013390, "Corners": -0.029603}

#Load in fixtures file from football-data
fixtures = pd.read_csv("LaLiga/20_21.csv")

#Load in home advantage data from first 152 games behind closed doors
f = open("home_advantage_dict.json")
home_adv_dict = json.load(f)

# for i, row in fixtures.iterrows():
#     home = row.HomeTeam
#     away = row.AwayTeam
#     match = home + "-" + away
#     for team in [home, away]:
#         for match_number in ordered_fixtures[team]:
#             if ordered_fixtures[team][match_number]["Match"] == match:
#                 if team == home:
#                     ordered_fixtures[team][match_number]["ShotsFor"] = row.HS
#                     ordered_fixtures[team][match_number]["ShotsAgainst"] = row.AS
#                     ordered_fixtures[team][match_number]["ShotsOnTargetFor"] = row.HST
#                     ordered_fixtures[team][match_number]["ShotsOnTargetAgainst"] = row.AST
#                     ordered_fixtures[team][match_number]["CornersFor"] = row.HC
#                     ordered_fixtures[team][match_number]["CornersAgainst"] = row.AC
#                 elif team == away:
#                     ordered_fixtures[team][match_number]["ShotsFor"] = row.AS
#                     ordered_fixtures[team][match_number]["ShotsAgainst"] = row.HS
#                     ordered_fixtures[team][match_number]["ShotsOnTargetFor"] = row.AST
#                     ordered_fixtures[team][match_number]["ShotsOnTargetAgainst"] = row.HST
#                     ordered_fixtures[team][match_number]["CornersFor"] = row.AC
#                     ordered_fixtures[team][match_number]["CornersAgainst"] = row.HC

behind_closed_doors_games = 152

#Start simulating bets from 16th October
start_date = "16/10/2020"
start_date_time = datetime.datetime.strptime(start_date, '%d/%m/%Y')
week = 1

betting_log = {}

goals = 0
matches = 0

profit_1x2 = 0

while week < 32:

    #Simulate home advantage for goals, corners, shots, shots on target based on current distributions
    goals_mu = home_adv_dict["Goals"]["Sum"] / behind_closed_doors_games
    goals_sigma_squared = (home_adv_dict["Goals"]["Squared Sum"] / behind_closed_doors_games) - goals_mu**2
    goals_home_adv = np.random.normal(goals_mu, math.sqrt(goals_sigma_squared) / math.sqrt(behind_closed_doors_games), 1)

    corners_mu = home_adv_dict["Corners"]["Sum"] / behind_closed_doors_games
    corners_sigma_squared = (home_adv_dict["Corners"]["Squared Sum"] / behind_closed_doors_games) - corners_mu**2
    corners_home_adv = np.random.normal(corners_mu, math.sqrt(corners_sigma_squared) / math.sqrt(behind_closed_doors_games), 1)

    shots_mu = home_adv_dict["Shots"]["Sum"] / behind_closed_doors_games
    shots_sigma_squared = (home_adv_dict["Shots"]["Squared Sum"] / behind_closed_doors_games) - shots_mu**2
    shots_home_adv = np.random.normal(shots_mu, math.sqrt(shots_sigma_squared) / math.sqrt(behind_closed_doors_games), 1)

    shots_target_mu = home_adv_dict["SOT"]["Sum"] / behind_closed_doors_games
    shots_target_sigma_squared = (home_adv_dict["SOT"]["Squared Sum"] / behind_closed_doors_games) - shots_target_mu**2
    shots_target_home_adv = np.random.normal(shots_target_mu, math.sqrt(shots_target_sigma_squared) / math.sqrt(behind_closed_doors_games), 1)

    # if week == 1:
    #     print(goals_home_adv, corners_home_adv, shots_home_adv, shots_target_home_adv)

    #Iterate through match by match
    for i, row in fixtures.iterrows():
        match_date = row.Date
        match_date_time = datetime.datetime.strptime(match_date, '%d/%m/%Y')
        end_date_time = start_date_time + datetime.timedelta(days = 7)

        #If match is in the current week we are simulating
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

            home_shots_on_target_for = 0
            home_shots_on_target_against = 0
            home_shots_for = 0
            home_shots_against = 0
            home_corners_for = 0
            home_corners_against = 0

            away_shots_on_target_for = 0
            away_shots_on_target_against = 0
            away_shots_for = 0
            away_shots_against = 0
            away_corners_for = 0
            away_corners_against = 0

            #Iterate through teams previous fixtures and calculate all weighted averages
            if home_index < 12:
                #Uses all of a teams previous matches when inside this branch
                for i in range(1, home_index):
                    if ordered_fixtures[home][str(i)]["Match"].split("-")[0] == home:
                        home_fixture = True
                    else:
                        home_fixture = False

                    #Adjust parameters for current home advantage values at each point
                    home_shots_on_target_for += ((ordered_fixtures[home][str(i)]["ShotsOnTargetFor"] + 1 - home_fixture * (shots_target_home_adv / 2) + (1 - home_fixture) * (shots_target_home_adv / 2)) \
                    * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])

                    home_shots_on_target_against += ((ordered_fixtures[home][str(i)]["ShotsOnTargetAgainst"] + 1 + home_fixture * (shots_target_home_adv / 2) - (1 - home_fixture) * (shots_target_home_adv / 2)) \
                     * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])

                    home_shots_for += ((ordered_fixtures[home][str(i)]["ShotsFor"] + 2 - home_fixture * (shots_home_adv / 2) + (1 - home_fixture) * (shots_home_adv / 2)) \
                    * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])
                    home_shots_against += ((ordered_fixtures[home][str(i)]["ShotsAgainst"] + 2 + home_fixture * (shots_home_adv / 2) - (1 - home_fixture) * (shots_home_adv / 2)) \
                     * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])

                    home_corners_for += ((ordered_fixtures[home][str(i)]["CornersFor"] + 1 - home_fixture * (corners_home_adv / 2) + (1 - home_fixture) * (corners_home_adv / 2)) \
                    * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])
                    home_corners_against += ((ordered_fixtures[home][str(i)]["CornersAgainst"] + 1 + home_fixture * (corners_home_adv / 2) - (1 - home_fixture) * (corners_home_adv / 2)) \
                     * (i / (home_index - 1))) / sum([i / (home_index - 1) for i in range(1, home_index)])

            elif home_index >= 12:
                #Uses previous ten matches inside this branch
                for i in range(home_index - 10, home_index):
                    if ordered_fixtures[home][str(i)]["Match"].split("-")[0] == home:
                        home_fixture = True
                    else:
                        home_fixture = False
                    home_shots_on_target_for += ((ordered_fixtures[home][str(i)]["ShotsOnTargetFor"] + 1 - home_fixture * (shots_target_home_adv / 2) + (1 - home_fixture) * (shots_target_home_adv / 2)) \
                    * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

                    home_shots_on_target_against += ((ordered_fixtures[home][str(i)]["ShotsOnTargetAgainst"] + 1 + home_fixture * (shots_target_home_adv / 2) - (1 - home_fixture) * (shots_target_home_adv / 2)) \
                     * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

                    #print(home_index, home_shots_for, ordered_fixtures[home][str(i)]["ShotsFor"], i)
                    home_shots_for += ((ordered_fixtures[home][str(i)]["ShotsFor"] + 2 - home_fixture * (shots_home_adv / 2) + (1 - home_fixture) * (shots_home_adv / 2)) \
                    * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])
                    #print(home_shots_for)

                    home_shots_against += ((ordered_fixtures[home][str(i)]["ShotsAgainst"] + 2 + home_fixture * (shots_home_adv / 2) - (1 - home_fixture) * (shots_home_adv / 2)) \
                     * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

                    home_corners_for += ((ordered_fixtures[home][str(i)]["CornersFor"] + 1 - home_fixture * (corners_home_adv / 2) + (1 - home_fixture) * (corners_home_adv / 2)) \
                    * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

                    home_corners_against += ((ordered_fixtures[home][str(i)]["CornersAgainst"] + 1 + home_fixture * (corners_home_adv / 2) - (1 - home_fixture) * (corners_home_adv / 2)) \
                     * ((i - (home_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

            #Same code as above except home avdantage element is the opposite
            if away_index < 12:
                for i in range(1, away_index):
                    if ordered_fixtures[away][str(i)]["Match"].split("-")[0] == away:
                        home_fixture = True
                    else:
                        home_fixture = False

                    away_shots_on_target_for += ((ordered_fixtures[away][str(i)]["ShotsOnTargetFor"] + 1 - home_fixture * (shots_target_home_adv / 2) + (1 - home_fixture) * (shots_target_home_adv / 2)) \
                    * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_shots_on_target_against += ((ordered_fixtures[away][str(i)]["ShotsOnTargetAgainst"] + 1 + home_fixture * (shots_target_home_adv / 2) - (1 - home_fixture) * (shots_target_home_adv / 2)) \
                     * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])

                    away_shots_for += ((ordered_fixtures[away][str(i)]["ShotsFor"] + 2 - home_fixture * (shots_home_adv / 2) + (1 - home_fixture) * (shots_home_adv / 2)) \
                    * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_shots_against += ((ordered_fixtures[away][str(i)]["ShotsAgainst"] + 2 + home_fixture * (shots_home_adv / 2) - (1 - home_fixture) * (shots_home_adv / 2)) \
                     * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])

                    away_corners_for += ((ordered_fixtures[away][str(i)]["CornersFor"] + 1 - home_fixture * (corners_home_adv / 2) + (1 - home_fixture) * (corners_home_adv / 2)) \
                    * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])
                    away_corners_against += ((ordered_fixtures[away][str(i)]["CornersAgainst"] + 1 + home_fixture * (corners_home_adv / 2) - (1 - home_fixture) * (corners_home_adv / 2)) \
                     * (i / (away_index - 1))) / sum([i / (away_index - 1) for i in range(1, away_index)])

            elif away_index >= 12:
                for i in range(away_index - 10, away_index):
                    if ordered_fixtures[away][str(i)]["Match"].split("-")[0] == home:
                        home_fixture = True
                    else:
                        home_fixture = False

                    away_shots_on_target_for += ((ordered_fixtures[away][str(i)]["ShotsOnTargetFor"] + 1 - home_fixture * (shots_target_home_adv / 2) + (1 - home_fixture) * (shots_target_home_adv / 2)) \
                    * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

                    away_shots_on_target_against += ((ordered_fixtures[away][str(i)]["ShotsOnTargetAgainst"] + 1 + home_fixture * (shots_target_home_adv / 2) - (1 - home_fixture) * (shots_target_home_adv / 2)) \
                     * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

                    away_shots_for += ((ordered_fixtures[away][str(i)]["ShotsFor"] + 2 - home_fixture * (shots_home_adv / 2) + (1 - home_fixture) * (shots_home_adv / 2)) \
                    * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

                    away_shots_against += ((ordered_fixtures[away][str(i)]["ShotsAgainst"] + 2 + home_fixture * (shots_home_adv / 2) - (1 - home_fixture) * (shots_home_adv / 2)) \
                     * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

                    away_corners_for += ((ordered_fixtures[away][str(i)]["CornersFor"] + 1 - home_fixture * (corners_home_adv / 2) + (1 - home_fixture) * (corners_home_adv / 2)) \
                    * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

                    away_corners_against += ((ordered_fixtures[away][str(i)]["CornersAgainst"] + 1 + home_fixture * (corners_home_adv / 2) - (1 - home_fixture) * (corners_home_adv / 2)) \
                     * ((i - (away_index - 11)) / 10)) / sum([i / 10 for i in range(1, 11)])

            #Final params are the average of the for/against params
            home_shots_target_param = (home_shots_on_target_for + away_shots_on_target_against) / 2
            away_shots_target_param = (away_shots_on_target_for + home_shots_on_target_against) / 2
            home_shots_param = (home_shots_for + away_shots_against) / 2
            away_shots_param = (away_shots_for + home_shots_against) / 2
            home_corners_param = (home_corners_for + away_corners_against) / 2
            away_corners_param = (away_corners_for + home_corners_against) / 2

            #Plug calculated parameters into equation from Poisson regression
            #Adjust for home advantage and remove the additional 1 to avoid negatives
            home_goals_param = math.exp(coeffs["Intercept"]
                                        + coeffs["SOT"] * home_shots_target_param
                                        + coeffs["Shots"] * home_shots_param
                                        + coeffs["Corners"] * home_corners_param
                                        ) - 1 + goals_home_adv / 2

            away_goals_param = math.exp(coeffs["Intercept"]
                                        + coeffs["SOT"] * away_shots_target_param
                                        + coeffs["Shots"] * away_shots_param
                                        + coeffs["Corners"] * away_corners_param
                                        ) - 1 - goals_home_adv / 2

            #Calculate draw factor based on absolute supremacy
            supremacy = home_goals_param - away_goals_param
            draw_factor = -0.04549851 * supremacy**2 + 0.02775876 * abs(supremacy) + 1.10795869

            #Create goals grid and generator based on model parameters
            goals_grid = create_goals_grid(home_goals_param, away_goals_param, draw_factor)
            generator = points_grid_generator(goals_grid)

            #Get market handicap line and calculate our probabilities for this line plus the 1x2 market
            asian_handicap_line = row.AHh
            our_asian_handicap = calc_asian_handicap(goals_grid, generator, asian_handicap_line)
            our_1x2 = calc_1X2(goals_grid, generator)

            #Compare our prices to the market
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

            #Any bets placed are then recorded in full detail
            if bet_home or bet_away:
                result = result_asian_handicap(row.FTHG - row.FTAG, asian_handicap_line)
                if week not in betting_log:
                    betting_log[week] = {}
                if bet_home:
                    betting_log[week][match] = {"Selection": "home", "Line": asian_handicap_line,
                                                "Price": market_home, "Result": result, "Score": (row.FTHG, row.FTAG),
                                                "Params": (float(home_goals_param), float(away_goals_param))}
                elif bet_away:
                    betting_log[week][match] = {"Selection": "away", "Line": asian_handicap_line,
                                                "Price": market_home, "Result": result, "Score": (row.FTHG, row.FTAG),
                                                "Params": (float(home_goals_param), float(away_goals_param))}

            if bet_home_1x2:
                if week not in betting_log:
                    betting_log[week] = {}
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

                if match not in betting_log[week]:
                    betting_log[week][match] = {"Selection1X2": "home",
                                                "Price1X2": market_home_1x2, "Result1X2": result_1x2, "Score": (row.FTHG, row.FTAG),
                                                "Params": (float(home_goals_param), float(away_goals_param))}
                else:
                    betting_log[week][match]["Selection1X2"] = "home"
                    betting_log[week][match]["Price1X2"] = market_home_1x2
                    betting_log[week][match]["Result1X2"] = result_1x2

            if bet_away_1x2:
                if week not in betting_log:
                    betting_log[week] = {}
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
                if match not in betting_log[week]:
                    betting_log[week][match] = {"Selection1X2": "away",
                                                "Price1X2": market_away_1x2, "Result1X2": result_1x2, "Score": (row.FTHG, row.FTAG),
                                                "Params": (float(home_goals_param), float(away_goals_param))}
                else:
                    betting_log[week][match]["Selection1X2"] = "away"
                    betting_log[week][match]["Price1X2"] = market_away_1x2
                    betting_log[week][match]["Result1X2"] = result_1x2

            #Update information about home advantage in behind closed doors games
            behind_closed_doors_games += 1
            home_adv_dict["Goals"]["Sum"] += row.FTHG - row.FTAG
            home_adv_dict["Goals"]["Squared Sum"] += math.pow(row.FTHG - row.FTAG, 2)
            home_adv_dict["SOT"]["Sum"] += row.HST - row.AST
            home_adv_dict["SOT"]["Squared Sum"] += math.pow(row.HST - row.AST, 2)
            home_adv_dict["Shots"]["Sum"] += row.HS - row.AS
            home_adv_dict["Shots"]["Squared Sum"] += math.pow(row.HS - row.AS, 2)
            home_adv_dict["Corners"]["Sum"] += row.HC - row.AC
            home_adv_dict["Corners"]["Squared Sum"] += math.pow(row.HC - row.AC, 2)

        elif match_date_time < start_date_time:
            pass
        elif match_date_time > start_date_time:
            break

    #Move on to the next week
    week += 1
    start_date_time = end_date_time

#Iterate through the betting log to find the total amount staked per week along with profit for Asian handicap
for week in betting_log:
    betting_log[week]["Profit"] = 0
    betting_log[week]["Stake"] = 0
    for bet in betting_log[week]:
        if bet not in ["Profit", "Stake"]:
            if "Result" in betting_log[week][bet]:
                betting_log[week]["Stake"] += 1
                if (betting_log[week][bet]["Result"] == betting_log[week][bet]["Selection"]):
                    betting_log[week]["Profit"] += betting_log[week][bet]["Price"] - 1
                elif (betting_log[week][bet]["Result"] == "win_void"):
                    if betting_log[week][bet]["Selection"] == "home":
                        betting_log[week]["Profit"] += (betting_log[week][bet]["Price"] - 1) * 0.5
                    elif betting_log[week][bet]["Selection"] == "away":
                        betting_log[week]["Profit"] += -0.5
                elif (betting_log[week][bet]["Result"] == "lose_void"):
                    if betting_log[week][bet]["Selection"] == "home":
                        betting_log[week]["Profit"] += -0.5
                    elif betting_log[week][bet]["Selection"] == "away":
                        betting_log[week]["Profit"] += (betting_log[week][bet]["Price"] - 1) * 0.5
                else:
                    betting_log[week]["Profit"] += -1

#Same as above but for the 1x2 market
for week in betting_log:
    betting_log[week]["Profit1X2"] = 0
    betting_log[week]["Stake1X2"] = 0
    for bet in betting_log[week]:
        if bet not in ["Profit", "Stake", "Profit1X2", "Stake1X2"]:
            if "Result1X2" in betting_log[week][bet]:
                betting_log[week]["Stake1X2"] += 1
                if (betting_log[week][bet]["Result1X2"] == betting_log[week][bet]["Selection1X2"]):
                    betting_log[week]["Profit1X2"] += betting_log[week][bet]["Price1X2"] - 1
                else:
                    betting_log[week]["Profit1X2"] += -1

pprint(betting_log)
# print(sum(betting_log[week]["Profit"] for week in betting_log) / sum(betting_log[week]["Stake"] for week in betting_log))
# print(sum(betting_log[week]["Profit"] for week in betting_log))

print(sum(betting_log[week]["Profit1X2"] for week in betting_log) / sum(betting_log[week]["Stake1X2"] for week in betting_log))
print(profit_1x2)

lines = []
for week in betting_log:
    for key in betting_log[week]:
        if key not in ["Profit", "Profit1X2", "Stake", "Stake1X2"]:
            if "Line" in betting_log[week][key]:
                line = float(betting_log[week][key]["Line"])
                selection = betting_log[week][key]["Selection"]
                if selection == "away":
                    line = -line
                lines.append(line)

ordered_lines = sorted(set(lines))

plt.figure()
plt.bar(ordered_lines, [lines.count(line) for line in ordered_lines], width = 0.1)
plt.xlabel("Line")
plt.ylabel("Frequency")
# plt.show()

weeks = []
profit = []
profit_1x2 = []
for week in betting_log:
    weeks.append(week)
    profit.append(betting_log[week]["Profit"])
    profit_1x2.append(betting_log[week]["Profit1X2"])


plt.figure()
plt.bar(weeks, profit)
plt.xlabel("Week")
plt.ylabel("Total Units Profit")
# plt.show()

plt.figure()
plt.bar(weeks, profit_1x2)
plt.xlabel("Week")
plt.ylabel("Total Units Profit")
# plt.show()

with open("betting_log_1.json", "w+") as outfile:
    json.dump(betting_log, outfile)

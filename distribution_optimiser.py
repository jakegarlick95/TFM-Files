import numpy as np
import pandas as pd
import json
import math
from pprint import pprint
import matplotlib.pyplot as plt
from grids import optimise_match, create_goals_grid, sim_match
import sys

observed_margins = []
simulated_margins = []

seasons = ["19_20", "20_21", "21_22", "22_23",
           "England_19_20", "England_20_21", "England_21_22", "England_22_23",
           "Germany_19_20", "Germany_20_21", "Germany_21_22", "Germany_22_23",
           "Italy_19_20", "Italy_20_21", "Italy_21_22", "Italy_22_23"]
# seasons = ["19_20"]

supremacies = []
draw_factors = []

np.random.seed(123456)

for season in seasons:
    print(season)
    filepath = "LaLiga/" + season + ".csv"

    season_data = pd.read_csv(filepath, on_bad_lines = "skip")

    for i, row in season_data.iterrows():
        #Extract pinnacle 1x2 prices
        prices_1x2 = [row.PSCH, row.PSCD, row.PSCA]

        #Pinnacle total goals prices
        prices_over_under = [row["PC>2.5"], row["PC<2.5"]]

        #Handicap line and prices
        handicap = row["AHCh"]
        prices_handicap = [row.PCAHH, row.PCAHA]

        prices_dict = {"1X2": prices_1x2,
                       "O/U": {"2.5": prices_over_under},
                       "AH": {str(handicap): prices_handicap}}

        #Run optimiser for this match
        lambdas = optimise_match(prices_dict)

        home_xg = lambdas[0]
        away_xg = lambdas[1]

        supremacies.append(abs(home_xg - away_xg))
        draw_factors.append(lambdas[2])

        #Simulate score for the match based on optimised parameters
        sim_score = sim_match(home_xg, away_xg, lambdas[2])

        #Log simulated and observed margins
        sim_margin = sim_score[0] - sim_score[1]
        observed_margin = row.FTHG - row.FTAG

        observed_margins.append(abs(observed_margin))
        simulated_margins.append(abs(sim_margin))

#Ordered vectors of margins along with their counts
observed_margin_vector = np.arange(min(observed_margins + simulated_margins), max(observed_margins + simulated_margins), 1)
observed_margin_count = [observed_margins.count(i) for i in np.arange(min(observed_margins + simulated_margins), max(observed_margins + simulated_margins))]

simulated_margin_vector = np.arange(min(observed_margins + simulated_margins), max(observed_margins + simulated_margins), 1)
simulated_margin_count = [simulated_margins.count(i) for i in np.arange(min(observed_margins + simulated_margins), max(observed_margins + simulated_margins))]

plt.figure()
plt.bar(observed_margin_vector, observed_margin_count, alpha = 0.5)
plt.bar(simulated_margin_vector, simulated_margin_count, alpha = 0.2, color = "red")
plt.xticks(observed_margin_vector)
plt.xlabel("Winning Margin")
plt.ylabel("Frequency")
plt.title("Observed Frequencies in Blue, Simulated Frequencies in Red")
plt.savefig("draw_factor_abs_bar_chart.png")
plt.show()

#Polyfit for draw factor
fit = np.polyfit(supremacies, draw_factors, 2)
#print(fit)

#Plot polyfit over plot of supremacy vs draw factor
plt.figure()
plt.scatter(supremacies, draw_factors)
xs = np.linspace(0, 4, 400)
plt.plot(xs, np.poly1d(fit)(xs), color = "red")
plt.xlabel("Absolute Supremacy")
plt.ylabel("Draw Inflation Factor")
plt.savefig("draw_factor_plot.png")
plt.show()

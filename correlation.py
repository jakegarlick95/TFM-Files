import pandas as pd
from pprint import pprint
import math
import json

data = pd.read_csv("2022_RMdSG_la_liga.csv", sep = ";")

correlations = {}

#Drop rows containing team averages for the season
data = data.drop(labels = [39 * i + 38 for i in range(20)] + [780], axis = 0)

conceded_correlations = {}

#Iterate through all columns and calculate correlation coefficients
for column in data:
    if column not in ["Goals", "Team", "match", "Conceded goals"]:
        corr = data[column].corr(data["Goals"])
        if not math.isnan(corr):
            correlations[column] = corr
        corr2 = data[column].corr(data["Conceded goals"])
        if not math.isnan(corr2):
            conceded_correlations[column] = corr2

#Sort based on absolute value in descending order (most correlated first)
sorted_correlations = sorted(correlations.items(), key=lambda item: abs(item[1]), reverse = True)

``` Comment back in if you want to save the JSON or pprint the output in the terminal``
# with open("sorted_correlations.json", "w+") as outfile:
#     json.dump(sorted_correlations, outfile)
# pprint(sorted_correlations)

sorted_conceded_correlations = sorted(conceded_correlations.items(), key = lambda item: abs(item[1]), reverse = True)

# with open("sorted_conceded_correlations.json", "w+") as outfile:
#     json.dump(sorted_conceded_correlations, outfile)
# pprint(sorted_conceded_correlations)

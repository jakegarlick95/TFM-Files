2022_RMdSG_la_liga.csv is the original CSV provided by Raul Martinez de Santos from EHU/UPV.

betting_log_1.json is output from the file first_model_pricing.py

betting_log_2.json is output from the file second_model.py

correlation.py is the file used to find the correlation of all recorded statistics with goals scored and goas conceded. This file outputs two JSON: sorted_correlations.json and sorted_conceded_correlations.json

distribution_optimiser.py is the file which was used to model the underlying distribution. It is currently importing the final version of the Poisson model from grids.py. For a given model, this file optimises over 5000+ matches to find close matched parameters for a bookmakers prices, then we simulate each match and compare the observed margins vs our simulated margins to test the accuracy of our distribution.

first_model_pricing.py is the first iteration of the model just using data found at football-data.co.uk
It uses the Poisson regression model calculated in first_model.R, along with some simulated home advantage values which update each week as our sample size of behind closed doors matches increases. It prices each match using this first model, then simulates bets on a week by week basis using real bookmaker prices. All results are logged and output to betting_log_1.json.

first_model.R is the file used to calculate the Poisson regression model for this first model.

fixture_order.py is a file which is used to output a JSON to ordered_fixtures.json, which gives each match per team a numerical index in time order, along with the relevant statistics for that match.

grids.py contains the function which creates our grid of probabilities for a particular model (currently the final approximately Poisson model with a draw inflation factor applied with the excess probability removed proportionally from all margins greater than or equal to 2). The function points_grid_generator is just to make the calculation of markets faster, namely, the functions for calculating 1x2, over/under total goals and Asian handicap. The function optimise_match takes in a set of input prices and then minimises the squared error between some market probabilities and probabilities for a given input to return optimal model parameters. The function sim_match simulates a match score given a grid of probabilities. result_asian_handicap is just used to result an Asian handicap market given a match score and a line.

home_advantage.py calculates home advantage values for relevant statistics over our training set of 650 matches which were played with crowds and also new values over the initial 152 matches played behind closed doors prior to the start of our testing set. It outputs the relevant information required to find the distributions of each home advantage value to the dictionary home_advantage_dict.json.

margin_function.py contains a function which takes in a set of margined market prices and outputs demargined probabilities.

ordered_data.py takes in the initial data set provided by Raul Martinez de Santos from EHU/UPV and puts all rows into chronological order by cross referencing matches with the dates which are contained in the file for the same season from football-data.co.uk. This outputs to ordered_data.csv.

second_model.py contains the second iteration of the Poisson regression model based on the detailed data provided by Raul Martinez de Santos from EHU/UPV. Similarly to the first model, it calculates the appropriate weighted averages for the input parameters to the Poisson regression and then prices each match, placing and logging bets where apropriate. The output is found in betting_log_2.json.

second_model.R was used to calculate the Poisson regression for this second model.

training_set.csv contains the training set of the first Poisson regression, namely, 1300 rows corresponding to the statistics per team of the 650 matches made up of the entire 2018/2019 season and the 270 matches of 2019/2020 prior to the suspension of the league due to the Covid pandemic.

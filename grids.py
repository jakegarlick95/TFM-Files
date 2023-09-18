import numpy as np
from scipy.stats import poisson
from margin_function import remove_margin_powerwise
from scipy import optimize
import math
from pprint import pprint

def create_goals_grid(lx, ly, df):

    home_goals = poisson.pmf(np.arange(0, 15, 1), lx)
    away_goals = poisson.pmf(np.arange(0, 15, 1), ly)

    #Add remaining miniscule probability so that it sums to 1
    home_goals[-1] += 1 - np.sum(home_goals)
    away_goals[-1] += 1 - np.sum(away_goals)

    goals_grid = np.outer(home_goals, away_goals)

    less_than_equal_to_one_prob = 0

    #Sum all draws and 1 goal margins then multiply diagonal
    for i in range(len(home_goals)):
        less_than_equal_to_one_prob += goals_grid[i][i]
        if i < len(home_goals) - 1:
            less_than_equal_to_one_prob += goals_grid[i+1][i]
            less_than_equal_to_one_prob += goals_grid[i][i+1]
        goals_grid[i][i] *= df

    prob_to_remove = np.sum(goals_grid) - 1
    total_prob_to_change = 1 - less_than_equal_to_one_prob

    #Proportionally remove added on amount from all margins of 2+
    for i in range(len(home_goals)):
        for j in range(len(away_goals)):
            if abs(i - j) > 1:
                goals_grid[i][j] -= prob_to_remove * (goals_grid[i][j] / total_prob_to_change)

    return goals_grid / np.sum(goals_grid)

def points_grid_generator(points_grid):

    #Create this just because it is faster for pricing markets
    grid_length_home = len(points_grid)
    grid_length_away = len(points_grid[0])
    points_diff_grid = np.fromfunction(lambda i, j: i - j, (grid_length_home, grid_length_away))
    points_total_grid = np.fromfunction(lambda i, j: i + j, (grid_length_home, grid_length_away))
    return {"points_diff_grid": points_diff_grid, "points_total_grid": points_total_grid}

def calc_1X2(points_grid, points_grid_dict):
    points_diff_grid = points_grid_dict["points_diff_grid"]

    home_probability = np.sum(points_grid[points_diff_grid > 0])
    draw_probability = np.sum(points_grid[points_diff_grid == 0])
    away_probability = np.sum(points_grid[points_diff_grid < 0])

    norm_home_probability = home_probability/(home_probability + draw_probability + away_probability)
    norm_draw_probability = draw_probability/(home_probability + draw_probability + away_probability)
    norm_away_probability = away_probability/(home_probability + draw_probability + away_probability)
    return norm_home_probability, norm_draw_probability, norm_away_probability

def calc_over_under(points_grid, points_grid_dict, strike):
    strike = float(strike)
    points_total_grid = points_grid_dict["points_total_grid"]

    over_probability = np.sum(points_grid[points_total_grid > strike])
    under_probability = np.sum(points_grid[points_total_grid < strike])

    norm_over_probability = over_probability/(over_probability+under_probability)
    norm_under_probability = under_probability/(over_probability+under_probability)

    return norm_over_probability, norm_under_probability

def calc_asian_handicap(points_grid, points_grid_dict, strike):

    strike = float(strike)
    points_diff_grid = points_grid_dict["points_diff_grid"]

    if (strike % 1 == 0) or ((strike - 0.5) % 1 == 0):

        #Simple half or whole lines

        home_probability = np.sum(points_grid[points_diff_grid + strike > 0])
        away_probability = np.sum(points_grid[points_diff_grid + strike < 0])

        norm_home_probability = home_probability / (home_probability + away_probability)
        norm_away_probability = away_probability / (home_probability + away_probability)

        return norm_home_probability, norm_away_probability

    elif (strike + 0.25) % 1 == 0:

        #First special case - lines like +0.75, -0.25, -1.25

        strike_1 = strike - 0.25
        strike_2 = strike + 0.25

        void_prob = np.sum(points_grid[points_diff_grid + strike_2 == 0]) / 2
        home_prob = np.sum(points_grid[points_diff_grid + strike_2 > 0])
        away_prob = np.sum(points_grid[points_diff_grid + strike_2 < 0])

        new_home_prob = home_prob / (1 - void_prob)
        new_away_prob = (away_prob + void_prob) / (1 - void_prob)

        return new_home_prob, new_away_prob

    elif (strike - 0.25) % 1 == 0:

        #Second special case - lines like +0.25, -0.75

        strike_1 = strike + 0.25
        strike_2 = strike - 0.25

        void_prob = np.sum(points_grid[points_diff_grid + strike_2 == 0]) / 2
        home_prob = np.sum(points_grid[points_diff_grid + strike_2 > 0])
        away_prob = np.sum(points_grid[points_diff_grid + strike_2 < 0])

        new_home_prob = (home_prob + void_prob) / (1 - void_prob)
        new_away_prob = away_prob / (1 - void_prob)

        return new_home_prob, new_away_prob

def optimise_match(prices_dict):

    #Convert margined market prices to demargined probs
    probs_dict = {'1X2': 0, 'O/U': {}, "AH": {}}
    for market in prices_dict:
        if market == '1X2':
            prices = prices_dict[market]
            raw_prices = remove_margin_powerwise(prices)
            probs_dict['1X2'] = [1 / raw_prices[i] for i in range(3)]
        elif market == 'O/U':
            for line in prices_dict['O/U']:
                prices = prices_dict[market][line]
                raw_prices = remove_margin_powerwise(prices)
                probs_dict['O/U'][line] = [1 / raw_prices[i] for i in range(2)]
        elif market == "AH":
            for line in prices_dict["AH"]:
                prices = prices_dict[market][line]
                raw_prices = remove_margin_powerwise(prices)
                probs_dict["AH"][line] = [1 / raw_prices[i] for i in range(2)]

    def calc_squared_error(inputs):

        #For set of inputs, create grids and price markets
        goals_grid = create_goals_grid(inputs[0], inputs[1], inputs[2])
        points_grid_dict = points_grid_generator(goals_grid)
        our_probs = {}
        our_probs['1X2'] = calc_1X2(goals_grid, points_grid_dict)
        our_probs['O/U'] = {}
        for line in prices_dict['O/U']:
            our_probs['O/U'][line] = calc_over_under(goals_grid, points_grid_dict, line)
        our_probs["AH"] = {}
        for line in prices_dict["AH"]:
            our_probs["AH"][line] = calc_asian_handicap(goals_grid, points_grid_dict, line)
        error = 0

        #Calculate squared error of our probs vs. demargined market probs
        for k in our_probs.keys():
            if k == '1X2':
                for i, prob in enumerate(our_probs[k]):
                    error += math.pow(prob-probs_dict[k][i], 2)

            elif k in ['O/U', "AH"]:
                for strike in our_probs[k]:
                    for i, prob in enumerate(our_probs[k][strike]):
                        error += math.pow(prob-probs_dict[k][strike][i], 2)

        return error

    #Minimise squared error function
    expected_goals = optimize.fmin(calc_squared_error, (1.5, 1.5, 1.05), disp = False)

    return expected_goals

def sim_match(l_h, l_a, df):

    #Creates grid, ravels to list and then the cumulative sum
    goals_grid = create_goals_grid(l_h, l_a, df)
    c = goals_grid.ravel().cumsum()

    #Generates random number, finds corresponding list index, unravels to 2D score
    score = np.unravel_index(c.searchsorted(np.random.uniform(0, c[-1])), goals_grid.shape)
    return list(score)

def result_asian_handicap(margin, strike):

    strike = float(strike)

    if (strike - 0.5) % 1 == 0:
        if margin + strike > 0:
            return "home"
        elif margin + strike < 0:
            return "away"
    if strike % 1 == 0:
        if margin + strike > 0:
            return "home"
        elif margin + strike < 0:
            return "away"
        elif margin + strike == 0:
            return "void"
    if (strike - 0.25) % 1 == 0:
        if margin + (strike - 0.25) > 0:
            return "home"
        elif margin + (strike - 0.25) < 0:
            return "away"
        elif margin + (strike - 0.25) == 0:
            return "win_void"
    if (strike + 0.25) % 1 == 0:
        if margin + (strike + 0.25) > 0:
            return "home"
        elif margin + (strike + 0.25) < 0:
            return "away"
        elif margin + (strike + 0.25) == 0:
            return "lose_void"

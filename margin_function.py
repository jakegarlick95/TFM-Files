from scipy import optimize
import math

def remove_margin_powerwise(prices):

    #Convert to probs
    margin_probs = [1 / price for price in prices]

    def remove_x_margin(x):
        #Remove specified amount of margin applied
        return abs(sum([prob**x for prob in margin_probs]) - 1)

    #Minimises difference between sum of demargined probs and 1
    margin = optimize.fmin(remove_x_margin, 1)

    demargined_probs = [prob**margin for prob in margin_probs]

    return [1 / prob for prob in demargined_probs]

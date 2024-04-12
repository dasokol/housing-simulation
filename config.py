"""
global vars and config parameters for simulation
"""


# number of monte carlo simulations to run
N_SIMULATIONS = 1000
# simulate n years into future
N_YEARS = 10

# from google calculator on https://www.google.com/search?q=mortgage+rate+average
# for 800+ credit score in VA with 20% down and 600k loan amount 15-yr fixed, assuming 0 points; 04/04/24
MORTGAGE_RATE_MEAN = 0.06459
# it's hard to say what this is, and it tends to vary, but I chose value from
# https://www.freddiemac.com/research/insight/20230216-when-rates-are-higher-borrowers-who-shop-around-save
MORTGAGE_RATE_STD_DEV = 0.0040
# if set, then the simulations assume you've shopped around for a better-than-average mortgage rate
# specifically, it sets the mortgage rate mean to be 1 std dev lower when drawing random gaussian simulation values (84th percentile)
ASSUME_GOOD_LOAN_FOUND = False
# same as good loan, except mean is set to 2 std dev lower (98th percentile); if both set, this value is used
ASSUME_GREAT_LOAN_FOUND = False

# property purchase price range you'd like to investigate
PROPERTY_PRICE_MEAN = 750000
PROPERTY_PRICE_STD_DEV = 50000
DOWN_PAYMENT = 0.2

# inflation
# https://www.gurufocus.com/market/us-inflation-contributors
INFLATION_MEAN = 0.0239
INFLATION_STD_DEV = 0.0123
# TODO use some function to determine multiyear trends for these params; for instance, if inflation is high one year it's likely to still be somewhat high the next

# stock market performance, simulates opportunity cost of buying (ie you could put all this money into market instead of a property)
# http://www.moneychimp.com/articles/volatility/standard_deviation.htm#:~:text=An%20S%26P%20500%20index%20fund,interest%20at%20a%20guaranteed%20rate.
MARKET_RETURN_MEAN = 0.09
MARKET_RETURN_STD_DEV = 0.15

# housing market performance, simulates what you might be able to sell property for
# surprisingly hard to find already-calculated data on this, just guessing it
HOUSING_RETURN_MEAN = 0.038
HOUSING_RETURN_STD_DEV = 0.03
# encompasses things like HOA (assuming it's a condo), insurance, taxes, etc
ANNUAL_HOUSING_COST_MEAN = 17000
ANNUAL_HOUSING_COST_STD_DEV = 1500
# if set, then the simulations assume your location has high-than-average growth
# specifically, it sets the housing return mean to be 1 std dev higher when drawing random gaussian simulation values (84th percentile)
ASSUME_GOOD_HOUSING_GROWTH = False
# same as good, except mean is set to 2 std dev higher (98th percentile); if both set, this value is used
ASSUME_GREAT_HOUSING_GROWTH = False

# rental performance
# from https://www.rentcafe.com/average-rent-market-trends/us/va/arlington/ and https://www.rent.com/virginia/arlington/ashton-heights-neighborhood
# 2 bedroom cost in Arlington
MONTHLY_RENT_COST_MEAN = 3095
MONTHLY_RENT_COST_STD_DEV = 175
# just good guesses; assumes you stay in each place for a few years (with price increases from landlord) and move to a cheaper place when it gets too expensive
ANNUAL_RENT_COST_GROWTH_RATE_MEAN = 0.06
ANNUAL_RENT_COST_GROWTH_RATE_STD_DEV = 0.03
AMORTIZED_ANNUAL_MOVING_COST_MEAN = 400
AMORTIZED_ANNUAL_MOVING_COST_STD_DEV = 100
# represents concessions from moving; does not capture rent price drop, as that is calculated based on expected rent cost growth
AMORTIZED_ANNUAL_MOVING_SAVINGS_MEAN = 1000
AMORTIZED_ANNUAL_MOVING_SAVINGS_STD_DEV = 200

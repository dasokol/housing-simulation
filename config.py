"""
global vars and config parameters for simulation
"""
# constant vals
MONTHS_PER_YEAR = 12.0


# https://www.gurufocus.com/market/us-inflation-contributors
ANNUAL_INFLATION_MEAN = 0.0239
ANNUAL_INFLATION_STD_DEV = 0.0123


# NOTES:
# parameters containing the term "annual" as a substring means they'll be recalculated every year of the simulation
# if a parameter has a corresponding <parameter>_growth_rate parameter, the latter determines future values of the former
# annual_rental_market_price* must be listed in config before annual_rental_cost* to ensure they're populated first since the latter rely on the former
CONFIG = {
    # these are fixed and not drawn at random
    "fixed_parameters": {
        # number of monte carlo simulations to run
        "n_simulations": 1,
        # simulate n years into future; at end of simulation, we liquidate all assets and compare net worth of owner vs renter
        "n_years": 20,
        # fraction paid down on home purchase
        "down_payment": 0.2,
        "loan_term_years": 15,
        # ratio of mortgage principal and interest (not including taxes or insurance) to gross, pre-tax income; rule of thumb based on 28% rule
        "mortgage_to_income_ratio": 0.25,
        # TODO make income grow with inflation? possible including good + great income growth assumptions, or maybe this doesn't really matter
        # TODO add savings rate, probably 0.33 because investing all remaining money is too unrealistic because of taxes and non-housing cost of living
        # TODO add prior net worth, probably 250k to defray cost of down payment so simulation is cash-flow positive (for simplification)
        # assume renter moves to new rental place every n_years_rental_move
        "n_years_rental_move": 4,
        # if set, then the simulations assume you've shopped around for a better-than-average mortgage rate
        # specifically, it sets the mortgage rate mean to be 1 std dev lower when drawing random gaussian simulation values (84th percentile)
        "assume_good_loan_found": False,
        # same as good loan, except mean is set to 2 std dev lower (98th percentile); if both set, this value is used
        "assume_great_loan_found": False,
        # if set, then the simulations assume your location has high-than-average growth
        # specifically, it sets the housing return mean to be 1 std dev higher when drawing random gaussian simulation values (84th percentile)
        "assume_good_housing_growth": False,
        # same as good, except mean is set to 2 std dev higher (98th percentile); if both set, this value is used
        "assume_great_housing_growth": False,
        # TODO implement refinancing
        # simulates refinancing mortgage to a lower rate half way through simulation
        "simulate_refinancing": False,
        # TODO add a nongaussian distribution parameter which allows for drawing random values from user-specified distribution?
        # TODO add parameter for early mortgage payments
    },

    "mortgage_rate": {
        # from google calculator on https://www.google.com/search?q=mortgage+rate+average
        # for 800+ credit score in va with 20% down and 600k loan amount 15-yr fixed, assuming 0 points; 04/04/24
        "mean": 0.06459,
        # it's hard to say what this is, and it tends to vary, but I chose value from
        # https://www.freddiemac.com/research/insight/20230216-when-rates-are-higher-borrowers-who-shop-around-save
        "std_dev": 0.0040,
    },

    # property purchase price range you'd like to investigate
    "property_price": {
        "mean": 750000,
        "std_dev": 50000,
    },

    "annual_inflation": {
        "mean": ANNUAL_INFLATION_MEAN,
        "std_dev": ANNUAL_INFLATION_STD_DEV,
        # TODO use some function to determine multiyear trends for these params; for instance, if inflation is high one year it's likely to still be somewhat high the next
    },

    # stock market performance, simulates opportunity cost of buying (ie you could put all this money into market instead of a property)
    "annual_stock_market_return": {
        # http://www.moneychimp.com/articles/volatility/standard_deviation.htm#:~:text=an%20s%26p%20500%20index%20fund,interest%20at%20a%20guaranteed%20rate.
        "mean": 0.09,
        "std_dev": 0.15,
    },

    # housing market performance, simulates what you might be able to sell property for
    "annual_housing_market_return": {
        # surprisingly hard to find already-calculated data on this, just guessing it
        "mean": 0.038,
        "std_dev": 0.05,
    },
    
    # cost of owning a house, which encompasses things like hoa (assuming it's a condo), insurance, taxes, repairs, etc
    "annual_homeowner_cost": {
        "mean": 17500,
        "std_dev": 1500,
    },
    # TODO should we add housing cost growth? i think taxes don't go up until property is sold, but insurance and hoa could rise

    # captures average rental price in the market which renter can get if he moves
    "annual_rental_market_price": {
        # from https://www.rentcafe.com/average-rent-market-trends/us/va/arlington/ and https://www.rent.com/virginia/arlington/ashton-heights-neighborhood
        # 2 bedroom cost in arlington
        "mean": 3095*12,
        "std_dev": 175*12,
    },

    "annual_rental_market_price_growth_rate": {
        # assuming growth at inflation rate above
        "mean": ANNUAL_INFLATION_MEAN,
        "std_dev": ANNUAL_INFLATION_STD_DEV,
    },
    
    # captures realized rental performance for renter
    "annual_rental_cost": {
        "mean": 3095*12,
        "std_dev": 175*12,
    },

    "annual_rental_cost_growth_rate": {
        # guesses based on personal experience
        # assumes you stay in each place for n_years_rental_move years (landlord raises prices yearly), moving to a new place when current is too expensive
        "mean": 0.06,
        "std_dev": 0.03,
    },

    # amortized params don't happen every year in real life, but we amortize them so we can apply them each year in the simulation for simplicity
    # represents costs involved with moving between rentals, assuming you move roughly every 3-4 years
    "amortized_annual_moving_cost": {
        "mean": 400,
        "std_dev": 100,
    },
    
    # represents rent concessions, etc. gained from moving; does not capture rent price drop, as that is calculated based on expected rent cost growth
    "amortized_annual_moving_saving": {
        "mean": 1000,
        "std_dev": 200,
    },
}

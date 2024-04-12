"""
global vars and config parameters for simulation
"""


CONFIG = {
    # these are fixed and not drawn at random
    "fixed_parameters": {
        # number of monte carlo simulations to run
        "n_simulations": 1000,
        # simulate n years into future
        "n_years": 10,
        # fraction paid down on home purchase
        "down_payment": 0.2,
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
    },

    "mortgage_rate": {
        # from google calculator on https://www.google.com/search?q=mortgage+rate+average
        # for 800+ credit score in va with 20% down and 600k loan amount 15-yr fixed, assuming 0 points; 04/04/24
        "mean": 0.06459,
        # it's hard to say what this is, and it tends to vary, but i chose value from
        # https://www.freddiemac.com/research/insight/20230216-when-rates-are-higher-borrowers-who-shop-around-save
        "std_dev": 0.0040,
    },

    # property purchase price range you'd like to investigate
    "property_price": {
        "mean": 750000,
        "std_dev": 50000,
    },

    "inflation": {
        # https://www.gurufocus.com/market/us-inflation-contributors
        "mean": 0.0239,
        "std_dev": 0.0123,
        # TODO use some function to determine multiyear trends for these params; for instance, if inflation is high one year it's likely to still be somewhat high the next
    },

    # stock market performance, simulates opportunity cost of buying (ie you could put all this money into market instead of a property)
    "market_return": {
        # http://www.moneychimp.com/articles/volatility/standard_deviation.htm#:~:text=an%20s%26p%20500%20index%20fund,interest%20at%20a%20guaranteed%20rate.
        "mean": 0.09,
        "std_dev": 0.15,
    },

    # housing market performance, simulates what you might be able to sell property for
    "housing_return": {
        # surprisingly hard to find already-calculated data on this, just guessing it
        "mean": 0.038,
        "std_dev": 0.03,
    },
    
    # cost of owning a house, which encompasses things like hoa (assuming it's a condo), insurance, taxes, etc
    "annual_housing_cost": {
        "mean": 17000,
        "std_dev": 1500,
    },
    # TODO should we add housing cost growth? i think taxes don't go up until property is sold, but insurance and hoa could rise

    # rental performance
    "annual_rent_cost": {
        # from https://www.rentcafe.com/average-rent-market-trends/us/va/arlington/ and https://www.rent.com/virginia/arlington/ashton-heights-neighborhood
        # 2 bedroom cost in arlington
        "mean": 3095*12,
        "std_dev": 175*12,
        # just good guesses; assumes you stay in each place for a few years (with price increases from landlord) and move to a cheaper place when it gets too expensive
        "growth_rate_mean": 0.06,
        "growth_rate_std_dev": 0.03,
    },

    # represents costs involved with moving between rentals
    "amortized_annual_moving_cost": {
        "mean": 400,
        "std_dev": 100,
    },
    # represents concessions from moving; does not capture rent price drop, as that is calculated based on expected rent cost growth
    "amortized_annual_moving_savings": {
        "mean": 1000,
        "std_dev": 200,
    },
}

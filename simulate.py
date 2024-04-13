"""
Monte Carlo simulation to predict many different possible housing outcomes
usage:
    # configure values you want in config.py and then run:
    python simulate.py
"""
from config import *
import random
import json


def generate_params(fixed_params):
    """
    generate the parameters required for one simulation
    these are generated based on random things like drawing from normal distributions using parameters that make sense
    returns dict with values
    """
    simulation_params = {}
    for param_base_name in CONFIG:
        params = CONFIG[param_base_name]
        param_mean = params["mean"]
        param_std_dev = params["std_dev"]

        # handle fixed params assumptions
        if param_base_name == "mortgage_rate":
            if fixed_params["assume_great_loan_found"]:
                param_mean -= param_std_dev * 2
            elif fixed_params["assume_good_loan_found"]:
                param_mean -= param_std_dev
        elif param_base_name == "annual_housing_market_return":
            if fixed_params["assume_great_housing_growth"]:
                param_mean += param_std_dev * 2
            elif fixed_params["assume_good_housing_growth"]:
                param_mean += param_std_dev
        
        # if param is calculated annually, we generate each year's value (if no corresponding growth_rate param); otherwise, it remains same every year of simulation
        # if there's a <param_base_name>_growth_rate param, then we just generate the first value here and generate the others using the growth_rate param later
        if "annual" in param_base_name and not f"{param_base_name}_growth_rate" in CONFIG:
            param_value = []
            n_years_to_generate = fixed_params["n_years"]
            # if it's a growth_rate param, we already have starting value and only need to generate n_years - 1 more values
            if "growth_rate" in param_base_name:
                n_years_to_generate -= 1
            for _ in range(n_years_to_generate):
                # drawing from normal distribution to get value for parameter
                annual_value = random.gauss(mu=param_mean, sigma=param_std_dev)
                param_value.append(annual_value)
        else:
            param_value = random.gauss(mu=param_mean, sigma=param_std_dev)
        
        simulation_params[param_base_name] = param_value

    # once all <param_base_name>_growth_rate params are generated, we can then generate the rest of their param_base_name counterpart values
    for param_base_name in simulation_params:
        param_growth_rates = simulation_params.get(f"{param_base_name}_growth_rate")
        # only consider params with corresponding growth_rate counterpart
        if param_growth_rates is None:
            continue

        current_param_value = simulation_params[param_base_name]
        param_value = [current_param_value]
        for i, param_growth_rate in enumerate(param_growth_rates):
            # simulate annual_rental_cost changes based on rental moves every n_years_rental_move years; then param_value is reset to market price
            if param_base_name == "annual_rental_cost" and (len(param_value) + 1) % fixed_params["n_years_rental_move"] == 0:
                # i is one year behind simulation year, so we add one to get current year market price
                current_param_value = simulation_params["annual_rental_market_price"][i + 1]
            else:
                current_param_value *= (1.0 + param_growth_rate)
            
            param_value.append(current_param_value)

        simulation_params[param_base_name] = param_value

    return simulation_params


def calculate_monthly_mortgage_principal_and_interest(property_price, mortgage_rate, loan_term_years, down_payment):
    """
    calculate the monthly mortgage amount using simulation param values
    m = p(i * (1 + i)**n) / ((1 + i)**n - 1)
    https://www.rocketmortgage.com/learn/how-to-calculate-mortgage
    """
    p = property_price * (1.0 - down_payment)
    i = mortgage_rate / MONTHS_PER_YEAR
    n = loan_term_years * MONTHS_PER_YEAR
    m = (p * (i * (1.0 + i)**n)) / ((1.0 + i)**n - 1.0)

    return m, p, i, n


def calculate_remaining_mortgage_balance(p, i, n, s):
    """
    calculate the remaining mortgage balance using mortgage-related values
    https://www.mortgagequote.com/calculate-a-mortgage-payoff.php
    b = p((1 + i)**n - (1 + i)**s) / (-1 + (1 + i)**n)
    """
    return p*((1 + i)**n - (1 + i)**s) / (-1 + (1 + i)**n)


def run_homeowner_simulation(fixed_params, simulation_params):
    """
    simulates homeowner performance into the future
    returns the property value at the end of the simulation period and a list of nominal (not inflation adjusted) annual housing payment sums
    """
    property_price = simulation_params["property_price"]
    mortgage_rate = simulation_params["mortgage_rate"]
    loan_term_years = fixed_params["loan_term_years"]
    down_payment = fixed_params["down_payment"]

    monthly_mortgage_principal_and_interest, principal, interest_rate, n_payments_total = calculate_monthly_mortgage_principal_and_interest(
        property_price, mortgage_rate, loan_term_years, down_payment)
    annual_mortgage_principal_and_interest = monthly_mortgage_principal_and_interest * MONTHS_PER_YEAR
    # simulate property price change
    current_property_value = property_price
    for housing_market_return_value in simulation_params["annual_housing_market_return"]:
        current_property_value *= (1.0 + housing_market_return_value)

    annual_homeowner_costs = simulation_params["annual_homeowner_cost"]
    annual_total_homeowner_costs = []
    n_years = fixed_params["n_years"]
    for i in range(n_years):
        current_year_total_housing_cost = annual_homeowner_costs[i]
        # stop mortgage payments after principal and interest paid off, i is number of years paid so far
        if i < loan_term_years:
            current_year_total_housing_cost += annual_mortgage_principal_and_interest
        
        annual_total_homeowner_costs.append(current_year_total_housing_cost)

    # add down payment to first year
    down_payment_amount = property_price * down_payment
    annual_total_homeowner_costs[0] += down_payment_amount

    remaining_mortgage_balance = 0.0
    n_payments_remaining = max((loan_term_years - n_years) * MONTHS_PER_YEAR, 0)
    # if n_years is less than loan_term_years, then we still owe money on mortgage;
    if n_payments_remaining > 0:
        n_payments_made = n_payments_total - n_payments_remaining
        remaining_mortgage_balance = calculate_remaining_mortgage_balance(principal, interest_rate, n_payments_total, n_payments_made)
    
    return current_property_value, annual_total_homeowner_costs, remaining_mortgage_balance


def run_renter_simulation(fixed_params, simulation_params, annual_total_homeowner_costs):
    """
    simulates renter performance into the future
    also simulates investing money left over from not purchasing property into stock market
    returns the stock value at the end of the simulation period and a list of nominal (not inflation adjusted) annual rental payment sums
    """
    annual_total_renter_costs = []
    annual_rental_costs = simulation_params["annual_rental_cost"]
    amortized_annual_moving_costs = simulation_params["amortized_annual_moving_cost"]
    amortized_annual_moving_savings = simulation_params["amortized_annual_moving_saving"]
    for i in range(fixed_params["n_years"]):
        current_year_total_rental_cost = annual_rental_costs[i] + amortized_annual_moving_costs[i] - amortized_annual_moving_savings[i]
        annual_total_renter_costs.append(current_year_total_rental_cost)

    current_stock_value = 0.0
    annual_stock_market_returns = simulation_params["annual_stock_market_return"]
    for i in range(fixed_params["n_years"]):
        # TODO account for homeowner stock investment in years when homeowner payments are less than renter payments?
        renter_surplus_cash = annual_total_homeowner_costs[i] - annual_total_renter_costs[i]
        # investing cash up front for simplicity; this is slightly inaccurate since renters pay monthly in reality and stocks compound almost continuously
        if renter_surplus_cash > 0:
            current_stock_value += renter_surplus_cash

        current_stock_value *= (1.0 + annual_stock_market_returns[i])
    
    return current_stock_value, annual_total_renter_costs


def run_simulation(fixed_params):
    """
    run a simulation iteration
    """
    simulation_params = generate_params(fixed_params)
    print("Running simulation with parameters:")
    print(json.dumps(simulation_params, indent=4))
    end_property_value, annual_total_homeowner_costs, remaining_mortgage_balance = run_homeowner_simulation(fixed_params, simulation_params)
    end_stock_value, annual_total_renter_costs = run_renter_simulation(fixed_params, simulation_params, annual_total_homeowner_costs)
    # TODO calculate value after property sale, ie taxes, selling fees, etc.
    # TODO calculate value after stock sale, ie taxes, selling fees, etc.

    print(f"End property value: {end_property_value}")
    print(f"Annual total homeowner costs: {annual_total_homeowner_costs}")
    print(f"Remaining mortgage balance: {remaining_mortgage_balance}")
    print(f"End stock value: {end_stock_value}")
    print(f"Annual total renter costs: {annual_total_renter_costs}")
    

def main():
    # TODO add command that reads user-specified mortgage values, fixes these, and then runs the simulations
    fixed_params = CONFIG.pop("fixed_parameters")
    for i in range(fixed_params["n_simulations"]):
        run_simulation(fixed_params)


if __name__=="__main__":
    main()

"""
Monte Carlo simulation to predict many different possible housing outcomes
usage:
    # configure values you want in config.py and then run:
    python simulate.py
    python simulate.py --interactive # -i for short, allows you to enter your mortgage and income info
"""
from config import *
import random
import json
import argparse
import statistics


def parse_input(fixed_params):
    """
    read CLI arguments and act on them
    modifies fixed_params based on user input if interactive is set
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interactive", dest="interactive", default=False, help="Interactively enter values for mortgage and income", type=bool,
                        action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    # interactive command reads user-specified income and mortgage values, fixes these, and then runs the simulations
    if args.interactive:
        print("Running interactive mode. Please answer the questions. If any information is left out, we'll use simulated defaults.")
        annual_income = input("What is your annual gross income? E.g. 123456.78.\n")
        if annual_income:
            annual_income = float(annual_income)
        initial_net_worth = input("What is your net worth?\n")
        if initial_net_worth:
            initial_net_worth = float(initial_net_worth)
        mortgage_rate = input("What is your mortgage rate percentage? E.g. 6.78.\n")
        if mortgage_rate:
            mortgage_rate = float(mortgage_rate) / 100.0
        property_price = input("What is your home's purchase price?\n")
        if property_price:
            property_price = float(property_price)

        fixed_params["annual_income"] = annual_income
        fixed_params["initial_net_worth"] = initial_net_worth
        fixed_params["mortgage_rate"] = mortgage_rate
        fixed_params["property_price"] = property_price


def fmt_dollars(amount):
    """
    format amount as dollars with commas
    """
    return '${:,.2f}'.format(amount)


def generate_params(fixed_params):
    """
    generate the parameters required for one simulation
    these are generated based on random things like drawing from normal distributions using parameters that make sense
    returns dict with values
    """
    simulation_params = {}
    for param_base_name in CONFIG:
        # if fixed value set, it means we override with user interactive value
        param_fixed_value = fixed_params.get(param_base_name)
        if param_fixed_value:
            simulation_params[param_base_name] = param_fixed_value
            continue
        
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


def calculate_stock_assets(annual_income, annual_total_costs, fixed_params, simulation_params):
    """
    calculate value of stock assets at end of simulation
    for simplicity, we assume annual income stays same and we ignore other cost of living and taxes
    these can be ignored since they're the exact same and ignored in both homeowner and renter simulations
    """
    n_years = fixed_params["n_years"]
    taxes_and_nonhousing_cost_of_living_to_income_ratio = fixed_params["taxes_and_nonhousing_cost_of_living_to_income_ratio"]
    initial_net_worth = fixed_params["initial_net_worth"]
    annual_stock_market_returns = simulation_params["annual_stock_market_return"]
    current_stock_value = 0.0
    for i in range(n_years):
        surplus_cash = (annual_income * (1.0 - taxes_and_nonhousing_cost_of_living_to_income_ratio)) - annual_total_costs[i]
        # add net worth into surplus cash for first year so we're cash positive after down payment
        if i == 0:
            surplus_cash += initial_net_worth
        
        # investing cash up front for simplicity; this is slightly inaccurate since most costs are monthly in reality and stocks compound almost continuously
        if surplus_cash > 0:
            current_stock_value += surplus_cash
        else:
            print(f"WARNING: annual costs exceed annual income by ${abs(surplus_cash)}")

        current_stock_value *= (1.0 + annual_stock_market_returns[i])

    return current_stock_value


def run_homeowner_simulation(fixed_params, simulation_params):
    """
    simulates homeowner performance into the future
    also simulates investing money left over from not paying rent into stock market
    returns the property value at the end of the simulation period, a list of nominal (not inflation adjusted) annual housing payment sums,
    remaining mortgage balance, annual income, stock_assets
    """
    property_price = simulation_params["property_price"]
    mortgage_rate = simulation_params["mortgage_rate"]
    loan_term_years = fixed_params["loan_term_years"]
    down_payment = fixed_params["down_payment"]

    monthly_mortgage_principal_and_interest, principal, interest_rate, n_payments_total = calculate_monthly_mortgage_principal_and_interest(
        property_price, mortgage_rate, loan_term_years, down_payment)
    annual_mortgage_principal_and_interest = monthly_mortgage_principal_and_interest * MONTHS_PER_YEAR
    annual_income = fixed_params.get("annual_income")
    if not annual_income:
        annual_income = annual_mortgage_principal_and_interest / fixed_params["mortgage_to_income_ratio"]
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

    stock_assets = calculate_stock_assets(annual_income, annual_total_homeowner_costs, fixed_params, simulation_params)
    
    return current_property_value, annual_total_homeowner_costs, remaining_mortgage_balance, annual_income, stock_assets


def run_renter_simulation(fixed_params, simulation_params, annual_total_homeowner_costs, annual_income):
    """
    simulates renter performance into the future
    also simulates investing money left over from not purchasing property into stock market
    returns the stock value at the end of the simulation period and a list of nominal (not inflation adjusted) annual rental payment sums
    """
    annual_total_renter_costs = []
    annual_rental_costs = simulation_params["annual_rental_cost"]
    amortized_annual_moving_costs = simulation_params["amortized_annual_moving_cost"]
    amortized_annual_moving_savings = simulation_params["amortized_annual_moving_saving"]
    n_years = fixed_params["n_years"]
    for i in range(n_years):
        current_year_total_rental_cost = annual_rental_costs[i] + amortized_annual_moving_costs[i] - amortized_annual_moving_savings[i]
        annual_total_renter_costs.append(current_year_total_rental_cost)

    stock_assets = calculate_stock_assets(annual_income, annual_total_renter_costs, fixed_params, simulation_params)
    
    return stock_assets, annual_total_renter_costs


def liquidate_all_assets(is_married, property_price, end_property_value, remaining_mortgage_balance, homeowner_stock_assets, renter_stock_assets):
    """
    calculate both homeowner and renter net worth by simulating sale of all assets
    considers taxes as well also considers property sale fees
    assumes all stock and home value (minus home purchase price) is long term capital gain for simplicity
    uses 15% long term capital gain rate since we'd likely be selling gradually and not pushing ourselves into the ultra-high 20% bracket
    return homeowner_net_worth, renter_net_worth
    """
    long_term_capital_gains_tax_rate = 0.15
    property_capital_gain = end_property_value - property_price
    property_capital_gain_exempt_amount = 500000 if is_married else 250000
    property_capital_gain_taxable_amount = max(property_capital_gain - property_capital_gain_exempt_amount, 0)
    property_capital_gain_total_tax = property_capital_gain_taxable_amount * long_term_capital_gains_tax_rate
    # miscellaneous selling fees, assuming 7.5% for simplicity
    selling_cost_rate = 0.075
    selling_cost_amount = end_property_value * selling_cost_rate
    homeowner_net_worth = end_property_value - remaining_mortgage_balance - selling_cost_amount - property_capital_gain_total_tax + \
        (homeowner_stock_assets * (1.0 - long_term_capital_gains_tax_rate))
    renter_net_worth = (renter_stock_assets * (1.0 - long_term_capital_gains_tax_rate))

    return homeowner_net_worth, renter_net_worth


def dollars_today(simulation_params, amount):
    """
    convert amount into today's dollars by using inflation params
    """
    annual_inflation = simulation_params["annual_inflation"]
    current_amount = amount
    # working backwards from end yoy inflation values through each previous one until simulation beginning
    for inflation_value in reversed(annual_inflation):
        current_amount /= (1.0 + inflation_value)

    return current_amount


def run_simulation(fixed_params):
    """
    run a simulation iteration
    return homeowner_net_worth_dollars_today, renter_net_worth_dollars_today
    """
    simulation_params = generate_params(fixed_params)
    is_debug = fixed_params["debug_mode"]
    if is_debug:
        print("Running simulation with parameters:")
        print(json.dumps(simulation_params, indent=4))
    
    end_property_value, annual_total_homeowner_costs, remaining_mortgage_balance, annual_income, homeowner_stock_assets = run_homeowner_simulation(
        fixed_params, simulation_params)
    renter_stock_assets, annual_total_renter_costs = run_renter_simulation(fixed_params, simulation_params, annual_total_homeowner_costs, annual_income)

    if is_debug:
        print(f"Annual income: {fmt_dollars(annual_income)}")
        print(f"End property value: {end_property_value}")
        print(f"Homeowner stock assets: {homeowner_stock_assets}")
        print(f"Annual total homeowner costs: {annual_total_homeowner_costs}")
        print(f"Remaining mortgage balance: {fmt_dollars(remaining_mortgage_balance)}")
        print(f"Renter stock assets: {fmt_dollars(renter_stock_assets)}")
        print(f"Annual total renter costs: {annual_total_renter_costs}")
    
    # calculate both net worths at end of simulation
    homeowner_net_worth, renter_net_worth = liquidate_all_assets(fixed_params["married_at_simulation_end"], simulation_params["property_price"],
        end_property_value, remaining_mortgage_balance, homeowner_stock_assets, renter_stock_assets)
    if is_debug:
        print(f"Homeowner net worth: {fmt_dollars(homeowner_net_worth)}")
        print(f"Renter net worth: {fmt_dollars(renter_net_worth)}")
    
    # convert net worths to today's dollars using inflation values
    homeowner_net_worth_dollars_today = dollars_today(simulation_params, homeowner_net_worth)
    renter_net_worth_dollars_today = dollars_today(simulation_params, renter_net_worth)
    if is_debug:
        print(f"Homeowner net worth in today's dollars: {fmt_dollars(homeowner_net_worth_dollars_today)}")
        print(f"Renter net worth in today's dollars: {fmt_dollars(renter_net_worth_dollars_today)}")
    
    return homeowner_net_worth_dollars_today, renter_net_worth_dollars_today


def main():
    fixed_params = CONFIG.pop("fixed_parameters")
    parse_input(fixed_params)
    n_simulations = fixed_params["n_simulations"]
    homeowner_net_worths = []
    renter_net_worths = []
    for i in range(n_simulations):
        homeowner_net_worth_dollars_today, renter_net_worth_dollars_today = run_simulation(fixed_params)
        homeowner_net_worths.append(homeowner_net_worth_dollars_today)
        renter_net_worths.append(renter_net_worth_dollars_today)

    # analysis across simulation runs showing statistics comparing homeowner vs renter
    homeowner_net_worth_mean = statistics.mean(homeowner_net_worths)
    renter_net_worth_mean = statistics.mean(renter_net_worths)
    homeowner_beats_renter_rate = sum([(homeowner_net_worth > renter_net_worths[i]) for i, homeowner_net_worth in enumerate(homeowner_net_worths)]) / n_simulations
    print(f"Results across {n_simulations} simulations extended {fixed_params['n_years']} years into the future:")
    print(f"Being a homeowner beats being a renter (in net worth) in {round(homeowner_beats_renter_rate * 100.0, 2)}% of simulations")
    print(f"Homeowner average net worth at simulation end in today's dollars: {fmt_dollars(homeowner_net_worth_mean)}")
    print(f"Renter average net worth at simulation end in today's dollars: {fmt_dollars(renter_net_worth_mean)}")
    # TODO print average home purchase price, end value, stock value in today's dollars; do we need to do all these in future dollars too? probably not, too much info


if __name__=="__main__":
    main()

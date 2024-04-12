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
        
        # if param is calculated annually, we generate each year's value (if no corresponding growth_rate param); otherwise, it remains same every year of simulation
        # if there's a <param_base_name>_growth_rate param, then we just generate the first value here and generate the others using the growth_rate param later
        if "annual" in param_base_name and not f"{param_base_name}_growth_rate" in CONFIG:
            param_value = []
            n_years_to_generate = fixed_params["n_years"]
            # if it's a growth_rate param, we already have starting value and only need to generate n_years - 1 more values
            if "growth_rate" in param_base_name:
                n_years_to_generate -= 1
            # TODO change values based on fixed params assumptions, non-fixed params growth rates, and rental moves
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
        if not param_growth_rates:
            continue

        current_param_value = simulation_params[param_base_name]
        param_value = [current_param_value]
        for param_growth_rate in param_growth_rates:
            current_param_value *= (1.0 + param_growth_rate)
            param_value.append(current_param_value)

        simulation_params[param_base_name] = param_value

    return simulation_params


def run_simulation(fixed_params):
    """
    run a simulation iteration
    """
    simulation_params = generate_params(fixed_params)
    print("Running simulation with parameters:")
    print(json.dumps(simulation_params, indent=4))
    
    

def main():
    fixed_params = CONFIG.pop("fixed_parameters")
    for i in range(fixed_params["n_simulations"]):
        run_simulation(fixed_params)


if __name__=="__main__":
    main()

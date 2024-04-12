"""
Monte Carlo simulation to predict many different possible housing outcomes
usage:
    # configure values you want in config.py and then run:
    python simulate.py
"""
from config import *
import random


def generate_params():
    """
    generate the parameters required for one simulation
    these are generated based on random things like drawing from normal distributions using parameters that make sense
    returns dict with values
    """
    
    mortgage_rate = random.gauss()
    
def run_simulation():
    """
    run a simulation iteration
    """
    simulation_params = generate_params()
    

def main():
    for i in range(N_SIMULATIONS):
        run_simulation()


if __name__=="__main__":
    main()

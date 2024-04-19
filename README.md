# housing-simulation
A Monte Carlo simulation for the housing market.

## What is it?

This project simulates many possible future scenarios to investigate the following question:
Should I buy a home or be a renter? It provides insight on this question by generating
many parameters in the housing, rental, and stock markets while playing them forwards in time
to estimate the homeowner or renter's future net worth. These parameters are adjustable in the ```config.py```
file, and changing them can considerably affect the outcome of the simulations. For each simulation run,
the program actually generates two simulations: one to model the homeownership decision and another for the
renter. The best way to learn from this is to set the values in ```config.py``` to be as close to your situation as
possible and subsequently running the simulation by modifying parameters one by one to understand their effects.

## How does it work?

The project utilizes a technique called Monte Carlo simulation in order to create parameters which
determine future outcomes. Specifically, for many of the base parameters defined in ```config.py```
it will use the specified mean and standard deviation values to randomly draw parameter values for
a given simulation run. For instance, if inflation mean is 2% and standard deviation 1%, it will
draw from a normal distribution
```
N(μ=0.02, σ=0.01)
```
a value for annual inflation in each simulated year. These generated parameter values will then be
used to extrapolate future performance of simulated assets in the housing, rental, and stock markets.
After extrapolating according to the many generated simulation parameters, the assets of the homeowner and renter are all
liquidated, and net worth is computed after subtracting applicable taxes, fees, etc. This is then repeated
according to the ```n_simulations``` config parameter. Once all the simulations run, the program prints summary statistics
across all the simulation runs in aggregate to elucidate the impact changing parameters has on the end financial
results. You'll notice the aggregate simulation results stabilize more the higher the value of ```n_simulations```.
This is due to the [Law of Large Numbers](https://en.wikipedia.org/wiki/Law_of_large_numbers) and means that the
more simulation iterations run, the more the resulting values converge to their true expected values. Thus, it is
recommended to run the simulations with ```n_simulations``` set to at least 10,000 in order to reduce noise.

## How do I run it?

Usage:
```
# configure values you want in config.py and then run:
python simulate.py
python simulate.py --interactive # -i for short, allows you to enter your mortgage and income info
python simulate.py --help # -h for short, print info on program usage
```

## What assumptions does the simulation make?

- Individuals start with some specified amount of net worth in cash. This cash is then immediately invested in stocks or housing
assets and grows throughout the duration of the simulation. The homeowner immediately uses it to pay the down payment, and
then the rest is invested in stocks. The renter immediately puts it all into stocks.
- At simulation end, all assets are liquidated so net worth values can be compared on equal terms in cash.
- The values currently in ```config.py``` are an example geared towards housing in Arlington, VA. Please update these
according to your own situation.
- The program assumes most config values are independent. A few of them are currently set based on the value of inflation. In reality,
though, these values are correlated to various degrees. This reduces the effectiveness of the simulation somewhat, but
by the nature of drawing from a normal distribution there will naturally be a wide variety of scenarios captured, many of which
should closely match reality nevertheless.
- Individuals invest their savings solely into stocks. The simulation captures cost of living, taxes, housing, etc., but the remainder
goes into the stock market. The config currently manifests this as an S and P 500 investment.
- Investing in stocks achieves market average returns. Results may vary.
- Actions are annually computed, thus there is a yearly granularity which doesn't entirely capture reality, such as compound interest, etc.
It's likely to be close enough for all intents and purposes, however.
- No multiyear trends such as recessions are modeled yet.
- Simulation parameters are drawn from a normal distribution. The normal distribution is a great practical tool which accurately models a
surprising number of natural phenomena. However, not everything fits this model, so the simulated parameters may not always reflect reality.
In practice, the normal distribution is usually one the best tools to use in the absence of additional insights into the true data generating
distribution.
- Homeowner lives in same house throughout simulation period, while renters move occasionally to find better rental rates.

## What ideas have I learned or reinforced with the simulation?

- The greatest value of this is to compare the effects of changing various config parameters, not in predicting any specific future
outcome. If used correctly, one learns about the relative importance of each paramenter, rather than determining net worth provided
by homeownership vs. rentership.
- The relative importance of exponential parameter compared with non-exponential ones is poignant. Raising the mean growth rate of
housing prices, an exponential growth parameter, just 1% will typically have a much greater effect on net worth than large tax breaks
worth tens of thousands of dollars. Likewise, if stocks outperform their historic growth by just 1%, then homeownership will rarely beat
rentership.
- Macroeconomic trends seem more important than anything else in predicting financial impact of the choice between owning a home and
renting. In particular, the stock market and housing market matter the most.
- It's worth shopping around a bit for a good mortgage rate, but the importance of this usually pales in comparison to that of the other
exponential variables in the experiment. It's often better to get a percent extra housing price growth than the same magnitude reduction
in mortgage rate and other mortgage parameters.
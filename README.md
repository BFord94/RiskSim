# RiskSim
## Introduction
A small series of tools for introductory market risk calculations. We demonstrate a basic Brownian Motion Monte-Carlo simulation model for stock prices, calibrated using historical data, some simple risk calculations using historical simulation, and finally show how a model can evaluated by backtesting.

## How-to
The notebook "stock_simulation.pynb" demonstrates the basic functionalities, via an example simulation, calculation of risk meaures, and backtesting. 

## Contents
### Monte-Carlo simulation
The first modules defines a series of classes used to download market time series data for a given stock price, and to simulate the future evolution of the stock price over some specified period. Included are methods to load in data, plot time series data and the subsequent daily returns distribution. In the StockModel object, one can calibrate (by user input, or using historical data), and simulate the stock price as a simple BM process, as well as plot the simulated paths.

### Risk calculations
Included are functions to compute the Value-at-Risk for a stock price, and expected shortfall risk measures.

### Backtesting
Finally, we also include some functions to demonstrate backtesting, used to test a projection model against historical data, by comparing what the model would have predicted in the past against what actually happened.

## Future work
-Alternative simulation models, such as Heston  
-Pricing functionality for other derivatives  
-Portfolio class to deal with multiple equities  
-Counterparty credit risk implementation (with collateral etc)

### Author
Dr. Billy Ford  
billyford1994@gmail.com
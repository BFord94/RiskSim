from functions_import import *
from stock_classes import *

def var_exceptions_count(stock_name, start_date, end_date,\
						 n_years, percentile):
	"""
	Count the number of daily VaR exceptions for given backtesting set
	Parameters:
		stock_name - Name of the stock to backtest
		start_date - Starting date of the backtesting window
		end_date - Final date of the backtesting window
		n_years - Number of years of historical data to use 
				  for VaR calculation
		percentile - Percentile VaR to compute
	"""
	# Need data to cover the backtesting window and VaR calculation
	# on day 0 of BT window
	start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
	var_start_date = start_date - datetime.timedelta(days = n_years*365)
	stock = StockData(stock_name)
	stock.get_data(var_start_date, end_date)
	# Compute daily returns
	stock.data.loc[:,"Returns"] = stock.data.loc[:,"Adj Close"] \
							- stock.data.loc[:,"Adj Close"].shift(1)
	stock.data.loc[:,"VaR"] = stock.data.loc[:,"Returns"].rolling(n_years*365).\
						quantile(1-percentile/100)
	n_exceptions = len(stock.data[stock.data.loc[:,"Returns"] < stock.data.loc[:,"VaR"]])
	return n_exceptions

def generate_binomial_distribution(n, p):
	"""
	Generate a binomial distribution 
	Parameters:
		n - Total number of trials
		p - Probability of the first outcome
	"""
	# Generate binomial distribution
	binomial = binom(n, p)
	return binomial

def compute_p_value(n_observations, n_exceptions, p):
	"""
	Compute the p-value representing the probability of obtaining less than the
	observed number of backtesting exceptions
	Parameters:
		n_observations - Total number of trials, i.e. length of lookback
						 window in days
		n_exceptions - Number of observed backtesting exceptions
		p - Probability of a backtesting exception, i.e. one minus the
			VaR percentile
	"""
	# Generate the binomial
	binomial = generate_binomial_distribution(n_observations, p)
	# Initialise x values
	x = np.arange(binom.ppf(0.01, n_observations, p), \
				  binom.ppf(0.99, n_observations, p))
	# Plot binomial
	plt.bar(x, binomial.pmf(x))
	plt.vlines(n_exceptions, ymin=0, ymax=0.1, color='r', \
			label="Observed # exceptions", linestyle='dashed')
	plt.xlabel("Number of exceptions")
	plt.ylabel("Probability")
	plt.show()
	# Find p-value
	p_value = binomial.cdf(n_exceptions)
	return p_value 



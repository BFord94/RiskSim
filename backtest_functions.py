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
	stock.data["Returns"] = stock.data["Adj Close"] \
							- stock.data["Adj Close"].shift(1)
	stock.data["VaR"] = stock.data["Returns"].rolling(n_years*365).\
						quantile(1-percentile/100)
	n_exceptions = len(stock.data[stock.data["Returns"] < stock.data["VaR"]])
	return n_exceptions

def generate_binomial_distribution(n, p):
	"""
	Generate a binomial distribution 
	Parameters:
		n - Total number of trials
		p - Probability of the first outcome
	"""
	# Initialise x values
	x = np.arange(binom.ppf(0.01, n, p), binom.ppf(0.99, n, p))
	# Generate binomial distribution
	binomial = binom(n, p)
	plt.bar(x, binomial.pmf(x))
	plt.xlabel("Number of exceptions")
	plt.ylabel("Probability")
	plt.show()
	return binomial

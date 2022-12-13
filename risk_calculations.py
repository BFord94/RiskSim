from functions_import import *
from stock_classes import *

def grab_hist_data(stock_name, start_date, end_date):
	"""
	Grab dataset for computing risk calculations
	Parameters:
		stock_name - Name of the stock to grab data for
		start_date - Start date to collect historical data for VaR calculation
		end_date - Final date to collect historical data for VaR calculation	
	"""
	# Generate historical data
	stock = StockData(stock_name)
	stock.get_data(start_date, end_date)
	# Compute returns
	stock.data["Returns"] = stock.data["Adj Close"] \
	- stock.data["Adj Close"].shift(1)
	return stock.data

def var(stock_name, start_date, end_date, horizon, percentile):
	"""
	Compute Value-at-Risk using historical simulation, 
	with specified horizon and percentile
	Parameters:
		stock_name - Name of the stock to compute VaR for
		start_date - Start date to collect historical data for VaR calculation
		end_date - Final date to collect historical data for VaR calculation
		horizon - Number fo days to measure returns
		percentile - Quantile of distribution to measure
	"""
	# Grab data
	stock_data = grab_hist_data(stock_name, start_date, end_date)
	# Compute VaR with sqrt(t) approximation
	var = stock_data['Returns'].quantile(1 \
		  - float(percentile)/100)*m.sqrt(horizon)
	return var

def expected_shortfall(stock_name, start_date, end_date, horizon, percentile):
	"""
	Compute expected shortfall using historical simulation,
	with specified horizon and percentile
	Parameters:
		stock_name - Name of the stock to compute VaR for
		start_date - Start date to collect historical data for VaR calculation
		end_date - Final date to collect historical data for VaR calculation
		horizon - Number fo days to measure returns
		percentile - Quantile of distribution to measure
	"""
	# Grab data
	stock_data = grab_hist_data(stock_name, start_date, end_date)
	perc = stock_data['Returns'].quantile(1-float(percentile)/100)
	# Filter data by perecntile and compute ES
	stock_data = stock_data[stock_data['Returns'] < perc]
	es = stock_data['Returns'].mean()*m.sqrt(horizon)
	return es

def plot_returns(data, n, var=None, es=None):
	"""
	Plot the distrubtion of returns, and show the VaR and ES 
	(if calculated)
	Parameters:
		data - Time series data with returns 
		n - Number of days returns measured for VaR/ES
		var - VaR value, default None if not computed
		es - ES value, default None if not computed
	"""
	# Plot returns distribution, grab bin heights for VaR/ES line
	data["nday Returns"] = data["Adj Close"] \
						   - data["Adj Close"].shift(n)
	heights, bins, patches = plt.hist(data["nday Returns"], bins=50)
	h = heights.max()
	plt.xlabel(str(n)+"-day Returns [$]")
	plt.ylabel("Frequency")
	# Only plot VaR/ES line if they have been calculated
	if var is not None:
		plt.vlines(var, ymin=0, ymax=h , color='g', \
			label=str(n)+"-Day VaR", linestyle='dashed')
	if es is not None:
		plt.vlines(es, ymin=0, ymax=h , color='r', \
			label=str(n)+"-Day ES", linestyle='dashed')
	plt.legend(loc='best')
	plt.show()
	return True


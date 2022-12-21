from functions_import import *

class StockData:
	"""
	Stock data object, used to read in historical data for a specified stock 
	Attributes:
		name - The name of the stock to read data for, 
		   	   using yahoo naming convention
		data - Pandas dataframe containing daily stock price data
		data_state - Boolean identifier that is True when data has been read, 
					 otherwise False
		start_date - First date for which data has been read, 
					 if data has not been read is None
		end_date - Final date for which data has been read, 
				   if data has not been read is None
	"""
	def __init__(self, name):
		self.name = name
		self.data = None
		self.data_state = False
		self.start_date = None
		self.end_date = None

	def get_data(self, start_date, end_date):
		"""
		Grab time series data from pandas_datareader
		Parameters: 
			start_date - First date to begin collecting time series data for
			end_date - Final date to collect time series data for
		"""
		self.start_date = start_date
		self.end_date = end_date
		start_date, end_date = pd.to_datetime(start_date, format='%d/%m/%Y'), \
							   pd.to_datetime(end_date, format='%d/%m/%Y')
		ticker = self.name
		try:
			data = pdr.DataReader(ticker, data_source = 'yahoo', \
			   	start = start_date, end = end_date)
		except:
			yfin.pdr_override()
			data = pdr.get_data_yahoo(ticker, start = start_date, end = end_date)
		data = data[["Adj Close"]]
		self.data = data

	def timeseries_plot(self):
		"""
		Plot time series of adjusted closing price
		"""
		# Need to read data before plotting
		if self.data is None:
			print("Error, no data fetched for this stock, \
				  cannot plot time series.")
		plt.plot(self.data)
		plt.xlabel("Date")
		plt.ylabel(self.name+" price [$]")
		plt.show()

	def returns_plot(self):
		"""
		Plot daily returns 
		"""
		# Need to read data before computing returns
		if self.data is None:
			print("Error, no data fetched for this stock, \
				  cannot compute returns.")
		self.data["Returns"] = self.data["Adj Close"] - self.data["Adj Close"].shift(1)
		plt.hist(self.data["Returns"],bins=50)
		plt.xlabel("Daily Returns [$]")
		plt.ylabel("Frequency")
		plt.show()

	def __str__(self):
		"""
		Define print output for object
		"""
		text = "Stock name: "+str(self.name)+"\n"
		if self.data_state:
			text += "Daily data read for period " \
				 +str(self.start_date)+" to "+str(self.end_date)+"\n"
		else:
			text += "Daily data not read"

class StockModel:
	"""
	Stock model object, used to define a GBM model for a given stock
	Attributes:
		stock_name - Name of the stock to be modelled
		mu - The drift parameter of the GBM model, 
			 can be calibrated by user input or using historical data
		sigma - The volatility parameter of the GBM model, 
		 		can be calibrated by user input or using historical data
		npaths - Number of paths to simulate
		calibrated_state - Status of the calibration, 
						   default value is None is model uncalibrated, 
						   "Data" if model has been calibrated with data,
						   "Manual" if model has been calibrated with 
						   user input
		calibration_start_date - First date to begin data calibration
		calibration_end_date - Final date for data calibration
		simulated_state - Boolean identifier, False by default,
						  True if model has been simulated
		simulation_start_date - First date to begin simulation
		simulation_end_date - Final date for the simulation
	"""
	def __init__(self, stock_name):
		self.stock_name = stock_name
		self.mu = None
		self.sigma = None
		self.npaths = None
		self.calibrated_state = None
		self.calibration_start_date = None
		self.calibration_end_date = None
		self.simulated_state = False
		self.simulation_start_date = None
		self.simulation_end_date = None

	def manual_calibrate(self, mu, sigma):
		"""
		Set model parameters manually
		Parameters:
			mu - User input drift value
			sigma - User input volatility value
		""" 
		self.mu = mu 
		self.sigma = sigma
		self.calibrated_state = "Manual"

	def calibrate(self, start_date, end_date):
		"""
		Use historical data to calibrate model parameters
		Parameters:
			start_date - First date to begin calibration
			end_date - Final date for calibration
		"""
		# Get data
		stock = StockData(self.stock_name)
		stock.get_data(start_date, end_date)
		data = stock.data
		self.calibration_start_date = start_date 
		self.calibration_end_date = end_date
		# Compute absolute returns
		data["Abs Returns"] = data["Adj Close"] - data["Adj Close"].shift(1)
		# Convert to log returns
		data["Log Returns"] = np.log(1 + (data["Abs Returns"]\
							  / data["Adj Close"].shift(1)))
		mu, sigma = data["Log Returns"].mean(), data["Log Returns"].std()
		# Approximate drift as the log returns mean 
		# minus half the volatility squared
		mu = mu - sigma**2/2
		self.mu = mu
		self.sigma = sigma
		self.calibrated_state = "Data"

	def simulate(self, start_date, end_date, npaths):
		"""
		Simulate daily stock price as a geometric brownian motion process
		Parameters:
			start_date - First date to begin simulation
			end_date - Final date for simulation
			npaths - Number of paths to simulate
		"""
		# initialise simulation parameters
		self.simulation_start_date = start_date
		self.simulation_end_date = end_date
		self.npaths = npaths
		start_date, end_date = pd.to_datetime(start_date, format='%d/%m/%Y'), \
							   pd.to_datetime(end_date, format='%d/%m/%Y')
		ndays = int((end_date - start_date) / np.timedelta64(1, 'D'))
		# simulate random grid
		random_grid = norm.ppf(np.random.rand(ndays,npaths))
		# generate daily returns
		returns = np.exp(self.mu + self.sigma*random_grid)
		# get start price
		stock = StockData(self.stock_name)
		stock.get_data(start_date, end_date)
		s0 = stock.data["Adj Close"][0]
		# create simulation grid and initialise with starting values
		stock_prices = np.zeros_like(random_grid)
		stock_prices[0] = s0
		# iterate over simulation days
		for i in range(1,ndays):
			stock_prices[i] = stock_prices[i-1]*returns[i]
		# Write simulation to a datafrmae
		sim_data = pd.DataFrame(stock_prices, \
				   columns=["path_"+str(p+1) for p in range(npaths)])
		dates = pd.date_range(start_date, end_date \
							 - np.timedelta64(1, 'D'),freq='d')
		# Add dates and reorder columns
		sim_data["Date"] = dates
		col_list = sim_data.columns.to_list()
		col_list.insert(0,col_list.pop())
		sim_data = sim_data[col_list]
		self.simulation = sim_data
		self.simulated_state = True
		return self.simulation

	def plot_paths(self):
		"""
		Plot simulated paths 
		"""
		for p in range(self.npaths):
			plt.plot(self.simulation["Date"], \
				     self.simulation["path_"+str(p+1)])
		plt.xlabel("Date")
		plt.ylabel("Stock Price [$]")
		plt.show()

	def __str__(self):
		"""
		Define print output for object
		"""
		text = "Stock name: "+str(self.stock_name)
		if self.calibrated_state == "Data":
			text += "\nModel calibrated using data for " \
				 + str(self.calibration_start_date)+" to " \
				 + str(self.calibration_end_date)
			text += "\nModel parameters mu: " + str(self.mu) + ", sigma: " \
				 + str(self.sigma)
		elif self.calibrated_state == "Manual":
			text += "\nModel calibrated manually\n"
			text += "\nModel parameters mu: " + str(self.mu) + ", sigma: " \
				 + str(self.sigma)
		else:
			text += "\nModel not calibrated."
		if self.simulated_state:
			text += "\nModel simulated between dates " \
				 + str(self.simulation_start_date) + " to "\
				 + str(self.simulation_end_date)
		else:
			text += "\nModel not simulated."
		return text


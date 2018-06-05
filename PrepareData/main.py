from classes import *
from sys import argv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


df = None
DATA = None

def read_data(filename):
	try:
		# print('Trying to read %s...' % filename)
		f = open(filename, 'r', encoding='UTF-8')
		res = f.read()
		f.close()
		if not res:
			print('Empty file')
			return None
		return res
	except:
		print('Invalid arguments or filename')
		return None
		

def make_list(data):
	data = data.split('///')
	return [i.split('@@')[0] for i in data] 


def make_daily_dataframe(frame):
	new_frame = frame.resample('D').agg({'Action': lambda x: '; '.join(x), 'Difference': np.sum, 'Total': lambda x: x.iloc[-1] if x.any() else np.nan})
	new_frame.Total = new_frame.Total.fillna(method='ffill')
	return new_frame
	

def read_config(filename):
	try:
		d = {}
		with open(filename, 'r') as f:
			for line in f:
				(key, val) = line.split()
				d[key] = val
		print(d)
		return d
	except:
		print('Error during reading config...')
		return {}
	

def main():
	filename = 'sms.data'
	cfg_name = 'main.cfg'
	config = {}
	if len(argv) == 2:
		filename = argv[1]
	elif len(argv) == 3:
		filename = argv[1]
		cfg_name = argv[2]
	data = read_data(filename)
	if not data:
		exit()
	config = read_config(cfg_name)
	lines = make_list(data)
	objects = []
	for line in lines:
		# print("Parsing: %s" % line)
		single_sms_object = TelecardSmsObject(line, False)
		if single_sms_object.valid:
			objects.append(single_sms_object)
	print("Total valid objects: %d" % len(objects))
	df = pd.DataFrame()
	for obj in objects:
		df = df.append(obj.generateDataFrame())
	if 'Salary_filter' in config:
		filter = 0
		try:
			filter = int(config['Salary_filter'])
		except:
			print('Error in Saary_filter. Foramt is Salary_filter int, ex: Salary_filter 1111')
		df.loc[((df.Action == '') & (df.Difference >= filter)), 'Action'] = 'Salary'
	df['Action'] = df['Action'] + '(' + df['Difference'].astype('str') + ')'
	print("Generated dataFrame!")
	print(df)
	if 'CN' in config:
		print("Filtering main card...")
		filtered = df[df.CN == config['CN']]
		daily = make_daily_dataframe(filtered)
		print(daily)
		plot = daily.plot(subplots=True, grid=True)
		'''
		Some matplotlib bugs here
		print(plot)
		plot[0].xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=(1),
									 interval=1))
		plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%d.%m'))
		plt.gca().xaxis.grid(True, which="minor")
		'''
	else:
		plot = df.plot(subplots=True, grid=True)
	plt.tight_layout()
	plt.show()	

	
if __name__ == "__main__":
	main()
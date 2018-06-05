from classes import *
from sys import argv
import pandas as pd


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


def main():
	filename = 'sms.data'
	if len(argv) == 2:
		filename = argv[1]
	data = read_data(filename)
	if not data:
		exit()
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
		print(obj)
	print("Generated dataFrame!")
	print(df)
	

if __name__ == "__main__":
	main()
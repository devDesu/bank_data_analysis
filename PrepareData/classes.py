import re
import datetime
import pandas as pd


class BaseSmsObject:
	def __str__(self):
		raise NotImplementedError
	
	def __init__(self):
		pass
	
	def generateDataFrame(self):
		raise NotImplementedError

		
def read_backwards_until(char, _data, start_pos=None):
	if start_pos is None:
		start_pos = len(_data) - 1
	for i in range(start_pos, 0, -1):
		if _data[i] == char:
			return i
	return -1


class TelecardSmsObject(BaseSmsObject):
	
	datetime_print_format = "%H:%M:%S %d.%m.%Y, %a"
	diff_error = "Error during parsing difference. Leaving..."
	total_error = "Error during parsing total sum left. Leaving..."
	time_error = "Error during parsing time. Leaving..."
	date_error = "Error during parsing date. Leaving..."
	
	def prepare_regexes(self):
		self.CN_regex = re.compile(r'\*[0-9]{4}')
		self.diff_regex = re.compile(r'(-|\+)?[0-9]{1,5}(\.[0-9]{1,2})?')
		self.time_regex = re.compile(r'(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]')
		self.special_time_regex = re.compile(r'(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]')
		self.date_regex = re.compile(r'(0[1-9]|1[0-9]|2[0-9]|3[0-1])\.(0[1-9]|1[0-2])\.(1[0-9]|2[0-9])') # from 01.01.10 to 31.12.29
		self.total_regex = re.compile(r'[0-9]{1,6}(\.[0-9]{1,2})?')
	
	def __str__(self):
		if self.valid:
			return "{2}. ({0}) {1}: {3}. Left {4}".format(self.card_number, 
														  self.action,
														  self.datetime.strftime(self.datetime_print_format),
														  self.diff, 
														  self.total)
		return "Invalid data!"
			
	
	def prefill(self):
		self.card_number = None
		self.diff = None
		self.datetime = None
		self.action = ''
		self.total = None
		self.valid = False
	
	def log(self, data):
		if self.logable:
			print(data)
	
	def __init__(self, data, log=True):
		'''
		data@param - sms body we have to parse
		data ex: *XXXX -119р ACTION 28.03.18 12:19 Доступно 11111.08р
		'''
		self.logable = log
		self.prepare_regexes()
		self.prefill()
		position = 0
		temp = data[position:5]  # card number starts with *, then 4 digits, ex: *1111
		if not self.CN_regex.fullmatch(temp):
			self.log('Broken data: {}!'.format(data))
			return
		self.card_number = temp
		position += 6 # omit space
		space_pos = data.find(' ', 6)
		temp = data[position:space_pos]  # difference is after CN, some digits + cuurency, ends with space, ex: ^ -11р ^
		if not self.diff_regex.fullmatch(temp[:-1]):
			self.log('Broken data, invalid difference, trying another parse function...')
			self.parse_special(data)
			return
		self.diff = float(temp[:-1])
		position = space_pos + 1
		# now we'll read string from it end
		space_pos = read_backwards_until(' ', data)
		temp = data[space_pos+1:]  # omit space
		if not self.total_regex.fullmatch(temp[:-1]):
			self.log(self.total_error)
			return
		self.total = float(temp[:-1])
		backwards_pos = space_pos - 9 # omit available
		temp = data[backwards_pos-5:backwards_pos]
		if not self.time_regex.fullmatch(temp):
			self.log(self.time_error)
			return
		self.time = temp
		backwards_pos -= 6
		temp = data[backwards_pos-8:backwards_pos]
		if not self.date_regex.fullmatch(temp):
			self.log(self.date_error)
			return
		self.datetime = datetime.datetime.strptime('%s %s' % (self.time, temp), '%H:%M %d.%m.%y')
		backwards_pos -= 9
		self.action = data[position:backwards_pos]
		self.valid = True
	
	def parse_special(self, data):
		'''
		data@param - new(?) sms body format
		data ex: *XXXX sub_action 120р SOME ACTION 06.06.18 16:52:46 Доступно 11111.11р
		
		!IMPORTANT! Only "Покупка" sub_action is used now
		
		'''
		position = 6
		space_pos = data.find(' ', 6)
		self.sub_action = data[6:space_pos]
		position = space_pos + 1
		space_pos = data.find(' ', position)
		temp = data[position:space_pos-1]  # ignore currency
		if not self.diff_regex.fullmatch(temp):
			self.log('Failed to parse in specail way...')
			return
		self.diff = float(temp)
		position = space_pos + 1
		if self.sub_action == 'Покупка':
			self.diff *= -1
		# now we'll read string from it end
		space_pos = read_backwards_until(' ', data)
		temp = data[space_pos+1:-1]  # omit space
		if not self.total_regex.fullmatch(temp):
			self.log(self.total_error)
			return
		self.total = float(temp)
		backwards_pos = space_pos - 9 # omit available
		temp = data[backwards_pos-8:backwards_pos]
		if not self.special_time_regex.fullmatch(temp):
			self.log(self.time_error)
			return
		self.time = temp
		backwards_pos -= 9
		temp = data[backwards_pos-8:backwards_pos]
		if not self.date_regex.fullmatch(temp):
			self.log(self.date_error)
			return
		self.datetime = datetime.datetime.strptime('%s %s' % (self.time, temp), '%H:%M:%S %d.%m.%y')
		backwards_pos -= 9
		self.action = data[position:backwards_pos]
		self.valid = True
		
	def generateDataFrame(self):
		temp = {"CN": [self.card_number], 
			    "Difference": [self.diff],
				"Datetime": [self.datetime],
				"Action": [self.action],
				"Total": [self.total],
				"Valid": [self.valid]
				}
		return pd.DataFrame.from_records(temp, index='Datetime')
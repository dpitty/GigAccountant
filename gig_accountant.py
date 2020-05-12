import csv
import locale #currency formatting
from datetime import datetime
'''
This first protoype is built in May 2020
Note that format of CSV records may change from PayPal, TaskRabbit
'''
class PaymentReceived:
	#_publicAttr = 'whatever'

	#date parameter is datetime object
	def __init__(self, dollarAmount=0, date=None, fromWho=None, payMethod=None):
		self.__dollarAmount = dollarAmount
		self.__date = date
		self.__fromWho = fromWho
		self.__payMethod = payMethod

	def __str__(self):
		return ', '.join([\
			locale.currency(self.__dollarAmount),\
			str(None) if self.__date is None else self.__date.strftime('%Y-%m-%d'),\
			str(self.__fromWho),\
			str(self.__payMethod)])


class TaskRabbitPayment(PaymentReceived):
	#require types Dict and string?
	@classmethod
	def fromDict(cls, fullDict):
		result = cls(\
			dollarAmount=float(fullDict['Earnings'].strip('$'))+float(fullDict['Tip'].strip('$')),\
			date=datetime.strptime(fullDict['Time'], '%Y-%m-%d'),\
			fromWho=fullDict['Title'],\
			payMethod='TaskRabbit')
		result.__fullDict = fullDict
		return result

class PayPalPayment(PaymentReceived):

	#return None for 'not a payment received'
	@classmethod
	def fromDict(cls, fullDict):
		if not cls.isPayment(fullDict):
			return None
		result = cls(\
			dollarAmount=float(fullDict['Amount']),\
			date=datetime.strptime(fullDict['Date'], '%m/%d/%Y'),\
			fromWho=fullDict['Name'],\
			payMethod='PayPal')
		#TODO use a constant variable for date format '%m/%d/%Y'?
		result.__fullDict = fullDict
		return result

	@classmethod
	def isPayment(cls, fullDict):
		#Note, use == for string comparison. 'is' compares object id (not contents)
		#Discard all blank Amounts and negatives Amounts
		if fullDict['Amount'] == '' or float(fullDict['Amount']) <= 0:
			return False
		#Include only Status = Completed (ignore Pending, Cancelled, Reversed, Paid)
		#YES Type = General Payment and Status = Completed
		if fullDict['Type'] == 'General Payment' and fullDict['Status'] == 'Completed':
			return True
		#YES Type = Mobile Payment and Status = Completed
		if fullDict['Type'] == 'Mobile Payment' and fullDict['Status'] == 'Completed':
			return True
		#YES Type = Website Payment and Status = Completed
		if fullDict['Type'] == 'Website Payment' and fullDict['Status'] == 'Completed':
			return True
		#Anything else is not a payment, for now
		#E.g.: Status = Paid and Type = Invoice Sent does not describe a payment...
		return False


class WyzantPayment(PaymentReceived):
	#Note. No easy way to get a spreadsheet of payments... but maybe straight from HTML?
	#Maybe a script that fills the form specifying dates and retrieves the data?
	#I'm copy-pasting into a spreadsheet. It introducs all sorts of irregularities
	#Like a ' ' at the end of column titles
	@classmethod
	def fromDict(cls, fullDict):
		#Filter out Status incomplete? How often does that happen?
		result = cls(\
			dollarAmount=float(fullDict['Earned ']),\
			date=datetime.strptime(fullDict['Date '].split(' ')[0], '%m/%d/%Y'),\
			fromWho=fullDict['Student '].split(' \n')[0],\
			payMethod='Wyzant')
		#TODO use a constant variable for date format '%m/%d/%Y'?
		result.__fullDict = fullDict
		return result		


def load_tr_payments(csvfilename):
	result = []
	with open(csvfilename, encoding='utf-8') as csvfile:
		#discard first three lines
		next(csvfile)
		next(csvfile)
		next(csvfile)
		csvreader = csv.DictReader(csvfile)
		for row_as_dict in csvreader: #row is a dict
			#print(row_as_dict)
			result.append(TaskRabbitPayment.fromDict(row_as_dict))
	return result

def load_pp_payments(csvfilename):
	result = []
	num_non_payment_rows = 0
	#Need utf-8-sig to handle non-English symbols as well as BOM
	#\ufeff
	#https://stackoverflow.com/questions/17912307/u-ufeff-in-python-string
	with open(csvfilename, encoding='utf-8-sig') as csvfile:
		csvreader = csv.DictReader(csvfile)
		for row_as_dict in csvreader:
			p = PayPalPayment.fromDict(row_as_dict)
			if p:
				result.append(p)
			else:
				num_non_payment_rows += 1
	print("Found",num_non_payment_rows,"Non-payment rows in",csvfilename)
	return result

def load_wa_payments(csvfilename):
	result = []
	with open(csvfilename, encoding='utf-8') as csvfile:
		csvreader = csv.DictReader(csvfile)
		for row_as_dict in csvreader:
			result.append(WyzantPayment.fromDict(row_as_dict))
	return result

def main():
	locale.setlocale( locale.LC_ALL, '' ) #to print dollars format
	
	#Test TaskRabbit
	tr_csvfilename = 'C:\\Users\\user\\Desktop\\taskrabbit2019.csv'
	tr_payments = load_tr_payments(tr_csvfilename) #list of PaymentReceived objects
	for p in tr_payments:
		print(p)

	#Test PayPal
	pp_csvfilename = 'C:\\Users\\user\\Desktop\\PayPal2019.csv'
	pp_payments = load_pp_payments(pp_csvfilename)
	for p in pp_payments:
		print(p)

	#Test Wzyant
	wa_csvfilename = 'C:\\Users\\user\\Desktop\\wyzant2019detail.csv'
	wa_payments = load_wa_payments(wa_csvfilename)
	for p in wa_payments:
		print(p)

if __name__ == "__main__":
    main()

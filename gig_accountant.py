import csv
import locale #currency formatting
from datetime import datetime

print("Hello, gig accountant")

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


def load_tr_payments(csvfilename):
	result = []
	with open(csvfilename) as csvfile:
		#discard first three lines
		next(csvfile)
		next(csvfile)
		next(csvfile)
		csvreader = csv.DictReader(csvfile)
		for row_as_dict in csvreader: #row is a dict
			#print(row_as_dict)
			result.append(TaskRabbitPayment.fromDict(row_as_dict))
	return result


locale.setlocale( locale.LC_ALL, '' ) #to print dollars format
pr = PaymentReceived(fromWho='sanity test')
print(pr)

tr_csvfilename = 'C:\\Users\\user\\Desktop\\taskrabbit2019.csv'
tr_payments = load_tr_payments(tr_csvfilename) #list of PaymentReceived objects
for p in tr_payments:
	print(p)

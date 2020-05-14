import csv
import locale #currency formatting
from datetime import datetime, timedelta
import collections #defaultdict


class PaymentsAccumulator:
	#__payments is a list of PaymentReceived objects
	def __init__(self, payments=[]):
		self.__payments = payments

	def add(self, morePayments=[]):
		self.__payments.extend(morePayments)

	def __str__(self):
		return f'There are {len(self.__payments)} payments in the list'

	def paymentsSortedNewestFirst(self): #descending date
		return sorted(self.__payments, key=lambda p : p.getDate(), reverse=True)

	def sortByDate(self): #ascending date
		self.__payments.sort(key=lambda p : p.getDate())

	#6 is for Sunday
	#Returns datetime 
	#Note: giving week=-1 (correctly) produces the final Sunday of last year's December
	def sundayThisWeek(self, week, yr): #int, int
		return datetime(yr,1,1) + timedelta(weeks=week-1, days=(6-datetime(yr,1,1).weekday()))

	#A dictionary, each week (int) maps to a list of Payments for that week
	#These kind of weeks start on Sunday (see datetime documentation, %U)
	#We sort-by-date payments for each week while we're at it
	def __paymentsByWeek(self):
		paymentsByWeek = collections.defaultdict(list) # weeks[weekNumber] -> list of Payments that week
		for p in self.__payments:
			paymentsByWeek[int(p.getDate().strftime('%U'))].append(p) #%U for week# (yields string)
		for payments in paymentsByWeek.values():
			payments.sort(key=lambda p : p.getDate())
		return paymentsByWeek

	#Assuming a yearly report - all Payments from same year
	#Assuming sorted by date, but not it should work for unsorted anyway.
	def weeklySummary(self):
		if self.__payments is None:
			print('No income to report')
			return
		thisYear = self.__payments[0].getDate().year		
		
		for week,payments in self.__paymentsByWeek().items():
			thisSunday = self.sundayThisWeek(week, thisYear)
			#%A %b %d -> e.g. Sunday May 4
			print(' Week of', thisSunday.strftime('%A %b %d'),\
						'-', (thisSunday + timedelta(days=6)).strftime('%A, %b %d'),':',\
			 			locale.currency(sum(p.getDollarAmount() for p in payments)))
			for p in payments:
				print('\t',p)
			print()


	def grandTotal(self):
		return locale.currency(\
			sum(p.getDollarAmount() for p in self.__payments))

'''
This first protoype is built in May 2020
Note that format of CSV records may change from PayPal, TaskRabbit
'''
class PaymentReceived:

	locale.setlocale( locale.LC_ALL, '' ) #to print dollars format

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

	def __repr__(self):
		return f'[{str(self)}]'

	def getDate(self):
		return self.__date

	def getDollarAmount(self):
		return self.__dollarAmount

	@classmethod
	def parseMoney(cls, stringMoney):
		return float(stringMoney.replace(',','').strip('$'))


	#"Virtual"/abstract function for readPaymentsFromCSV?

class TaskRabbitPayment(PaymentReceived):
	@classmethod
	def fromDict(cls, fullDict):
		result = cls(\
			dollarAmount=cls.parseMoney(fullDict['Earnings'])+cls.parseMoney(fullDict['Tip']),\
			date=datetime.strptime(fullDict['Time'], '%Y-%m-%d'),\
			fromWho=fullDict['Title'],\
			payMethod='TaskRabbit')
		result.__fullDict = fullDict
		return result

	@classmethod
	def readPaymentsFromCSV(cls, csvfilename):
		result = []
		with open(csvfilename, encoding='utf-8') as csvfile:
			#discard first three lines of the CSV file (junk)
			for i in range(3): next(csvfile)
			csvreader = csv.DictReader(csvfile)
			for row_as_dict in csvreader:
				result.append(TaskRabbitPayment.fromDict(row_as_dict))
		return result

class PayPalPayment(PaymentReceived):

	#return None for 'not a payment received'
	@classmethod
	def fromDict(cls, fullDict):
		if not cls.isPayment(fullDict):
			return None
		result = cls(\
			#.replace() to remove ',' from dollar amount e.g. '-4,000.00'
			dollarAmount=cls.parseMoney(fullDict['Amount']),\
			date=datetime.strptime(fullDict['Date'], '%m/%d/%Y'),\
			fromWho=fullDict['Name'],\
			payMethod='PayPal')
		result.__fullDict = fullDict
		return result

	@classmethod
	def isPayment(cls, fullDict):
		#Discard all blank Amounts and negatives Amounts
		if fullDict['Amount'] == '' or cls.parseMoney(fullDict['Amount']) <= 0:
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

	@classmethod
	def readPaymentsFromCSV(cls, csvfilename):
		result = []
		num_non_payment_rows = 0 #Handy for sanity check
		#Need utf-8-sig to handle non-English symbols as well as "BOM" #\ufeff
		#https://stackoverflow.com/questions/17912307/u-ufeff-in-python-string
		with open(csvfilename, encoding='utf-8-sig') as csvfile:
			csvreader = csv.DictReader(csvfile)
			for row_as_dict in csvreader:
				p = PayPalPayment.fromDict(row_as_dict)
				if p:
					result.append(p)
				else:
					num_non_payment_rows += 1
		return result


class WyzantPayment(PaymentReceived):
	#TODO. No easy way to get a spreadsheet of payments... so maybe straight from HTML?
	#Maybe a script that fills the forms then retrieves the data?
	#I'm copy-pasting into a spreadsheet. It give quirks like ' ' at end of column titles
	@classmethod
	def fromDict(cls, fullDict):
		#Filter out Status incomplete? How often does that happen?
		result = None
		if 'ID' in fullDict: #"PayOut type" CSV records
			result = cls(\
				dollarAmount=cls.parseMoney(fullDict['Total']),\
				date=datetime.strptime(fullDict['Date'].split(' ')[0], '%m/%d/%y'),\
				fromWho='(Direct deposit)',\
				payMethod='Wyzant')
		else: #"Student-by-student type" CSV records
			result = cls(\
				dollarAmount=cls.parseMoney(fullDict['Earned ']),\
				date=datetime.strptime(fullDict['Date '].split(' ')[0], '%m/%d/%Y'),\
				fromWho=fullDict['Student '].split(' \n')[0],\
				payMethod='Wyzant')
		result.__fullDict = fullDict
		return result

	@classmethod
	def readPaymentsFromCSV(cls, csvfilename):
		result = []
		with open(csvfilename, encoding='utf-8') as csvfile:
			csvreader = csv.DictReader(csvfile)
			for row_as_dict in csvreader:
				result.append(WyzantPayment.fromDict(row_as_dict))
			return result




def main():
	
	#Test TaskRabbit
	tr_csvfilename = 'C:\\Users\\user\\Desktop\\taskrabbit2019.csv'
	tr_payments = TaskRabbitPayment.readPaymentsFromCSV(tr_csvfilename) #list of PaymentReceived objects
	for p in tr_payments:
		print(p)

	#Test PayPal
	pp_csvfilename = 'C:\\Users\\user\\Desktop\\PayPal2019.csv'
	pp_payments = PayPalPayment.readPaymentsFromCSV(pp_csvfilename)
	for p in pp_payments:
		print(p)

	#Test Wzyant
	wa_csvfilename = 'C:\\Users\\user\\Desktop\\wyzant2019detail.csv'
	wa_payments = WyzantPayment.readPaymentsFromCSV(wa_csvfilename)
	for p in wa_payments:
		print(p)

	#Test the payments accumulator
	accumulator = PaymentsAccumulator()
	accumulator.add(tr_payments + pp_payments + wa_payments)
	#print(accumulator)
	print(f'{len(tr_payments)} TR + {len(pp_payments)} PP + {len(wa_payments)} WA')
	print(accumulator.paymentsSortedNewestFirst()[:10])
	
if __name__ == "__main__":
    main()

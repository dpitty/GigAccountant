from gig_accountant import *

def main():
	print("Hello weekly 2020")
	
	#Load TaskRabbit payments
	tr_csvfilename = 'C:\\Users\\user\\Desktop\\taskrabbit2020.csv'
	tr_payments = TaskRabbitPayment.readPaymentsFromCSV(tr_csvfilename) #list of PaymentReceived objects

	#Load PayPal payments
	pp_csvfilename = 'C:\\Users\\user\\Desktop\\PayPal2020.csv'
	pp_payments = PayPalPayment.readPaymentsFromCSV(pp_csvfilename)

	#Load Wyzant payments by Student
	wa_student_csvfilename = 'C:\\Users\\user\\Desktop\\wyzant2020detail.csv'
	wa_student_payments = WyzantPayment.readPaymentsFromCSV(wa_student_csvfilename)

	#Load Wyzant payments by Payout
	wa_payout_csvfilename = 'C:\\Users\\user\\Desktop\\wyzant2020payouts.csv'
	wa_payout_payments = WyzantPayment.readPaymentsFromCSV(wa_payout_csvfilename)

	#Test the payments accumulator
	accumulator = PaymentsAccumulator(tr_payments + pp_payments + wa_student_payments)
	accumulator.weeklySummary()
	print("2020 grand total", accumulator.grandTotal())

if __name__ == "__main__":
	main()
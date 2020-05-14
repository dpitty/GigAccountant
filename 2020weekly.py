from gig_accountant import *


def main():
	print("Hello weekly 2020")
	print(PaymentReceived())

	#Test TaskRabbit
	tr_csvfilename = 'C:\\Users\\user\\Desktop\\taskrabbit2020.csv'
	tr_payments = load_tr_payments(tr_csvfilename) #list of PaymentReceived objects
	# for p in tr_payments:
	# 	print(p)

	#Test PayPal
	pp_csvfilename = 'C:\\Users\\user\\Desktop\\PayPal2020.csv'
	pp_payments = load_pp_payments(pp_csvfilename)
	# for p in pp_payments:
	# 	print(p)

	#Test Wzyant
	wa_student_csvfilename = 'C:\\Users\\user\\Desktop\\wyzant2020detail.csv'
	wa_student_payments = load_wa_payments(wa_student_csvfilename)
	# for p in wa_student_payments:
	# 	print(p)

	#Test WyzAnt by Payout
	wa_payout_csvfilename = 'C:\\Users\\user\\Desktop\\wyzant2020payouts.csv'
	wa_payout_payments = load_wa_payments(wa_payout_csvfilename)
	# for p in wa_payout_payments:
	# 	print(p)

	#Test the payments accumulator
	accumulator = PaymentsAccumulator()
	accumulator.add(tr_payments)
	accumulator.add(pp_payments)
	accumulator.add(wa_student_payments)
	#accumulator.add(wa_payout_payments)
	#print(accumulator)
	#print(f'{len(tr_payments)} TR + {len(pp_payments)} PP + {len(wa_payments)} WA')
	#print(accumulator.paymentsSortedNewestFirst()[:10])
	print("2020 grand total", accumulator.grandTotal())
	accumulator.weeklySummary()


if __name__ == "__main__":
	main()
from sqlalchemy import alias

from db import session as s
from db import Account, Transaction, Bank

from dataclean import clean_name
from util import is_blank

import api_bank_codes

# Data interfaces

def upsert_account(code, acc_type, bank, company):
	"""Atomic operation
	includes commit
	does not include normalisation 
	"""

	acc = get_account_by_code(code)
	if acc:
		if company and company != acc.organisation:
			print("Account %s with different owner: old: %d; new: %d"\
				%(code, acc.organisation.name, company.name))
			# TODO: merge organisations
	else:
		owner_id = company.id if company else None
		if code:
			acc = Account(code=code, acc_type=acc_type, bank=bank, owner_id=owner_id)
		else:
			acc = Account(acc_type=acc_type, bank=bank, owner_id=owner_id)
		
		s.add(acc)
		s.commit()

	return acc

def upsert_bank(jurisdiction, bank_code=None, name=None):
	bank = get_bank(jurisdiction, bank_code)
	if not bank:
		bank = Bank(code=bank_code, name=None, jurisdiction=jurisdiction)

		s.add(bank)
		s.commit()

	return bank

def get_bank(jurisdiction, bank_code=None):
	return s.query(Bank).filter(Bank.jurisdiction == jurisdiction,\
		Bank.code == bank_code).first()

def get_account_by_code(code):
	return s.query(Account).filter(Account.code == code).first()

#def upsert_account_detail(iban, code_local, jurisdiction, checksum,\
#		d["bank_code"], d["account_number"], sepa, d["currency"], validity)

def insert_transaction(amount_orig, amount_usd, amount_eur, currency,\
		investigation, purpose, date, source_file, from_account, to_account):

	from_acc = get_account_by_code(from_account.code) if from_account else None
	to_acc = get_account_by_code(to_account.code) if to_account else None
	trx = Transaction(amount_orig=amount_orig, amount_usd=amount_usd, amount_eur=amount_eur,\
		currency=currency, investigation=investigation,\
		purpose=purpose, date=date, source_file=source_file,\
		payee=from_acc, beneficiary=to_acc)

	s.add(trx)
	s.commit()

	return trx

# Banks util

def account_type(code):
	"""Assuming code is normalised"""
	if not code or is_blank(code):
		return "LOCAL" 
	if code[0:2].isalpha():
		if code[2:4].isdigit():
			return "IBAN"
		elif code[2:4].isalpha() and len(code) in [8,11]:
			return "SWIFT"

	return "LOCAL"

def account_country(code):
	acc_type = account_type(code)
	if acc_type == "SWIFT":
		return code[4:6]
	if acc_type == "IBAN":
		return code[:2]
	return None

def account_bank_code(code):
	acc_type = account_type(code)
	if acc_type == "IBAN":
		return api_bank_codes.get_account_bank(code)
	if acc_type == "SWIFT":
		#if len(code) == 8:
		#	code = code + "XXX"
		return api_bank_codes.get_account_bank(code)
	return None

# Public interfaces

def get_transactions_query():
	#print(s.query(Transaction).from_self())
	#[[util.format_amount(t.amount_orig), t.currency, t.payee.code, t.beneficiary.code, t.date.date().isoformat()]\
	payee = alias(Account, name="payee")
	beneficiary = alias(Account, name="beneficiary")

	q = s.query(\
		Transaction.amount_usd.label("amount_usd"),\
		Transaction.currency,\
		payee.c.code.label("payee"),\
		beneficiary.c.code.label("beneficiary"),\
		Transaction.date).\
		join(payee, Transaction.payee_id==payee.c.id).\
		join(beneficiary, Transaction.beneficiary_id==beneficiary.c.id)
	return q
	# return Transaction

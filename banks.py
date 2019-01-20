from sqlalchemy import select, delete
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy import func, alias, text, column, bindparam

from db import Session, session as s
from db import Account, Transaction, Organisation, Bank

from jurisdictions import jurisdiction_by_code
from organisations import merge_organisations

from bank_util import account_type

import api_bank_codes

from dataclean import clean_name
from util import is_blank

# Data interfaces

def upsert_account(code, acc_type, bank, company=None):
	"""Atomic operation
	includes commit
	does not include normalisation 
	"""
	# TODO: Cleanup search of accounts
	# Does not solve the entire problem. Remains scenario when local refereces comes before IBAN reference
	acc = None
	if acc_type == "LOCAL":
		iban_acc = get_iban_account_by_local_code(code)
		if iban_acc:
			acc = iban_acc
			code = iban_acc.code
			acc_type = "IBAN"

	acc = acc if acc else get_account_by_code(code)
	if acc:
		if acc.organisation:
			if company and company != acc.organisation:
				print("Account %s with different owner: old: %s; new: %s"\
					%(code, acc.organisation.name, company.name))
				merge_organisations(acc.organisation.id, company.id)
		elif company:
				acc.organisation = company
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
		bank = Bank(code=bank_code, name=name, jurisdiction=jurisdiction)

		s.add(bank)
	elif name:
		if not bank.name:
			bank.name = name
		elif bank.name != name:
			print("Bank with different name: old: %s; new: %s"\
				%(bank.name, name))
			if len(name) > len(bank.name):
				bank.name = name

	s.commit()

	return bank

def get_bank(jurisdiction, bank_code=None):
	return s.query(Bank).filter(Bank.jurisdiction == jurisdiction,Bank.code == bank_code).first()

def get_account_by_code(code):
	return s.query(Account).filter(Account.code == code).first()

def get_iban_account_by_local_code(code):
	return s.query(Account).filter(Account.code.like("%"+code), Account.acc_type=="IBAN").first()

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

def _query_incoming_transactions(acc):
	s = Session.object_session(acc)
	return s.query(Transaction).filter(Transaction.beneficiary_id==acc.id)

def _query_outgoing_transactions(acc):
	s = Session.object_session(acc)
	return s.query(Transaction).filter(Transaction.payee_id==acc.id)

def _merge_local_accounts(long_acc, short_acc):
	"""remove short_code account"""
	s = Session.object_session(short_acc)
	incoming = _query_incoming_transactions(short_acc)
	for trx in incoming:
		trx.beneficiary_id=long_acc
	outgoing = _query_outgoing_transactions(short_acc)
	for trx in outgoing:
		trx.payee_id=long_acc
	s.delete(short_acc)

	s.commit()

def _query_local_accounts(s):
	# TODO: len <= 5 to be set on import
	return s.query(Account).filter(Account.acc_type=="LOCAL",func.length(Account.code) > 5).all()

def _query_iban_account_candidate(local_acc):
	"""Not checking if has more than one result"""
	s = Session.object_session(local_acc)
	return s.query(Account).filter(Account.acc_type=="IBAN",Account.code.like('%' + local_acc.code)).first()


# Banks util

def bank_from_swift(code):
	country_code = code[4:6]
	jurisdiction = jurisdiction_by_code(country_code)

	name = api_bank_codes.get_account_bank_name(code)
	bank_code = api_bank_codes.get_account_bank_code(code)
	return upsert_bank(name=name, bank_code=bank_code, jurisdiction=jurisdiction)

def account_from_iban(code):
	country_code = code[0:2]
	jurisdiction = jurisdiction_by_code(country_code)

	acc_type = account_type(code)
	bank_code = account_bank_code(code)
	b = upsert_bank(bank_code=bank_code, jurisdiction=jurisdiction)

	acc = upsert_account(code, acc_type, b)

def account_bank_code(code):
	acc_type = account_type(code)
	if acc_type == "IBAN":
		return api_bank_codes.get_account_bank_code(code)
	if acc_type == "SWIFT":
		#if len(code) == 8:
		#	code = code + "XXX"
		return api_bank_codes.get_account_bank_code(code)
	return None

def preload_cached_accounts():
	from glob import glob
	glob = glob(api_bank_codes.bank_codes_path + "*.json")
	swift = []
	iban = []
	prefix_len = len(api_bank_codes.bank_codes_path)
	for path in glob:
		code = path[prefix_len:-5]
		if len(code) < 12: # SWIFT
			swift.append(bank_from_swift(code))
		else: # IBAN
			iban.append(account_from_iban(code))

	return (iban, swift)

# Batch-related services

def clean_local_accounts():
	s = Session()
	local_accs = _query_local_accounts(s)
	for next in local_accs:
		candidate = _query_iban_account_candidate(next)
		if candidate:
			_merge_local_accounts(candidate, next)
	s.close()


# Portal-related services

def query_organisation_by_account(code):
	s = Session()
	org = s.query(Organisation).join(Account, Account.owner_id==Organisation.id).filter(Account.code==code).first()
	result = org.json()
	s.close()
	return result


def get_transactions_statement():
	s = """
select
	amount_usd,
	tpo.name payee_org,
	tpa.code payee_acc,
	tbo.name beneficiary_org,
	tba.code beneficiary_acc,
	currency,
	tt.date_created date
from "transaction" tt
join account tpa on tpa.id=tt.payee_id
join account tba on tba.id=tt.beneficiary_id
join organisation tpo on tpo.id=tpa.owner_id
join organisation tbo on tbo.id=tba.owner_id
	"""
	subquery = text(s).columns()

	return select([column("amount_usd"),\
		column("payee_org"),column("payee_acc"),\
		column("beneficiary_org"),column("beneficiary_acc"),\
		column("currency"),column("date", type_=DateTime)]).select_from(subquery)

def get_intermediaries_statement():
	s = "select inflow, outflow, balance, source, intermediary, destination from intermediary"
	subquery = text(s).columns()

	return select([column("inflow"),column("outflow"),column("balance"),\
		column("source"),column("intermediary"),column("destination")])\
		.select_from(subquery)

if __name__ == '__main__':
	preload_cached_accounts()
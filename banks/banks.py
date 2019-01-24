from sqlalchemy import select, delete
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy import func, alias, text, column, bindparam

from db import Session
from db import Account, Transaction, Organisation, Bank

from jurisdictions import jurisdiction_by_code
from organisations import merge_organisations

#from util import is_blank, format_amount

from .util import account_type
from .api_bank_codes import get_account_bank_name, get_account_bank_code, account_bank_code
from .api_bank_codes import get_cached_accounts

# Data interfaces

def upsert_account(code, acc_type, bank_id, org_id=None):
	"""Atomic operation
	includes commit
	does not include normalisation 
	"""
	# TODO: Cleanup search of accounts
	# Does not solve the entire problem. Remains scenario when local refereces comes before IBAN reference
	s = Session()
	acc = None
	if acc_type == "LOCAL":
		iban_acc = _get_iban_account_by_local_code(s, code)
		if iban_acc:
			acc = iban_acc
			code = iban_acc.code
			acc_type = "IBAN"

	acc = acc if acc else _get_account_by_code(s, code)
	if acc:
		if acc.organisation:

			if org_id and org_id != acc.owner_id:
				print("Account %s with different owner: old: %s; new: %s"\
					%(code, acc.owner_id, org_id))
				merge_organisations(acc.owner_id, org_id)
				org_id = acc.owner_id
		elif org_id:
				acc.owner_id = org_id
	else:
		#bank = _get_bank(s, bank_id)
		if code:
			acc = Account(code=code, acc_type=acc_type, bank_id=bank_id, owner_id=org_id)
		else:
			acc = Account(acc_type=acc_type, bank_id=bank_id, owner_id=org_id)
		
		s.add(acc)

	s.commit()
	result = acc.id
	s.close()

	return result

def upsert_bank(jurisdiction_id, bank_code=None, name=None):
	s = Session()
	bank = _get_bank(s, jurisdiction_id, bank_code)
	if not bank:
		bank = Bank(code=bank_code, name=name, country_id=jurisdiction_id)
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
	result = bank.id
	s.close()

	return result

def _get_bank(s, jurisdiction_id, bank_code=None):
	return s.query(Bank).filter(Bank.country_id == jurisdiction_id,Bank.code == bank_code).first()

def get_bank(jurisdiction_id, bank_code=None):
	s = Session()
	bank = _get_bank(s, jurisdiction_id, bank_code)
	result = bank.id if bank else None
	s.close()
	return result

def _get_account(s, acc_id):
	return s.query(Account).get(acc_id)

def _get_account_by_code(s, code):
	return s.query(Account).filter(Account.code == code).first()

def get_account_by_code(code):
	s = Session()
	acc = _get_account_by_code(s, code)
	result = acc.id if acc else None
	s.close()
	return result

def _get_iban_account_by_local_code(s, code):
	return s.query(Account).filter(Account.code.like("%"+code), Account.acc_type=="IBAN").first()

def get_iban_account_by_local_code(code):
	s = Session()
	result = _get_iban_account_by_local_code(s, code)
	s.close()
	return result.id

def insert_transaction(amount_orig, amount_usd, amount_eur, currency,\
		investigation, purpose, date, source_file, from_acc_id, to_acc_id):
	s = Session()

	from_acc = _get_account(s, from_acc_id) if from_acc_id else None
	to_acc = _get_account(s, to_acc_id) if to_acc_id else None
	trx = Transaction(amount_orig=amount_orig, amount_usd=amount_usd, amount_eur=amount_eur,\
		currency=currency, investigation=investigation,\
		purpose=purpose, date=date, source_file=source_file,\
		payee=from_acc, beneficiary=to_acc)

	s.add(trx)
	s.commit()

	return trx.id

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
	jurisdiction_id = jurisdiction_by_code(country_code)

	name = get_account_bank_name(code)
	bank_code = get_account_bank_code(code)
	return upsert_bank(name=name, bank_code=bank_code, jurisdiction_id=jurisdiction_id)

def account_from_iban(code):
	country_code = code[0:2]
	jurisdiction_id = jurisdiction_by_code(country_code)

	acc_type = account_type(code)
	bank_code = account_bank_code(code)
	b = upsert_bank(bank_code=bank_code, jurisdiction_id=jurisdiction_id)

	return upsert_account(code, acc_type, b)

def preload_cached_accounts():
	swift = []
	iban = []
	for code in get_cached_accounts():
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
	s = """
select
	inflow, outflow, balance,
	source_org, source_acc,
	intermediary_org, intermediary_acc,
	destination_org, destination_acc
from intermediary
"""
	subquery = text(s).columns()

	return select([column("inflow"),column("outflow"),column("balance"),\
		column("source_org"), column("source_acc"),\
		column("intermediary_org"), column("intermediary_acc"),\
		column("destination_org"), column("destination_acc")])\
		.select_from(subquery)


if __name__ == '__main__':
	preload_cached_accounts()
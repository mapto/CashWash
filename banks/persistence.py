from db import Account, Transaction, Organisation, Bank

from db import Session

from organisations import merge_organisations
from jurisdictions import cached_jurisdictions
from util import is_blank

from .lazyinit import iban_accounts, swift_banks, cash_bank_accounts, account_owners

# from . import debug
debug = False

def upsert_account(code, acc_type, bank_id, org_id=None, fetched=False):
	"""Atomic operation
	includes commit
	does not include normalisation 
	"""
	# TODO: Cleanup search of accounts
	# Does not solve the entire problem. Remains scenario when local refereces comes before IBAN reference
	if code in iban_accounts:  # IBAN
		return iban_accounts[code]

	s = Session()

	if acc_type == "CASH":
		if bank_id:
			if bank_id not in cash_bank_accounts:
				acc = Account(code=None, acc_type="CASH", bank_id=bank_id, owner_id=org_id, fetched=True)
				s.add(acc)
				s.commit()
				cash_bank_accounts[bank_id] = acc.id
				s.close()
			return cash_bank_accounts[bank_id]
		else:
			print("CASH account without bank: code: %s, org: %d"%(code, org_id))

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
				if debug: print("Account %s with different owner: old: %s; new: %s"\
					%(code, acc.owner_id, org_id))
				merge_organisations(acc.owner_id, org_id)
				org_id = acc.owner_id
		elif org_id:
				acc.owner_id = org_id
	else:
		if not code:
			print("Account without code: bank: %d, org: %d, type: %s"%(bank_id, org_id, acc_type))
		#bank = _get_bank(s, bank_id)
		acc = Account(code=code, acc_type=acc_type, bank_id=bank_id, owner_id=org_id, fetched=fetched)
		
		s.add(acc)

	s.commit()
	result = acc.id
	s.close()

	return result

def upsert_bank(jurisdiction_id, bank_code=None, name=None, fetched=False):
	if bank_code and bank_code in swift_banks:
		return swift_banks[bank_code]

	if is_blank(name):
		name = None
	s = Session()
	bank = _get_bank(s, jurisdiction_id, bank_code)
	if not bank:
		bank = Bank(code=bank_code, name=name, country_id=jurisdiction_id, fetched=fetched)
		s.add(bank)
		cash_account = Account(code=None, acc_type="CASH", bank=bank, fetched=True) # CASH accounts don't really exist, so all pre-fetched
		s.add(cash_account)
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
	if bank_code and bank_code in swift_banks:
		return swift_banks[bank_code]

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
	if code in iban_accounts:
		return iban_accounts[code]

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

	# print("from: %d"%from_acc_id)
	from_acc = _get_account(s, from_acc_id) if from_acc_id else None
	# print("to: %d"%to_acc_id)
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
	"""Import makes sure that len(code) > 5"""
	return s.query(Account).filter(Account.acc_type=="LOCAL").all()

def _query_iban_account_candidate(local_acc):
	"""Not checking if has more than one result, code is unique in model"""
	s = Session.object_session(local_acc)
	return s.query(Account).filter(Account.acc_type=="IBAN",Account.code.like('%' + local_acc.code)).first()

def clean_local_accounts():
	s = Session()
	local_accs = _query_local_accounts(s)
	for next in local_accs:
		candidate = _query_iban_account_candidate(next)
		if candidate:
			_merge_local_accounts(candidate, next)
	s.close()

def _get_organisation_by_account(s, acc_id):
	return s.query(Account).get(acc_id).owner_id

def get_organisation_by_account(acc_id):
	if not acc_id:
		return None

	s = Session()
	result = _get_organisation_by_account(s, acc_id)
	s.close()
	return result


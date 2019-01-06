from db import session as s
from db import Organisations, Accounts, Transactions

from dataclean import clean_name
from util import is_blank 

def upsert_organisation(name, name_norm, jurisdiction, org_type, core):
	"""Includes normalisation
	Update not implemented
	"""

	name = clean_name(name)
	org = organisation_by_name(name)
	if org:
		if name_norm != None and name_norm != org.name_norm:
			print("Organisation %s with different normalised name: old: '%s'; new: '%s'"\
				%(name, org.name_norm, name_norm))
		if jurisdiction != None and jurisdiction != org.jurisdiction:
			print("Organisation %s with different jurisdiction: old: '%s'; new: '%s'"\
				%(name, org.jurisdiction, jurisdiction))
		if org_type != None and org_type != org.org_type:
			print("Organisation %s with different type: old: '%s'; new: '%s'"\
				%(name, org.org_type, org_type))
		if core != None and core != org.core:
			print("Organisation %s with different core: old: '%s'; new: '%s'"\
				%(name, org.core, core))
	else:
		org = Organisations(name=name, name_norm=name_norm, jurisdiction=jurisdiction,\
			org_type=org_type, core=core)
		
		s.add(org)
		s.commit()

	return org

def organisation_by_name(name):
	return s.query(Organisations).filter(Organisations.name.like(name)).first()


def upsert_account(code, acc_type, jurisdiction, owner):
	"""Atomic operation
	includes commit
	does not include normalisation 
	"""

	acc = account_by_code(code)
	if acc:
		if owner and owner.id != acc.owner_id:
			print("Account %s with different owner: old: %d; new: %d"\
				%(code, acc.owner_id, owner.id))		
	else:
		owner_id = owner.id if owner else None
		acc = Accounts(code=code, acc_type=acc_type, jurisdiction=jurisdiction, owner_id=owner_id)
		
		s.add(acc)
		s.commit()

	return acc

def account_by_code(code):
	return s.query(Accounts).filter(Accounts.code.like(code)).first()

def account_type(code):
	if not code or is_blank(code):
		return "CASH" 
	if code[0:2].isalpha():
		if code[2:4].isdigit():
			return "IBAN"
		elif code[2:4].isalpha() and len(code) >= 8:
			return "SWIFT"
	elif code[0:2].isdigit():
		return "LOCAL"
	return "CASH"


def insert_transaction(amount_orig, amount_usd, amount_eur, amount_orig_currency,\
		investigation, purpose, date, source_file, from_account, to_account):

	from_id = from_account.id if from_account else None
	to_id = to_account.id if to_account else None
	trx = Transactions(amount_orig=amount_orig, amount_usd=amount_usd, amount_eur=amount_eur,\
		amount_orig_currency=amount_orig_currency, investigation=investigation,\
		purpose=purpose, date=date, source_file=source_file,\
		from_account_id=from_id, to_account_id=to_id)

	s.add(trx)
	s.commit()

	return trx

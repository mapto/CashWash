from db import session as s
from db import Organisation, Alias, Jurisdiction, Account, Transaction

from dataclean import clean_name
from util import is_blank 

def upsert_organisation(name, name_norm, jurisdiction, org_type, core):
	"""Includes normalisation
	Update not implemented
	"""

	name = clean_name(name)
	name_norm = clean_name(name_norm)
	org = organisation_by_name(name)
	if org:
		#if name_norm != None and name_norm != org.name_norm:
		#	print("Organisation %s with different normalised name: old: '%s'; new: '%s'"\
		#		%(name, org.name_norm, name_norm))
		# if jurisdiction != None and jurisdiction != org.jurisdiction:
		#	print("Organisation %s with different jurisdiction: old: '%s'; new: '%s'"\
		#		%(name, org.jurisdiction, jurisdiction))
		if org_type != None and org_type != org.org_type:
			print("Organisation %s with different type: old: '%s'; new: '%s'"\
				%(name, org.org_type, org_type))
		if core != None and core != org.core:
			print("Organisation %s with different core: old: '%s'; new: '%s'"\
				%(name, org.core, core))
	else:
		org = Organisation(name=name, org_type=org_type, core=core)
		s.add(org)
		s.commit()

	jurisdiction = upsert_jurisdiction(jurisdiction, org)
	
	alias = upsert_alias(name, org)
	alias = upsert_alias(name_norm, org)

	return org

def organisation_by_name(name):
	return s.query(Organisation).filter(Organisation.name.like(name)).first()


def upsert_alias(alias, owner):
	"""Atomic operation
	includes commit
	does not include normalisation 
	"""

	if not owner:
		return None
	owner_id = owner.id
	alias = alias_by_name_and_owner(alias, owner_id)
	if not alias:
		alias = Alias(alias=alias, org_id=owner_id)
		
		s.add(alias)
		s.commit()

	return alias

def alias_by_name_and_owner(name, owner_id):
	return s.query(Alias).filter(\
		Alias.alias == name,
		Alias.org_id == owner_id).first()


def upsert_jurisdiction(country, owner):
	"""Atomic operation
	includes commit
	does not include normalisation 
	"""

	if not owner:
		return None
	owner_id = owner.id
	jurisdiction = jurisdiction_by_country_and_owner(country, owner_id)
	if not jurisdiction:
		jurisdiction = Jurisdiction(country=country, org_id=owner_id)
		
		s.add(jurisdiction)
		s.commit()

	return jurisdiction

def jurisdiction_by_country_and_owner(country, owner_id):
	return s.query(Jurisdiction).filter(\
		Jurisdiction.country == country,\
		Jurisdiction.org_id == owner_id).first()


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
			# TODO: merge organisations
	else:
		owner_id = owner.id if owner else None
		acc = Account(code=code, acc_type=acc_type, jurisdiction=jurisdiction, owner_id=owner_id)
		
		s.add(acc)
		s.commit()

	return acc

def account_by_code(code):
	return s.query(Account).filter(Account.code.like(code)).first()

#def upsert_account_detail(iban, code_local, jurisdiction, checksum,\
#		d["bank_code"], d["account_number"], sepa, d["currency"], validity)

def insert_transaction(amount_orig, amount_usd, amount_eur, amount_orig_currency,\
		investigation, purpose, date, source_file, from_account, to_account):

	from_id = from_account.id if from_account else None
	to_id = to_account.id if to_account else None
	trx = Transaction(amount_orig=amount_orig, amount_usd=amount_usd, amount_eur=amount_eur,\
		amount_orig_currency=amount_orig_currency, investigation=investigation,\
		purpose=purpose, date=date, source_file=source_file,\
		from_account_id=from_id, to_account_id=to_id)

	s.add(trx)
	s.commit()

	return trx


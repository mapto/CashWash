from sqlalchemy import alias, text, select, column

from db import Session, session as s
from db import Organisation, Alias, Jurisdiction, Account, Transaction

from dataclean import clean_name
from util import is_blank 

def upsert_organisation(name, org_type, core):
	"""Includes normalisation
	Update not implemented
	"""

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

	return org

def merge_organisations(this_id, that_id):
	"""remove short_code account"""
	success = True
	s = Session()
	this = _get_organisation(s, this_id)
	if not this:
		return False
	that = _get_organisation(s, that_id)
	if not that:
		return False

	# name, org_type, core
	if len(that.name) < len(this.name):
		this.name = that.name

	if this.org_type and that.org_type and this.org_type != that.org_type:
		print("Organisation %s with different type: old: '%s'; new: '%s'"\
			%(this.name, this.org_type, that.org_type))
		success = False
	if this.core and that.core and this.core != that.core:
		print("Organisation %s with different core: old: '%s'; new: '%s'"\
			%(this.name, this.core, that.core))
		success = False

	# accounts, aliases
	this.aliases = this.aliases + that.aliases
	this.accounts = this.accounts + that.accounts

	s.delete(that)
	s.commit()
	s.close
	return success

def _get_organisation(s, org_id):
	return s.query(Organisation).get(org_id)

def get_organisation(org_id):
	s = Session()
	org = _get_organisation(s, org_id)
	result = org.json()
	s.close()
	return result

def organisation_by_name(name):
	return s.query(Organisation).filter(Organisation.name.like(name)).first()

def upsert_alias(name, company, jurisdiction):
	"""Atomic operation
	includes commit
	does not include normalisation 
	"""
	name = clean_name(name)
	if not name or not company:
		return None
	alias = get_alias(name, company, jurisdiction)
	if not alias:
		alias = Alias(alias=name, organisation=company, jurisdiction=jurisdiction)
		s.add(alias)

	if len(name) < len(company.name):
		company.name = name

	s.commit()
	return alias

def alias_by_name_and_owner(name, owner_id):
	return s.query(Alias).filter(\
		Alias.alias == name,
		Alias.org_id == owner_id).first()

def get_alias(name, organisation, jurisdiction):
	return s.query(Alias).filter(\
		Alias.alias == name,\
		Alias.organisation == organisation,\
		Alias.jurisdiction == jurisdiction).first()


def get_accounts_statement(org_id):
	s = """
select
	ta.code code,
	tb.name bank
from account ta
join bank tb on tb.id=ta.bank_id
where ta.owner_id=%d
	"""
	subquery = text(s % org_id).columns()  # This let's it be used as a subquery

	return select([column("code"),column("bank")]).select_from(subquery)

def get_aliases_statement(org_id):
	s = """
select
	ta.alias alias,
	tj.code country
from alias ta
join jurisdiction tj on tj.id=ta.country_id
where ta.org_id=%d
	"""
	subquery = text(s % org_id).columns()  # This let's it be used as a subquery

	return select([column("alias"),column("country")]).select_from(subquery)

def get_incoming_statement(org_id):
	s = """
select
sum(ttrx.amount_usd) total,
tsorg.name source
from organisation tdorg
join account tdacc on tdacc.owner_id=tdorg.id
join "transaction" ttrx on ttrx.beneficiary_id=tdacc.id
join account tsacc on tsacc.id=ttrx.payee_id
join organisation tsorg on tsorg.id=tsacc.owner_id
where tdorg.id=%d
group by tsorg.id
	"""
	subquery = text(s % org_id).columns()  # This let's it be used as a subquery

	return select([column("total"),column("source")]).select_from(subquery)

def get_outgoing_statement(org_id):
	s = """
select
sum(ttrx.amount_usd) total,
tdorg.name destination
from organisation tdorg
join account tdacc on tdacc.owner_id=tdorg.id
join "transaction" ttrx on ttrx.beneficiary_id=tdacc.id
join account tsacc on tsacc.id=ttrx.payee_id
join organisation tsorg on tsorg.id=tsacc.owner_id
where tsorg.id=%d
group by tdorg.id
	"""
	subquery = text(s % org_id).columns()  # This let's it be used as a subquery

	return select([column("total"),column("destination")]).select_from(subquery)

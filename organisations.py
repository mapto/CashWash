from db import session as s
from db import Organisation, Alias, Jurisdiction, Account, Transaction

from dataclean import clean_name
from util import is_blank 

def upsert_organisation(name, org_type, core):
	"""Includes normalisation
	Update not implemented
	"""

	name = clean_name(name)
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

def organisation_by_name(name):
	return s.query(Organisation).filter(Organisation.name.like(name)).first()


def upsert_alias(name, company, jurisdiction):
	"""Atomic operation
	includes commit
	does not include normalisation 
	"""
	name = clean_name(name)
	if not company:
		return None
	owner_id = company.id
	alias = get_alias(name, company, jurisdiction)
	if not alias:
		alias = Alias(alias=name, organisation=company, jurisdiction=jurisdiction)
		
		s.add(alias)
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



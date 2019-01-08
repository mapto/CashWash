from db import session as s
from db import Jurisdiction

from util import is_blank

def upsert_jurisdiction(country):
	if not country or is_blank(country):
		return None
	jurisdiction = jurisdiction_by_country(country)
	if not jurisdiction:
		jurisdiction = Jurisdiction(country=country)

		s.add(jurisdiction)
		s.commit()

	return jurisdiction

def link_organisation_jurisdiction(country, organisation): 
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

def jurisdiction_by_country(country):
	return s.query(Jurisdiction).filter(Jurisdiction.country == country).first()

def jurisdiction_by_country_and_company(country, company):
	return s.query(Jurisdiction).filter(\
		Jurisdiction.country == country,\
		company in Jurisdiction.companies).first()



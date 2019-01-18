from db import Session, session as s
from db import Jurisdiction

from util import is_blank

def upsert_jurisdiction(code):
	if not code or is_blank(code):
		return None
	jurisdiction = jurisdiction_by_code(code)
	if not jurisdiction:
		jurisdiction = Jurisdiction(code=code)

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
	jurisdiction = jurisdiction_by_code_and_owner(country, owner_id)
	if not jurisdiction:
		jurisdiction = Jurisdiction(name=country, code=code, org_id=owner_id)
		
		s.add(jurisdiction)
		s.commit()

	return jurisdiction

def jurisdiction_by_code(code):
	return s.query(Jurisdiction).filter(Jurisdiction.code == code).first()

def jurisdiction_by_code_and_company(code, company):
	return s.query(Jurisdiction).filter(\
		Jurisdiction.code == code,\
		company in Jurisdiction.companies).first()

def preload_jurisdictions():
	from import_jurisdictions import import_countries
	
	all = []
	for next in import_countries():
		all.append(Jurisdiction(name=next["name"], code=next["code"]))
	s = Session()
	s.add_all(all)
	s.commit()
	s.close()

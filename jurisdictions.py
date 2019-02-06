from db import Session
from db import Jurisdiction

from util import is_blank

def upsert_jurisdiction(code):
	s = Session()
	if not code or is_blank(code):
		return None
	jurisdiction = _jurisdiction_by_code(s, code)
	if not jurisdiction:
		jurisdiction = Jurisdiction(code=code)

		s.add(jurisdiction)
		s.commit()
	result = jurisdiction.id
	s.close()

	return result
'''
def _link_organisation_jurisdiction(s, country, organisation): 
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
'''
def _jurisdiction_by_code(s, code):
	return s.query(Jurisdiction).filter(Jurisdiction.code == code).first()

def get_jurisdiction_code(id):
	s = Session()
	result = s.query(Jurisdiction).get(id).code
	s.close()
	return result

def jurisdiction_by_code(code):
	s = Session()
	result = _jurisdiction_by_code(s, code)
	s.close()
	return result.id
'''
def _jurisdiction_by_code_and_company(s, code, company):
	return s.query(Jurisdiction).filter(\
		Jurisdiction.code == code,\
		company in Jurisdiction.companies).first()

def jurisdiction_by_code_and_company(code, company):
	s = Session()
	return s.query(Jurisdiction).filter(\
		Jurisdiction.code == code,\
		company in Jurisdiction.companies).first()
'''
def preload_jurisdictions():
	from import_jurisdictions import import_countries
	
	all = []
	for next in import_countries():
		all.append(Jurisdiction(name=next["name"], code=next["code"]))
	s = Session()
	s.add_all(all)
	s.commit()
	s.close()

if __name__ == '__main__':
	preload_jurisdictions()
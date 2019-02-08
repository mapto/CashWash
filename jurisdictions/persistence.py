"""Jurisdictions are a small complete list.
Thus they can be operated from a dictionary.
Still, persisted in DB for query consitency.
Thus maintaining both synchronised and using at convenience."""

from db import Session
from db import Jurisdiction

from .lazyinit import cached_jurisdictions

# from . import debug
debug = False

def _jurisdiction_by_code(s, code):
	return s.query(Jurisdiction).filter(Jurisdiction.code == code).first()

def get_jurisdiction_code(id):
	s = Session()
	result = s.query(Jurisdiction).get(id).code
	s.close()
	return result

def jurisdiction_by_code(code):
	return cached_jurisdictions[code] if code in cached_jurisdictions else cached_jurisdictions["XX"]

def preload_jurisdictions():
	from import_jurisdictions import import_countries
	
	all = []
	for next in import_countries():
		all.append(Jurisdiction(name=next["name"], code=next["code"]))
	all.append(Jurisdiction(name="Unknown", code="XX"))
	s = Session()
	s.add_all(all)
	s.commit()
	committed = s.query(Jurisdiction).all()
	for next in committed:
		cached_jurisdictions[next.code] = next.id
	if debug: print(cached_jurisdictions)
	s.close()
	return cached_jurisdictions


"""Jurisdictions are a small complete list.
Thus they can be operated from a dictionary.
Still, persisted in DB for query consitency.
Thus maintaining both synchronised and using at convenience."""

from db import Session
from db import Jurisdiction

from .lazyinit import _cached_jurisdictions
from .api_wikipedia import import_countries

from .statements import get_jurisdictions_statement

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
	return _cached_jurisdictions[code] if code in _cached_jurisdictions else _cached_jurisdictions["XX"]

def _query_db_cache(s):
	return s.query(Jurisdiction).all()

def _load_db_cache(s):
	global _cached_jurisdictions
	committed = _query_db_cache(s)
	for next in committed:
		_cached_jurisdictions[next.code] = next.id
	return len(_cached_jurisdictions)

def cached_jurisdictions():
	if not _cached_jurisdictions:
		s = Session()
		if len(_query_db_cache(s)) == 0:
			all = []
			for next in import_countries():
				all.append(Jurisdiction(name=next["name"], code=next["code"]))
			all.append(Jurisdiction(name="Unknown", code="XX"))
			s.add_all(all)
			s.commit()
		_load_db_cache(s)
		if debug: print(_cached_jurisdictions)
		s.close()
	return _cached_jurisdictions


#!/usr/bin/env python3

"""Test with: python -m doctest -v api_open_corporates.py
"""

from os import path, makedirs
from datetime import datetime
import json

from private import oc_api_key as api_key
from settings import data_path, dateformat_log

import api_util as util

oc_path = data_path + 'opencorporates/'

# see documentation at
# https://bank.codes/api-iban/
# https://bank.codes/api-swift-code/

missing_jurisdictions = ["BZ", "IT"]

token_var = "api_token=%s&per_page=100" % api_key
search_page = "search?q=%s"
jurisdiction_var = "country_code=%s"

entities = ["companies", "officers", "corporate_groupings", "statements", "placeholders"]
searchable_entitites = ["companies", "officers", "corporate_groupings"]
searchable_statements = ["gazette_notices", "control_statements", "trademark_registrations"]

base_url = "https://api.opencorporates.com/v0.4/"
search_url = base_url + "%s/" + search_page + "&" + token_var

search_file = "search.%s.%s.json"

"https://api.opencorporates.com/companies/nl/17087985"
"https://api.opencorporates.com/v0.4/companies/search?q=barclays+bank"
"https://api.opencorporates.com/v0.4/officers/search?q=john+smith"
"https://api.opencorporates.com/v0.4/officers/%s"
"https://api.opencorporates.com/v0.4/statements/11499887"
"https://api.opencorporates.com/v0.4/placeholders/645258/network"
"statements/gazette_notices/search"
"statements/control_statements/search"
"statements/trademark_registrations/search"
"https://api.opencorporates.com/v0.4/jurisdictions/match?q=Delaware"

"https://api.opencorporates.com/v0.4/account_status?api_token=yourapitokengoeshere"

datestamp = datetime.now().strftime(dateformat_log[:6])

query_limit = 10000
counter_path = "%scounter.%s.txt" % (oc_path, datestamp)
query_counter = False

def init():
	if not path.exists(oc_path):
		makedirs(oc_path)

def _limit_queries(query_path, query_counter):
	"""Query path is needed in order to know if query is already cached, and thus excluded from the counter"""
	if not query_counter:
		#if path.exists(counter_path):
		try:
			with open(counter_path, 'r') as f:
				query_counter = int(f.read())
		except FileNotFoundError:
			query_counter = 0

	if not path.exists(query_path):
		if query_counter >= query_limit:
			return True
	
		query_counter += 1
		with open(counter_path, 'w') as f:
			f.write(str(query_counter))

	return False

def _perform_search(query_path, filename):
	if not api_key or _limit_queries(query_path, query_counter):
		raise PermissionError("Daily limit reached")
	return util.get_json_cached(query_path, filename)

def _build_search_url(term, domain="companies", jurisdiction=None):
	"""
	>>> _build_search_url("DENISON")
	'https://api.opencorporates.com/v0.4/companies/search?q=DENISON&api_token=ocJkZYgSAxxp2RGKpKKS&per_page=100'

	>>> _build_search_url("RIVERLANE", jurisdiction="gb")
	'https://api.opencorporates.com/v0.4/companies/search?q=RIVERLANE&country_code=gb&api_token=ocJkZYgSAxxp2RGKpKKS&per_page=100'

	>>> _build_search_url("EUROTRADE INTERNATIONAL HOLDING", domain="corporate_groupings", jurisdiction="us")
	'https://api.opencorporates.com/v0.4/corporate_groupings/search?q=EUROTRADE INTERNATIONAL HOLDING&country_code=us&api_token=ocJkZYgSAxxp2RGKpKKS&per_page=100'

	>>> _build_search_url("EUROTRADE INTERNATIONAL", domain="statements/control_statements", jurisdiction="us")
	'https://api.opencorporates.com/v0.4/statements/control_statements/search?q=EUROTRADE INTERNATIONAL&country_code=us&api_token=ocJkZYgSAxxp2RGKpKKS&per_page=100'

	>>> _build_search_url("RIVERLANE", domain="statements/control_statements", jurisdiction="gb")
	'https://api.opencorporates.com/v0.4/statements/control_statements/search?q=RIVERLANE&country_code=gb&api_token=ocJkZYgSAxxp2RGKpKKS&per_page=100'
	"""
	composed = term + "&" + (jurisdiction_var % jurisdiction.lower()) if jurisdiction else term
	return search_url % (domain, composed)

def _build_search_file(term, domain="companies", jurisdiction=None):
	"""
	>>> _build_search_file("DENISON")
	'search.companies.DENISON.json'

	>>> _build_search_file("RIVERLANE", jurisdiction="gb")
	'search.companies.gb.RIVERLANE.json'

	>>> _build_search_file("EUROTRADE INTERNATIONAL HOLDING", domain="corporate_groupings", jurisdiction="us")
	'search.corporate_groupings.us.EUROTRADE INTERNATIONAL HOLDING.json'

	>>> _build_search_file("EUROTRADE INTERNATIONAL", domain="statements.control_statements", jurisdiction="us")
	'search.statements.control_statements.us.EUROTRADE INTERNATIONAL.json'

	"""
	composed = domain + "." + jurisdiction.lower() if jurisdiction else domain
	return search_file % (composed, term)

def search_entities(term, domain="companies", jurisdiction=None):
	if jurisdiction in missing_jurisdictions:
		raise KeyError("Jurisdiction %s not present in OC"%jurisdiction)

	# query_path = base_url + "companies" + "/" + (search_url % term) + "&" + token_var
	query_url = _build_search_url(term, domain, jurisdiction)
	query_path = oc_path + _build_search_file(term, domain, jurisdiction)
	return _perform_search(query_path, query_url)

def search_statements(term, domain="control_statements", jurisdiction=None):
	if jurisdiction in missing_jurisdictions:
		raise KeyError("Jurisdiction %s not present in OC"%jurisdiction)

	# query_path = base_url + "statements" + "/" + "gazette_notices" + "/" + (search_url % term) + "&" + token_var
	query_url = _build_search_url(term, "statements/" + domain, jurisdiction)
	query_path = oc_path + _build_search_file(term, "statements." + domain, jurisdiction)
	
	return _perform_search(query_path, query_url)

if __name__ == '__main__':
	init()
	#print(search_entities("LCM ALLIANCE"))
	#print(search_entities("EUROTRADE INTERNATIONAL HOLDING", jurisdiction="us"))
	#print(search_entities("DENISON", "BZ"))
	print(search_statements("RIVERLANE", jurisdiction="gb"))
	for domain in searchable_entitites:
		print(search_entities("EUROTRADE INTERNATIONAL", domain, jurisdiction="us"))
	for domain in searchable_statements:
		print(search_statements("EUROTRADE INTERNATIONAL", domain, jurisdiction="us"))


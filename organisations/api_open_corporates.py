#!/usr/bin/env python3

"""Test with: python -m doctest -v api_open_corporates.py
"""

from os import path, makedirs
from datetime import datetime
import json

import api_util as util

import organisations.api_open_corporates_settings as api_settings

# see documentation at
# https://bank.codes/api-iban/
# https://bank.codes/api-swift-code/

missing_jurisdictions = ["BZ", "IT"]

token_var = "api_token=%s&per_page=100" % api_settings.key
search_page = "search?q=%s"
jurisdiction_var = "country_code=%s"

entities = ["companies", "officers", "corporate_groupings", "statements", "placeholders"]
searchable_entitites = ["companies", "officers", "corporate_groupings"]
searchable_statements = ["gazette_notices", "control_statements", "trademark_registrations"]

base_url = "https://api.opencorporates.com/v0.4/"
search_url = base_url + "%s/" + search_page + "&" + token_var

search_file = "search.%s.%s.json"
companies_file_pattern = search_file % ("companies", "*.*")

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

def init():
	if not path.exists(api_settings.api_path):
		makedirs(api_settings.api_path)

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

def search_entities(term, domain=None, jurisdiction=None):
	if jurisdiction in missing_jurisdictions:
		raise KeyError("Jurisdiction %s not present in OC"%jurisdiction)
	if not domain:
		result = {"api_version": "0.4", "results": {"page": 1, "per_page": 100, "total_pages": 1, "total_count": 0}}
		for domain in searchable_entitites:
			answer = search_entities(term, domain, jurisdiction)
			result["results"][domain] = answer["results"][domain]
			result["results"]["total_count"] += answer["results"]["total_count"]
		return result

	# query_path = base_url + "companies" + "/" + (search_url % term) + "&" + token_var
	query_url = _build_search_url(term, domain, jurisdiction)
	query_path = api_settings.api_path + _build_search_file(term, domain, jurisdiction)
	return util.peform_search(query_path, query_url, api_settings)

def search_statements(term, domain=None, jurisdiction=None):
	if jurisdiction in missing_jurisdictions:
		raise KeyError("Jurisdiction %s not present in OC"%jurisdiction)
	if not domain:
		result = {"api_version": "0.4", "results": {"page": 1, "per_page": 100, "total_pages": 1, "total_count": 0}}
		for domain in searchable_statements:
			answer = search_statements(term, domain, jurisdiction)
			found_count = answer["results"]["total_count"]
			if found_count:
				result["results"][domain] = answer["results"]["statements"]
				result["results"]["total_count"] += found_count
		return result

	# query_path = base_url + "statements" + "/" + "gazette_notices" + "/" + (search_url % term) + "&" + token_var
	query_url = _build_search_url(term, "statements/" + domain, jurisdiction)
	query_path = api_settings.api_path + _build_search_file(term, "statements." + domain, jurisdiction)
	
	return util.peform_search(query_path, query_url, api_settings)

def get_cached_results_count(term, jurisdiction):
	filename = api_settings.api_path + _build_search_file(term, jurisdiction=jurisdiction)
	result = util.get_local_json(filename)
	if not result:
		return 0
	else:
		return int(result["results"]["total_count"])
	
def get_cached_companies():
	return util.get_cached_list(companies_file_pattern, api_settings)

if __name__ == '__main__':
	init()
	#print(search_entities("LCM ALLIANCE"))
	#print(search_entities("EUROTRADE INTERNATIONAL HOLDING", jurisdiction="us"))
	#print(search_entities("DENISON", "BZ"))
	print(search_statements("RIVERLANE", jurisdiction="gb"))
	print(search_entities("EUROTRADE INTERNATIONAL", jurisdiction="us"))
	print(search_statements("EUROTRADE INTERNATIONAL", jurisdiction="us"))


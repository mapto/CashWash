#!/usr/bin/env python3

from os import path
from datetime import datetime
import json

from private import oc_api_key as api_key
from settings import data_path
from settings import dateformat_log

import api_util as util

import banks

oc_path = data_path + 'opencorporates/'

# see documentation at
# https://bank.codes/api-iban/
# https://bank.codes/api-swift-code/

token_var = "api_token=%s&per_page=100" % api_key
search_page = "search?q=%s"

entities = ["companies", "officers", "corporate_groupings", "statements", "placeholders"]
searchable_entitites = ["companies", "officers", "corporate_groupings"]
searchable_statements = ["gazette_notices", "control_statements", "trademark_registrations"]

base_url = "https://api.opencorporates.com/v0.4/"
search_url = base_url + "%s" + 

iban_url = 'https://api.bank.codes/iban/json/%s/' % api_key
swift_url = 'https://api.bank.codes/swift/json/%s/' % api_key
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

#query_limit = 50
query_limit = 10000
counter_path = "%scounter.%s.txt" % (oc_path, datestamp)
query_counter = False

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


def _search_entities(term):
	acc_type = banks.account_type(code)
	query_path = base_url + "companies" + "/" + (search_url % term) + "&" + token_var
	_perform_search(query_path, "search.companies.%s" % term)

def _search_statements(term):
	acc_type = banks.account_type(code)
	query_path = base_url + "statements" + "/" + "gazette_notices" + "/" + (search_url % term) + "&" + token_var

	if not api_key or _limit_queries(query_path, query_counter):
		raise PermissionError("Daily limit reached")
	return util.get_json_cached(query_path, urls[acc_type] + code)

if __name__ == '__main__':
	pass
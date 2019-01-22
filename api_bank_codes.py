#!/usr/bin/env python3

from os import path
from datetime import datetime
import json

from private import bankcodes_api_key as api_key
from settings import data_path
from settings import dateformat_log

from settings import data_path


import api_util as util

from bank_util import account_type

bank_codes_path = data_path + 'bank_codes/'

# see documentation at
# https://bank.codes/api-iban/
# https://bank.codes/api-swift-code/

iban_url = 'https://api.bank.codes/iban/json/%s/' % api_key
swift_url = 'https://api.bank.codes/swift/json/%s/' % api_key

urls = {"IBAN": iban_url, "SWIFT": swift_url}

datestamp = datetime.now().strftime(dateformat_log[:6])

#query_limit = 50
query_limit = 19
counter_path = "%scounter.%s.txt" % (bank_codes_path, datestamp)
query_counter = False

def _limit_queries(query_path, query_counter):
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

def _get_account_info(code):
	acc_type = account_type(code)
	query_path = bank_codes_path + code + ".json"

	if not api_key:
		raise PermissionError("Missing API key")
	if _limit_queries(query_path, query_counter):
		raise PermissionError("Daily limit reached")
	return util.get_json_cached(query_path, urls[acc_type] + code)

def get_account_country(code):
	try:
		data = _get_account_info(code)
	except PermissionError:
		return None

	valid = False
	if data and ("result" in data):
		valid = data["result"]["validation"]["iban_validity"] == "Valid"
		data = data["result"]["data"]
	valid = valid or (("valid" in data) and (data["valid"].upper() == "TRUE"))
	if not valid:
		print("Invalid code: %s" % code)
		raise LookupError(json.dumps(data))

	if "countrycode" not in data:
		print(data)

	return data["countrycode"]

def get_account_bank_name(code):
	try:
		data = _get_account_info(code)
	except PermissionError:
		return None

	valid = False
	if data and ("result" in data):
		valid = data["result"]["validation"]["iban_validity"] == "Valid"
		data = data["result"]["data"]
	valid = valid or (("valid" in data) and data["valid"])
	if not valid:
		print("Invalid code: %s" % code)
		raise LookupError(json.dumps(data))

	if not {"bic", "bank", "bank_code"}.intersection(data):
		print(data)

	if "bank" in data:
		return data["bank"]
	if "bank_code" in data:
		return data["bank_code"]
	if "bic" in data:
		return data["bic"]
	return None

def get_account_bank_code(code):
	try:
		data = _get_account_info(code)
	except PermissionError:
		return None

	valid = False
	if data and ("result" in data):
		valid = data["result"]["validation"]["iban_validity"] == "Valid"
		data = data["result"]["data"]
	valid = valid or (("valid" in data) and data["valid"])
	if not valid:
		print("Invalid code: %s" % code)
		raise LookupError(json.dumps(data))

	if not {"bic", "bank", "bank_code"}.intersection(data):
		print(data)

	if "bic" in data:
		return data["bic"]
	if "bank_code" in data:
		return data["bank_code"]
	if "bank" in data:
		return data["bank"]
	return None

if __name__ == '__main__':
	"""
	swifts = ["BARCGB22", "BOTKGB2L", "COBADEFFXXX", "BKCHCNBJ", "BKCHHKHH",\
		"BKTRUS33", "DEUTDEFFXXX", "BOFAUS3N", "HASEHKHH", "HEBACY2N", "HSBCHKHHHKH",\
		"HSBCHKHHHKH", "AIZKLV22XXX", "HYIBLI22", "IDBLILIT", "KABANL2A",\
		"NORSDE71", "NRAKAEAK", "OWHBDEFF", "PAHAAZ22", "TDOMUS33", "UBSWCHZH80A",\
		"VOAGLI22", "YAPITRIS"]
	for next in swifts:
		print(get_account_bank_name(next))
		print(get_account_country(next))
	"""
	from datatables import get_datatable_intermediaries
	l = get_datatable_intermediaries(None, 0, 20, order={"col": 1, "dir": "desc"})
	from bank_util import account_type

	# import json; print(json.dumps(l))
	for row in l["data"]:
		if row[6] and account_type(row[6]) == "IBAN":
			print(row[6])
			print(_get_account_info(row[6]))
			print(get_account_bank_name(row[6]))
			print(get_account_country(row[6]))

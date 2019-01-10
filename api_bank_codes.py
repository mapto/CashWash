#!/usr/bin/env python3

from os import path
from datetime import datetime
import json

from settings import bankcodes_api_key as api_key
from settings import data_path
from settings import dateformat_log

import api_util as util

import banks

bank_codes_path = data_path + 'bank_codes/'

# see documentation at
# https://bank.codes/api-iban/
# https://bank.codes/api-swift-code/

iban_url = 'https://api.bank.codes/iban/json/%s/' % api_key
swift_url = 'https://api.bank.codes/swift/json/%s/' % api_key

urls = {"IBAN": iban_url, "SWIFT": swift_url}

datestamp = datetime.now().strftime(dateformat_log[:6])

#query_limit = 50
query_limit = 20
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
	acc_type = banks.account_type(code)
	query_path = bank_codes_path + code + ".json"

	if not api_key or _limit_queries(query_path, query_counter):
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
	valid = valid or (("valid" in data) and data["valid"])
	if not valid:
		raise LookupError(json.dumps(data))

	return data["countrycode"]

def get_account_bank(code):
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
		raise LookupError(json.dumps(data))

	if "bank" in data:
		return data["bank"]
	if "bank_code" in data:
		return data["bank_code"]
	return None

if __name__ == '__main__':
	print(get_account_bank("EE273300333505610002"))
	print(get_account_bank("IT78T0605569721000000001000"))
	print(get_account_country("IT78T0605569721000000001000"))

	swifts = ["BARCGB22", "BOTKGB2L", "COBADEFFXXX", "BKCHCNBJ", "BKCHHKHH",\
		"BKTRUS33", "DEUTDEFFXXX", "BOFAUS3N", "HASEHKHH", "HEBACY2N", "HSBCHKHHHKH",\
		"HSBCHKHHHKH", "AIZKLV22XXX", "HYIBLI22", "IDBLILIT", "KABANL2A",\
		"NORSDE71", "NRAKAEAK", "OWHBDEFF", "PAHAAZ22", "TDOMUS33", "UBSWCHZH80A",\
		"UFUKBORU", "VOAGLI22", "YAPITRIS"]
	for next in swifts:
		print(get_account_bank(next))
		print(get_account_country(next))

	print(get_account_bank("TR410012300615100016777301"))
	print(get_account_bank("AE710200000025597675100"))
	print(get_account_bank("GE30BG0000000268330400"))
	print(get_account_bank("HU77103000021038728648820016"))
	print(get_account_bank("LV42AIZK0000010332433"))

	print(get_account_bank("SE9291900000091950511016"))
	print(get_account_bank("CY89002001200000004102425748"))
	print(get_account_bank("GB18MIDL40251931762265"))
	print(get_account_bank("ES2501825699680010381354"))
	print(get_account_bank("PL78109017660000000104850421"))

	print(get_account_bank("SI56020440258064957"))
	print(get_account_bank("LI8108800000023018098"))
	print(get_account_bank("CH2008528102153080001"))
	print(get_account_bank("FR7617789000011051095700063"))
	print(get_account_bank("LT427044060003148544"))

	print(get_account_bank("LU710021117983300000"))
	print(get_account_bank("BE27230039300073"))
	print(get_account_bank("NL18RABO0135362261"))
	print(get_account_bank("CZ5201000000351367730207"))
	print(get_account_bank("RO44UGBI0000482007133EUR"))

	print(get_account_bank("BG91RZBB91551402635603"))
	print(get_account_bank("AT311924000100462787"))
#	print(get_account_bank(""))
#	print(get_account_bank(""))
#	print(get_account_bank(""))


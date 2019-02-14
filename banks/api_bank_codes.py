from os import path
from datetime import datetime
import json
from requests.exceptions import ConnectionError

# from . import debug
# debug = True
debug = False

import api_util as util

from .util import account_type
from .lazyinit import cached_accounts

import banks.api_bank_codes_settings as api_settings

# see documentation at
# https://bank.codes/api-iban/
# https://bank.codes/api-swift-code/

bank_name_fields = ["bank", "email", "web"]
bank_code_fields = ["swift_code", "bic", "bank_code", "sort_code", "blz", "bank_branch_code"]

urls = {"IBAN": 'https://api.bank.codes/iban/json/%s/' % api_settings.key,\
	"SWIFT": 'https://api.bank.codes/swift/json/%s/' % api_settings.key}

bank_codes_file_pattern = "*.json"

def _get_account_info(code, offline=False):
	query_url = urls[account_type(code)] + code
	query_path = api_settings.api_path + code + ".json"
	if offline:
		return util.get_local_json(query_path)
	return util.peform_search(query_path, query_url, api_settings)

def fetch_account_info(code, offline=False):
	try:
		data = _get_account_info(code, offline)
		if not data:
			if len(code) == 11: # long SWIFT
				data = _get_account_info(code[:8], offline)
			if len(code) == 8: # short SWIFT
				data = _get_account_info(code + 'XXX', offline)
	except (PermissionError, ConnectionError) as err:
		print("PermissionError|ConnectionError: %s"% err)
		return None

	valid = False
	if data and ("result" in data): # IBAN
		valid = data["result"]["validation"]["iban_validity"] == "Valid"
		if valid:
			data = data["result"]["data"]
			if not offline and "swift_code" in data:  # Also make a request to fetch SWIFT data
				fetch_account_info(data["swift_code"][:8], offline=False)
	if not data and len(code) == 11: # long SWIFT
		data = fetch_account_info(code[:8], offline=offline) # short SWIFT

	valid = valid or data and (("valid" in data) and (data["valid"].upper() == "TRUE"))
	if not valid:
		if debug: print("Invalid code: %s" % code)
		raise LookupError(json.dumps(data))
	return data

def get_cached_accounts():
	global cached_accounts
	if not cached_accounts:
		cached_accounts = util.get_cached_list(bank_codes_file_pattern, api_settings)
	return cached_accounts

def get_account_country(code, offline=False):
	data = fetch_account_info(code, offline)

	if data and "countrycode" in data:
		return data["countrycode"]

	if debug: print("Unable to get bank country from %s" % data)
	return None


def get_account_bank_name(code, offline=False):
	data = fetch_account_info(code, offline)
	if not data:
		return None

	acc_type = account_type(code)
	if acc_type == "IBAN":
		for val in bank_name_fields + bank_code_fields:
			if val in data and data[val].strip():
				return data[val]
	elif acc_type == "SWIFT":
		if data and "bank" in data:
			return data["bank"]

	if debug: print("Unable to get bank name from %s" % data)
	return None

def get_account_bank_code(code, offline=False):
	data = fetch_account_info(code, offline)
	if not data:
		return None

	acc_type = account_type(code)
	if acc_type == "IBAN":
		for val in bank_code_fields:
			if val in data and data[val].strip():
				return data[val]
	elif acc_type == "SWIFT":
		return code

	if debug: print("Unable to get bank code from %s" % data)
	return None

def account_bank_code(code, offline=False):
	acc_type = account_type(code)
	if acc_type == "IBAN":
		return get_account_bank_code(code, offline)
	if acc_type == "SWIFT":
		return code
	return None


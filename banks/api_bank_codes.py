from os import path
from datetime import datetime
import json
from requests.exceptions import ConnectionError

# from . import debug
debug = False

import api_util as util

from .util import account_type

import banks.api_bank_codes_settings as api_settings

# see documentation at
# https://bank.codes/api-iban/
# https://bank.codes/api-swift-code/

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
	except (PermissionError, ConnectionError) as err:
		if debug: print(err)
		return None

	valid = False
	if data and ("result" in data):
		valid = data["result"]["validation"]["iban_validity"] == "Valid"
		if valid:
			data = data["result"]["data"]
	valid = valid or (("valid" in data) and (data["valid"].upper() == "TRUE"))
	if not valid:
		print("Invalid code: %s" % code)
		raise LookupError(json.dumps(data))
	return data

def get_cached_accounts():
	return util.get_cached_list(bank_codes_file_pattern, api_settings)

def get_account_country(code):
	data = fetch_account_info(code)

	if not data or "countrycode" not in data:
		print("Unable to get account country from %s" % data)
		return None

	return data["countrycode"]

def get_account_bank_name(code, offline=False):
	data = fetch_account_info(code, offline)
	
	if not data:
		return None
	if not data or not {"bic", "bank", "bank_code", "bank_branch_code"}.intersection(data):
		print("Unable to get bank name from %s" % data)
		print(data)
		return None

	if "bank" in data:
		return data["bank"]
	if "bank_code" in data:
		return data["bank_code"]
	if "bic" in data:
		return data["bic"]
	if "bank_branch_code" in data:
		return data["bank_branch_code"]
	return None

def get_account_bank_code(code, offline=False):
	data = fetch_account_info(code, offline)
	
	if not data or not {"bic", "bank", "bank_code", "bank_branch_code"}.intersection(data):
		if debug: print("Unable to get bank code from %s" % data)
		return None

	if "bic" in data:
		return data["bic"]
	if "bank_code" in data:
		return data["bank_code"]
	if "bank" in data:
		return data["bank"]
	if "bank_branch_code" in data:
		return data["bank_branch_code"]
	return None

def account_bank_code(code, offline=False):
	acc_type = account_type(code)
	if acc_type == "IBAN":
		return get_account_bank_code(code, offline)
	if acc_type == "SWIFT":
		#if len(code) == 8:
		#	code = code + "XXX"
		return get_account_bank_code(code, offline)
	return None


from os import path
from datetime import datetime
import json
from requests.exceptions import ConnectionError

from . import api_key, data_path, dateformat_log
#from . import debug
debug = False

from api_util import get_json_cached

from .util import account_type

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
		if query_counter > query_limit:
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
	return get_json_cached(query_path, urls[acc_type] + code)

def fetch_account_info(code):
	try:
		data = _get_account_info(code)
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
	from glob import glob
	files = glob(bank_codes_path + "*.json")
	prefix_len = len(bank_codes_path)
	return [path[prefix_len:-5] for path in files]

def get_account_country(code):
	data = fetch_account_info(code)

	if not data or "countrycode" not in data:
		print(data)
		return None

	return data["countrycode"]

def get_account_bank_name(code):
	data = fetch_account_info(code)
	
	if not data:
		return None
	if not data or not {"bic", "bank", "bank_code", "bank_branch_code"}.intersection(data):
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

def get_account_bank_code(code):
	data = fetch_account_info(code)
	
	if not data or not {"bic", "bank", "bank_code", "bank_branch_code"}.intersection(data):
		print(data)
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

def account_bank_code(code):
	acc_type = account_type(code)
	if acc_type == "IBAN":
		return get_account_bank_code(code)
	if acc_type == "SWIFT":
		#if len(code) == 8:
		#	code = code + "XXX"
		return get_account_bank_code(code)
	return None


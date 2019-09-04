from jurisdictions import jurisdiction_by_code

#from util import is_blank, format_amount

from .util import account_type
from .api_bank_codes import get_account_bank_name, get_account_bank_code, account_bank_code
from .api_bank_codes import get_cached_accounts

from .persistence import upsert_bank, upsert_account
from .persistence import get_account_by_code, get_organisation_by_account

from .lazyinit import iban_accounts, swift_banks

debug = False
# debug = True

# Data interfaces

# Banks util

def bank_from_swift(code, fetched=False):
	"""fetched indicates if the data was cached from some API"""
	if code in swift_banks:
		return swift_banks[code]

	country_code = code[4:6]
	jurisdiction_id = jurisdiction_by_code(country_code)
	if not fetched:
		code = code[:8]  # Ignore branch info

	try:
		name = get_account_bank_name(code, offline=fetched)
		bank_code = get_account_bank_code(code, offline=fetched)
	except LookupError as e:
		if debug: print("LookupError: %s"%e)
		name = None
		bank_code = code

	return upsert_bank(name=name, bank_code=bank_code, jurisdiction_id=jurisdiction_id, fetched=fetched)

def account_from_iban(code, fetched=False):
	"""fetched indicates if data is to be searched only locally. Would be present if it was cached from some API."""
	country_code = code[0:2]
	jurisdiction_id = jurisdiction_by_code(country_code)

	try:
		b = None
		bank_code = account_bank_code(code, offline=fetched)
		if bank_code and account_type(bank_code) == "SWIFT":
			b = bank_from_swift(bank_code, fetched=True)
		if not b:
			b = upsert_bank(bank_code=bank_code, jurisdiction_id=jurisdiction_id, fetched=fetched)
		acc_id = upsert_account(code, account_type(code), b)
	except LookupError as e:
		if debug: print("LookupError: %s"%e)
		acc_id = None

	return acc_id

# Batch-related services

def preload_cached_accounts():
	upsert_bank(jurisdiction_id=None, name="UNKNOWN", fetched=True)
	cached = get_cached_accounts()
	print("Number of cached accounts: %d" % len(cached))
	
	for code in cached:
		if len(code) < 12: # SWIFT
			swift_banks[code] = bank_from_swift(code, fetched=True)
			if len(code) == 11:
				if code[:8] not in swift_banks:
					swift_banks[code[:8]] = swift_banks[code]
			elif len(code) == 8:
				if code + 'XXX' not in swift_banks:
					swift_banks[code + 'XXX'] = swift_banks[code]
		else: # IBAN
			iban_accounts[code] = account_from_iban(code, fetched=True)

	if debug:
		print(iban_accounts)
		print(swift_banks)
	return (iban_accounts, swift_banks)

def is_cached_swift_code(name):
	if len(name) not in [8,11] or not code[0:4].isalpha():
		return False
	return name in swift_banks

# Portal-related services
def query_organisation_by_account_code(code):
	if not code:
		return None
	acc_id = get_account_by_code(code)
	return get_organisation_by_account(acc_id)



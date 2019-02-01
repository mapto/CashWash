from jurisdictions import jurisdiction_by_code

#from util import is_blank, format_amount

from .util import account_type
from .api_bank_codes import get_account_bank_name, get_account_bank_code, account_bank_code
from .api_bank_codes import get_cached_accounts
from .persistence import upsert_bank, upsert_account

# Data interfaces

# Banks util

def bank_from_swift(code, fetched=False):
	"""fetched indicates if the data was cached from some API"""
	country_code = code[4:6]
	jurisdiction_id = jurisdiction_by_code(country_code)

	name = get_account_bank_name(code)
	bank_code = get_account_bank_code(code)
	return upsert_bank(name=name, bank_code=bank_code, jurisdiction_id=jurisdiction_id, fetched=fetched)

def account_from_iban(code, fetched=False):
	"""fetched indicates if the data was cached from some API"""
	country_code = code[0:2]
	jurisdiction_id = jurisdiction_by_code(country_code)

	acc_type = account_type(code)
	bank_code = account_bank_code(code)
	b = upsert_bank(bank_code=bank_code, jurisdiction_id=jurisdiction_id, fetched=fetched)

	return upsert_account(code, acc_type, b)

# Batch-related services

def preload_cached_accounts():
	swift = []
	iban = []
	for code in get_cached_accounts():
		if len(code) < 12: # SWIFT
			swift.append(bank_from_swift(code, fetched=True))
		else: # IBAN
			iban.append(account_from_iban(code, fetched=True))

	return (iban, swift)


if __name__ == '__main__':
	preload_cached_accounts()
#!/usr/bin/env python3

import api_util

import banks

from datatables import get_datatable_cashflows

"""
for code in banks.get_cached_accounts():
	try:
		banks.fetch_account_info(code, offline=False)
	except LookupError as e:
		print(code)
		print(e)
"""
l = get_datatable_cashflows(None, 0, 1000, order={"col": 1, "dir": "desc"})

for row in l["data"]:
	for col in [4,6,8]:
		if row[col] and banks.account_type(row[col]) == "IBAN":
			try:
				print(row[col])
				print(banks.get_account_bank_name(row[col], offline=False))
				# print(banks.get_account_country(row[col], offline=False))
			except LookupError as e:
				print("Invalid account: %s" % row[col])
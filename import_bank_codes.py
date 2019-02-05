#!/usr/bin/env python3
from datatables import get_datatable_cashflows
from banks import account_type, get_account_bank_name, get_account_country

l = get_datatable_cashflows(None, 0, 500, order={"col": 1, "dir": "desc"})

# import json; print(json.dumps(l))
for row in l["data"]:
	for col in [4,6,8]:
		if row[col] and account_type(row[col]) == "IBAN":
			print(row[col])
			#print(_get_account_info(row[col]))
			try:
				print(get_account_bank_name(row[col]))
				print(get_account_country(row[col]))
			except LookupError as e:
				print("Invalid account: %s" % row[col])

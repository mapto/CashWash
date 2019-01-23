#!/usr/bin/env python3
from datatables import get_datatable_intermediaries
from banks import account_type, get_account_bank_name, get_account_country

l = get_datatable_intermediaries(None, 0, 50, order={"col": 0, "dir": "desc"})

# import json; print(json.dumps(l))
for row in l["data"]:
	if row[6] and account_type(row[6]) == "IBAN":
		print(row[6])
		#print(_get_account_info(row[6]))
		print(get_account_bank_name(row[6]))
		print(get_account_country(row[6]))

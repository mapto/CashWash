#!/usr/bin/env python3

import json
import re
from datetime import datetime

import requests

from settings import dateformat, data_path

import util

# from db import Organisation, Account, Transaction

import jurisdictions, banks, organisations

laundromat_url = 'https://cdn.occrp.org/projects/azerbaijanilaundromat/interactive/dkdata.json'
laundromat_json = data_path + "laundromat.json"


def read_role(row, role):
	name = row[role + "_name"]
	norm = row[role + "_name_norm"]
	country = row[role + "_jurisdiction"]
	org_type = row[role + "_type"]
	core = row[role + "_core"]

	code = str(row[role + "_account"])
	code = re.sub(r"\s" , "", code)
	acc_type = banks.account_type(code)
	if acc_type == "IBAN":
		acc_country = code[0:2]
		if acc_country != row[role + "_bank_country"]:
			print("Account %s with conflicting bank country: jurisdiction: '%s'; code: '%s'"\
				%(code, row[role + "_bank_country"], acc_country))

	elif acc_type == "SWIFT":
		acc_country = code[4:6]		
	else:
		acc_country = row[role + "_bank_country"]

	jurisdiction = jurisdictions.upsert_jurisdiction(country)
	acc_jurisdiction = jurisdictions.upsert_jurisdiction(acc_country)

	account = banks.get_account_by_code(code)
	if account:
		if account.organisation:
			org = account.organisation
		else:
			org = organisations.upsert_organisation(norm, org_type, core)

		organisations.upsert_alias(name, org, jurisdiction)
		organisations.upsert_alias(norm, org, jurisdiction)
	else:
		org = organisations.upsert_organisation(norm, org_type, core)
		organisations.upsert_alias(name, org, jurisdiction)
		organisations.upsert_alias(norm, org, jurisdiction)

		bank_code = banks.account_bank_code(code)
		acc_bank = banks.upsert_bank(jurisdiction, bank_code)
		account = banks.upsert_account(code, acc_type, acc_bank, org)

	return account


def read_transaction(row, from_account, to_account):
	amount_orig = util.parse_amount(row['amount_orig'])
	amount_usd = util.parse_amount(row['amount_usd'])
	amount_eur = util.parse_amount(row['amount_eur'])
	amount_orig_currency = row['amount_orig_currency']

	investigation = row['investigation']
	purpose = row['purpose']
	date = datetime.strptime(row['date'], dateformat)
	source_file = row['source_file']

	return banks.insert_transaction(amount_orig, amount_usd, amount_eur, amount_orig_currency,\
		investigation, purpose, date, source_file, from_account, to_account)

def json2db(data):
	for row in data:
		# print(row)

		from_acc = read_role(row, "payer")
		to_acc = read_role(row, "beneficiary")

		read_transaction(row, from_acc, to_acc)

if __name__ == '__main__':
	data = util.get_cached(laundromat_json, laundromat_url)

	json2db(data["data"])


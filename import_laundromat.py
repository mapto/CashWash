#!/usr/bin/env python3

import json
import re
from datetime import datetime

import requests

from settings import dateformat

import util

from db import Organisations, Accounts, Transactions

import service

laundromat_url = 'https://cdn.occrp.org/projects/azerbaijanilaundromat/interactive/dkdata.json'
laundromat_json = "data/laundromat.json"


def read_org(row, role):
	"""In the laundromat data role can be "payer" or "beneficiary"
	"""
	name = row[role + "_name"]
	norm = row[role + "_name_norm"]
	country = row[role + "_jurisdiction"]
	org_type = row[role + "_type"]
	core = row[role + "_core"]
	
	return service.upsert_organisation(name, norm, country, org_type, core)

def read_account(row, org, role):
	code = str(row[role + "_account"])
	code = re.sub(r"\s" , "", code)
	acc_type = service.account_type(code)
	if acc_type in ["IBAN", "SWIFT"]:
		country = code[0:2]
	else:
		country = row[role + "_bank_country"]
	service.upsert_account(code, acc_type, country, org)

def read_transaction(row, from_account, to_account):
	amount_orig = util.parse_amount(row['amount_orig'])
	amount_usd = util.parse_amount(row['amount_usd'])
	amount_eur = util.parse_amount(row['amount_eur'])
	amount_orig_currency = row['amount_orig_currency']

	investigation = row['investigation']
	purpose = row['purpose']
	date = datetime.strptime(row['date'], dateformat)
	source_file = row['source_file']

	return service.insert_transaction(amount_orig, amount_usd, amount_eur, amount_orig_currency,\
		investigation, purpose, date, source_file, from_account, to_account)

def json2db(data):
	for row in data:
		# print(row)

		payer = read_org(row, "payer")
		beneficiary = read_org(row, "beneficiary")

		from_acc = read_account(row, payer, "payer")
		to_acc = read_account(row, beneficiary, "beneficiary")

		read_transaction(row, from_acc, to_acc)

if __name__ == '__main__':
	data = util.get_cached(laundromat_json, laundromat_url)

	json2db(data["data"])


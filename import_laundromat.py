#!/usr/bin/env python3

import json
import re
from datetime import datetime

import requests

from settings import dateformat, data_path
import dataclean
import util, api_util

# from db import Organisation, Account, Transaction

import jurisdictions, banks, organisations

laundromat_json_url = 'https://cdn.occrp.org/projects/azerbaijanilaundromat/interactive/dkdata.json'
laundromat_json = data_path + "laundromat.json"

laundromat_csv_url = 'https://public.data.occrp.org/open/Combined%20Laundromats%2020180602.csv'
laundromat_csv = data_path + "laundromat.csv"

def read_role(row, role):
	country = row[role + "_jurisdiction"].strip()
	if len(country) != 2:
		if not util.is_blank(country):
			print("Country %s is not ISO-639-1 code" % country)
		country = None

	name = dataclean.clean_name(row[role + "_name"], country)
	norm = dataclean.clean_name(row[role + "_name_norm"], country)

	org_type = row[role + "_type"]
	core = row[role + "_core"].upper() == "TRUE"

	code = str(row[role + "_account"])
	code = re.sub(r"\s" , "", code)
	acc_type = banks.account_type(code)
	acc_country = row[role + "_bank_country"]

	bank_name = dataclean.clean_name(row[role + "_bank"], acc_country)
	bank_code = None
	#bank_code = banks.account_bank_code(code) if util.is_blank(bank_name) else None

	if acc_type == "IBAN":
		bank_country = code[0:2]
		if not util.is_blank(bank_country) and acc_country != bank_country:
			if not util.is_blank(acc_country):
				print("Account %s with conflicting bank country: jurisdiction: '%s'; code: '%s'"\
					%(code, acc_country, bank_country))
			acc_country = bank_country
	elif acc_type == "SWIFT":
		acc_country = code[4:6]		

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

		acc_bank = banks.upsert_bank(jurisdiction, bank_code=bank_code, name=bank_name)
		account = banks.upsert_account(code, acc_type, acc_bank, org)

	return account


def read_transaction(row, from_account, to_account):
	amount_orig = util.parse_amount(row['amount_orig'])
	amount_usd = util.parse_amount(row['amount_usd'])
	amount_eur = util.parse_amount(row['amount_eur'])
	currency = row['amount_orig_currency']

	investigation = row['investigation']
	purpose = row['purpose']
	date = datetime.strptime(row['date'], dateformat)
	source_file = row['source_file']

	return banks.insert_transaction(amount_orig, amount_usd, amount_eur, currency,\
		investigation, purpose, date, source_file, from_account, to_account)

def json2db(data):
	'''
	{
		"payer_name": "AZARBAYCAN METANOL KOMPANI MMC",
		"payer_jurisdiction": "AZ",
		"payer_account": "33817018409333311204",
		"source_file": "pdf/LCM ALLIANCE Account statement 30.06.12-31.12.14.xml",
		"amount_orig": 535470.0,
		"id": 6049,
		"beneficiary_type": "Company",
		"beneficiary_core": true,
		"amount_orig_currency": "USD",
		"beneficiary_name": "LCM ALLIANCE LLP",
		"beneficiary_jurisdiction": "GB",
		"investigation": "az",
		"beneficiary_bank_country": "EE",
		"beneficiary_name_norm": "LCM ALLIANCE LLP",
		"payer_core": false,
		"beneficiary_account": "EE27 3300 3335 0561 0002",
		"purpose": "1206295100052180 OCT4121800021 ADVANCE PAYM FOR THE INST RUMENTATIO N AND CONTROL CABLES BOM IN ACC WIT H THE CON TR DD 25.06.2012",
		"date": "2012-06-30",
		"amount_usd": 535470,
		"amount_eur": "$431,762.31",
		"payer_type": "Company",
		"payer_name_norm": "AZARBAYCAN METANOL KOMPANI MMC",
		"payer_bank_country": "33"
	}
	'''

	for row in data:
		# print(row)

		from_acc = read_role(row, "payer")
		to_acc = read_role(row, "beneficiary")

		read_transaction(row, from_acc, to_acc)

def csv2db(data):
	"""
	combined dataset:
	0: "origin",
	+1: "date",
	+2: "amount",
	+3: "currency",
	+4: "amount_eur",
	+5: "amount_usd",
	+6: "purpose",
	+7: "payer_name",
	+8: "payer_name_original",
	+9: "payer_jurisdiction",
	+10: "payer_core",
	+11: "payer_account",
	+12: "payer_bank",
	+13: "payer_bank_country",
	+14: "beneficiary_name",
	+15: "beneficiary_name_original",
	+16: "beneficiary_jurisdiction",
	+17: "beneficiary_core",
	+18: "beneficiary_account",
	+19: "beneficiary_bank",
	+20: "beneficiary_bank_country",
	21: "reference_no",
	22: "sequence_no",
	+23: "source_file"
	"""
	json_data = []
	for row in data:
		json_data.append({\
			"payer_name": row[8],\
			"payer_name_norm": row[7],\
			"payer_type": "Unknown",\
			"payer_core": row[10],\
			"payer_jurisdiction": row[9],\
			"payer_account": row[11],\
			"payer_bank": row[12],\
			"payer_bank_country": row[13],\

			"beneficiary_name": row[15],\
			"beneficiary_name_norm": row[14],\
			"beneficiary_type": "Unknown",\
			"beneficiary_core": row[17],\
			"beneficiary_jurisdiction": row[16],\
			"beneficiary_account": row[18],\
			"beneficiary_bank": row[19],\
			"beneficiary_bank_country": row[20],\

			"source_file": row[23],\
			#"id": 6049,
			"investigation": "%s:%s:%s"%(row[0],row[21],row[22]),\
			"purpose": row[6],\
			"date": row[1],\

			"amount_orig": row[2],\
			"amount_usd": row[5],\
			"amount_eur": row[4],\
			"amount_orig_currency": row[3]\
		})

	return json2db(json_data)

if __name__ == '__main__':
	#data = api_util.get_json_cached(laundromat_json, laundromat_json_url)
	#json2db(data["data"])

	data = api_util.get_csv_cached(laundromat_csv, laundromat_csv_url)
	csv2db(data[1:])


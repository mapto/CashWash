#!/usr/bin/env python3

import json
import re
from datetime import datetime

import requests

from settings import dateformat, data_path
import dataclean
import util, api_util

import db_views

# from db import Organisation, Account, Transaction

import jurisdictions, banks, organisations

laundromat_json_url = 'https://cdn.occrp.org/projects/azerbaijanilaundromat/interactive/dkdata.json'
laundromat_json = data_path + "laundromat.json"

laundromat_csv_url = 'https://public.data.occrp.org/open/Combined%20Laundromats%2020180602.csv'
laundromat_csv = data_path + "laundromat.csv"

def read_role(name, norm=None, country="XX", code=None, bank_name=None, acc_country="XX", core=False):
	jurisdiction_id = jurisdictions.jurisdiction_by_code(country)

	code = re.sub(r"\s" , "", code).lstrip("0")
	acc_type = banks.account_type(code)

	try:
		bank_code = banks.account_bank_code(code, offline=True) if util.is_blank(bank_name) and not util.is_blank(code) else None
		bank_code = None if util.is_blank(bank_code) or util.contains_whitespace(bank_code) else bank_code
	except LookupError as e:
		bank_code = None

	if acc_type == "CASH" and banks.account_type(name) == "SWIFT":
		bank_code = name
		code = None
		name = None
		norm = None
		acc_bank_id = banks.get_bank(jurisdiction_id, bank_code)\
			or banks.upsert_bank(jurisdiction_id, bank_code=bank_code, name=bank_name)
		acc_id = banks.upsert_account(code, acc_type, acc_bank_id, None)
		return acc_id		
	elif acc_type == "IBAN":
		bank_country = code[0:2]
		if not bank_country or (bank_country not in jurisdictions.cached_jurisdictions().keys()):
			print("Unrecognised account country: %s" % bank_country)
			bank_country = "XX"
		if acc_country != bank_country:
			if not util.is_blank(acc_country):
				print("Account %s with conflicting bank country: jurisdiction: '%s'; code: '%s'"\
					%(code, acc_country, bank_country))
			acc_country = bank_country
	elif acc_type == "SWIFT":
		acc_country = code[4:6]

	acc_jurisdiction_id = jurisdictions.jurisdiction_by_code(acc_country)
	acc_id = banks.get_account_by_code(code)
	if acc_id:
		org_id = banks.get_organisation_by_account(acc_id)\
			or organisations.upsert_organisation(norm, core)
			# or organisations.upsert_organisation(norm, org_type, core)
		organisations.upsert_alias(name, org_id, jurisdiction_id)
		if norm != name:
			organisations.upsert_alias(norm, org_id, jurisdiction_id)
	else:
		org_id = organisations.upsert_organisation(norm, core)
		# org_id = organisations.upsert_organisation(norm, org_type, core)
		# TODO: Problem creating alias if the organisation is not yet persisted
		organisations.upsert_alias(name, org_id, jurisdiction_id)
		if norm != name:
			organisations.upsert_alias(norm, org_id, jurisdiction_id)

		acc_bank_id = banks.get_bank(jurisdiction_id, bank_code)\
			or banks.upsert_bank(jurisdiction_id, bank_code=bank_code, name=bank_name)
		acc_id = banks.upsert_account(code, acc_type, acc_bank_id, org_id)

	return acc_id

def parse_role(row, role):
	country = util.clean_confusables(row[role + "_jurisdiction"].strip())
	"""
	if len(country) != 2:
		if not util.is_blank(country):
			print("Country %s is not ISO-639-1 code" % country)
		country = None
	"""
	name = dataclean.clean_name(row[role + "_name"], country)
	norm = dataclean.clean_name(row[role + "_name_norm"], country)

	# org_type = row[role + "_type"]
	core = row[role + "_core"].upper() == "TRUE"

	code = str(row[role + "_account"])
	acc_country = util.clean_confusables(row[role + "_bank_country"])
	bank_name = dataclean.clean_name(row[role + "_bank"], acc_country)

	return read_role(name, norm, country, code, bank_name, acc_country, core)

def parse_transaction(row, from_acc_id, to_acc_id):
	amount_orig = util.parse_amount(row['amount_orig'])
	amount_usd = util.parse_amount(row['amount_usd'])
	amount_eur = util.parse_amount(row['amount_eur'])
	currency = row['amount_orig_currency']

	investigation = row['investigation']
	purpose = row['purpose']
	date = datetime.strptime(row['date'], dateformat)
	source_file = row['source_file']

	return banks.insert_transaction(amount_orig, amount_usd, amount_eur, currency,\
		investigation, purpose, date, source_file, from_acc_id, to_acc_id)

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
	print("Preloading jurisdictions...")
	jurisdictions.cached_jurisdictions()
	print("Preloading cached accounts...")
	banks.preload_cached_accounts()
	print("Importing transactions...")
	total = len(data); counter = 0
	start = datetime.now()
	for row in data:
		# print(row)
		counter += 1
		if not (100 * counter / total % 1): print("Importing %d%%..."%(100 * counter / total))
		from_acc = parse_role(row, "payer")
		to_acc = parse_role(row, "beneficiary")
		parse_transaction(row, from_acc, to_acc)
	end = datetime.now()
	elapsed = (end-start).total_seconds()
	print("Transactions imported in %d mins %f secs." % (elapsed//60, elapsed%60))
	print("Merging duplicate accounts...")
	banks.clean_local_accounts()
	print("Optimising aliases...")
	organisations.optimise_aliases()
	print("Generating views...")
	start = datetime.now()
	db_views.init()
	end = datetime.now()
	elapsed = (end-start).total_seconds()
	print("Views generated in %f secs." % elapsed)

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

	json2db(json_data)

if __name__ == '__main__':
	from db import setup_db; setup_db()
	#data = api_util.get_json_cached(laundromat_json, laundromat_json_url)
	#json2db(data["data"])

	data = api_util.get_csv_cached(laundromat_csv, laundromat_csv_url)
	csv2db(data[1:])


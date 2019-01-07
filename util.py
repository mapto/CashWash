from os import path
import requests
import json
import re

def list2csv(l, filename):
	with open(filename, 'w') as f:
		f.write("\n".join(l))

def dict2csv(d, filename):
	with open(filename, 'w') as f:  # Just use 'w' mode in 3.x
		for k,v in d.items():
			# k = k.encode('utf-8')
			f.write("%s,%s\n"%(k,v))

def dump_counts(d, filename):
	with open(filename, 'w') as f:  # Just use 'w' mode in 3.x
		for k,v in d.items():
			# k = k.encode('utf-8')
			f.write("%4d: %s\n"%(v,k))

def csv2list(filename):
	with open(filename) as f:
		lines = f.read().splitlines()

def is_blank(s):
	return not s or s.upper() in ["NONE", "NULL", "UNKNOWN"] 

def parse_amount(s):
	try:
		v = re.sub(r"\$", "", s)
		v = re.sub(r"\,", "", v)
	except TypeError: # not a string
		v = s
	return int(float(v) * 100)

def account_type(code):
	"""Assuming code is normalised"""
	if not code or is_blank(code):
		return "CASH" 
	if code[0:2].isalpha():
		if code[2:4].isdigit():
			return "IBAN"
		elif code[2:4].isalpha() and len(code) >= 8:
			return "SWIFT"
	elif code[0:2].isdigit():
		return "LOCAL"
	return "CASH"

def get_cached(filename, url):
	if path.isfile(filename):
		with open(filename, 'r') as f:
			data = json.load(f)
	else:
		response = requests.get(url)
		response.raise_for_status()
		data = response.json()
		with open(filename, 'w') as f:
			json.dump(data, f)

	return data


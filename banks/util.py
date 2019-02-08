import re

from util import is_blank
from jurisdictions import cached_jurisdictions

def account_type(code):
	"""Assuming code is normalised"""
	if not code or is_blank(code) or len(code) < 6:
		return "CASH" 
	if code[0:2].isalpha():
		if code[2:4].isdigit() and code[0:2] in cached_jurisdictions():
			return "IBAN"
		elif len(code) in [8,11] and code[2:4].isalpha() and not re.search(r"\s", code):
			return "SWIFT"

	return "LOCAL"

def account_country(code):
	acc_type = account_type(code)
	if acc_type == "SWIFT":
		return code[4:6]
	if acc_type == "IBAN":
		return code[:2]
	return None


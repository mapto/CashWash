from util import is_blank

def account_type(code):
	"""Assuming code is normalised"""
	if not code or is_blank(code) or len(code) < 6:
		return "UNKNOWN" 
	if code[0:2].isalpha():
		if code[2:4].isdigit():
			return "IBAN"
		elif code[2:4].isalpha() and len(code) in [8,11]:
			return "SWIFT"

	return "LOCAL"

def account_country(code):
	acc_type = account_type(code)
	if acc_type == "SWIFT":
		return code[4:6]
	if acc_type == "IBAN":
		return code[:2]
	return None


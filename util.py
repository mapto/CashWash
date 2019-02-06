import re
import json

from confusable_homoglyphs.confusables import is_confusable

from settings import precision_digits
precision_format_string = "%." + str(precision_digits) + "f"
from settings import debug

blanks = ["NONE", "NULL", "UNKNOWN"]

def diff(inflow, outflow):
	"Safely calculate difference, handling null arriving from DB"
	outflow = outflow or 0
	inflow = inflow or 0
	return inflow - outflow

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
	return not s or not s.strip() or s.strip().upper() in blanks

def parse_amount(s):
	try:
		v = re.sub(r"\$|\,", "", s)
		#v = re.sub(r"\$", "", s)
		#v = re.sub(r"\,", "", v)
	except TypeError: # not a string
		v = s
	return int(float(v) * (10 ** precision_digits))

def format_amount(d):
	if not d:
		return "0." + "0" * precision_digits
	return precision_format_string % (float(d) / (10 ** precision_digits))

def clean_confusables(s):
	confusions = is_confusable(s, greedy=True, preferred_aliases=["latin"])
	result = s
	#print(confusions)
	if not confusions:
		return s
	for next in confusions:
		found = next['character']
		if len(next['homoglyphs']) > 1:
			print("In %s found %s"%(s,json.dumps(next)))
		generic = next['homoglyphs'][0]['c']
		result = result.replace(found, generic)
	return result

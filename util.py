import re

from settings import precision_digits

blanks = ["NONE", "NULL", "UNKNOWN"]

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
	return not s or s.upper() in blanks

def parse_amount(s):
	try:
		v = re.sub(r"\$|\,", "", s)
		#v = re.sub(r"\$", "", s)
		#v = re.sub(r"\,", "", v)
	except TypeError: # not a string
		v = s
	return int(float(v) * (10 ** precision_digits))

def format_amount(d):
	return ("%." + str(precision_digits) + "f")%(float(d) / (10 ** precision_digits))


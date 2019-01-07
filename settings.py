from os import path

from private import bankcodes_api_key

#host = '185.80.0.213'
host = 'localhost'
port = 8080
curdir = path.dirname(path.realpath(__file__))
path.curdir = curdir

data_path = curdir + "/data/"

db_path = 'sqlite:///' + data_path + 'CashWash.db'

#debug = True
debug = False

intermediaries_csv = data_path +'intermediaries.csv'
autoalias_py = "autoalias.py"

dateformat = "%Y-%m-%d"

# TODO: Make country-dependent dictionary
'''
legal_forms = {\
	"IT": ["SPA", "SRL"],\
	"GB": ["SPA", "SRL"],\
	"DE": ["SPA", "SRL"],\
}
'''
legal_form =\
	['LTD', 'LIMITED', 'LLP', 'LLC', 'LP',\
	'GMBH', 'ZOO', 'AG', 'AS', 'SPA', 'SL', 'SRL', 'SAS', 'SA', \
	'INC', 'CO', 'CORP', 'BVBA',\
	'BV', 'HK']
	# TODO: remove CO

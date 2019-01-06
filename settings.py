from os import path

#host = '185.80.0.213'
host = 'localhost'
port = 8080
curdir = path.dirname(path.realpath(__file__))
path.curdir = curdir
db_path = 'sqlite:///' + curdir + '/data/CashWash.db'

#debug = True
debug = False

intermediaries_csv = 'data/intermediaries.csv'
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

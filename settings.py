from os import path

curdir = path.dirname(path.realpath(__file__))
path.curdir = curdir

host = 'localhost'
port = 80  # Change this if you host any web sites locally

# Make sure that directory paths throughout this project always finish with a slash (/)
static_path = curdir + "/static/"
data_path = curdir + "/data/"

db_path = data_path + 'CashWash.db'
db_url = 'sqlite:///' + db_path + '?check_same_thread=False'

intermediaries_csv = data_path +'intermediaries.csv'
autoalias_py = "autoalias.py"

precision_digits = 2  # Currency precision. Leave as is unless you introduce some high-precision calculations

dateformat = "%Y-%m-%d"  # Used by the original Laundromat dataset
dateformat_log = "%Y%m%d%H%M%S" # Used to generate data backups

# debug = True
debug = False


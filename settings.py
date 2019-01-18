from os import path

curdir = path.dirname(path.realpath(__file__))
path.curdir = curdir

#host = '185.80.0.213'
host = 'localhost'
port = 80
static_path = curdir + "/static/"
data_path = curdir + "/data/"

db_path = data_path + 'CashWash.db'
db_url = 'sqlite:///' + db_path + '?check_same_thread=False'

intermediaries_csv = data_path +'intermediaries.csv'
autoalias_py = "autoalias.py"

precision_digits = 2

dateformat = "%Y-%m-%d"
dateformat_log = "%Y%m%d%H%M%S"

debug = True
#debug = False


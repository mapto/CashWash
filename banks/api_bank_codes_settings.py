from datetime import datetime

from private import oc_api_key as api_key
from . import data_path, dateformat_log

api_path = data_path + 'bank_codes/'
counter_path = "%scounter.%s.txt" % (api_path, datetime.now().strftime(dateformat_log[:6]))
limit = 19
key = api_key
counter = False


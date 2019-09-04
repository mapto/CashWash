#!/usr/bin/env python3

import csv

from settings import data_path

from db import Session

import banks

dest = data_path + "transactions.csv"

unit = 10000000

def transactions2csv(dest):
	s = Session()
	statement = banks.get_transaction_log_statement()
	result = s.execute(statement).fetchall()
	s.close()
	total = len(result)

	header = True
	with open(dest, 'w') as csvfile:
	    spamwriter = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

	    for next in result:
	    	if header:
	    		spamwriter.writerow(next.keys())
	    		header = False

	    	row = list(next.values())
	    	amount = row[0]
	    	while amount > unit:
	    		row[0] = unit
	    		amount -= unit
	    		spamwriter.writerow(row)
	    	row[0] = amount
    		spamwriter.writerow(row)

transactions2csv(dest)

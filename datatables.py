"""Server-side processing for https://datatables.net/manual/server-side"""

from sqlalchemy import func, column

from db import Session

from util import format_amount

import banks, organisations, jurisdictions

datatable_empty = {"draw": 1, "lenght": 25, "start": 0, "recordsTotal": 0, "recordsFiltered": 0, "data": []}
default_order = {"col": 0, "dir": "asc"}


# Util

def _read_order(cols, request_args):
	order = []
	order_col = 1
	for i in range(cols):
		order_col = request_args.get('order[%d][column]'%i)
		order_dir = request_args.get('order[%d][dir]'%i)
		if order_col:
			order.append((order_col, order_dir))
		else:
			break
	return order	

def _total_records(statement):
	s = Session()
	result = s.execute(statement).fetchall()
	s.close()
	return len(result)

def _get_page(statement, page_num=0, page_size=25, order=default_order):
	s = Session()
	col = column(statement.columns.keys()[order["col"]])
	order_func = getattr(col, order["dir"]) if order else None
	offset = page_num * page_size
	pg_stmt = statement.order_by(order_func()).offset(offset).limit(offset + page_size)
	result = s.execute(pg_stmt)
	s.close()
	return result


# Transactions

def get_datatable_transactions(draw, start=0, length=25, order=None):
	page = start/length if start and length else 0

	q = banks.get_transactions_statement()
	total_records = _total_records(q)

	response = {"draw": draw, "length": length, "start": start, \
		"recordsTotal": total_records, "recordsFiltered": total_records,\
		"data": [[format_amount(t.amount_usd),\
			t.payee_org, t.payee_acc,\
			t.beneficiary_org, t.beneficiary_acc, t.currency, t.date.date().isoformat()]\
			for t in _get_page(q, page, length, order)]}
	return response

def get_datatable_cashflows(draw, start=0, length=25, order=None):
	page = start/length if start and length else 0

	q = banks.get_cashflows_statement()
	total_records = _total_records(q)

	response = {"draw": draw, "length": length, "start": start, \
		"recordsTotal": total_records, "recordsFiltered": total_records,\
		"data": [[\
			format_amount(t.inflow), format_amount(t.outflow), format_amount(t.balance),\
			t.source_org, t.source_acc,\
			t.intermediary_org, t.intermediary_acc,\
			t.destination_org, t.destination_acc]\
			for t in _get_page(q, page, length, order)]}
	return response


# Organisations

def get_datatable_organisations(draw, start=0, length=25, order=None):
	page = start/length if start and length else 0

	q = organisations.get_organisations_statement()
	total_records = _total_records(q)

	response = {"draw": draw, "length": length, "start": start, \
		"recordsTotal": total_records, "recordsFiltered": total_records,\
		"data": [[t.id,	t.name, format_amount(t.inflow), format_amount(t.outflow), format_amount(t.balance)]\
			for t in _get_page(q, page, length, order)]}
	return response

def get_datatable_intermediaries(draw, start=0, length=25, order=None):
	page = start/length if start and length else 0

	q = banks.get_intermediaries_statement()
	total_records = _total_records(q)

	response = {"draw": draw, "length": length, "start": start, \
		"recordsTotal": total_records, "recordsFiltered": total_records,\
		"data": [[\
			format_amount(t.inflow), format_amount(t.outflow), format_amount(t.balance),\
			t.intermediary_org, t.intermediary_acc]\
			for t in _get_page(q, page, length, order)]}
	return response

def get_datatable_aliases(org_id, draw, start=0, length=25, order=None):
	page = start/length if start and length else 0

	q = organisations.get_aliases_statement(org_id)
	total_records = _total_records(q)
	response = {"draw": draw, "length": length, "start": start, \
		"recordsTotal": total_records, "recordsFiltered": total_records,\
		"data": [[t.alias, t.country]\
			for t in _get_page(q, page, length, order)]}
	return response

def get_datatable_accounts(org_id, draw, start=0, length=25, order=None):
	page = start/length if start and length else 0

	q = organisations.get_accounts_statement(org_id)
	total_records = _total_records(q)
	response = {"draw": draw, "length": length, "start": start, \
		"recordsTotal": total_records, "recordsFiltered": total_records,\
		"data": [[t.code, t.bank]\
			for t in _get_page(q, page, length, order)]}
	return response

def get_datatable_incoming(org_id, draw, start=0, length=25, order=None):
	page = start/length if start and length else 0

	q = organisations.get_incoming_statement(org_id)
	total_records = _total_records(q)
	response = {"draw": draw, "length": length, "start": start, \
		"recordsTotal": total_records, "recordsFiltered": total_records,\
		"data": [[format_amount(t.total), t.source]\
			for t in _get_page(q, page, length, order)]}
	return response

def get_datatable_outgoing(org_id, draw, start=0, length=25, order=None):
	page = start/length if start and length else 0

	q = organisations.get_outgoing_statement(org_id)
	total_records = _total_records(q)
	response = {"draw": draw, "length": length, "start": start, \
		"recordsTotal": total_records, "recordsFiltered": total_records,\
		"data": [[format_amount(t.total), t.destination]\
			for t in _get_page(q, page, length, order)]}
	return response


# Banks

def get_datatable_banks(draw, start=0, length=25, order=None):
	page = start/length if start and length else 0

	q = banks.get_banks_statement()
	total_records = _total_records(q)
	response = {"draw": draw, "length": length, "start": start, \
		"recordsTotal": total_records, "recordsFiltered": total_records,\
		"data": [[t.name, t.code, t.jurisdiction, t.accs, t.orgs]\
			for t in _get_page(q, page, length, order)]}
	return response


# Jurisdictions

def get_datatable_jurisdictions(draw, start=0, length=25, order=None):
	page = start/length if start and length else 0

	q = jurisdictions.get_jurisdictions_statement()
	total_records = _total_records(q)
	response = {"draw": draw, "length": length, "start": start, \
		"recordsTotal": total_records, "recordsFiltered": total_records,\
		"data": [[t.name, t.code, t.aliases, t.orgs, t.banks, t.accs]\
			for t in _get_page(q, page, length, order)]}
	return response

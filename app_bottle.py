#!/usr/bin/env python3
import json

import bottle
from bottle import get, route, request, response, run, error, static_file

from settings import host, port, static_path
from settings import curdir, db_url
from settings import debug

import banks, organisations

import datatables

# Errors
@error(404)
def mistake404(code):
    return 'Sorry, this page does not exist.'

@error(405)
def mistake405(code):
    return 'The given call is not allowed by the application.'

@error(422)
def mistake422(code):
    return 'The request was well-formed but was unable to be followed due to semantic errors.'

@error(500)
def mistake500(code):
    return 'Server experienced internal problem.'

@error(504)
def mistake504(code):
    return 'Unable to access internal service.'

# Object requests
@route('/owner/<code>', method=['GET'])
def get_organisation_by_account(code):
	return banks.query_organisation_by_account(code)

# Util
## Datatables
def _prepare_datatable_parameters(request):
	draw = request.query['draw']
	start = request.query['start']
	start = int(start) if start else 0

	length = request.query['length']
	length = int(length) if length else 25

	order_col = request.query['order[0][column]']
	if order_col:
		order_dir = request.query['order[0][dir]']
		order = {"col": int(order_col),\
			"dir": order_dir if order_dir else "asc"}
	else:
		order = None
	
	return (draw, start, length, order)	

# API queries
@route('/summary', method=['GET'])
def get_summary():
	return static_file("summary.json", root=static_path + "js") # bottle wants root path without trailing slash

@route('/api/bank_codes/<code>', method=['GET'])
def query_bank_codes(code):
	return banks.fetch_account_info(code)

@route('/api/open_corporates/<name>', method=['GET'])
@route('/api/open_corporates/<name>/<jurisdiction>', method=['GET'])
def query_open_corporates(name, jurisdiction=None):
	return organisations.search_entities(name, jurisdiction=jurisdiction)


# Datatables
## Transactions
@route('/datatables/transactions', method=['GET'])
def get_datatable_transactions():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_transactions(*params)	
	return response

@route('/datatables/cashflows', method=['GET'])
def get_datatable_cashflows():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_cashflows(*params)
	return response


## Organisations
@route('/datatables/organisations', method=['GET'])
def get_datatable_organisations():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_organisations(*params)	
	return response

@route('/datatables/intermediaries', method=['GET'])
def get_datatable_intermediaries():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_intermediaries(*params)
	return response

@route('/datatables/aliases/<org_id>', method=['GET'])
def get_datatable_aliases(org_id):
	if not org_id:
		return datatable_empty

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_aliases(int(org_id), *params)
	return response

@route('/datatables/accounts/<org_id>', method=['GET'])
def get_datatable_accounts(org_id):
	if not org_id:
		return datatable_empty

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_accounts(int(org_id), *params)
	return response

@route('/datatables/incoming/<org_id>', method=['GET'])
def get_datatable_incoming(org_id):
	if not org_id:
		return datatable_empty

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_incoming(int(org_id), *params)
	return response


@route('/datatables/outgoing/<org_id>', method=['GET'])
def get_datatable_outgoing(org_id):
	if not org_id:
		return datatable_empty

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_outgoing(int(org_id), *params)
	return response


## Banks
@route('/datatables/banks', method=['GET'])
def get_datatable_banks():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_banks(*params)
	return response


## Jurisdictions
@route('/datatables/jurisdictions', method=['GET'])
def get_datatable_jurisdictions():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_jurisdictions(*params)
	return response


# Static resources
@route('/<resource_type:re:(js|css|images)>/<filename:re:.*\.(js|css|png)>')
def send_resource(resource_type, filename):
	return static_file(filename, root=static_path + resource_type)

@route('/')
@route('/<filename:re:.*\.html>')
def send_page(filename='index.html'):
	return static_file(filename, root=static_path[:-1]) # bottle wants root path without trailing slash


if __name__ == '__main__':
    run(host=host, port=port, reloader=True, debug=debug)


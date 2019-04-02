#!/usr/bin/env python3
import json

from bottle import Bottle, static_file, request

from settings import host, port, static_path
from settings import curdir, db_url
from settings import debug

import banks, organisations

import datatables

app = Bottle()

# Errors
@app.error(404)
def mistake404(code):
    return 'Sorry, this page does not exist.'

@app.error(405)
def mistake405(code):
    return 'The given call is not allowed by the application.'

@app.error(422)
def mistake422(code):
    return 'The request was well-formed but was unable to be followed due to semantic errors.'

@app.error(500)
def mistake500(code):
    return 'Server experienced internal problem.'

@app.error(504)
def mistake504(code):
    return 'Unable to access internal service.'

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
@app.get('/summary')
def get_summary():
	return static_file("summary.json", root=static_path + "js") # bottle wants root path without trailing slash

@app.get('/api/bank_codes/<code>')
def query_bank_codes(code):
	if not code:
		app.abort(405, "Cannot process empty code")
	result = banks.fetch_account_info(code)
	if not result:
		app.abort(504, "Failed fetching bank code")
	return result

@app.get('/api/open_corporates/<name>')
@app.get('/api/open_corporates/<name>/<jurisdiction>')
def query_open_corporates(name, jurisdiction=None):
	return organisations.search_entities(name, jurisdiction=jurisdiction)

# Object requests
@app.get('/owner/<account_code>')
def get_organisation_by_account(account_code):
	if not account_code:
		app.abort(405, "Empty code has no owner")
	org_id = banks.query_organisation_by_account_code(account_code)
	return organisations.get_organisation(org_id)

@app.get('/alias/<name>')
@app.get('/alias/<name>/<country>')
def get_alias_history(name, country=None):
	return query_open_corporates(name, country)


# Datatables
## Transactions
@app.get('/datatables/transactions')
def get_datatable_transactions():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_transactions(*params)	
	return response

@app.get('/datatables/cashflows')
def get_datatable_cashflows():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_cashflows(*params)
	return response


## Organisations
@app.get('/datatables/organisations')
def get_datatable_organisations():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_organisations(*params)	
	return response

@app.get('/datatables/intermediaries')
def get_datatable_intermediaries():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_intermediaries(*params)
	return response

@app.get('/datatables/aliases/<org_id:int>')
def get_datatable_aliases(org_id):
	if not org_id:
		return datatable_empty

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_aliases(int(org_id), *params)
	return response

@app.get('/datatables/accounts/<org_id:int>')
def get_datatable_accounts(org_id):
	if not org_id:
		return datatable_empty

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_accounts(int(org_id), *params)
	return response

@app.get('/datatables/incoming/<org_id:int>')
def get_datatable_incoming(org_id):
	if not org_id:
		return datatable_empty

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_incoming(int(org_id), *params)
	return response


@app.get('/datatables/outgoing/<org_id:int>')
def get_datatable_outgoing(org_id):
	if not org_id:
		return datatable_empty

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_outgoing(int(org_id), *params)
	return response


## Banks
@app.get('/datatables/banks')
def get_datatable_banks():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_banks(*params)
	return response


## Jurisdictions
@app.get('/datatables/jurisdictions')
def get_datatable_jurisdictions():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_jurisdictions(*params)
	return response


# Static resources
@app.get('/<resource_type:re:(js|css|images)>/<filename:re:.*\.(js|css|png)>')
def send_resource(resource_type, filename):
	return static_file(filename, root=static_path + resource_type)

@app.get('/')
@app.get('/<filename:re:.*\.html>')
def send_page(filename='index.html'):
	return static_file(filename, root=static_path[:-1]) # bottle wants root path without trailing slash


if __name__ == '__main__':
    app.run(host=host, port=port, reloader=True, debug=debug)


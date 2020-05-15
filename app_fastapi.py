#!/usr/bin/env python3
from os import path

import json

from fastapi import FastAPI, HTTPException

from settings import host, port, static_path
from settings import curdir, db_url
from settings import debug

import banks, organisations

import datatables

app = FastAPI()

def static_file(filename: str, root: str):
	contents = None
	with open(path.join(root, filename), "r") as f:
		contents = f.read
	return contents

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
async def get_summary():
	return static_file("summary.json", root=static_path + "js") # bottle wants root path without trailing slash

@app.get('/api/bank_codes/{code}')
async def query_bank_codes(code: str = None):
	if not code:
		raise HTTPException(status_code=405, detail="Cannot process empty code")
	result = banks.fetch_account_info(code)
	if not result:
		raise HTTPException(status_code=504, detail="Failed fetching bank code")
	return result

@app.get('/api/open_corporates/{name}')
@app.get('/api/open_corporates/{name}/{jurisdiction}')
async def query_open_corporates(name: str, jurisdiction: str = None):
	return organisations.search_entities(name, jurisdiction=jurisdiction)

# Object requests
@app.get('/owner/{account_code}')
async def get_organisation_by_account(account_code: str):
	if not account_code:
		raise HTTPException(status_code=405, detail="Empty code has no owner")		
	org_id = banks.query_organisation_by_account_code(account_code)
	return organisations.get_organisation(org_id)

@app.get('/alias/{name}')
@app.get('/alias/{name}/{country}')
async def get_alias_history(name: str, country: str=None):
	return query_open_corporates(name, country)


# Datatables
## Transactions
@app.get('/datatables/transactions')
async def get_datatable_transactions():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_transactions(*params)	
	return response

@app.get('/datatables/cashflows')
async def get_datatable_cashflows():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_cashflows(*params)
	return response


## Organisations
@app.get('/datatables/organisations')
async def get_datatable_organisations():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_organisations(*params)	
	return response

@app.get('/datatables/intermediaries')
async def get_datatable_intermediaries():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_intermediaries(*params)
	return response

@app.get('/datatables/aliases/{org_id}')
async def get_datatable_aliases(org_id: int):
	if not org_id:
		return datatable_empty

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_aliases(int(org_id), *params)
	return response

@app.get('/datatables/accounts/{org_id}')
async def get_datatable_accounts(org_id: int):
	if not org_id:
		return datatable_empty

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_accounts(int(org_id), *params)
	return response

@app.get('/datatables/incoming/{org_id}')
async def get_datatable_incoming(org_id: int):
	if not org_id:
		return datatable_empty

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_incoming(int(org_id), *params)
	return response


@app.get('/datatables/outgoing/{org_id}')
async def get_datatable_outgoing(org_id: int):
	if not org_id:
		return datatable_empty

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_outgoing(int(org_id), *params)
	return response


## Banks
@app.get('/datatables/banks')
async def get_datatable_banks():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_banks(*params)
	return response


## Jurisdictions
@app.get('/datatables/jurisdictions')
async def get_datatable_jurisdictions():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_jurisdictions(*params)
	return response


# Static resources
@app.get('/<resource_type:re:(js|css|images)>/<filename:re:.*\.(js|css|png)>')
async def send_resource(resource_type, filename):
	return static_file(filename, root=static_path + resource_type)

@app.get('/')
@app.get('/<filename:re:.*\.html>')
async def send_page(filename='index.html'):
	return static_file(filename, root=static_path[:-1])

if __name__ == '__main__':
	import uvicorn
	uvicorn.run(app, host=host, port=port, reload=True, debug=debug)

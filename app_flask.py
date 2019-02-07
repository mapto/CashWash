#!/usr/bin/env python3
import json

from werkzeug.routing import BaseConverter

from flask import Flask, jsonify
from flask import send_from_directory
from flask import request

from settings import host, port, static_path
# from settings import debug
debug = True

import banks, organisations

import datatables

app = Flask(__name__, static_url_path="")

# Object requests
@app.route('/owner/<code>', methods=['GET'])
def get_organisation_by_account(code):
	return jsonify(banks.query_organisation_by_account(code))

# Datatables
def _prepare_datatable_parameters(request):
	draw = request.args.get('draw')
	start = request.args.get('start')
	start = int(start) if start else 0

	length = request.args.get('length')
	length = int(length) if length else 25

	order_col = request.args.get('order[0][column]')
	if order_col:
		order_dir = request.args.get('order[0][dir]')
		order = {"col": int(order_col),\
			"dir": order_dir if order_dir else "asc"}
	else:
		order = None
	
	return (draw, start, length, order)	

# API queries
@app.route('/summary', methods=['GET'])
def get_summary():
	return send_from_directory(static_path + "js", "summary.json")

@app.route('/api/bank_codes/<code>', methods=['GET'])
def query_bank_codes(code):
	return jsonify(banks.fetch_account_info(code))

@app.route('/api/open_corporates/<name>', methods=['GET'])
@app.route('/api/open_corporates/<name>/<jurisdiction>', methods=['GET'])
def query_open_corporates(name, jurisdiction=None):
	return jsonify(organisations.search_entities(name, jurisdiction=jurisdiction))


# Datatables
## Transactions
@app.route('/datatables/transactions', methods=['GET'])
def get_datatable_transactions():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_transactions(*params)	
	return jsonify(response)

@app.route('/datatables/cashflows', methods=['GET'])
def get_datatable_cashflows():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_cashflows(*params)
	return jsonify(response)


## Organisations
@app.route('/datatables/organisations', methods=['GET'])
def get_datatable_organisations():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_organisations(*params)	
	return jsonify(response)

@app.route('/datatables/intermediaries', methods=['GET'])
def get_datatable_intermediaries():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_intermediaries(*params)
	return jsonify(response)

@app.route('/datatables/aliases/<org_id>', methods=['GET'])
def get_datatable_aliases(org_id):
	if not org_id:
		return jsonify(datatable_empty)

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_aliases(int(org_id), *params)
	return jsonify(response)

@app.route('/datatables/accounts/<org_id>', methods=['GET'])
def get_datatable_accounts(org_id):
	if not org_id:
		return jsonify(datatable_empty)

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_accounts(int(org_id), *params)
	return jsonify(response)

@app.route('/datatables/incoming/<org_id>', methods=['GET'])
def get_datatable_incoming(org_id):
	if not org_id:
		return jsonify(datatable_empty)

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_incoming(int(org_id), *params)
	return jsonify(response)


@app.route('/datatables/outgoing/<org_id>', methods=['GET'])
def get_datatable_outgoing(org_id):
	if not org_id:
		return jsonify(datatable_empty)

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_outgoing(int(org_id), *params)
	return jsonify(response)


## Banks
@app.route('/datatables/banks', methods=['GET'])
def get_datatable_banks():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_banks(*params)
	return jsonify(response)


## Jurisdictions
@app.route('/datatables/jurisdictions', methods=['GET'])
def get_datatable_jurisdictions():
	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_jurisdictions(*params)
	return jsonify(response)


# Static resources
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

@app.route('/<regex("js|css|images"):resource_type>/<path:path>')
def send_resource(resource_type, path):
	return send_from_directory(static_path + resource_type, path)

@app.route('/')
def root():
    return app.send_static_file("index.html")


if __name__ == '__main__':
    app.run(host, port, debug)


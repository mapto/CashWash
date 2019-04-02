#!/usr/bin/env python3
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

# Errors
@app.errorhandler(404)
def mistake404(code):
    return 'Sorry, this page does not exist.', 405

@app.errorhandler(405)
def mistake405(code):
    return 'The given call is not allowed by the application.', 405

@app.errorhandler(422)
def mistake422(code):
    return 'The request was well-formed but was unable to be followed due to semantic errors.', 405

@app.errorhandler(500)
def mistake500(code):
    return 'Server experienced internal problem.', 405

@app.errorhandler(504)
def mistake504(code):
    return 'Unable to access internal service.', 405

# Util
## Datatables
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
	if not code:
		app.abort(405, "Cannot process empty code")
	result = banks.fetch_account_info(code)
	if not result:
		app.abort(504, "Failed fetching bank code")
	return jsonify(result)

@app.route('/api/open_corporates/<name>', methods=['GET'])
@app.route('/api/open_corporates/<name>/<jurisdiction>', methods=['GET'])
def query_open_corporates(name, jurisdiction=None):
	return jsonify(organisations.search_entities(name, jurisdiction=jurisdiction))

# Object requests
@app.route('/owner/<code>', methods=['GET'])
def get_organisation_by_account(code):
	if not code:
		app.abort(405, "Cannot process empty code")
	org_id = banks.query_organisation_by_account_code(code)
	return jsonify(organisations.get_organisation(org_id))


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

@app.route('/datatables/aliases/<int:org_id>', methods=['GET'])
def get_datatable_aliases(org_id):
	if not org_id:
		return jsonify(datatable_empty)

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_aliases(int(org_id), *params)
	return jsonify(response)

@app.route('/datatables/accounts/<int:org_id>', methods=['GET'])
def get_datatable_accounts(org_id):
	if not org_id:
		return jsonify(datatable_empty)

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_accounts(int(org_id), *params)
	return jsonify(response)

@app.route('/datatables/incoming/<int:org_id>', methods=['GET'])
def get_datatable_incoming(org_id):
	if not org_id:
		return jsonify(datatable_empty)

	params = _prepare_datatable_parameters(request)
	response = datatables.get_datatable_incoming(int(org_id), *params)
	return jsonify(response)


@app.route('/datatables/outgoing/<int:org_id>', methods=['GET'])
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


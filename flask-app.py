#!flask/bin/python
import json

from werkzeug.routing import BaseConverter

from flask import Flask, jsonify
from flask import send_from_directory
from flask import request

from settings import host, port, static_path
from settings import debug

import util

import banks, organisations

import pagination

datatable_empty = {"draw": 1, "lenght": 25, "start": 0, "recordsTotal": 0, "recordsFiltered": 0, "data": []}

app = Flask(__name__, static_url_path="")

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

@app.route('/datatables/transactions', methods=['GET'])
def get_datatable_transactions():
	draw = request.args.get('draw')
	start = request.args.get('start')
	start = int(start) if start else 0

	length = request.args.get('length')
	length = int(length) if length else 25
	
	page = start/length if start and length else 0

	order = {"col": int(request.args.get('order[0][column]')), "dir": request.args.get('order[0][dir]')}

	q = banks.get_transactions_statement()
	response = {"draw": draw, "length": length, "start": start, \
		"recordsTotal": pagination.count_total(q), "recordsFiltered": pagination.count_total(q),\
		"data": [[util.format_amount(t.amount_usd), t.payee_org, t.payee_acc, t.beneficiary_org, t.beneficiary_acc, t.currency, t.date]\
			for t in pagination.get_page(q, page, length, order)]}
	return jsonify(response)


@app.route('/datatables/aliases/<org_id>', methods=['GET'])
def get_datatable_aliases(org_id):
	if not org_id:
		return jsonify(datatable_empty)

	draw = request.args.get('draw')
	start = request.args.get('start')
	start = int(start) if start else 0

	length = request.args.get('length')
	length = int(length) if length else 25
	
	page = start/length if start and length else 0

	order = {"col": int(request.args.get('order[0][column]')), "dir": request.args.get('order[0][dir]')}

	q = organisations.get_aliases_statement(int(org_id))
	response = {"draw": draw, "length": length, "start": start, \
		"recordsTotal": pagination.count_total(q), "recordsFiltered": pagination.count_total(q),\
		"data": [[t.alias, t.country]\
			for t in pagination.get_page(q, page, length, order)]}

	return jsonify(response)


# Serve static content
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

@app.route('/<regex("js|css|images|fonts"):resource_type>/<path:path>')
def send_resource(resource_type, path):
	return send_from_directory(static_path + resource_type, path)

@app.route('/')
def root():
    return app.send_static_file("index.html")


if __name__ == '__main__':
    app.run(host, port, debug)

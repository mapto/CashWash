#!flask/bin/python
from flask import Flask, jsonify

from settings import host, port, debug

import banks

app = Flask(__name__)

@app.route('/transactions/', methods=['GET'])
@app.route('/transactions/<int:page>/', methods=['GET'])
@app.route('/transactions/<int:page>/<int:size>/', methods=['GET'])
def get_transactions(page=0, size=25):
	response = "{'page': %d, 'size': %d, 'data': %s}"
	return jsonify(response % (page, size, banks.get_transactions(page, size)))

if __name__ == '__main__':
    app.run(host, port, debug)

from os import path
import requests
import json

def get_json_cached(filename, url):
	if path.isfile(filename):
		with open(filename, 'r') as f:
			data = json.load(f)
	else:
		response = requests.get(url)
		response.raise_for_status()
		data = response.json()
		with open(filename, 'w') as f:
			json.dump(data, f)

	return data

def get_csv_cached(filename, url):
	# TODO
	raise NotImplementedError()

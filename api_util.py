from os import path
import requests
import json, csv

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
	if not path.isfile(filename):
		response = requests.get(url)
		response.raise_for_status()
		data = response.content
		with open(filename, 'wb') as f:
			f.write(data)

	with open(filename, 'r', encoding="utf-8") as csvfile:
		csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
		data = [data for data in csvreader]
		# data = [[bytes(s, "utf-8") for s in data] for data in csvreader]

	return data

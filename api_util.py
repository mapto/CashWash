from os import path
import requests
import json, csv

# debug = True
debug = False

def _limit_queries(query_path, settings):
	"""Query path is needed in order to know if query is already cached, and thus excluded from the counter"""
	if not settings.counter:
		#if path.exists(counter_path):
		try:
			with open(settings.counter_path, 'r') as f:
				settings.counter = int(f.read())
		except FileNotFoundError:
			settings.counter = 0

	if not path.exists(query_path):
		if settings.counter > settings.limit:
			return True
	
		settings.counter += 1
		with open(settings.counter_path, 'w') as f:
			f.write(str(settings.counter))

	return False

def peform_search(query_path, query_url, settings):
	if not settings.key:
		raise PermissionError("Missing API key")
	if _limit_queries(query_path, settings):
		raise PermissionError("Daily limit reached")
	return get_json_cached(query_path, query_url)

def get_local_json(filename):
	if debug: print("Trying local file: %s"%filename)
	if path.isfile(filename):
		with open(filename, 'r') as f:
			data = json.load(f)
	else:
		data = None
	return data


def get_cached_list(pattern, settings):
	from glob import glob
	files = glob(settings.api_path + pattern)
	prefix_len = len(settings.api_path)
	return [path[prefix_len:-5] for path in files]


# Online file fetchers

def get_json_cached(filename, url):
	if path.isfile(filename):
		if debug: print("Reading local json: %s"%filename)
		with open(filename, 'r') as f:
			data = json.load(f)
	else:
		if debug: print("Fetching remote json: %s"%url)
		response = requests.get(url)
		response.raise_for_status()
		data = response.json()
		with open(filename, 'w') as f:
			json.dump(data, f)

	return data

def get_csv_cached(filename, url):
	if path.isfile(filename):
		if debug: print("Reading local csv: %s"%filename)
		with open(filename, 'r', encoding="utf-8") as csvfile:
			csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
			data = [data for data in csvreader]
			# data = [[bytes(s, "utf-8") for s in data] for data in csvreader]
	else:
		if debug: print("Fetching remote csv: %s"%url)
		response = requests.get(url)
		response.raise_for_status()
		data = response.content
		with open(filename, 'wb') as f:
			f.write(data)

	return data

def get_xml_cached(filename, url):
	if path.isfile(filename):
		if debug: print("Reading local xml: %s"%filename)
		with open(filename, 'r', encoding="utf-8") as xmlfile:
			data = xmlfile.read()
	else:
		if debug: print("Fetching remote xml: %s"%url)
		response = requests.get(url)
		response.raise_for_status()
		data = response.content
		with open(filename, 'wb') as f:
			f.write(data)

	return data

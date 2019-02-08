#!/usr/bin/env python3
""" Import from Wikipedia"""

from pyquery import PyQuery

from settings import data_path
from api_util import get_xml_cached

wiki_page = "https://en.wikipedia.org/wiki/ISO_3166-1"

def import_countries():
	src = get_xml_cached(data_path + "countries.html", wiki_page)
	#print(src)
	pq = PyQuery(src)
	table = pq("div.mw-parser-output table.wikitable.sortable")[1]
	rows = pq("tr", table)[1:]

	data = []
	for row in rows:
		a = [pq(e).text() for e in pq("td", row)]
		data.append({"name": a[0], "code": a[1]})

	return data

if __name__ == '__main__':
	import_countries()
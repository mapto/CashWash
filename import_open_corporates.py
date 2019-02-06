#!/usr/bin/env python3

from organisations import search_entities, search_statements
from organisations import searchable_entitites, searchable_statements
from organisations import get_all_simple_aliases
from organisations.api_open_corporates import missing_jurisdictions

if __name__ == '__main__':
	"""
	# search_entities("CRYSTALORD", jurisdiction="CY")
	
	#for domain in searchable_entitites:
	#	search_entities("CRYSTALORD", domain, jurisdiction="CY")
	
	#search_entities("Svetlana Mocan", "officers")
	#search_statements("Svetlana Mocan")
	essential = {\
		"CY": ["CRYSTALORD"],\
		"GB": [\
		"ALARO BUSINESS", "AUGELA SYSTEMS", "BONINVEST",\
		"CALDON HOLDINGS", "COVINGTON BUSINESS", "DRAYSCOTT", "FABERLEX",\
		"GRIDEN DEVELOPMENTS", "HILUX SERVICES",\
		"LCM ALLIANCE", "METASTAR INVEST", "MIRABAX INVESTMENTS",\
		"RIVERLANE", "RONIDA INVEST",\
		"SEABON", "STAMTRADE SERVICES",\
		"TOTTENHAM MANAGEMENT", "TREEGOLD DEVEPOMENT", "TENBY SERVICES",\
		"WESTBURN", "VALEMONT PROPERTIES"],\
		"NZ": ["CHESTER", "JETFIELD NETWORKS"]}
		#"RU": ["SEABON"]}

	for (jurisdiction, names) in essential.items():
		for name in names:
			print(name)
			for domain in searchable_entitites:
				search_entities(name, domain, jurisdiction=jurisdiction)
			for domain in searchable_statements:
				search_statements(name, domain, jurisdiction=jurisdiction)
	"""
	all = get_all_simple_aliases()
	for next in all:
		if next[1] not in missing_jurisdictions:
			search_entities(next[0], jurisdiction=next[1])

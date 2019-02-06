from .api_open_corporates import get_cached_companies, get_cached_results_count
from .persistence import get_all_aliases_by_one, update_org_name

#from .persistence import get_organisations

def optimise_aliases():
	counts = {}
	for next in get_cached_companies():
		parts = next.split(".")
		key = (parts[3], parts[2].upper()) # (name, jurisdiction), as defined in api_open_corporates._build_search_file
		current = get_cached_results_count(key[0], key[1])
		if current:
			counts[key] = current
	for key, count in counts.items():
		aliases = get_all_aliases_by_one(key[0], key[1])
		best = key
		best_org_id = None
		for next in aliases:
			if (next[0],next[1]) in counts and counts[(next[0],next[1])] < counts[best]:
				best = (next[0],next[1])
				best_org_id = next[3]
		if best_org_id:
			print("Setting name %s to organisation %d" %(best[0], best_org_id))
			update_org_name(best_org_id, best[0])

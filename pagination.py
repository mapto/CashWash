from sqlalchemy import func 

from db import session as s

def count_total(query):
	return query.count()

def get_page(query, page_num=0, page_size=25, order=None):
	""" 
	>>> order = {"col": 0, "dir": "asc"}
	>>> order = {"col": 5, "dir": "desc"}
	"""
	order_func = getattr(query.column_descriptions[order["col"]]["expr"], order["dir"]) if order else None
	offset = page_num * page_size
	result = query.order_by(order_func()).slice(offset, offset + page_size).all()
	return result

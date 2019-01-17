from sqlalchemy import func, column

from db import Session

def count_total(statement):
	s = Session()
	result = s.execute(statement).fetchall()
	s.close()
	return len(result)

def get_page(statement, page_num=0, page_size=25, order={"col": 0, "dir": "desc"}):
	s = Session()
	col = column(statement.columns.keys()[order["col"]])
	order_func = getattr(col, order["dir"]) if order else None
	offset = page_num * page_size
	pg_stmt = statement.order_by(order_func()).offset(offset).limit(offset + page_size)
	result = s.execute(pg_stmt)
	s.close()
	return result

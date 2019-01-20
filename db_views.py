"""sqlite syntax"""

from db import Session

drop_table_intermediary ="""
drop table if exists intermediary
"""

# in- and out-flows of intermediaries
create_table_intermediary ="""
CREATE TABLE intermediary(
  inflow INTEGER,
  outflow INTEGER,
  balance INTEGER,
  source VARCHAR,
  intermediary VARCHAR,
  destination VARCHAR
)
"""
# table
populate_table_intermediary = """
insert into intermediary 
select
	sum(tf.amount_usd) inflow,
	sum(tt.amount_usd) outflow,
	sum(tf.amount_usd) - sum(tt.amount_usd) balance,
	ts.code source,
	ti.code intermediary,
	td.code destination
from "transaction" tf
join "transaction" tt on tf.beneficiary_id=tt.payee_id
join account ts on ts.id=tf.payee_id
join account ti on ti.id=tt.payee_id AND ti.id IS NOT NULL AND ti.code IS NOT NULL
JOIN account td on td.id=tt.beneficiary_id
GROUP BY intermediary
"""
# view - legacy - structure needs to be updated in accordance to table version
'''
create_view_intermediary = """
create view intermediary as
select
	sum(tf.amount_usd) inflow,
	sum(tt.amount_usd) outflow,
	ts.code source,
	ti.code intermediary,
	td.code destination
from "transaction" tf
join "transaction" tt on tf.beneficiary_id=tt.payee_id
join account ts on ts.id=tf.payee_id
join account ti on ti.id=tt.payee_id
join account td on td.id=tt.beneficiary_id
group by intermediary
order by inflow desc, outflow desc;
"""
'''
# select * from intermediary;

# drop view if exists intermediary;
# drop table if exists intermediary;

def init_intermediary_table():
	s = Session()
	s.execute(drop_table_intermediary)
	s.execute(create_table_intermediary)
	s.execute(populate_table_intermediary)
	s.commit()
	s.close()

def init_derived():
	init_intermediary_table()

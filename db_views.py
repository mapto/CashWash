"""sqlite syntax"""

from db import Session

drop_table_intermediary ="""
drop table if exists intermediary
"""

# in- and out-flows of intermediaries
create_table_intermediary ="""
CREATE TABLE intermediary(
  inflow  INTEGER,
  outflow INTEGER,
  balance INTEGER,
  source_org       VARCHAR,
  source_acc       VARCHAR,
  intermediary_org VARCHAR,
  intermediary_acc VARCHAR,
  destination_org  VARCHAR,
  destination_acc  VARCHAR
)
"""
# table
populate_table_intermediary = """
insert into intermediary 
select
	sum(tf.amount_usd) inflow,
	sum(tt.amount_usd) outflow,
	sum(tf.amount_usd) - sum(tt.amount_usd) balance,
	tso.name source_org,       tsa.code source_acc,       
	tio.name intermediary_org, tia.code intermediary_acc,
	tdo.name destination_org,  tda.code destination_acc  
from "transaction" tf
JOIN "transaction" tt ON tf.beneficiary_id=tt.payee_id
JOIN account tsa      ON tsa.id=tf.payee_id
JOIN organisation tso ON tso.id=tsa.owner_id
JOIN account tia      ON tia.id=tt.payee_id AND tia.id IS NOT NULL AND tia.code IS NOT NULL AND NOT tia.code = ""
JOIN organisation tio ON tio.id=tia.owner_id
JOIN account tda      ON tda.id=tt.beneficiary_id
JOIN organisation tdo ON tdo.id=tda.owner_id
GROUP BY intermediary_org
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

if __name__ == '__main__':
	init_derived()
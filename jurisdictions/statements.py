"""Used by datatables.
Aims for generic SQL syntax"""

from sqlalchemy import text, column, select

def get_jurisdictions_statement():
	s = """
select 
	tjur.name, tjur.code,
	count(distinct tali.id) aliases,
	count(distinct torg.id) orgs,
	count(distinct tbank.id) banks,
	count(distinct tacc.id) accs
from jurisdiction tjur
left outer join alias tali on tali.country_id=tjur.id
left outer join organisation torg on torg.id=tali.org_id
left outer join bank tbank on tbank.country_id=tjur.id
left outer join account tacc on tacc.bank_id=tbank.id
where tjur.code is not null
group by tjur.id
	"""
	subquery = text(s).columns()

	return select([column("name"),column("code"),\
		column("aliases"), column("orgs"),\
		column("banks"), column("accs")])\
		.select_from(subquery)

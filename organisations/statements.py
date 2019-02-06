"""Used by datatables"""

from sqlalchemy import text, column, select, bindparam
from sqlalchemy import String

def get_accounts_statement(org_id):
	s = """
select
	ta.code code,
	tb.name bank
from account ta
join bank tb on tb.id=ta.bank_id
where ta.owner_id=%d and ta.code!=""
	"""
	subquery = text(s % org_id).columns()  # This Lets it be used as a subquery

	return select([column("code"),column("bank")]).select_from(subquery)

def get_aliases_statement(org_id):
	s = """
select
	ta.alias alias,
	tj.code country
from alias ta
left join jurisdiction tj on tj.id=ta.country_id
where ta.org_id=%d
	"""
	subquery = text(s % org_id).columns()  # This Lets it be used as a subquery

	return select([column("alias"),column("country")]).select_from(subquery)

def get_incoming_statement(org_id):
	s = """
select
	sum(ttrx.amount_usd) total,
	tsorg.name source
from organisation tdorg
join account tdacc on tdacc.owner_id=tdorg.id
join "transaction" ttrx on ttrx.beneficiary_id=tdacc.id
join account tsacc on tsacc.id=ttrx.payee_id
join organisation tsorg on tsorg.id=tsacc.owner_id
where tdorg.id=%d
group by tsorg.id
	"""
	subquery = text(s % org_id).columns()  # This Lets it be used as a subquery

	return select([column("total"),column("source")]).select_from(subquery)

def get_outgoing_statement(org_id):
	s = """
select
	sum(ttrx.amount_usd) total,
	tdorg.name destination
from organisation tdorg
join account tdacc on tdacc.owner_id=tdorg.id
join "transaction" ttrx on ttrx.beneficiary_id=tdacc.id
join account tsacc on tsacc.id=ttrx.payee_id
join organisation tsorg on tsorg.id=tsacc.owner_id
where tsorg.id=%d
group by tdorg.id
	"""
	subquery = text(s % org_id).columns()  # This Lets it be used as a subquery

	return select([column("total"),column("destination")]).select_from(subquery)

def get_all_aliases_by_one_statement(alias, jurisdiction):
	s = """
select 
	ta2.alias alias,
	tjur.code jurisdiction,
	tjur.id jurisdiction_id,
	ta2.org_id org_id
from alias ta1
join organisation torg on torg.id=ta1.org_id
join alias ta2 on ta2.org_id=torg.id
join jurisdiction tjur on tjur.id=ta2.country_id
where ta1.alias=:alias AND tjur.code=:jurisdiction
"""
	subquery = text(s).bindparams(bindparam('alias', alias, type_=String),\
								  bindparam('jurisdiction', jurisdiction, type_=String)).columns()
	return select([column("alias"),column("jurisdiction"),column("jurisdiction_id"),column("org_id")]).select_from(subquery)

def get_all_simple_aliases_statement():
	s = """
select 
	tali.alias alias,
	tjur.code code
from alias tali
join jurisdiction tjur on tjur.id=tali.country_id
where tali.alias not like '% %' and tali.country_id is not null
and tali.alias not like 'INN%'
	"""
	subquery = text(s).columns()
	return select([column("alias"),column("code")]).select_from(subquery)

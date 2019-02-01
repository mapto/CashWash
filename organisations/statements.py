"""Used by datatables"""

from sqlalchemy import text, column, select

def get_accounts_statement(org_id):
	s = """
select
	ta.code code,
	tb.name bank
from account ta
join bank tb on tb.id=ta.bank_id
where ta.owner_id=%d and ta.code!=""
	"""
	subquery = text(s % org_id).columns()  # This let's it be used as a subquery

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
	subquery = text(s % org_id).columns()  # This let's it be used as a subquery

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
	subquery = text(s % org_id).columns()  # This let's it be used as a subquery

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
	subquery = text(s % org_id).columns()  # This let's it be used as a subquery

	return select([column("total"),column("destination")]).select_from(subquery)

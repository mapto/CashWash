"""Used by datatables"""

from sqlalchemy import text, column, select
from sqlalchemy import DateTime

def get_transactions_statement():
	s = """
select
	amount_usd,
	tpo.name payee_org,
	tpa.code payee_acc,
	tbo.name beneficiary_org,
	tba.code beneficiary_acc,
	currency,
	tt.date_created date
from "transaction" tt
join account tpa on tpa.id=tt.payee_id
join account tba on tba.id=tt.beneficiary_id
join organisation tpo on tpo.id=tpa.owner_id
join organisation tbo on tbo.id=tba.owner_id
	"""
	subquery = text(s).columns()

	return select([column("amount_usd"),\
		column("payee_org"),column("payee_acc"),\
		column("beneficiary_org"),column("beneficiary_acc"),\
		column("currency"),column("date", type_=DateTime)]).select_from(subquery)

def get_intermediaries_statement():
	s = """
select
	inflow, outflow, balance,
	intermediary_org, intermediary_acc
from intermediary
	"""
	subquery = text(s).columns()

	return select([column("inflow"),column("outflow"),column("balance"),\
		column("intermediary_org"), column("intermediary_acc")])\
		.select_from(subquery)

def get_cashflows_statement():
	s = """
select
	inflow, outflow, balance,
	source_org, source_acc,
	intermediary_org, intermediary_acc,
	destination_org, destination_acc
from cashflow
	"""
	subquery = text(s).columns()

	return select([column("inflow"),column("outflow"),column("balance"),\
		column("source_org"), column("source_acc"),\
		column("intermediary_org"), column("intermediary_acc"),\
		column("destination_org"), column("destination_acc")])\
		.select_from(subquery)

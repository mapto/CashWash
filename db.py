#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, func 
from sqlalchemy import Integer, String, Boolean, DateTime

from settings import db_path
if __name__ == '__main__':
	debug = True
else:
	from settings import debug

Base = declarative_base()

engine = create_engine(db_path, echo=debug)

class Organisation(Base):
	__tablename__ = 'organisation'

	id = Column(Integer, primary_key=True)

	name = Column(String)
	name_norm = Column(String)
	# account = Column(String)
	# jurisdiction = Column(String)
	# bank_country = Column(String) # automatically extracted, TBV
	org_type = Column(String) # Company, Person, Invalid
	core = Column(Boolean)

	date_created = Column(DateTime, default=func.current_timestamp())


class Alias(Base):
	__tablename__ = 'alias'

	id = Column(Integer, primary_key=True)

	alias = Column(String, unique=True)

	org_id = Column(Integer, ForeignKey("organisation.id"))

	date_created = Column(DateTime, default=func.current_timestamp())


class Jurisdiction(Base):
	__tablename__ = 'jurisdiction'

	id = Column(Integer, primary_key=True)

	country = Column(String)

	org_id = Column(Integer, ForeignKey("organisation.id"))

	date_created = Column(DateTime, default=func.current_timestamp())


class Account(Base):
	__tablename__ = 'account'

	id = Column(Integer, primary_key=True)

	code = Column(String, unique=True)
	acc_type = Column(String) # IBAN, SWIFT, CASH, LOCAL # see service.account_type
	jurisdiction = Column(String)

	owner_id = Column(Integer, ForeignKey("organisation.id"))

	date_created = Column(DateTime, default=func.current_timestamp())


class AccountDetail(Base):
	__tablename__ = 'account_detail'

	id = Column(Integer, primary_key=True)

	code = Column(String, unique=True)
	code_local = Column(String)
	jurisdiction = Column(String)
	checksum = Column(String)
	bank_code = Column(String)
	account = Column(String)
	check_digit = Column(String)
	sepa = Column(Boolean)
	currency = Column(String)

	validity = Column(String) # contains "True" if valid, explanation otherwise

	account_id = Column(Integer, ForeignKey("account.id"))
	bank_id = Column(Integer, ForeignKey("bank.id"))

	date_created = Column(DateTime, default=func.current_timestamp())


class Bank(Base):

	__tablename__ = 'bank'

	id = Column(Integer, primary_key=True)

	code = Column(String, unique=True)
	name = Column(String)
	city = Column(String)
	branch = Column(String)
	address = Column(String)
	postcode = Column(String)
	jurisdiction = Column(String)

	validity = Column(String) # contains "True" if valid, explanation otherwise

	date_created = Column(DateTime, default=func.current_timestamp())


class Transaction(Base):
	__tablename__ = 'transaction'

	id = Column(Integer, primary_key=True)

	'''
	payer_name = Column(String)
	payer_name_norm = Column(String)
	payer_account = Column(String)
	payer_jurisdiction = Column(String)
	payer_bank_country = Column(String) # automatically extracted, TBV
	payer_type = Column(String)
	payer_core = Column(Boolean)
	'''

	amount_orig = Column(Integer)
	amount_usd = Column(Integer)
	amount_eur = Column(Integer)
	amount_orig_currency = Column(Integer)

	'''
	beneficiary_name = Column(String)
	beneficiary_name_norm = Column(String)
	beneficiary_account = Column(String)
	beneficiary_jurisdiction = Column(String)
	beneficiary_bank_country = Column(String)
	beneficiary_type = Column(String)
	beneficiary_core = Column(Boolean)
	'''

	investigation = Column(String)
	purpose = Column(String)
	date = Column(DateTime, default=func.current_timestamp())
	source_file = Column(String)

	from_account_id = Column(Integer, ForeignKey("account.id"))
	to_account_id = Column(Integer, ForeignKey("account.id"))

	date_created = Column(DateTime, default=func.current_timestamp())


Session = sessionmaker(bind=engine)

session = Session()

if __name__ == '__main__':
	print("Creating database at: %s" % db_path)
	Base.metadata.create_all(engine)
	
	#session = Session()
	#session.add_all([mecca, new_york, berlin, london, milano, brasilia])
	#session.commit()

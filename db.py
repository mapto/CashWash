#!/usr/bin/env python3

import os

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, func 
from sqlalchemy import Integer, String, Boolean, DateTime

from settings import db_url, db_path, dateformat_log

from settings import debug
# from settings import debug as settings_debug
# debug = __name__ == '__main__' or settings_debug

Base = declarative_base()

engine = create_engine(db_url, echo=debug)

class Alias(Base):
	__tablename__ = 'alias'

	id = Column(Integer, primary_key=True)

	alias = Column(String) # TODO: unique per country

	org_id = Column(Integer, ForeignKey("organisation.id"))
	country_id = Column(Integer, ForeignKey("jurisdiction.id"))

	date_created = Column(DateTime, default=func.current_timestamp())

	organisation = relationship("Organisation", back_populates="aliases")
	jurisdiction = relationship("Jurisdiction", back_populates="aliases")
	#jurisdiction = relationship("Jurisdiction")


class Organisation(Base):
	__tablename__ = 'organisation'

	id = Column(Integer, primary_key=True)

	name = Column(String) # preferred name
	# account = Column(String)
	# jurisdiction = Column(String)
	# bank_country = Column(String) # automatically extracted, TBV
	org_type = Column(String) # Company, Person, Invalid
	core = Column(Boolean)

	date_created = Column(DateTime, default=func.current_timestamp())

	accounts = relationship("Account", back_populates="organisation")
	aliases = relationship("Alias", back_populates="organisation")


class Jurisdiction(Base):
	__tablename__ = 'jurisdiction'

	id = Column(Integer, primary_key=True)

	country = Column(String)

	aliases = relationship("Alias", back_populates="jurisdiction")
	banks = relationship("Bank", back_populates="jurisdiction")


class Account(Base):
	__tablename__ = 'account'

	id = Column(Integer, primary_key=True)

	code = Column(String, unique=True)
	acc_type = Column(String) # IBAN, SWIFT, CASH, LOCAL # see service.account_type

	detail = Column(Integer, ForeignKey("account_detail.id"))
	owner_id = Column(Integer, ForeignKey("organisation.id"))
	bank_id = Column(Integer, ForeignKey("bank.id"))

	date_created = Column(DateTime, default=func.current_timestamp())

	bank = relationship("Bank", back_populates="accounts")
	organisation = relationship("Organisation", back_populates="accounts")
	detail = relationship("AccountDetail", back_populates="account")

	outgoing = relationship("Transaction", back_populates="payee", foreign_keys="Transaction.payee_id")
	incoming = relationship("Transaction", back_populates="beneficiary", foreign_keys="Transaction.beneficiary_id")


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

	account_id = Column(Integer, ForeignKey("account.id"), nullable=False)

	date_created = Column(DateTime, default=func.current_timestamp())

	account = relationship("Account", back_populates="detail")


class Bank(Base):

	__tablename__ = 'bank'

	id = Column(Integer, primary_key=True)

	code = Column(String, unique=True)
	name = Column(String)
	#city = Column(String)
	#branch = Column(String)
	#address = Column(String)
	#postcode = Column(String)

	country_id = Column(Integer, ForeignKey("jurisdiction.id"))

	date_created = Column(DateTime, default=func.current_timestamp())

	jurisdiction = relationship("Jurisdiction", back_populates="banks")
	accounts = relationship("Account", back_populates="bank")


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

	payee_id = Column(Integer, ForeignKey(Account.id))
	beneficiary_id = Column(Integer, ForeignKey(Account.id))

	date_created = Column(DateTime, default=func.current_timestamp())

	payee = relationship("Account", back_populates="outgoing", foreign_keys="Transaction.payee_id")
	beneficiary = relationship("Account", back_populates="incoming", foreign_keys="Transaction.beneficiary_id")


Session = sessionmaker(bind=engine)

session = Session()

if __name__ == '__main__':
	if os.path.exists(db_path):
		backup = "%s.%s.%s" % (db_path[:-3], datetime.now().strftime(dateformat_log), db_path[-2])
		print("Backup previous database at: %s" % backup)
		os.rename(db_path, backup)

	print("Creating database at: %s" % db_url)
	Base.metadata.create_all(engine)
	
	#session = Session()
	#session.add_all([mecca, new_york, berlin, london, milano, brasilia])
	#session.commit()

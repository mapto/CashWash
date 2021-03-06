#!/usr/bin/env python3

import os

from datetime import datetime
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy import Column, ForeignKey, UniqueConstraint, Index, func 
from sqlalchemy import Integer, String, Boolean, DateTime

from settings import db_url, db_path, dateformat_log

from settings import debug
# from settings import debug as settings_debug
# debug = __name__ == '__main__' or settings_debug
#debug = False

import util

Base = declarative_base()

engine = create_engine(db_url, echo=debug, poolclass=SingletonThreadPool)

class Alias(Base):
	__tablename__ = 'alias'

	id = Column(Integer, primary_key=True)

	alias = Column(String) # TODO: unique per country

	org_id = Column(Integer, ForeignKey("organisation.id"))
	country_id = Column(Integer, ForeignKey("jurisdiction.id"))

	date_created = Column(DateTime, default=func.current_timestamp())

	organisation = relationship("Organisation", back_populates="aliases")
	jurisdiction = relationship("Jurisdiction", back_populates="aliases")
	

	__table_args__ = (UniqueConstraint("alias", "country_id", "org_id"),)

	def json(self):
		return {"id": self.id, "alias": self.alias, "org": self.org_id,\
			"country": self.country_id}
			#"country": self.country_id, "date": self.date_created.date().isoformat()}
	
	def __repr__(self):
		return json.dumps(self.json())
	
Index("AliasIndex", "alias", "country_id", "org_id", unique=True)

class Organisation(Base):
	__tablename__ = 'organisation'

	id = Column(Integer, primary_key=True)

	name = Column(String) # preferred name
	# account = Column(String)
	# jurisdiction = Column(String)
	# bank_country = Column(String) # automatically extracted, TBV
	# org_type = Column(String) # Company, Person, Invalid
	core = Column(Boolean)
	fetched = Column(Boolean, default=False)
	
	date_created = Column(DateTime, default=func.current_timestamp())

	accounts = relationship("Account", back_populates="organisation")
	aliases = relationship("Alias", back_populates="organisation")

	def __repr__(self):
		return json.dumps(self.json())

	def json(self):
		return {"id": self.id, "name": self.name} #,\
		#return {"id": self.id, "name": self.name, "date": self.date_created.date().isoformat()} #,\
		#	"accounts": [a.code for a in self.accounts],\
		#	"aliases": [a.alias for a in self.aliases]}
		#return str({"name": self.name, "date": self.date_created.date().isoformat()})
		#return self.name


class Jurisdiction(Base):
	__tablename__ = 'jurisdiction'

	id = Column(Integer, primary_key=True)

	name = Column(String)
	code = Column(String, unique=True)

	aliases = relationship("Alias", back_populates="jurisdiction")
	banks = relationship("Bank", back_populates="jurisdiction")

	def __repr__(self):
		return json.dumps(self.json())

	def json(self):
		return {"id": self.id, "name": self.name, "code": self.code}


class Account(Base):
	__tablename__ = 'account'

	id = Column(Integer, primary_key=True)

	code = Column(String, unique=True)
	acc_type = Column(String) # IBAN, SWIFT, CASH, LOCAL # see service.account_type

	#detail = Column(Integer, ForeignKey("account_detail.id"))
	owner_id = Column(Integer, ForeignKey("organisation.id"))
	bank_id = Column(Integer, ForeignKey("bank.id"), nullable=False)

	fetched = Column(Boolean, default=False)
	date_created = Column(DateTime, default=func.current_timestamp())

	bank = relationship("Bank", back_populates="accounts")
	organisation = relationship("Organisation", back_populates="accounts")
	#detail = relationship("AccountDetail", back_populates="account")

	outgoing = relationship("Transaction", back_populates="payee", foreign_keys="Transaction.payee_id")
	incoming = relationship("Transaction", back_populates="beneficiary", foreign_keys="Transaction.beneficiary_id")

	def __repr__(self):
		return json.dumps(self.json())

	def json(self):
		return {"code": self.code, "organisation": self.owner_id, "bank": bank_id}
		#return {"code": self.code, "organisation": self.owner_id,\
		#	"date": self.date_created.date().isoformat()}

"""
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
"""

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

	fetched = Column(Boolean, default=False)
	date_created = Column(DateTime, default=func.current_timestamp())

	jurisdiction = relationship("Jurisdiction", back_populates="banks")
	accounts = relationship("Account", back_populates="bank")

	def __repr__(self):
		return json.dumps(self.json())

	def json(self):
		return {"id": self.id, "name": self.name, "code": self.code}


class Transaction(Base):
	__tablename__ = 'transaction'

	id = Column(Integer, primary_key=True)

	amount_orig = Column(Integer)
	amount_usd = Column(Integer)
	amount_eur = Column(Integer)
	currency = Column(String)

	investigation = Column(String)
	purpose = Column(String)
	date = Column(DateTime, default=func.current_timestamp())
	source_file = Column(String)

	payee_id = Column(Integer, ForeignKey(Account.id))
	beneficiary_id = Column(Integer, ForeignKey(Account.id))

	date_created = Column(DateTime, default=func.current_timestamp())

	payee = relationship("Account", back_populates="outgoing", foreign_keys="Transaction.payee_id")
	beneficiary = relationship("Account", back_populates="incoming", foreign_keys="Transaction.beneficiary_id")

	def __repr__(self):
		return json.dumps(self.json())
	
	def json(self):
		return {"amount_eur": util.format_amount(self.amount_eur), "amount_usd": util.format_amount(self.amount_usd),\
			"amount": util.format_amount(self.amount_orig), "currency": self.currency,\
			"date": self.date_created.date().isoformat(),\
			"payee": self.payee.code, "beneficiary": self.beneficiary.code}
	


Session = sessionmaker(bind=engine,autoflush=False)

session = Session()

def setup_db(backup = True):
	if backup and os.path.exists(db_path):
		backup = "%s.%s.%s" % (db_path[:-3], datetime.now().strftime(dateformat_log), db_path[-2:])
		print("Backup previous database at: %s" % backup)
		os.rename(db_path, backup)

	print("Creating database at: %s" % db_url)
	Base.metadata.create_all(engine)

if __name__ == '__main__':
	setup_db()	

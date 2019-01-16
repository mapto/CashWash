select count(id) from jurisdiction;
select count(id) from bank;
select count(id) from account;
select count(id) from organisation;
select count(id) from alias;

select * from jurisdiction;
select * from alias;
select * from bank;
select * from account;
select * from organisation;
select * from "transaction";


select *
from account a
join organisation o on a.owner_id=o.id;

select count(a.id) c, o.name, o.id
from account a
join organisation o on a.owner_id=o.id
group by o.name, o.id
order by c desc;

-- organisation
-- explore types
select count(id) c, o.org_type
from organisation o
group by o.org_type;

-- explore legal forms
select * from alias a
join jurisdiction j on a.country_id=j.id
order by j.country;

select * from organisation o
where o.org_type = "Invalid";

-- organisation names that are potentially SWIFT codes
select * from organisation o where LENGTH(o.name) == 11 or LENGTH(o.name) == 8
order by o.name;

-- account
-- accounts that are potentially SWIFT codes
select * from account a where LENGTH(a.code) == 11;


-- count account countries
select
	count(id) cc,
	cf, ct
from (
	select
	    tt.id id,
		substr(tp.code, 1, 2) cf,
		substr(tb.code, 1, 2) ct
	from "transaction" tt
	join account tp on tt.payee_id=tp.id
	join account tb on tt.beneficiary_id=tb.id
) tpre
group by ct, cf
order by cc desc;

-- accounts in a country

select *
from account ta
where substr(code, 1,2) = 'TR'
group by code;

-- show amounts transferred by country
select
	tb.id,
	tb.code,
	sum(tt.amount_usd) s,
	count(tt.id) c
from "transaction" tt
join account tb on tt.beneficiary_id=tb.id
where substr(tb.code, 1,2) = 'IT'
group by tb.code
order by s desc;

-- show account owner
select *
from account tacc
join organisation torg on tacc.owner_id=torg.id
join alias tal on tal.org_id=torg.id
where tacc.id=2060;

-- company with most aliase
select
	torg.id, torg.name,
	count(tal.id) c
from organisation torg
join alias tal on tal.org_id=torg.id
group by torg.id, torg.name
order by c desc;

select *
from account tacc
join organisation torg on tacc.owner_id=torg.id
join alias tal on tal.org_id=torg.id
where torg.id=3446
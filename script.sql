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


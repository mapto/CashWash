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

select *
from account a
join organisation o on a.owner_id=o.id;

select count(a.id) c, o.name, o.id
from account a
join organisation o on a.owner_id=o.id
group by o.name, o.id
order by c desc;

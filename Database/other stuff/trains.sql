create table stations
(
    id int auto_increment,
    station varchar(100) charset utf8 not null,
    constraint stations_id_uindex
    unique (id),
    constraint stations_station_uindex
    unique (station)
)
comment 'Table with stations';
alter table stations add primary key (id);

create table trains
(
id int auto_increment,
model varchar(100) charset utf8 not null,
constraint trains_id_uindex
unique (id),
constraint trains_model_uindex
unique (model)
)
comment 'Table with models of trains';
alter table trains
add primary key (id);
create table types
(
id int auto_increment,
type varchar(100) charset utf8 not null,
constraint types_id_uindex
unique (id),
constraint types_type_uindex
unique (type)
)
comment 'Table with types';
alter table types
add primary key (id);
create table schedule
(
id int auto_increment,
from_id int not null,
to_id int not null,
depature_time time not null,
arrival_time time not null,
type_id int not null,
train_id int not null,
constraint schedule_id_uindex
unique (id),
constraint schedule_stations_id_fk
foreign key (from_id) references stations (id),
constraint schedule_stations_id_fk_2
foreign key (to_id) references stations (id),
constraint schedule_trains_id_fk
foreign key (train_id) references trains (id),
constraint schedule_types_id_fk
foreign key (type_id) references types (id)
);
alter table schedule
add primary key (id);

create table users
(
    id int auto_increment,
    login varchar(100) charset utf8 not null,
    password varchar(100) charset utf8 not null,
    constraint users_id_uindex
    unique (id),
    constraint users_login_uindex
    unique (login)
)
comment 'Table with users information';
alter table users
add primary key (id);

create table favorites
(
    id int auto_increment,
    user_id int not null,
    from_id int not null,
    to_id int not null,
    constraint favorites_id_uindex
        unique (id),
    constraint favorites_stations_id_fk
        foreign key (from_id) references stations (id),
    constraint favorites_stations_id_fk_2
        foreign key (to_id) references stations (id),
    constraint favorites_users_id_fk
        foreign key (user_id) references users (id)
)
comment 'Table with users favorites stations';
alter table favorites
add primary key (id);


create
    definer = root@localhost view true_schedule as
    select `s`.`id` AS `id`,
        `st1`.`station` AS `station_from`,
        `st2`.`station` AS `station_to`,
        `s`.`depature_time` AS `depature_time`,
        `s`.`arrival_time` AS `arrival_time`,
`train_schedule`.`types`.`type` AS `type`,
`tr`.`model` AS `model`
from ((((`train_schedule`.`schedule` `s` left join `train_schedule`.`stations` `st1` on ((`st1`.`id` = `s`.`from_id`))) left join
`train_schedule`.`stations` `st2` on ((`st2`.`id` = `s`.`to_id`))) left join `train_schedule`.`types` on
((`train_schedule`.`types`.`id` = `s`.`type_id`)))
left join `train_schedule`.`trains` `tr` on ((`tr`.`id` = `s`.`train_id`)))
order by `s`.`depature_time`;
create
definer = root@localhost procedure get_favorites(IN in_id int) comment 'Get full schedule'
begin
select s.id,
st1.station as station_from,
st2.station as station_to,
s.depature_time,
s.arrival_time,
types.type,
tr.model
from train_schedule.schedule s
left join train_schedule.stations st1 on (st1.id = s.from_id)
left join train_schedule.stations st2 on (st2.id = s.to_id)
left join train_schedule.types types on (types.id = s.type_id)
left join train_schedule.trains tr on (tr.id = s.train_id),
(select f.from_id as fid, f.to_id as tid from train_schedule.favorites f where f.user_id = in_id) as f
where s.from_id = f.fid
and s.to_id = f.tid
order by depature_time;
end;
create
definer = root@localhost procedure get_record(IN in_id int) comment 'Get record from schedule'
begin
select *, t.departure_time as depature_time, t.id
from true_schedule t
where t.id = in_id;
end;
create
definer = root@localhost procedure get_schedule() comment 'Get full schedule'
begin
select *, t.departure_time as depature_time from true_schedule t;
end;
create
definer = root@localhost procedure get_user(IN in_login varchar(100), IN in_password varchar(100))
comment 'Get user from users'
begin
if exists(select *
from train_schedule.users u
where u.login = in_login
and u.password = in_password) then
select *
from train_schedule.users u
where u.login = in_login
and u.password = in_password;
else
begin
if exists(select *
from train_schedule.users u
where u.login = in_login) then
select 0;
else
select 1;
end if;
end;
end if;
end;
create
definer = root@localhost procedure new_favorite(IN in_user_id int, IN in_from varchar(100), IN in_to varchar(100))
comment 'Get user from users'
begin
if exists(select s.id as from_idd
from train_schedule.stations s
where s.station = in_from) and
exists(select s.id as to_id
from train_schedule.stations s
where s.station = in_to)
then
begin
insert ignore favorites(user_id, from_id, to_id)
select in_user_id, s1.id, s2.id as f_id
from train_schedule.stations s1,
train_schedule.stations s2
where s1.station = in_from
and s2.station = in_to;
select 1 as done;
end;
else
if not exists(select s.id as from_idd
from train_schedule.stations s
where s.station = in_from) and
not exists(select s.id as to_id
from train_schedule.stations s
where s.station = in_to) then
begin
select 0 as from_exists, 0 as to_exists;
end;
else
if not exists(select s.id as from_idd
from train_schedule.stations s
where s.station = in_from) then
begin
select 0 as from_exists;
end;
else
select 0 as to_exists;
end if;
end if;
end if;
end;
create
definer = root@localhost procedure new_user(IN in_login varchar(100), IN in_password varchar(100))
comment 'Get user from users'
begin
if not exists(select *
from train_schedule.users u
where u.login = in_login)
then
begin
insert users(login, password) values (in_login, in_password);
select *
from train_schedule.users u
where u.login = in_login
and u.password = in_password;
end;
else
select 1 as alredy_exist;
end if;
end;


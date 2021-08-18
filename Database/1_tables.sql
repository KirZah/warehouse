drop database if exists warehouse;
create database if not exists warehouse;
# create database warehouse;
USE warehouse;

drop table IF EXISTS suppliers;
create table IF NOT EXISTS suppliers
(
    id      int auto_increment unique,
    name    varchar(50)  not null unique,
    address varchar(127) null,
    phone   varchar(20)  not null unique,
    email   varchar(64)  not null unique,
    note    varchar(255) null,
    PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARSET=utf8;

drop table IF EXISTS supplies;
create table IF NOT EXISTS supplies
(
    id              int auto_increment unique,
    suppliers_id    int             not null,
    date            date            not null,
    delivery_note   varchar(10)     not null unique,
    note            varchar(255)    null,
    PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARSET=utf8;

drop table IF EXISTS catalog;
create table IF NOT EXISTS catalog
(
    id              int auto_increment unique,
    product_name    varchar(50)     not null unique,
    price           DECIMAL(19,4)   not null,
    shelf_life      integer         null,
    description     varchar(255)    null,
    PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARSET=utf8;

drop table IF EXISTS goods;
create table IF NOT EXISTS goods
(
    id              int auto_increment unique,
    catalog_id      int             not null,
    state_id        tinyint         not null, # 1 - in stock, 2 - sold, 3 - lost
    production_date date            not null,
    note            varchar(255)    null,
    PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARSET=utf8;

drop table IF EXISTS goods_supplies;
create table IF NOT EXISTS goods_supplies
(
    goods_id    int not null unique,
    supplies_id int not null,
    PRIMARY KEY (goods_id)
) ENGINE=InnoDB CHARSET=utf8;


drop table IF EXISTS storage;
create table IF NOT EXISTS storage
(
    goods_id    int         not null unique,
    shelf       varchar(11) not null, # AA99AZ07 - CC-NN-CC-NN
    PRIMARY KEY (goods_id)
) ENGINE=InnoDB CHARSET=utf8;


drop table IF EXISTS customers;
create table IF NOT EXISTS customers
(
    id      int auto_increment unique,
    name    varchar(50)  not null,
    address varchar(127) not null,
    phone   varchar(20)  not null unique,
    email   varchar(64)  null unique,
    note    varchar(255) null,
    PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARSET=utf8;

drop table IF EXISTS goods_shipments;
create table IF NOT EXISTS goods_shipments
(
    goods_id     int not null unique,
    shipments_id int not null,
    PRIMARY KEY (goods_id)
) ENGINE=InnoDB CHARSET=utf8;

drop table IF EXISTS shipments;
create table IF NOT EXISTS shipments
(
    id              int auto_increment unique,
    customers_id    int             not null,
    date            date            not null,
    note            varchar(255)    null,
    delivery_note   varchar(10)     not null unique,
    PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARSET=utf8;


alter table goods
	add constraint goods_catalog_id_fk
		foreign key (catalog_id) references catalog (id);
# alter table goods
# 	add constraint goods_goods_supplies_id_fk
# 		foreign key (id) references goods_supplies (goods_id);

alter table supplies
	add constraint supplies_suppliers_id_fk
		foreign key (suppliers_id) references suppliers (id);

alter table goods_supplies
	add constraint goods_supplies_supplies_id_fk
	    foreign key (supplies_id) references supplies (id);
alter table goods_supplies
	add constraint goods_supplies_goods_id_fk
	    foreign key (goods_id) references goods (id) ON UPDATE CASCADE ON DELETE CASCADE;

alter table storage
	add constraint storage_goods_id_fk
	    foreign key (goods_id) references goods (id) ON UPDATE CASCADE ON DELETE CASCADE;

alter table goods_shipments
	add constraint goods_shipments_goods_id_fk
	    foreign key (goods_id) references goods (id) ON UPDATE CASCADE ON DELETE CASCADE,
# alter table goods_shipments
	add constraint goods_shipments_shipments_id_fk
		foreign key (shipments_id) references shipments (id);

alter table shipments
	add constraint shipments_customers_id_fk
		foreign key (customers_id) references customers (id);



drop table IF EXISTS package_states;
create table IF NOT EXISTS package_states
(
    id              tinyint auto_increment unique,
    state           VARCHAR(50),
    PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARSET=utf8;


alter table goods
	add constraint goods_state_id_fk
		foreign key (state_id) references package_states (id);


drop view if exists goods_view;
create view goods_view(id, product_name, price, state, production_date, expiration_date, description, note) as
    SELECT g.id, c.product_name, c.price, p.state, g.production_date,
          IF(ISNULL(c.shelf_life), NULL, DATE_ADD(g.production_date, INTERVAL c.shelf_life DAY)) as expiration_date,
          c.description, g.note FROM goods g
    Left join catalog c         ON g.catalog_id = c.id
    Left join package_states p  ON g.state_id   = p.id
    order by g.id desc;


insert into package_states(id, state) values (1, 'in stock');
insert into package_states(id, state) values (2, 'sold');
insert into package_states(id, state) values (3, 'lost');

# select * from goods_view;

# drop table IF EXISTS users;
# create table IF NOT EXISTS users
# (
#     id          int     not null auto_increment unique,
#     username    varchar(50) not null unique,
#     #password    varchar(50) charset utf8 not null,
#     roles_id    tinyint not null,
# #     constraint users_id_uindex
# #         unique (id),
# #     constraint users_login_uindex
# #         unique (login),
#     PRIMARY KEY (id)
# )
# comment 'Table with users information (roles)';
#
# drop table IF EXISTS roles;
# create table IF NOT EXISTS roles
# (
#     id          tinyint     not null auto_increment unique,
#     role        varchar(50) charset utf8 not null,
#     PRIMARY KEY (id)
# )
# comment 'Table with users information (roles)';
#
# alter table users
# 	add constraint users_roles_id_fk
# 		foreign key (roles_id) references roles (id);




#######################
# сделать триггер: при добавлении пользователя в warehouse.users добавлять его в mysql.user
#  upd: useless
# при добавлении товара в отправку изменять его state
#######################


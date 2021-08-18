use warehouse;
# SHOW GRANTS FOR 'Chyvak88'@'%';
# login with root
# SHOW GRANTS FOR 'root'@'localhost';
GRANT ALL PRIVILEGES ON *.* TO 'Chyvak88'@'%';  # PC (needed)
# GRANT ALL PRIVILEGES ON *.* TO 'Chyvak88'@'localhost';

CREATE ROLE if not exists  'developer';
GRANT ALL PRIVILEGES ON *.* TO 'developer'@'%';
# GRANT REPLICATION SLAVE ON *.* TO 'developer';  # PC (needed)

GRANT 'developer' TO 'Chyvak88'@'%';
# GRANT 'developer' TO 'Chyvak88'@'localhost';

SET DEFAULT ROLE 'developer' TO 'Chyvak88'@'%';
# SET DEFAULT ROLE 'developer' TO 'Chyvak88'@'localhost';
# login with Chyvak88
# SHOW GRANTS FOR 'Chyvak88'@'%' USING 'developer';


#################### CREATING FUNCTIONAL ROLES ####################
use warehouse;
# # dropping roles
# DROP   ROLE if      exists  'mysql_select';
# DROP   ROLE if      exists  'warehouse_update';
# creating roles

# CREATE ROLE if not  exists  'warehouse_update';
# granting table roles
# GRANT EXECUTE ON warehouse.* TO 'mysql_select'@'%';  # may add: SYSTEM_USER, ROLE_ADMIN
# GRANT UPDATE, SELECT ON warehouse.* TO 'warehouse_update'@'%';
# granting routine roles

# GRANT EXECUTE ON PROCEDURE warehouse.change_is_sold TO 'warehouse_update'@'%';


CREATE ROLE if not exists 'mysql_select';
GRANT SELECT ON mysql.user          TO 'mysql_select';
GRANT SELECT ON mysql.role_edges    TO 'mysql_select';
GRANT EXECUTE ON FUNCTION warehouse.get_user_role   TO 'mysql_select';

CREATE ROLE if not exists  'archive';
# archive
GRANT CREATE TEMPORARY TABLES, SELECT ON warehouse.* TO 'archive';
GRANT LOCK TABLES ON warehouse.*                     TO 'archive';
GRANT FILE, SYSTEM_VARIABLES_ADMIN ON *.*            TO 'archive';
GRANT EXECUTE ON PROCEDURE warehouse.archive                 TO 'archive';
GRANT EXECUTE ON PROCEDURE warehouse.create_temporary_tables TO 'archive';
GRANT EXECUTE ON PROCEDURE warehouse.drop_temporary_tables   TO 'archive';
GRANT EXECUTE ON PROCEDURE warehouse.truncate_tables         TO 'archive';
GRANT EXECUTE ON PROCEDURE warehouse.archive_from_tmp_tables TO 'archive';
# load_archive
GRANT CREATE TEMPORARY TABLES, SELECT, DROP ON warehouse.* TO 'archive';
GRANT EXECUTE ON PROCEDURE warehouse.copy_tables_from_tmp_to_warehouse TO 'archive';

# CREATE ROLE if not exists  'load_archive';
# # GRANT USAGE ON warehouse.* TO 'archive';
# GRANT CREATE TEMPORARY TABLES, SELECT ON warehouse.* TO 'load_archive';
# GRANT LOCK TABLES ON warehouse.* TO 'load_archive';
# GRANT FILE, SYSTEM_VARIABLES_ADMIN ON *.* TO 'load_archive';
# # GRANT EXECUTE ON PROCEDURE warehouse.archive TO 'archive';
# GRANT EXECUTE ON PROCEDURE warehouse.create_temporary_tables TO 'archive';
# GRANT EXECUTE ON PROCEDURE warehouse.drop_temporary_tables TO 'archive';
# GRANT EXECUTE ON PROCEDURE warehouse.truncate_tables TO 'archive';

# select *
# from mysql.user;

#################### CREATING WAREHOUSE ROLES #####################

# # dropping roles
# DROP   ROLE if      exists  'administrator';
# DROP   ROLE if      exists  'director';
# DROP   ROLE if      exists  'boss';
# DROP   ROLE if      exists  'pc_operator';
# DROP   ROLE if      exists  'warehouseman';
# DROP   ROLE if      exists  'salesman';
# # DROP   ROLE if      exists  'customer';
# creating roles
CREATE ROLE if not exists  'developer';
CREATE ROLE if not  exists  'administrator';
CREATE ROLE if not  exists  'director';
CREATE ROLE if not  exists  'boss';
CREATE ROLE if not  exists  'pc_operator';
CREATE ROLE if not  exists  'warehouseman';
CREATE ROLE if not  exists  'salesman';
# CREATE ROLE if not  exists  'customer';
# granting roles
GRANT ALL PRIVILEGES ON *.* TO 'developer'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'administrator'@'%';
GRANT 'archive' TO 'director'@'%';
GRANT SELECT, INSERT, DELETE, UPDATE ON warehouse.* TO 'director'@'%';
GRANT SELECT, INSERT, DELETE, UPDATE ON warehouse.* TO 'boss'@'%';

GRANT SELECT, INSERT ON warehouse.suppliers         TO 'pc_operator'@'%';
GRANT SELECT, INSERT ON warehouse.supplies          TO 'pc_operator'@'%';
GRANT SELECT, INSERT ON warehouse.goods_supplies    TO 'pc_operator'@'%';
GRANT SELECT, INSERT ON warehouse.goods             TO 'pc_operator'@'%';
GRANT SELECT, INSERT ON warehouse.catalog           TO 'pc_operator'@'%';
GRANT SELECT         ON warehouse.storage           TO 'pc_operator'@'%';
GRANT SELECT, INSERT ON warehouse.goods_shipments   TO 'pc_operator'@'%';
GRANT SELECT, INSERT ON warehouse.shipments         TO 'pc_operator'@'%';
GRANT SELECT, INSERT ON warehouse.customers         TO 'pc_operator'@'%';
GRANT SELECT, INSERT ON warehouse.goods_view        TO 'pc_operator'@'%';
GRANT SELECT         ON warehouse.package_states    TO 'pc_operator'@'%';

GRANT SELECT, INSERT, UPDATE ON warehouse.storage   TO 'warehouseman'@'%';
GRANT SELECT                 ON warehouse.goods     TO 'warehouseman'@'%';
GRANT SELECT                 ON warehouse.goods_view TO 'warehouseman'@'%';
GRANT SELECT                ON warehouse.package_states TO 'warehouseman'@'%';

GRANT SELECT                 ON warehouse.catalog   TO 'warehouseman'@'%';
GRANT SELECT, INSERT, UPDATE ON warehouse.customers TO 'salesman'@'%';
GRANT SELECT                 ON warehouse.goods     TO 'salesman'@'%';
GRANT SELECT                 ON warehouse.catalog   TO 'salesman'@'%';
GRANT SELECT                 ON warehouse.goods_view TO 'salesman'@'%';
GRANT SELECT                ON warehouse.package_states TO 'salesman'@'%';
# GRANT SELECT ON warehouse.catalog TO 'customer'@'%';
# GRANT SELECT ON warehouse.catalog TO 'customer'@'%';
# FLUSH PRIVILEGES;

# WHO CAN UPDATE AND DELETE INFORMATION
GRANT EXECUTE ON PROCEDURE warehouse.return_sold_package    TO 'developer'@'%', 'administrator'@'%', 'director'@'%', 'boss'@'%';

# WHO CAN ADD INFORMATION
GRANT EXECUTE ON PROCEDURE warehouse.sell_package   TO 'developer'@'%', 'administrator'@'%', 'director'@'%', 'boss'@'%', 'pc_operator'@'%';
GRANT EXECUTE ON PROCEDURE warehouse.add_goods      TO 'developer'@'%', 'administrator'@'%', 'director'@'%', 'boss'@'%', 'pc_operator'@'%';

# EVERYONE
GRANT EXECUTE ON FUNCTION warehouse.get_user_role TO 'developer'@'%', 'administrator'@'%', 'director'@'%', 'boss'@'%',
    'pc_operator'@'%', 'warehouseman'@'%', 'salesman'@'%';
# ^^^^^^^^^^^^^^^^^ CREATING ROLES ^^^^^^^^^^^^^^^^^^
# select * from mysql.User;
# SELECT * from mysql.role_edges;
# select * from information_schema.USER_PRIVILEGES;

################ CREATING FUNCTIONAL USERS ###############

# CREATE USER if not exists  'mysql_select_user'; # пришлось создать user
# GRANT 'mysql_select' TO 'mysql_select_user';
# set default role 'mysql_select' TO 'mysql_select_user';
#
# CREATE USER if not exists  'archive_user'; # пришлось создать user
# GRANT 'archive' TO 'archive_user';
# set default role 'archive' TO 'archive_user';

# show processlist;

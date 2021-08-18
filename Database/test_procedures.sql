############################################### ADD USER ###############################################################

####### CREATE AND DELETE ############
# create user
use warehouse;
SET @username := 'director',
    @host := 'localhost',
    @password := 'director',
    @role := 'director';
SET @username_and_hostname := CONCAT((@username), '@', (@host));
CALL add_user(@username, @host, @password, @role);
# showing user in mysql.user
select * From mysql.user WHERE User.User = @username AND User.Host = @host;
#^^^^^^^^^^^^
# delete user
SET @`sql` := CONCAT('DROP USER \'', @username, '\'@\'', @host, '\';');
select @sql; # reminding that he's now deleted
PREPARE stmt FROM @`sql`;
EXECUTE stmt;
DEALLOCATE PREPARE `stmt`;
#^^^^^^^^^^^^
#^^^^^^ CREATE AND DELETE ^^^^^^^^^^^^
CALL add_user(@username, @host, @password, @role);
drop user administrator2@'localhost';
drop user boss1@'%';
drop user pc_operator1@'%';
drop user salesman9@'localhost';
drop user archive_user@'localhost';
drop user 'boss'@'%';
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^





############################################### GET USER ROLE ##########################################################

SET @username := 'root',
    @host := 'localhost';
SELECT get_user_role(@username, @host );
(select * From mysql.role_edges where TO_USER = @username AND TO_HOST = @host);
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^





############################################### Change_state_to_sold ###################################################
CALL change_state_to_sold(1);
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^





############################################### ARCHIVE TABLES #########################################################
select * from information_schema.user_privileges where PRIVILEGE_TYPE='USAGE';

# SELECT sql_grants FROM common_schema.sql_show_grants WHERE user='app';
select * from information_schema.user_privileges where GRANTEE = (select current_user()); #'\'boss\'@\'localhost\'';
select CURRENT_USER();
call archive_table('goods', '/archive/goods.table');

use warehouse;
SET GLOBAL local_infile=1; # need to be done on server and on client side
                           # (in python mysql.connector variable local_infile=1 by default) - THE BIGGEST LIE IN MY LIFE!
# SET GLOBAL ENABLED_LOCAL_INFILE=1; # no
# SET GLOBAL loose_local_infile=1; # no
# CREATE USER 'replicate'@'localhost' IDENTIFIED BY 'replicate_password' REQUIRE SSL;
# GRANT REPLICATION SLAVE, BACKUP_ADMIN, CLONE_ADMIN ON *.* TO 'replicate'@'localhost'; # with root (REPLICATION SLAVE)

SHOW VARIABLES LIKE "secure_file_priv";
SHOW VARIABLES;

SHOW VARIABLES LIKE "local_infile";

# int i = 0;
# mysql_options(&mysql,MYSQL_OPT_LOCAL_INFILE,&i);
# mysql_options(&mysql,MYSQL_OPT_LOAD_DATA_LOCAL_DIR,"/my/local/data");


call archive(1);
call drop_temporary_tables();

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^





############################################### BACKUP TABLES ##########################################################
# ONLY POSSIBLE FROM A CLIENT (or write here load from file FROM each table (that's not very comfy, so better check it from client :( ))
# call backup_database(1);

DELIMITER //
drop procedure if exists check_table_exists//
CREATE PROCEDURE check_table_exists(table_name VARCHAR(100))
BEGIN
    DECLARE CONTINUE HANDLER FOR SQLSTATE '42S02' SET @err = 1;
    SET @err = 0;
    SET @table_name = table_name;
    SET @sql_query = CONCAT('SELECT 1 FROM ',@table_name);
    PREPARE stmt1 FROM @sql_query;
    IF (@err = 1) THEN
        SET @table_exists = 0;
    ELSE
        SET @table_exists = 1;
        DEALLOCATE PREPARE stmt1;
    END IF;
END //
DELIMITER ;

##############
# проверить не запущена ли архивация или другой load from file процесс
call create_temporary_tables();
##########
call check_table_exists('tmp_suppliers');
select @table_exists;
call drop_temporary_tables();
##########
# load_files_to_tmp_tables: begin
call load_file_to_tmp_table(3, 'suppliers');
call load_file_to_tmp_table(archive_number, 'supplies');
call load_file_to_tmp_table(archive_number, 'goods_supplies');
call load_file_to_tmp_table(archive_number, 'catalog');
call load_file_to_tmp_table(archive_number, 'goods');
call load_file_to_tmp_table(archive_number, 'storage');
call load_file_to_tmp_table(archive_number, 'goods_shipments');
call load_file_to_tmp_table(archive_number, 'shipments');
call load_file_to_tmp_table(archive_number, 'customers');
# end;
# <--- check if correct should be here
call truncate_tables();
# lock tables here
call copy_tables_from_tmp_to_warehouse();
# unlock tables here
call drop_temporary_tables();
###############
select * from goods_supplies;

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

##################
call add_goods(10, 1, '1111-1-1', '{note}');





############################################### SELL PACKAGE ###########################################################

call sell_package(685, 1);

select * from goods;
delete from warehouse.goods_shipments where goods_id = 2;
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



############################################### RETURN SOLD PACKAGE ####################################################

call return_sold_package(685);

select * from goods;

delete from warehouse.goods_shipments where goods_id = 3;
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^






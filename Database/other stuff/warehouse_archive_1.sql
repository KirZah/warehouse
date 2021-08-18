# загрузка из файла
# LOAD DATA INFILE ASE warehouse;
# D
# # TO DISK = '\\BAK01\backup\MyVLDB.bak'
# # WITH CHECKSUM, INIT;
# LOAD DATA;

INSTALL PLUGIN clone SONAME 'mysql_clone.dll';

SELECT PLUGIN_NAME, PLUGIN_STATUS
       FROM INFORMATION_SCHEMA.PLUGINS
       WHERE PLUGIN_NAME = 'clone';
#

# CLONE clone_action
#
# clone_action: {
#     LOCAL DATA DIRECTORY [=] 'clone_dir';
#   | INSTANCE FROM 'user'@'host':port
#     IDENTIFIED BY 'password'
#     [DATA DIRECTORY [=] 'clone_dir']
#     [REQUIRE [NO] SSL]
# }

CREATE USER 'replicate'@'localhost' IDENTIFIED BY 'replicate_password' REQUIRE SSL;
GRANT REPLICATION SLAVE, BACKUP_ADMIN, CLONE_ADMIN ON *.* TO 'replicate'@'localhost'; # with root (REPLICATION SLAVE)

set GLOBAL clone_valid_donor_list='localhost:3306';
SHOW VARIABLES LIKE 'clone_valid_donor_list';


# clones to any server
CLONE
#     LOCAL DATA DIRECTORY = 'clone_dir';
    INSTANCE FROM 'replicate'@'localhost':3306
    IDENTIFIED BY 'replicate_password'
    DATA DIRECTORY = 'D:/Kirill/Google Disk/_Programming_Projects/Warehouse Database (course work)/course_work/backup_databases/backup_warehouse4.db';
#     [REQUIRE [NO] SSL]

# clones to server's directory where mysql is running
# CLONE LOCAL DATA DIRECTORY = 'D:/Kirill/Google Disk/_Programming_Projects/Warehouse Database (course work)/course_work/backup_databases/backup_warehouse2.db';

# use mysql; use information_schema; use performance_schema; use sys;
SELECT BINLOG_FILE, BINLOG_POSITION FROM performance_schema.clone_status;
SELECT @@GLOBAL.GTID_EXECUTED;
SELECT * FROM performance_schema.clone_status;

# CHANGE MASTER TO MASTER_HOST = 'source_host_name', MASTER_PORT = source_port_num,
# #        ...
#        MASTER_AUTO_POSITION = 1,
#        FOR CHANNEL 'setup_channel';
#
# GRANT BACKUP_ADMIN ON *.* TO rpl_user@'%';
# RESET SLAVE FOR CHANNEL group_replication_recovery;


##################################################################################################
# plan

# install plugin
# create clone_user
# grant "BACKUP_ADMIN ON *.*", "SELECT ON performance_schema.*", "EXECUTE ON *.*", "CLONE_ADMIN ON *.*" TO clone_user
# SET GLOBAL clone_valid_donor_list = "localhost:3306";
# CLONE INSTANCE (and wait...)

# try 2
INSTALL PLUGIN CLONE SONAME "mysql_clone.dll"; # "mysql_clone.so" for linux
CREATE USER clone_user IDENTIFIED BY "clone_password";
GRANT BACKUP_ADMIN ON *.* to clone_user;
GRANT SELECT ON performance_schema.* TO clone_user; # root
GRANT EXECUTE ON *.* to clone_user;

# INSTALL PLUGIN CLONE SONAME "mysql_clone.so";
SET GLOBAL clone_valid_donor_list = "localhost:3306";
# CREATE USER clone_user IDENTIFIED BY "clone_password";
GRANT CLONE_ADMIN ON *.* to clone_user;

# GRANT SELECT ON performance_schema.* TO clone_user;
# GRANT EXECUTE ON *.* to clone_user;

CLONE INSTANCE
    FROM clone_user@localhost:3306
    IDENTIFIED BY "clone_password";

select STATE, CAST(BEGIN_TIME AS DATETIME) as "START TIME",
CASE WHEN END_TIME IS NULL THEN
LPAD(sys.format_time(POWER(10,12) * (UNIX_TIMESTAMP(now()) - UNIX_TIMESTAMP(BEGIN_TIME))), 10, ' ')
ELSE
LPAD(sys.format_time(POWER(10,12) * (UNIX_TIMESTAMP(END_TIME) - UNIX_TIMESTAMP(BEGIN_TIME))), 10, ' ')
END as DURATION
from performance_schema.clone_status;

select STAGE, STATE, CAST(BEGIN_TIME AS TIME) as "START TIME",
  CASE WHEN END_TIME IS NULL THEN
  LPAD(sys.format_time(POWER(10,12) * (UNIX_TIMESTAMP(now()) - UNIX_TIMESTAMP(BEGIN_TIME))), 10, ' ')
  ELSE
  LPAD(sys.format_time(POWER(10,12) * (UNIX_TIMESTAMP(END_TIME) - UNIX_TIMESTAMP(BEGIN_TIME))), 10, ' ')
  END as DURATION,
  LPAD(CONCAT(FORMAT(ROUND(ESTIMATE/1024/1024,0), 0), " MB"), 16, ' ') as "Estimate",
  CASE WHEN BEGIN_TIME IS NULL THEN LPAD('0%', 7, ' ')
  WHEN ESTIMATE > 0 THEN
  LPAD(CONCAT(CAST(ROUND(DATA*100/ESTIMATE, 0) AS BINARY), "%"), 7, ' ')
  WHEN END_TIME IS NULL THEN LPAD('0%', 7, ' ')
  ELSE LPAD('100%', 7, ' ') END as "Done(%)"
  from performance_schema.clone_progress;

# verify that clone completed successfully.
select STATE, ERROR_NO, BINLOG_FILE, BINLOG_POSITION, GTID_EXECUTED,
CAST(BEGIN_TIME AS DATETIME) as "START TIME",
CAST(END_TIME AS DATETIME) as "FINISH TIME",
sys.format_time(POWER(10,12) * (UNIX_TIMESTAMP(END_TIME) - UNIX_TIMESTAMP(BEGIN_TIME)))
as DURATION
from performance_schema.clone_status; #\G

# Clone has completed successfully and took about ... minutes to complete.
# Verify that all stages completed successfully and the time taken in individual stages.
select STAGE, STATE, CAST(BEGIN_TIME AS DATETIME) as "START TIME",
CAST(END_TIME AS DATETIME) as "FINISH TIME",
LPAD(sys.format_time(POWER(10,12) * (UNIX_TIMESTAMP(END_TIME) - UNIX_TIMESTAMP(BEGIN_TIME))), 10, ' ')
as DURATION
from performance_schema.clone_progress;

select STAGE, STATE, CAST(BEGIN_TIME AS TIME) as "START TIME",
  CAST(END_TIME AS TIME) as "FINISH TIME",
  LPAD(sys.format_time(POWER(10,12) * (UNIX_TIMESTAMP(END_TIME) - UNIX_TIMESTAMP(BEGIN_TIME))), 10, ' ')
  as DURATION
  from performance_schema.clone_progress;

###################################################
# try 3
SHOW VARIABLES LIKE "secure_file_priv";
# SHOW VARIABLES;

# saving data
CREATE TEMPORARY TABLE tmp_goods(
    id              int auto_increment unique,
    catalog_id      int             not null,
    is_sold         tinyint(1)      not null,
    production_date date            not null,
    note            varchar(255)    null,
    PRIMARY KEY (id)
);

LOCK TABLES warehouse.goods WRITE;
INSERT INTO tmp_goods
    SELECT * FROM warehouse.goods;
UNLOCK TABLES;
# SELECT * FROM tmp_goods;

SELECT * INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/backup warehouse/goods.table'
  FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
  LINES TERMINATED BY '\n'
  FROM tmp_goods;

DROP TEMPORARY TABLE tmp_goods;



# SELECT * FROM warehouse.goods INTO tmp_goods FOR UPDATE; # a trailing locking clause.
# # или так
# SELECT * FROM t1 FOR UPDATE INTO @myvar;

# loading saved data

SET GLOBAL local_infile=1; # need to be done
SET GLOBAL ENABLED_LOCAL_INFILE=1; # no
SET GLOBAL loose_local_infile=1; # no

delete from goods
limit 100;

LOAD DATA
    LOCAL
    INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/backup warehouse/goods.table'
    INTO TABLE warehouse.goods
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n';
#     LINES TERMINATED BY '\r\n';

LOAD DATA LOCAL INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/backup warehouse/table_goods' INTO TABLE warehouse.goods LINES TERMINATED BY '\r\n';

SHOW VARIABLES LIKE "local_infile";
SHOW VARIABLES LIKE "%local%";
select ENABLED_LOCAL
# int i = 0;
# mysql_options(&mysql,MYSQL_OPT_LOCAL_INFILE,&i);
# mysql_options(&mysql,MYSQL_OPT_LOAD_DATA_LOCAL_DIR,"/my/local/data");
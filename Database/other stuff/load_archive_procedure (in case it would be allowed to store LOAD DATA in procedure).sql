DELIMITER //


# ################  Error: 1295 (HY000): This command is not supported in the prepared statement protocol yet
# drop procedure if exists load_file_to_tmp_table //
# create
#     PROCEDURE load_file_to_tmp_table(IN archive_number int, IN table_name varchar(50))
#     comment 'loads file to tmp table'
#     LANGUAGE SQL
#     NOT DETERMINISTIC
#     MODIFIES SQL DATA
#     SQL SECURITY INVOKER
# begin
#     SET @`sql` := CONCAT('
#         LOAD DATA
#             LOCAL
#             INFILE \'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/warehouse/archive/', archive_number, '_', table_name ,'.csv\'
#             INTO TABLE warehouse.tmp_', table_name,'
#             FIELDS TERMINATED BY '','' OPTIONALLY ENCLOSED BY ''"''
#             LINES TERMINATED BY ''\r\n'';'
#         );
#     PREPARE `stmt` FROM @`sql`;
#     EXECUTE `stmt`;
#     DEALLOCATE PREPARE `stmt`;
# end //
#
# ################  Error: 1295 (HY000): "load_file_to_tmp_table" is not supported in the prepared statement protocol yet
# DROP PROCEDURE IF EXISTS load_archive//
# CREATE
# #     DEFINER = 'archive'@'%'
#     PROCEDURE load_archive(archive_number int)
#     comment 'Creates file of table on server'
#     LANGUAGE SQL
#     NOT DETERMINISTIC
#     MODIFIES SQL DATA
#     SQL SECURITY INVOKER # - чтобы не было ошибки администратор должен давать право на использование функции только тем, кто
#                          # upd: нужно проверить есть ли необходимые права у вызывающего пользователя
#                          # (не обязательно, админ просто не должен давать им право пользоваться этой процедурой (то есть присваивать только с ролью))
#                          # админимтратор не должен забирать эти права во время вызова данной функции (воможно что-то может пойти не так)
# #     SQL SECURITY DEFINER
# load_tables_from_file: BEGIN
#
#     DECLARE EXIT HANDLER FOR 1086 # errno = ?
#     file_not_exists_error: begin
# #         GET DIAGNOSTICS CONDITION 1086
# #             @sqlstate = RETURNED_SQLSTATE, @msg = MESSAGE_TEXT;
#         drop TEMPORARY table IF EXISTS tmp_suppliers;
#         drop TEMPORARY table IF EXISTS tmp_supplies;
#         drop TEMPORARY table IF EXISTS tmp_goods_supplies;
#         drop TEMPORARY table IF EXISTS tmp_catalog;
#         drop TEMPORARY table IF EXISTS tmp_goods;
#         drop TEMPORARY table IF EXISTS tmp_storage;
#         drop TEMPORARY table IF EXISTS tmp_goods_shipments;
#         drop TEMPORARY table IF EXISTS tmp_shipments;
#         drop TEMPORARY table IF EXISTS tmp_customers;
#         SET @`msg` := CONCAT('Needed archive_number=\'', archive_number,'\' is used already (you might have added some files but not all that needed)');
#         SIGNAL SQLSTATE 'HY000' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9960;
#     end;
#
#     # проверить не запущена ли архивация или другой load from file процесс
#     call create_temporary_tables();
#     load_files_to_tmp_tables: begin
#         call load_file_to_tmp_table(archive_number, 'suppliers');
#         call load_file_to_tmp_table(archive_number, 'supplies');
#         call load_file_to_tmp_table(archive_number, 'goods_supplies');
#         call load_file_to_tmp_table(archive_number, 'catalog');
#         call load_file_to_tmp_table(archive_number, 'goods');
#         call load_file_to_tmp_table(archive_number, 'storage');
#         call load_file_to_tmp_table(archive_number, 'goods_shipments');
#         call load_file_to_tmp_table(archive_number, 'shipments');
#         call load_file_to_tmp_table(archive_number, 'customers');
#     end;
#     # <--- check if correct should be here
#     call truncate_tables();
#     # lock tables here
#     call copy_tables_from_tmp_to_warehouse();
#     # unlock tables here
#     call drop_temporary_tables();
# END//
#     # SELECT * FROM tmp_goods;









DELIMITER ;

# loading saved data
# ALTER TABLE warehouse.goods AUTO_INCREMENT = 1;

# LOAD DATA
#     LOCAL
#     INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/warehouse/archive/1_goods.csv'
#     INTO TABLE warehouse.goods
#     FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
#     LINES TERMINATED BY '\r\n';




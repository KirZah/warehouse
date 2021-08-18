# check foreign keys procedure that could be borrowed later:
# https://stackoverflow.com/questions/2250775/force-innodb-to-recheck-foreign-keys-on-a-table-tables/12085689#12085689
#
# stored routines explanation
# https://stackoverflow.com/questions/26015160/deterministic-no-sql-or-reads-sql-data-in-its-declaration-and-binary-logging-i

DELIMITER //
use warehouse //

DROP PROCEDURE IF EXISTS add_user//
CREATE
    PROCEDURE add_user(IN username VARCHAR(50), IN host VARCHAR(50), IN password VARCHAR(50), IN role VARCHAR(50))
    comment 'creates user and give him privileges assigned to gained ROLE (cannot assign to user cause selecting where User.Host = ''%'')'
    LANGUAGE SQL
    NOT DETERMINISTIC
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
# SQL SECURITY может принимать два значения - DEFINER или INVOKER
# в случае INVOKER скрипт выполняется с правами пользователя , который её вызвал, а не как в случае с:
# DEFINER - когда скрипт выполняется с правами пользователя указанного в CREATE DEFINER.
add_user: BEGIN
    SET username := CONCAT('\'', TRIM(BOTH '\'' FROM username), '\''),
        host     := CONCAT('@\'', TRIM(BOTH '\'' FROM TRIM(LEADING '@' FROM host)), '\''), # убрать @ ??
        password := CONCAT('\'', TRIM(BOTH '\'' FROM password), '\''),
        role  := CONCAT(TRIM(BOTH '\'' FROM role));
    IF role IN ('developer', 'administrator', 'director', 'boss', 'pc_operator', 'warehouseman', 'salesman') THEN  # , 'archive'
        if exists(Select User From mysql.user WHERE User.User = role AND User.Host = '%') then
            create_user_and_set_role: begin
            create_user:
                BEGIN
                    SET @`sql` := CONCAT('CREATE USER ', username, host, ' IDENTIFIED BY ', password);
                    PREPARE `stmt` FROM @`sql`;
                    EXECUTE `stmt`;
                    DEALLOCATE PREPARE `stmt`;
                END;
            grant_role_to_user:
                BEGIN
                    SET @`sql` := CONCAT('GRANT ', role, '@\'%\' TO ', username, host, ';');
                    PREPARE `stmt` FROM @`sql`;
                    EXECUTE `stmt`;
                    DEALLOCATE PREPARE `stmt`;
                END;
            set_granted_role_as_default:
                BEGIN
                    SET @`sql` := CONCAT('SET DEFAULT ROLE ', role, '@\'%\' TO ', username, host, ';');
                    PREPARE `stmt` FROM @`sql`;
                    EXECUTE `stmt`;
                    DEALLOCATE PREPARE `stmt`;
                END;
            end;
        else
            return_error_role_not_created:
                begin
                    SET @`msg` := CONCAT('PROCEDURE \'add_user\' FAILED. Role \'', role, '\' is not created yet');
                    SIGNAL SQLSTATE 'ROLEP' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9991;
                    # LEAVE add_user;
                end;
        end if;
    ELSE
        return_error_unknown_role:
            begin
                SET @`msg` := CONCAT('PROCEDURE \'add_user\' FAILED. Got unknown role \'', role, '\'');
                SIGNAL SQLSTATE 'ROLEP' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9990;
                # LEAVE add_user;
            end;
    END IF;
END//

DROP FUNCTION IF EXISTS get_user_role//
CREATE
    DEFINER = 'mysql_select'@'%'
    FUNCTION get_user_role(username VARCHAR(50), host VARCHAR(50))
    RETURNS VARCHAR(50)
    comment 'returns user''s role'
    LANGUAGE SQL
    NOT DETERMINISTIC
    READS SQL DATA
    SQL SECURITY DEFINER
#     SQL SECURITY INVOKER
get_user_role: BEGIN
    SET username := CONCAT(TRIM(BOTH '\'' FROM username)),
        host     := CONCAT(TRIM(BOTH '\'' FROM TRIM(LEADING '@' FROM host)));

#     if

    # Можно после поиска по конкретному host добавить поиск в host='%' чтобы при наличии полььзователя с host=% тот мог также зайти (было бы найс так сделать, но потом)
    IF exists(select User From mysql.user WHERE User = username AND (mysql.user.Host = host)) THEN #  OR mysql.user.Host = '%'
        try_to_return_role:BEGIN
#         SET @role := (select * From mysql.role_edges where TO_USER = username AND TO_HOST = host);  # Idk why this didn't work
        IF exists(select TO_USER From mysql.role_edges where TO_USER = username AND TO_HOST = host) THEN
            return_role_for_exactly_host: begin
            RETURN (select FROM_USER From mysql.role_edges where TO_USER = username AND TO_HOST = host);  # 2 same corteges, yea that doesn't look good, but at least it's working
        end;
#         elseif exists(select TO_USER From mysql.role_edges where TO_USER = username AND TO_HOST = '%') THEN
#             return_role_for_any_host: begin
#             RETURN (select FROM_USER From mysql.role_edges where TO_USER = username AND TO_HOST = '%');  # 2 same corteges, yea that doesn't look good, but at least it's working
#         end;
        else
#             user_not_exist_in_mysql_role_edges_error: begin
# #             SET @`msg` := CONCAT('User \'', username,'\' does not have any role assigned nor on host \'', host, '\' nor for \'%\' (there is no record in \'mysql.role_edges\' table).');
#             SET @`msg` := CONCAT('User \'', username,'\' does not have any role assigned on host \'', host, '\' (there is no record in \'mysql.role_edges\' table).');
#             SIGNAL SQLSTATE 'ROLEF' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9981;
#             end;
            RETURN 'Unknown Role';
        end if;
        END;
    else user_not_exist_in_mysql_user_error: begin
            SET @`msg` := CONCAT('User \'', username,'\'@\'', host, '\' does not exist (there is no record in \'mysql.User\' table).');
            SIGNAL SQLSTATE 'USERF' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9980;
        end;
    end if;
END//


drop procedure if exists add_goods //
CREATE PROCEDURE add_goods(IN amount INT, in_catalog_id INT, in_production_date DATE, in_note VARCHAR(255))
    comment 'Adds Packages to table "goods"'
    LANGUAGE SQL
    NOT DETERMINISTIC
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
BEGIN
    DECLARE EXIT HANDLER FOR 1452
    file_exists_error: begin  # MESSAGE_TEXT VARCHAR(128)
        SET @`msg` := CONCAT('Cannot add goods: catalog_id=\'', in_catalog_id, '\' do not exist');
        SIGNAL SQLSTATE '23000' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9951;
    end;

    if amount <= 1000 then begin
        SET @i = 0;
        label1: LOOP
            IF @i < amount THEN
                begin
                    SET @i = @i + 1;
                    insert into goods(catalog_id, state_id, production_date, note) values(in_catalog_id, 1, in_production_date, in_note);
                    ITERATE label1;
                end;
            else
                LEAVE label1;
            END IF;
        END LOOP label1;
    end;
    else begin
        SET @`msg` := CONCAT('You cannot add more than 1 000 goods at once');
        SIGNAL SQLSTATE 'AMOUN' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9950;
    end;
    end if;
END//

drop procedure if exists sell_package //
CREATE PROCEDURE sell_package(IN in_goods_id INT, in_shipments_id int)
    comment 'Adds Packages to table "goods_shipments" if goods.state_id is correct and changes goods.state_id to "sold"'
#     comment 'Adds Packages to table "goods_shipments" if goods.state_id is correct
#             (if state was correct and package is sold then changes state to correct but returns error
#             (cause package is sold already))'
    LANGUAGE SQL
    NOT DETERMINISTIC
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
BEGIN

    DECLARE EXIT HANDLER FOR 1062 # [23000][1062] Duplicate entry '12' for key 'goods_shipments.PRIMARY'
        package_already_sold_error: begin  # MESSAGE_TEXT VARCHAR(128)
#             SET @`msg` := CONCAT('Package #\'', in_goods_id,'\' is in another shipment already. (Package''s state is now changed to "sold")');
            SET @`msg` := CONCAT('Package #\'', in_goods_id,'\' is in another shipment already.');
            SIGNAL SQLSTATE 'SELLP' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9941;
        end;
    DECLARE EXIT HANDLER FOR 1452 # [23000][1452] Cannot add or update a child row: a foreign key constraint fails
        shipment_not_exists_error: begin  # MESSAGE_TEXT VARCHAR(128)
            SET @`msg` := CONCAT('Shipment #\'', in_shipments_id,'\' do not exist');
            SIGNAL SQLSTATE 'SELLP' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9943;
        end;

    check_is_package_exists: begin
        if NOT exists(SELECT goods.state_id FROM goods WHERE goods.id = in_goods_id) THEN
            SET @`msg` := CONCAT('Package #\'', in_goods_id,'\' do not exist');
                SIGNAL SQLSTATE 'SELLP' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9942;
        end if;
    end ;

#     check_is_shipment_exists: begin
#         if NOT exists(SELECT shipments.id FROM shipments WHERE shipments.id = in_shipments_id) THEN
#             SET @`msg` := CONCAT('Shipment #\'', in_shipments_id,'\' do not exist');
#                 SIGNAL SQLSTATE 'SELLP' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9943;
#         end if;
#     end ;

#     change_package_state : BEGIN
#         SET @package_state = (SELECT goods.state_id FROM goods WHERE goods.id = in_goods_id);
        IF 1 = (SELECT goods.state_id FROM goods WHERE goods.id = in_goods_id) THEN BEGIN# @package_state
            insert into warehouse.goods_shipments(goods_id, shipments_id) values(in_goods_id, in_shipments_id);
            UPDATE goods SET goods.state_id = 2 WHERE goods.id = in_goods_id;
        END;
        ELSE unknown_goods_state_error: begin
                SET @`msg` := CONCAT('Package #\'', in_goods_id, '\' has incorrect state for operation ''SELL PACKAGE''');
                SIGNAL SQLSTATE 'STATE' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9940;
            end;
        END IF;
#     END;

    DELETE FROM storage WHERE goods_id = in_goods_id;

END//

drop procedure if exists return_sold_package //
CREATE PROCEDURE return_sold_package(IN in_goods_id INT)  # , in_shipments_id int
    comment 'deletes package from table "goods_shipments" and changes goods.state_id to "in stock"'
    LANGUAGE SQL
    NOT DETERMINISTIC
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
BEGIN

#     DECLARE EXIT HANDLER FOR 1452 # [23000][1452] Cannot add or update a child row: a foreign key constraint fails
#         shipment_not_exists_error: begin  # MESSAGE_TEXT VARCHAR(128)
#             SET @`msg` := CONCAT('Shipment #\'', in_shipments_id,'\' do not exist');
#             SIGNAL SQLSTATE 'SELLP' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9943;
#         end;

    check_is_package_exists: begin
        if NOT exists(SELECT goods.state_id FROM goods WHERE goods.id = in_goods_id) THEN
            SET @`msg` := CONCAT('Package #\'', in_goods_id,'\' do not exist');
                SIGNAL SQLSTATE 'RSELL' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9942;
        end if;
    end ;

#     check_is_shipment_exists: begin
#         if NOT exists(SELECT shipments.id FROM shipments WHERE shipments.id = in_shipments_id) THEN
#             SET @`msg` := CONCAT('Shipment #\'', in_shipments_id,'\' do not exist');
#                 SIGNAL SQLSTATE 'SELLP' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9943;
#         end if;
#     end ;

#     change_package_state : BEGIN
#         SET @package_state = (SELECT goods.state_id FROM goods WHERE goods.id = in_goods_id);
        IF 2 = (SELECT goods.state_id FROM goods WHERE goods.id = in_goods_id) THEN BEGIN # @package_state
            delete from warehouse.goods_shipments where goods_id = in_goods_id;  #  AND shipments_id = in_shipments_id
            UPDATE goods SET goods.state_id = 1 WHERE goods.id = in_goods_id;
        END;
        ELSE unknown_goods_state_error: begin
                SET @`msg` := CONCAT('Package #\'', in_goods_id, '\' has incorrect state for operation ''RETURN SOLD PACKAGE''');
                SIGNAL SQLSTATE 'STATE' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9940;
            end;
        END IF;
#     END;

    DELETE FROM storage WHERE goods_id = in_goods_id;

END//


drop procedure if exists archive_from_tmp_tables//
CREATE
    DEFINER = 'archive'@'%'
    PROCEDURE archive_from_tmp_tables(archive_number int, table_name varchar(50))
    comment 'Creates file of table on server'
    LANGUAGE SQL
    NOT DETERMINISTIC
#     READS SQL DATA
#     MODIFIES SQL DATA
    CONTAINS SQL
    SQL SECURITY DEFINER
#     SQL SECURITY INVOKER
create_table_file: BEGIN

    SET @`sql` := CONCAT('
            SELECT * INTO OUTFILE \'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/warehouse/archive/', archive_number, '_', table_name,'.csv\'
                FIELDS TERMINATED BY \',\' OPTIONALLY ENCLOSED BY \'"\'
                LINES TERMINATED BY ''\\r\\n''
                FROM tmp_', table_name,';'
            );
    PREPARE `stmt` FROM @`sql`;
    EXECUTE `stmt`;
    DEALLOCATE PREPARE `stmt`;

end //

DROP PROCEDURE IF EXISTS archive//
CREATE
#     DEFINER = 'archive'@'%'
    PROCEDURE archive(archive_number int)
    comment 'Creates file of table on server'
    LANGUAGE SQL
    NOT DETERMINISTIC
#     READS SQL DATA
    SQL SECURITY INVOKER # - чтобы не было ошибки администратор должен давать право на использование функции только тем, кто
                         # upd: нужно проверить есть ли необходимые права у вызывающего пользователя
                         # (не обязательно, админ просто не должен давать им право пользоваться этой процедурой (то есть присваивать только с ролью))
                         # админимтратор не должен забирать эти права во время вызова данной функции (воможно что-то может пойти не так)
#     SQL SECURITY DEFINER
create_table_file: BEGIN

    DECLARE EXIT HANDLER FOR 1086
    file_exists_error: begin  # MESSAGE_TEXT VARCHAR(128)
#         GET DIAGNOSTICS CONDITION 1086
#             @sqlstate = RETURNED_SQLSTATE, @msg = MESSAGE_TEXT;
        call drop_temporary_tables();

#         rollback;
#         ROLLBACK;
#         SET autocommit=1;
        SET @`msg` := CONCAT('Needed archive_number=\'', archive_number,'\' is used already (you might have added some files but not all that needed)');
        SIGNAL SQLSTATE 'ARHIV' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9960;
    end;

#     SET autocommit=0;
    START TRANSACTION;

# SELECT @A:=SUM(salary) FROM table1 WHERE type=1;
# UPDATE table2 SET summary=@A WHERE type=1;
#     START TRANSACTION;
    SET GLOBAL local_infile=1;
    call create_temporary_tables();
#     lock_tables: begin
# #         use warehouse; # privileges changes only after reconnection
# #         (select Table_name from information_schema.tables where table_schema = 'warehouse');
#         LOCK TABLES warehouse.suppliers WRITE;
#         LOCK TABLES warehouse.supplies WRITE;
#         LOCK TABLES warehouse.goods_supplies WRITE;
#         LOCK TABLES warehouse.catalog WRITE;
#         LOCK TABLES warehouse.goods WRITE;
#         LOCK TABLES warehouse.storage WRITE;
#         LOCK TABLES warehouse.goods_shipments WRITE;
#         LOCK TABLES warehouse.shipments WRITE;
#         LOCK TABLES warehouse.customers WRITE;
#     end ;
    copy_warehouse_tables_to_tmp: begin
        INSERT INTO tmp_suppliers
            SELECT  * FROM warehouse.suppliers FOR UPDATE;
        INSERT INTO tmp_supplies
            SELECT * FROM warehouse.supplies FOR UPDATE;
        INSERT INTO tmp_goods_supplies
            SELECT * FROM warehouse.goods_supplies FOR UPDATE;
        INSERT INTO tmp_catalog
            SELECT * FROM warehouse.catalog FOR UPDATE;
        INSERT INTO tmp_package_states
            SELECT * FROM warehouse.package_states FOR UPDATE;
        INSERT INTO tmp_goods
            SELECT * FROM warehouse.goods FOR UPDATE;
        INSERT INTO tmp_storage
            SELECT * FROM warehouse.storage FOR UPDATE;
        INSERT INTO tmp_goods_shipments
            SELECT * FROM warehouse.goods_shipments FOR UPDATE;
        INSERT INTO tmp_shipments
            SELECT * FROM warehouse.shipments FOR UPDATE;
        INSERT INTO tmp_customers
            SELECT * FROM warehouse.customers FOR UPDATE;
    end ;

#     UNLOCK TABLES;

    # SELECT * FROM tmp_goods;
    archive_from_tmp_tables: begin
        CALL archive_from_tmp_tables(archive_number, 'suppliers');
        DROP TEMPORARY TABLE tmp_suppliers;
        CALL archive_from_tmp_tables(archive_number, 'supplies');
        DROP TEMPORARY TABLE tmp_supplies;
        CALL archive_from_tmp_tables(archive_number, 'goods_supplies');
        DROP TEMPORARY TABLE tmp_goods_supplies;
        CALL archive_from_tmp_tables(archive_number, 'catalog');
        DROP TEMPORARY TABLE tmp_catalog;
        CALL archive_from_tmp_tables(archive_number, 'package_states');
        DROP TEMPORARY TABLE tmp_package_states;
        CALL archive_from_tmp_tables(archive_number, 'goods');
        DROP TEMPORARY TABLE tmp_goods;
        CALL archive_from_tmp_tables(archive_number, 'storage');
        DROP TEMPORARY TABLE tmp_storage;
        CALL archive_from_tmp_tables(archive_number, 'customers');
        DROP TEMPORARY TABLE tmp_customers;
        CALL archive_from_tmp_tables(archive_number, 'shipments');
        DROP TEMPORARY TABLE tmp_shipments;
        CALL archive_from_tmp_tables(archive_number, 'goods_shipments');
        DROP TEMPORARY TABLE tmp_goods_shipments;
    end ;
#     COMMIT;
END//

############# FOR "LOAD ARCHIVE" ##############

DROP PROCEDURE IF EXISTS create_temporary_tables//  # HANDLE [42S01][1050] Table 'tmp_suppliers' already exists
CREATE
    PROCEDURE create_temporary_tables()
    comment 'Creates temporary tables'
    LANGUAGE SQL
    NOT DETERMINISTIC
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
creating_temporary_tables: begin
        drop TEMPORARY table IF EXISTS warehouse.tmp_suppliers;
        drop TEMPORARY table IF EXISTS warehouse.tmp_supplies;
        drop TEMPORARY table IF EXISTS warehouse.tmp_goods_supplies;
        drop TEMPORARY table IF EXISTS warehouse.tmp_catalog;
        drop TEMPORARY table IF EXISTS warehouse.tmp_package_states;
        drop TEMPORARY table IF EXISTS warehouse.tmp_goods;
        drop TEMPORARY table IF EXISTS warehouse.tmp_storage;
        drop TEMPORARY table IF EXISTS warehouse.tmp_customers;
        drop TEMPORARY table IF EXISTS warehouse.tmp_goods_shipments;
        drop TEMPORARY table IF EXISTS warehouse.tmp_shipments;
        CREATE TEMPORARY TABLE tmp_suppliers        SELECT * FROM suppliers         LIMIT 0;
        CREATE TEMPORARY TABLE tmp_supplies         SELECT * FROM supplies          LIMIT 0;
        CREATE TEMPORARY TABLE tmp_goods_supplies   SELECT * FROM goods_supplies    LIMIT 0;
        CREATE TEMPORARY TABLE tmp_catalog          SELECT * FROM catalog           LIMIT 0;
        CREATE TEMPORARY TABLE tmp_package_states   SELECT * FROM package_states    LIMIT 0;
        CREATE TEMPORARY TABLE tmp_goods            SELECT * FROM goods             LIMIT 0;
        CREATE TEMPORARY TABLE tmp_storage          SELECT * FROM storage           LIMIT 0;
        CREATE TEMPORARY TABLE tmp_customers        SELECT * FROM customers         LIMIT 0;
        CREATE TEMPORARY TABLE tmp_goods_shipments  SELECT * FROM goods_shipments   LIMIT 0;
        CREATE TEMPORARY TABLE tmp_shipments        SELECT * FROM shipments         LIMIT 0;
END//

DROP PROCEDURE IF EXISTS truncate_tables//
CREATE
    PROCEDURE truncate_tables()
    comment 'Deletes all records in all tables'
    LANGUAGE SQL
    NOT DETERMINISTIC
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
truncate_tables: begin
    SET FOREIGN_KEY_CHECKS = 0;
    TRUNCATE TABLE warehouse.goods_shipments;
    TRUNCATE TABLE warehouse.shipments;
    TRUNCATE TABLE warehouse.customers;

    TRUNCATE TABLE warehouse.storage;

    TRUNCATE TABLE warehouse.goods_supplies;
    TRUNCATE TABLE warehouse.goods;
    TRUNCATE TABLE warehouse.catalog;
    TRUNCATE TABLE warehouse.package_states;

    TRUNCATE TABLE warehouse.supplies;
    TRUNCATE TABLE warehouse.suppliers;
    SET FOREIGN_KEY_CHECKS = 1;
END//

DROP PROCEDURE IF EXISTS copy_tables_from_tmp_to_warehouse//
CREATE
    PROCEDURE copy_tables_from_tmp_to_warehouse()
    comment 'copies tables from tmp to warehouse'
    LANGUAGE SQL
    NOT DETERMINISTIC
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
copy_tables_from_tmp_to_warehouse: begin
        INSERT INTO warehouse.suppliers         SELECT * FROM tmp_suppliers         FOR UPDATE;
        INSERT INTO warehouse.supplies          SELECT * FROM tmp_supplies          FOR UPDATE;
        INSERT INTO warehouse.catalog           SELECT * FROM tmp_catalog           FOR UPDATE;
        INSERT INTO warehouse.package_states    SELECT * FROM tmp_package_states    FOR UPDATE;
        INSERT INTO warehouse.goods             SELECT * FROM tmp_goods             FOR UPDATE;
        INSERT INTO warehouse.goods_supplies    SELECT * FROM tmp_goods_supplies    FOR UPDATE;
        INSERT INTO warehouse.storage           SELECT * FROM tmp_storage           FOR UPDATE;
        INSERT INTO warehouse.customers         SELECT * FROM tmp_customers         FOR UPDATE;
        INSERT INTO warehouse.shipments         SELECT * FROM tmp_shipments         FOR UPDATE;
        INSERT INTO warehouse.goods_shipments   SELECT * FROM tmp_goods_shipments   FOR UPDATE;
END//

DROP PROCEDURE IF EXISTS drop_temporary_tables//
CREATE
    PROCEDURE drop_temporary_tables()
    comment 'Drops temporary tables'
    LANGUAGE SQL
    NOT DETERMINISTIC
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
creating_temporary_tables: begin
        drop TEMPORARY table IF EXISTS warehouse.tmp_suppliers;
        drop TEMPORARY table IF EXISTS warehouse.tmp_supplies;
        drop TEMPORARY table IF EXISTS warehouse.tmp_goods_supplies;
        drop TEMPORARY table IF EXISTS warehouse.tmp_catalog;
        drop TEMPORARY table IF EXISTS warehouse.tmp_package_states;
        drop TEMPORARY table IF EXISTS warehouse.tmp_goods;
        drop TEMPORARY table IF EXISTS warehouse.tmp_storage;
        drop TEMPORARY table IF EXISTS warehouse.tmp_customers;
        drop TEMPORARY table IF EXISTS warehouse.tmp_goods_shipments;
        drop TEMPORARY table IF EXISTS warehouse.tmp_shipments;
END//

#^^^^^^^^^^^^ FOR "LOAD ARCHIVE" ^^^^^^^^^^^^^^


drop trigger if exists after_goods_delete //
CREATE TRIGGER after_goods_delete  # deletes unused catalog element after deleting package
AFTER DELETE
ON goods FOR EACH ROW BEGIN
    if NOT exists(select * from goods where goods.catalog_id = OLD.catalog_id) then
        DELETE FROM catalog WHERE catalog.id = old.catalog_id;
    END IF;
END //

DELIMITER ;




# DELIMITER //
# DROP PROCEDURE IF EXISTS change_package_state//
# CREATE
#     DEFINER = 'warehouse_update'@'%'
#     PROCEDURE change_package_state(IN goods_id int, IN new_state tinyint)
#     comment 'changes goods.state_id'
#     LANGUAGE SQL
#     NOT DETERMINISTIC
#     MODIFIES SQL DATA
#     SQL SECURITY DEFINER
# #     deterministic
# BEGIN
#     SET @package_state = (SELECT goods.state_id FROM goods WHERE goods.id = goods_id);
#     IF new_state = 1 THEN
#         sell_package : BEGIN
#             IF 0 = @package_state THEN  # (SELECT goods.state_id FROM goods WHERE goods.id = goods_id)
#                 UPDATE goods SET state = new_state WHERE goods.id = goods_id;
#             ELSE unknown_goods_state_error: begin
#                     SET @`msg` := CONCAT('Package #\'', goods_id, '\' has incorrect state=\'', @package_state,'\' for operation ''SELL PACKAGE''');
#                     SIGNAL SQLSTATE 'STATE' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9970;
#                 end;
#             END IF;
#         END;
#     ELSE IF new_state = 0 THEN
#         return_package : BEGIN
#             IF 1 = @package_state THEN  # (SELECT goods.state_id FROM goods WHERE goods.id = goods_id)
#                 UPDATE goods SET state = new_state WHERE goods.id = goods_id;
#             ELSE unknown_goods_state_error: begin
#                     SET @`msg` := CONCAT('Package #\'', goods_id, '\' has incorrect state=\'', @package_state,'\' for operation ''RETURN PACKAGE''');
#                     SIGNAL SQLSTATE 'STATE' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9970;
#                 end;
#             END IF;
#         END;
#         END IF;
#     ELSE
#         unknown_goods_state_error: begin
#             SET @`msg` := CONCAT('Cannot change goods.state_id to unknown value (new_value=\'', new_state,'\')');
#             SIGNAL SQLSTATE 'STATE' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9971;
#         END;
#     END IF;
# END //
#
# DELIMITER ;

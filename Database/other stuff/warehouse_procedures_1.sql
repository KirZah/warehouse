# granting access to procedures -> https://www.techonthenet.com/mysql/grant_revoke.php#:~:text=The%20syntax%20for%20granting%20EXECUTE,execute%20the%20function%20or%20procedure.
DELIMITER //
use warehouse //
DROP PROCEDURE IF EXISTS create_mysql_user//
CREATE PROCEDURE create_mysql_user(IN username VARCHAR(50), IN host VARCHAR(50), IN password VARCHAR(50))
BEGIN
#     DECLARE `host` CHAR(15) DEFAULT '@\'localhost\'';
    SET username := CONCAT('\'', TRIM(BOTH '\'' FROM username), '\''),
        host     := CONCAT('@\'', TRIM(BOTH '\'' FROM TRIM(LEADING '@' FROM host)), '\''),
        password := CONCAT('\'', TRIM(BOTH '\'' FROM password), '\'');
    SET @`sql` := CONCAT('CREATE USER ', username, host, ' IDENTIFIED BY ', password);
    PREPARE `stmt` FROM @`sql`;
    EXECUTE `stmt`;
END//
DELIMITER ;

# # with that any user will execute this with admin privileges
# DROP PROCEDURE account_count;
# CREATE DEFINER = 'admin'@'localhost' PROCEDURE account_count()
# BEGIN
#   SELECT 'Number of accounts:', COUNT(*) FROM mysql.user;
# END;
#
# CREATE DEFINER = 'admin'@'localhost' PROCEDURE account_count()
# SQL SECURITY INVOKER
# BEGIN
#   SELECT 'Number of accounts:', COUNT(*) FROM mysql.user;
# END;
#
# CALL account_count;
########################

##################
DELIMITER //
use warehouse //
DROP PROCEDURE IF EXISTS add_user//
CREATE PROCEDURE add_user(IN username VARCHAR(50), IN host VARCHAR(50), IN password VARCHAR(50), IN in_role VARCHAR(50))
SQL SECURITY INVOKER
# language sql
# deterministic
# sql security definer
# comment 'add user and give him privileges'
add_user: BEGIN

    SET username := CONCAT('\'', TRIM(BOTH '\'' FROM username), '\''),
        host     := CONCAT('@\'', TRIM(BOTH '\'' FROM TRIM(LEADING '@' FROM host)), '\''), # убрать @ ??
        password := CONCAT('\'', TRIM(BOTH '\'' FROM password), '\''),
        in_role  := CONCAT(TRIM(BOTH '\'' FROM in_role));
    #     @in_role  := CONCAT('\'', TRIM(BOTH '\'' FROM @in_role), '\'', '@\'%\''),
    SET     @username_and_host := CONCAT(username, host);
#     select @username_and_host;
    CASE in_role
        WHEN 'administrator' THEN
            BEGIN
#             set @username_and_host := CONCAT(@username, '@', @host);
#             CALL create_mysql_user(username, host, password);
#             GRANT 'administrator' TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#             SET DEFAULT ROLE 'administrator' TO @username_and_host;

            CALL create_mysql_user(username, host, password);
            SET @`sql` := CONCAT(
                'GRANT ', in_role, '@\'%\' TO ', username, host, ';'
                );
            PREPARE `stmt` FROM @`sql`;
            EXECUTE `stmt`;
            DEALLOCATE PREPARE `stmt`;

            SET @`sql` := CONCAT(
                'SET DEFAULT ROLE ', in_role, '@\'%\' TO ', username, host, ';'
                );
            PREPARE `stmt` FROM @`sql`;
            EXECUTE `stmt`;
            DEALLOCATE PREPARE `stmt`;
#             SET DEFAULT ROLE 'administrator' TO @username_and_host;
            END;
        WHEN 'boss' THEN
            BEGIN
#             CALL create_mysql_user(username, host, password);
#             GRANT 'boss' TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#             SET DEFAULT ROLE 'boss' TO @username_and_host;
            END;
        WHEN 'pc_operator' THEN
            BEGIN
#             CALL create_mysql_user(username, host, password);
#             GRANT 'pc_operator' TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#             SET DEFAULT ROLE 'pc_operator' TO @username_and_host;
            END;
        WHEN 'warehouseman' THEN
            BEGIN
#             CALL create_mysql_user(username, host, password);
#             GRANT 'warehouseman' TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#             SET DEFAULT ROLE 'warehouseman' TO @username_and_host;
            END;
        WHEN 'salesman' THEN
            BEGIN
#             CALL create_mysql_user(username, host, password);
#             GRANT 'salesman' TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#             SET DEFAULT ROLE 'salesman' TO @username_and_host;
            END;
        WHEN 'customer' THEN
            BEGIN
#             SET @in_role := 'customer';
            END;
        ELSE
            BEGIN
#             SET @host = host; USING @host;
             SET @`msg` := CONCAT('FAILED PROCEDURE add_user. Got unknown role \'', in_role, '\'');
             SIGNAL SQLSTATE '99999'
             SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 1000;
#             SET MESSAGE_TEXT = CONCAT('FAILED PROCEDURE add_user. Got unknown role \'', role, '\''), MYSQL_ERRNO = 1000;
#             LEAVE add_user;
            END;
    END CASE;
#     SET @got_role := 'customer';
#     select @got_role;
#
#     CALL create_mysql_user(username, host, password);
#     GRANT @in_role TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#     SET DEFAULT ROLE @in_role TO @username_and_host;
#     FLUSH PRIVILEGES;
   # CALL save_user_role(IN `username` VARCHAR(50), IN `host` VARCHAR(50), IN `role` VARCHAR(50))

END//

DELIMITER ;

use warehouse;
CALL add_user('administrator24', '%', 'administrator', 'administrator');
# MY ADMINISTRATORS NEED THIS PRIVILEGE: (to create with grants = activate users)
# Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
# UPDATE: NO THEY DON't cause EVEN Chyvak88 GETS THIS MESSAGE WHEN SMTH WRONG
###################
show grants for administrator;
GRANT 'administrator' TO administrator15;
show grants for 'administrator15'@'%' using 'administrator';
SET DEFAULT ROLE 'administrator' TO administrator15;

# set @username := 'warehouseman5',
#     @host := 'localhost',
#     @password := 'warehouseman5',
#     @in_role := 'warehouseman';
#
# SET @username := CONCAT('\'', TRIM(BOTH '\'' FROM @username), '\''),
#     @host     := CONCAT('\'', TRIM(BOTH '\'' FROM TRIM(LEADING '@' FROM @host)), '\''),
#     @password := CONCAT('\'', TRIM(BOTH '\'' FROM @password), '\''),
#     @in_role  := CONCAT('\'', TRIM(BOTH '\'' FROM @in_role), '\''),
# #     @in_role  := CONCAT('\'', TRIM(BOTH '\'' FROM @in_role), '\'', '@\'%\''),
#     @username_and_host := CONCAT(@username, '@', @host);
# select @username_and_host;
# set
#     @username_and_host := CONCAT(@username, '@', @host);
# select @username_and_host;
# select @host;
# select @in_role;
#
#  CALL create_mysql_user(@username, @host, @password);
#             GRANT CURRENT_ROLE TO @username_and_host;
#             SET DEFAULT ROLE @in_role TO @username_and_host;
#             FLUSH PRIVILEGES;

#########
###############3
##################
########################
###########################################
#
# DELIMITER //
# use warehouse //
#
# DROP PROCEDURE IF EXISTS create_mysql_user//
# CREATE PROCEDURE create_mysql_user(IN username VARCHAR(50), IN host VARCHAR(50), IN password VARCHAR(50))
# BEGIN
# #     DECLARE `host` CHAR(15) DEFAULT '@\'localhost\'';
#     SET username := CONCAT('\'', TRIM(BOTH '\'' FROM username), '\''),
#         host     := CONCAT('@\'', TRIM(BOTH '\'' FROM TRIM(LEADING '@' FROM host)), '\''),
#         password := CONCAT('\'', TRIM(BOTH '\'' FROM password), '\'');
#     SET @`sql` := CONCAT('CREATE USER ', username, host, ' IDENTIFIED BY ', password);
#     PREPARE `stmt` FROM @`sql`;
#     EXECUTE `stmt`;
# END//
#
# DROP PROCEDURE IF EXISTS add_user//
# CREATE PROCEDURE add_user(IN username VARCHAR(50), IN host VARCHAR(50), IN password VARCHAR(50), IN in_role VARCHAR(50))
# add_user: BEGIN
#     SET username := CONCAT('\'', TRIM(BOTH '\'' FROM username), '\''),
#         host     := CONCAT('\'', TRIM(BOTH '\'' FROM TRIM(LEADING '@' FROM host)), '\''),
#         password := CONCAT('\'', TRIM(BOTH '\'' FROM password), '\'');
#     SET
#         @username_and_host := CONCAT(username, '@', host);
#     CASE in_role
#         WHEN 'administrator' THEN
#             BEGIN
#             CALL create_mysql_user(username, host, password);
#             SET @`sql` := CONCAT(
#                 'GRANT ALL PRIVILEGES ON warehouse.* TO ', username, host, ';'
#                 );
#             PREPARE `stmt` FROM @`sql`;
#             EXECUTE `stmt`;
#             DEALLOCATE PREPARE `stmt`;
#             END;
#         WHEN 'boss' THEN
#             BEGIN
#             CALL create_mysql_user(username, host, password);
#             SET @`sql` := CONCAT(
#                 'GRANT SELECT, INSERT, DELETE, UPDATE ON warehouse.* TO ', username, host, ';'
#                 );
#
#             PREPARE `stmt` FROM @`sql`;
#             EXECUTE `stmt`;
#             DEALLOCATE PREPARE `stmt`;
#             END;
#         WHEN 'pc_operator' THEN
#             BEGIN
#             CALL create_mysql_user(username, host, password);
# #             SET @`sequels` :=
#             SET @`sql` := CONCAT(
# #                 'GRANT SELECT, INSERT ON warehouse.*                TO ', username, host, ';',
#                 'GRANT SELECT, INSERT ON warehouse.suppliers        TO ', username, host, ';',
#                 'GRANT SELECT, INSERT ON warehouse.supplies         TO ', username, host, ';',
#                 'GRANT SELECT, INSERT ON warehouse.goods_supplies   TO ', username, host, ';',
#                 'GRANT SELECT, INSERT ON warehouse.goods            TO ', username, host, ';',
#                 'GRANT SELECT, INSERT ON warehouse.catalog          TO ', username, host, ';',
#                 'GRANT SELECT         ON warehouse.storage          TO ', username, host, ';',
#                 'GRANT SELECT, INSERT ON warehouse.goods_shipments  TO ', username, host, ';',
#                 'GRANT SELECT, INSERT ON warehouse.shipments        TO ', username, host, ';',
#                 'GRANT SELECT, INSERT ON warehouse.customers        TO ', username, host, ';'
#                 );
#             PREPARE `stmt` FROM @`sql`;
#             EXECUTE `stmt`;
#             DEALLOCATE PREPARE `stmt`;
#             END;
#         WHEN 'warehouseman' THEN
#             BEGIN
#             CALL create_mysql_user(username, host, password);
#             GRANT 'warehouseman' TO username@host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#             SET DEFAULT ROLE 'warehouseman' TO @username_and_host;
#
#         ELSE
#             BEGIN
# #             SET @host = host; USING @host;
#              SET @`msg` := CONCAT('FAILED PROCEDURE add_user. Got unknown role \'', in_role, '\'');
#              SIGNAL SQLSTATE '99999'
#              SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 1000;
# #             SET MESSAGE_TEXT = CONCAT('FAILED PROCEDURE add_user. Got unknown role \'', role, '\''), MYSQL_ERRNO = 1000;
# #             LEAVE add_user;
#             END;
#     END CASE;
#     # GRANT SELECT, INSERT ON warehouse.suppliers         TO 'pc_operator'@'%';
#     # GRANT SELECT, INSERT ON warehouse.supplies          TO 'pc_operator'@'%';
#     # GRANT SELECT, INSERT ON warehouse.goods_supplies    TO 'pc_operator'@'%';
#     # GRANT SELECT, INSERT ON warehouse.goods             TO 'pc_operator'@'%';
#     # GRANT SELECT, INSERT ON warehouse.catalog           TO 'pc_operator'@'%';
#     # GRANT SELECT         ON warehouse.storage           TO 'pc_operator'@'%';
#     # GRANT SELECT, INSERT ON warehouse.goods_shipments   TO 'pc_operator'@'%';
#     # GRANT SELECT, INSERT ON warehouse.shipments         TO 'pc_operator'@'%';
#     # GRANT SELECT, INSERT ON warehouse.customers         TO 'pc_operator'@'%';
#     # GRANT SELECT, INSERT, UPDATE ON warehouse.storage   TO 'warehouseman'@'%';
#     # GRANT SELECT                 ON warehouse.goods     TO 'warehouseman'@'%';
#     # GRANT SELECT                 ON warehouse.catalog   TO 'warehouseman'@'%';
#     # GRANT SELECT, INSERT, UPDATE ON warehouse.customers TO 'salesman'@'%';
#     # GRANT SELECT                 ON warehouse.goods     TO 'salesman'@'%';
#     # GRANT SELECT                 ON warehouse.catalog   TO 'salesman'@'%';
#     # GRANT SELECT ON warehouse.catalog TO 'customer'@'%';
#     # GRANT SELECT ON warehouse.catalog TO 'customer'@'%';
#     FLUSH PRIVILEGES;
#     # CALL save_user_role(IN `username` VARCHAR(50), IN `host` VARCHAR(50), IN `role` VARCHAR(50))
# END//
#
# DELIMITER ;
#
# use warehouse;
# CALL add_user('warehouseman2', 'localhost', 'warehouseman2', 'warehouseman');
# ###################
# drop user 'username'@'localhost'; # need to drop username later
# drop user 'boss'@'localhost';
# ####################
# show grants;

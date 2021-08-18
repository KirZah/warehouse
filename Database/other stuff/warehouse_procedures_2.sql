# DELIMITER //
# use warehouse //
# DROP PROCEDURE IF EXISTS create_mysql_user//
# CREATE PROCEDURE create_mysql_user(IN username VARCHAR(50), IN host VARCHAR(50), IN password VARCHAR(50))
# SQL SECURITY INVOKER
# comment 'creates user'
# BEGIN
# #     DECLARE `host` CHAR(15) DEFAULT '@\'localhost\'';
#     SET username := CONCAT('\'', TRIM(BOTH '\'' FROM username), '\''),
#         host     := CONCAT('@\'', TRIM(BOTH '\'' FROM TRIM(LEADING '@' FROM host)), '\''),
#         password := CONCAT('\'', TRIM(BOTH '\'' FROM password), '\'');
#     SET @`sql` := CONCAT('CREATE USER ', username, host, ' IDENTIFIED BY ', password);
#     PREPARE `stmt` FROM @`sql`;
#     EXECUTE `stmt`;
# END//
# DELIMITER ;

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
# language sql - ?
deterministic # - ?
# SQL SECURITY может принимать два значения - DEFINER или INVOKER
# в случае INVOKER скрипт выполняется с правами пользователя , который её вызвал, а не как в случае с:
# DEFINER - когда скрипт выполняется с правами пользователя указанного в CREATE DEFINER.
comment 'creates user and give him privileges assigned to ROLE'
add_user: BEGIN
    IF in_role IN ('developer', 'administrator', 'boss', 'pc_operator', 'warehouseman', 'salesman') THEN
        BEGIN
            BEGIN
#             SET username := CONCAT('\'', TRIM(BOTH '\'' FROM username), '\''),
#                 host     := CONCAT('\'', TRIM(BOTH '\'' FROM TRIM(LEADING '@' FROM host)), '\''),
#                 password := CONCAT('\'', TRIM(BOTH '\'' FROM password), '\''),
#                 in_role  := CONCAT('\'', TRIM(BOTH '\'' FROM in_role), '\'', '@\'%\'');
#             SET @username_and_host := CONCAT(username, '@', host); # отдельно, т.к. изменения вступают в силу только после завершения SET
#
#             CALL create_mysql_user(username, host, password);
#             GRANT in_role TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#             SET DEFAULT ROLE in_role TO @username_and_host;
#             FLUSH PRIVILEGES;
END;
        SET username := CONCAT('\'', TRIM(BOTH '\'' FROM username), '\''),
            host     := CONCAT('@\'', TRIM(BOTH '\'' FROM TRIM(LEADING '@' FROM host)), '\''), # убрать @ ??
            password := CONCAT('\'', TRIM(BOTH '\'' FROM password), '\''),
            in_role  := CONCAT(TRIM(BOTH '\'' FROM in_role));
#         create_user: BEGIN
#                      SET @`sql` := CONCAT('CREATE USER ', username, host, ' IDENTIFIED BY ', password);
#                      PREPARE `stmt` FROM @`sql`;
#                      EXECUTE `stmt`;
#                      DEALLOCATE PREPARE `stmt`;
#         END;
        grant_role_to_user: BEGIN
#         CALL create_mysql_user(username, host, password);
        SET @`sql` := CONCAT('GRANT ', in_role, '@\'%\' TO ', username, host, ';');
        PREPARE `stmt` FROM @`sql`;
        EXECUTE `stmt`;
        DEALLOCATE PREPARE `stmt`;
        END;
        set_granted_role_as_default: BEGIN
        SET @`sql` := CONCAT('SET DEFAULT ROLE ', in_role, '@\'%\' TO ', username, host, ';');
        PREPARE `stmt` FROM @`sql`;
        EXECUTE `stmt`;
        DEALLOCATE PREPARE `stmt`;
        END;
#         adding_user_to
        END;
    else
        return_error: begin
        #             SET @host = host; USING @host;
        SET @`msg` := CONCAT('FAILED PROCEDURE add_user. Got unknown role \'', in_role, '\'');
        SIGNAL SQLSTATE 'ROLEP' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9999;
        #             SET MESSAGE_TEXT = CONCAT('FAILED PROCEDURE add_user. Got unknown role \'', role, '\''), MYSQL_ERRNO = 1000;
        #             LEAVE add_user;
        end;
    end if;
END//

# https://stackoverflow.com/questions/26015160/deterministic-no-sql-or-reads-sql-data-in-its-declaration-and-binary-logging-i
DROP FUNCTION IF EXISTS get_user_role//
CREATE DEFINER = 'administrator'@'%' FUNCTION get_user_role(username VARCHAR(50), host VARCHAR(50))
RETURNS VARCHAR(50)
SQL SECURITY DEFINER
    READS SQL DATA
comment 'returns user''s role'
get_user_role: BEGIN
    SET username := CONCAT(TRIM(BOTH '\'' FROM username)),
        host     := CONCAT(TRIM(BOTH '\'' FROM TRIM(LEADING '@' FROM host)));

    IF username IN (select User From mysql.user) THEN
        BEGIN
        IF username IN (select TO_USER From mysql.role_edges where TO_USER = username) THEN
            RETURN @role := (select FROM_USER From mysql.role_edges where TO_USER = username);
        else user_not_exist_in_mysql_role_edges_error: begin
            SET @`msg` := CONCAT('User \'', username,'\' doesn''t have any role assigned. (or administrator''s ROLE is powerless...)');
            SIGNAL SQLSTATE 'ROLEF' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9997;
            end;
        end if;
        END;
    else user_not_exist_in_mysql_user_error: begin
            SET @`msg` := CONCAT('User \'', username,'\' doesn''t exist in mysql.User. WHO ARE YOU? (or administrator''s ROLE is powerless...)');
            SIGNAL SQLSTATE 'USERF' SET MESSAGE_TEXT = @msg , MYSQL_ERRNO = 9998;
            end;
    end if;
END//
DELIMITER ;

use warehouse;
CALL add_user('Chyvak88', '%', 'Chyvak88', 'developer');
SELECT get_user_role('Chyvak88', '%');

###################

#     CASE in_role
#         WHEN 'administrator' THEN
#             BEGIN
#             CALL create_mysql_user(username, host, password);
#             GRANT 'administrator' TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#             SET DEFAULT ROLE 'administrator' TO @username_and_host;
#             END;
#         WHEN 'boss' THEN
#             BEGIN
#             CALL create_mysql_user(username, host, password);
#             GRANT 'boss' TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#             SET DEFAULT ROLE 'boss' TO @username_and_host;
#             END;
#         WHEN 'pc_operator' THEN
#             BEGIN
#             CALL create_mysql_user(username, host, password);
#             GRANT 'pc_operator' TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#             SET DEFAULT ROLE 'pc_operator' TO @username_and_host;
#             END;
#         WHEN 'warehouseman' THEN
#             BEGIN
#             CALL create_mysql_user(username, host, password);
#             GRANT 'warehouseman' TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#             SET DEFAULT ROLE 'warehouseman' TO @username_and_host;
#             END;
#         WHEN 'salesman' THEN
#             BEGIN
#             CALL create_mysql_user(username, host, password);
#             GRANT 'salesman' TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#             SET DEFAULT ROLE 'salesman' TO @username_and_host;
#             END;
#         WHEN 'customer' THEN
# #             BEGIN
#             SET @in_role := 'customer';
# #             END;
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
#     SET @got_role := 'customer';
#     select @got_role;

#     CALL create_mysql_user(username, host, password);
#     GRANT @in_role TO @username_and_host; # Access denied; you need (at least one of) the WITH ADMIN, ROLE_ADMIN, SUPER privilege(s) for this operation
#     SET DEFAULT ROLE @in_role TO @username_and_host;
#     FLUSH PRIVILEGES;
    # CALL save_user_role(IN `username` VARCHAR(50), IN `host` VARCHAR(50), IN `role` VARCHAR(50))
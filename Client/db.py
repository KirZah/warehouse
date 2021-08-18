import mysql
import mysql.connector
import mysql.connector.locales.eng
from mysql.connector import Error

from loguru import logger as lg
# lg.dbinfo("Client Started!")
# lg.dberror("lul")

from functions import insert_new_line_symbols, error_to_str, is_iterable
import exceptions

# from enum import Enum
# from collections import namedtuple
from tkinter import messagebox as mb  # while it's not a client connecting to the server app I can use that,
#                                       otherwise I would need to create my own exceptions and use them in client
#                                       to show errors


class DbTables:
    suppliers = "suppliers"
    supplies = "supplies"
    goods_supplies = "goods_supplies"
    catalog = "catalog"
    goods = "goods"
    storage = "storage"
    goods_shipments = "goods_shipments"
    shipments = "shipments"
    customers = "customers"


class DbRoles:
    # root = "root"
    developer = "developer"
    administrator = "administrator"
    director = "director"
    boss = "boss"
    pc_operator = "pc_operator"
    warehouseman = "warehouseman"
    salesman = "salesman"
    # customer = "customer"


class Connection:
    def __init__(self, host, user, password, database):
        lg.info("#CREATING Connection class")
        self._connection = None
        self._host = host
        self._username = user
        self._password = password
        self._database = database
        self._role = 'Unknown role'

    def get_connection(self):
        return self._connection

    def get_host(self):
        return self._host

    def get_username(self):
        return self._username

    def get_password(self):
        return self._password

    def get_database(self):
        return self._database

    def get_role(self):
        return self._role

    def try_to_connect(self):  # пока что тоже самое, что и connect()
        self.connect()

    def connect(self):  # rename to "check ability to connect"
        lg.info(f"#connect")
        try:
            self._connection = mysql.connector.connect(host=self._host,
                                                       user=self._username,
                                                       password=self._password,
                                                       database=self._database,
                                                       allow_local_infile=True
                                                       # auth_plugin='mysql_native_password'
                                                       )
            if self._connection.is_connected():
                db_info = self._connection.get_server_info()
                lg.dbinfo(f"Connected to MySQL Server version {db_info}")
                cursor = self._connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                lg.dbinfo(f"Database '{record[0]}' selected")
                cursor.execute(f"SELECT get_user_role('{self._username}', '{self._host}');")
                role = cursor.fetchone()[0]
                lg.dbinfo(f"Got user role = '{role}'")
                self._role = role
                cursor.close()

        except Error as e:
            lg.dberror(f"Error code: {e.errno}")  # error number
            lg.dberror(f"SQLSTATE value: {e.sqlstate}")  # SQLSTATE value
            lg.dberror(f"Error message: {e.msg}")  # error message
            lg.dberror(f"Error: {e}")  # error number, sqlstate, msg values
            # s = str(e)
            # lg.error(f"Error: {s}")  # error number, sqlstate, msg values
            return e
        else:
            lg.dbinfo("you've successfully connected")
            self.disconnect()
            return None

    def reconnect(self):
        lg.dbinfo(f"#reconnect")
        try:
            self._connection.reconnect(attempts=1, delay=0)
        except Error as e:
            lg.dberror(f"Error: {e}")  # error number, sqlstate, msg values
            return e
        else:
            # lg.dbinfo("you've successfully reconnected")
            return None

    def disconnect(self):
        lg.dbinfo("#disconnect")
        if self._connection is None:
            lg.error("There's no connection to close")
            return -1
        else:
            # try:
            self._connection.close()
            # except Error as e:
            #     lg.dberror("Error: {e}")  # error number, sqlstate, msg values
            #     return e
            # else:
            #     lg.dbinfo("you've successfully disconnected")
            #     return None

    def is_connected(self):
        # lg.info("#is_connected")
        if self._connection is None:
            # lg.debug("__connection is None")
            return False
        else:
            # lg.debug(f"self.__connection.is_connected() = {self.__connection.is_connected()}")
            return self._connection.is_connected()

def run_select_query(conn1, query, parameters=()):
    lg.info("#run_select_query")
    # lg.debug(f"BEFORE CONNECTING: connection = {conn1.get_connection()}")
    conn1.reconnect()
    # lg.debug(f"AFTER  CONNECTING: connection = {conn1.get_connection()}")
    if conn1.is_connected():
        try:
            cursor = conn1.get_connection().cursor()
            # lg.info(f"cursor={cursor}")
            cursor.execute(query, parameters)
            query_result = cursor.fetchall()
            cursor.close()
            conn1.disconnect()

        except Error as e:
            # lg.error(f"Error code: {e.errno}")  # error number
            # print("SQLSTATE value:", e.sqlstate)  # SQLSTATE value
            # print("Error message:", e.msg)  # error message
            lg.dberror(f"Error: {e}")  # errno, sqlstate, msg values
            # s = str(e)
            # print("Error:", s)  # errno, sqlstate, msg values
            conn1.disconnect()
            return e
        else:
            lg.dbinfo("Successfully ran select query")
            return query_result
    else:
        lg.dberror(f"Could not reconnect!")
        # raise exceptions.DBConnectionError("Could not reconnect!")
        return -1


def run_commit_query(conn1, query, parameters=()):
    lg.info("#run_commit_query")
    # lg.debug(f"BEFORE CONNECTING: connection = {conn1.get_connection()}")
    conn1.reconnect()
    # lg.debug(f"AFTER  CONNECTING: connection = {conn1.get_connection()}")
    if conn1.is_connected():
        try:
            cursor = conn1.get_connection().cursor()
            cursor.execute(query, parameters)

        except Error as e:
            # lg.error(f"Error code: {e.errno}")  # error number
            lg.dberror(f"Error: {e}")  # errno, sqlstate, msg values
            # conn1.get_connection().rollback()
            conn1.disconnect()
            return e
        else:
            lg.dbinfo("Successfully ran change query")
            conn1.get_connection().commit()
            cursor.close()
            conn1.disconnect()
            return None
    else:
        lg.dberror(f"Could not reconnect!")
        # raise exceptions.DBConnectionError("Could not reconnect!")
        return -1


def reconnect_raise(conn1):
    lg.info("#reconnect_raise")
    # lg.debug(f"BEFORE CONNECTING: connection = {conn1.get_connection()}")
    if not(conn1.reconnect() is None):
        raise exceptions.DBConnectionError("Could not reconnect!")
    # lg.debug(f"AFTER  CONNECTING: connection = {conn1.get_connection()}")

def run_commit_query_raise(conn1, query, parameters=()):
    lg.info("#run_commit_query_raise")
    if conn1.is_connected():
        try:
            cursor = conn1.get_connection().cursor()
            cursor.execute(query, parameters)

        except Error as e:
            # lg.error(f"Error code: {e.errno}")  # error number
            lg.dberror(f"Error: {e}")  # errno, sqlstate, msg values
            # conn1.get_connection().rollback()
            raise exceptions.DBError(error_to_str(e))
            # return e
        else:
            lg.dbinfo("Success #run_commit_query_raise")
            conn1.get_connection().commit()
            cursor.close()
            return None
    else:
        lg.dberror(f"No connection!")
        raise exceptions.DBConnectionError("No connection!")
        # return -1



def add_records_to_cmb(conn1, query, parameters, cmb):
    lg.info("#add_records_to_cmb")
    db_rows = run_select_query(conn1, query, parameters)
    lg.debug(f'db_rows={db_rows}')

    if db_rows.__class__ is int:
        lg.dberror(f"Could not reconnect!")
        mb.showerror(title="Connection Error!", message="Could not reconnect!")
    elif isinstance(db_rows, Error):
        # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
        lg.dberror(error_to_str(db_rows))
        mb.showerror(title="Database Error",
                     message=insert_new_line_symbols(error_to_str(db_rows)))
    elif db_rows == []:
        lg.dbinfo("Recieved empty array (There's no similar records)")

    elif is_iterable(db_rows):
        lg.debug('Recieved iterable object')
        for row in db_rows:
            # print(f'row={row}')
            # print(f"row[0]={row[0]}")
            # self.cmb_customer_name.insert("", 0, values=[row[0]])
            cmb['values'] = (*cmb['values'], row[0])  # adding rows to cmb
            # lg.info(f"row={row}")
    elif db_rows is None:
        lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')
    return


def get_next_id(conn1, table_name, lbl_notify):
    lg.info(f"#get_next_id ({table_name})")
    query = """ select MAX(id)+1 from """ + table_name
    parameters = ()
    db_rows = run_select_query(conn1, query, parameters)
    if db_rows.__class__ is int:
        lg.error(f"Didn't get id from database!")
        lg.dberror(f"Could not reconnect to database!")
        mb.showerror(title="Connection Error!", message="Could not reconnect!")
        lbl_notify.config(fg='red', text="Could not reconnect to database!")
        lbl_notify.grid()
        return "Could not reconnect to database!"
    elif isinstance(db_rows, Error):
        lg.dberror(error_to_str(db_rows))
        lbl_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
        lbl_notify.grid()
        return None
    elif db_rows[0][0] is None:
        lg.debug("Table is empty")
        return 1
    elif is_iterable(db_rows):
        next_id = db_rows[0][0]
        lg.debug(f"next id for '{table_name}' is {next_id}")
        return next_id
    else:
        lg.critical("UNKNOWN return from DB!")


def delete_record(conn1, table_name, row_id, attribute_name):
    lg.info(f"#delete_record from {table_name} where '{attribute_name}'={row_id}")
    query = f"""    DELETE FROM {table_name} 
                    WHERE {attribute_name} = {row_id}
            """
    parameters = ()

    db_rows = run_commit_query(conn1, query, parameters)
    if db_rows == -1:
        lg.dberror(f"Could not reconnect!")
        mb.showerror(title="Connection Error!", message="Could not reconnect!")
    elif isinstance(db_rows, Error):
        # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
        if db_rows.errno == 1451:
            lg.dberror(f"You CANNOT delete row #{row_id} "
                       f"from table '{table_name}'")
            mb.showerror(title="Database Error",
                         message=f"You CANNOT delete row #{row_id} "
                         f"from table '{table_name}', cause rows in "
                         f"other tables rely on it")
        else:
            error_msg = error_to_str(db_rows)
            lg.dberror(error_msg)
            mb.showerror(title="Database Error",
                         message=insert_new_line_symbols(error_msg))
    elif db_rows is None:
        lg.dbinfo(f"record deleted from {table_name} if '{attribute_name}'={row_id}")
        return 0
    elif db_rows == []:
        lg.debug("Recieved empty array")
    elif is_iterable(db_rows):
        lg.debug('Recieved iterable object')
    else:
        lg.critical("received smth else")
    return None


def get_primary_attribute(table_name):
    if (table_name == 'goods' or table_name == 'catalog'
            or table_name == 'suppliers' or table_name == 'supplies'
            or table_name == 'customers' or table_name == 'shipments'):
        attribute_name = 'id'
    elif (table_name == 'storage' or table_name == 'supplies_goods'
            or table_name == 'shipments_goods'):
        attribute_name = 'goods_id'
    else:
        lg.debug(f"Unknown table_name={table_name}")
        return None
    return attribute_name


def return_sold_package(conn1, row_id):
    lg.info(f"#return_sold_package(in_goods_id={row_id})")
    query = f"""call return_sold_package({row_id})"""
    parameters = ()

    db_rows = run_commit_query(conn1, query, parameters)
    if db_rows == -1:
        lg.dberror(f"Could not reconnect!")
        mb.showerror(title="Connection Error!", message="Could not reconnect!")
    elif isinstance(db_rows, Error):
        error_msg = error_to_str(db_rows)
        lg.dberror(error_msg)
        mb.showerror(title="Database Error", message=insert_new_line_symbols(error_msg))
    elif db_rows is None:
        lg.dbinfo(f"#return_sold_package(in_goods_id={row_id}) - SUCCESS")
    else:
        lg.critical("received smth else")
    return None




def delete_table_records(conn1, table_name, row_id):
    lg.info(f"#delete_record #{row_id} from {table_name}")
    # MAYBE CHANGE SMTH IN DB
    attribute_name = get_primary_attribute(table_name)
    if table_name == "storage":
        delete_record(conn1, table_name, row_id, attribute_name)
    elif table_name == DbTables.goods:
        if delete_record(conn1, DbTables.goods, row_id, attribute_name) != 0:
            return None
    elif table_name == "catalog":
        lg.debug("YOU DON'T WANT TO DELETE FROM HERE!")
        # lg.debug("delete all linked products first!")
        # delete_record(conn1, table_name, row_id, attribute_name)
        yes = mb.askyesno("Are you sure?",
                          f"Are you sure you want to delete row #{row_id}? "
                          f"(It's used ONLY when there've been an Error before. "
                          f"If there are any goods linked to this row you won't be "
                          f"able to delete anyway... so... I'm just asking :^))")
        if yes:
            delete_record(conn1, table_name, row_id, attribute_name)
        return 1
    elif table_name == "suppliers":
        lg.debug("delete all linked supplies first!")
        delete_record(conn1, table_name, row_id, attribute_name)
    elif table_name == "supplies":
        lg.debug("delete all linked goods_supplies first!")
        delete_record(conn1, table_name, row_id, attribute_name)
    elif table_name == "goods_supplies":
        # lg.debug("delete linked product first!")
        delete_record(conn1, table_name, row_id, attribute_name)
    elif table_name == "customers":
        lg.debug("delete all linked shipments first!")
        delete_record(conn1, table_name, row_id, attribute_name)
    elif table_name == "shipments":
        lg.debug("delete all linked goods_shipments first!")
        delete_record(conn1, table_name, row_id, attribute_name)
    elif table_name == DbTables.goods_shipments:
        return_sold_package(conn1, row_id)
    else:
        lg.debug("UNKNOWN TABLE (don't know how to delete)")
    return 0


def create_temporary_tables(conn1):
    lg.dbinfo(f"#create_temporary_tables")
    query = """ CALL create_temporary_tables()"""
    run_commit_query_raise(conn1, query)
    # lg.dbinfo(f"#create_temporary_tables - success")


def load_file_to_tmp_table(conn1, archive_number, table_name):
    lg.dbinfo(f"#load_file_to_tmp_table (table_name='{table_name}')")
    query = f"""
        LOAD DATA
            LOCAL
            INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/warehouse/archive/{archive_number}_{table_name}.csv'
            INTO TABLE warehouse.tmp_{table_name}
            FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
            LINES TERMINATED BY '\\r\\n';"""
    run_commit_query_raise(conn1, query)
    # lg.dbinfo(f"#load_file_to_tmp_table (table_name='{table_name}') - success ")


def drop_temporary_tables(conn1):
    lg.dbinfo("#drop_temporary_tables")
    query = """ CALL drop_temporary_tables()"""
    run_commit_query_raise(conn1, query)
    # lg.dbinfo("#drop_temporary_tables - success")


def truncate_tables(conn1):
    lg.dbinfo("#truncate_tables")
    query = f""" call truncate_tables();"""
    run_commit_query_raise(conn1, query)
    # lg.dbinfo("#truncate_tables - success")


def copy_tables_from_tmp_to_warehouse(conn1):
    lg.dbinfo("#copy_tables_from_tmp_to_warehouse")
    query = f""" call copy_tables_from_tmp_to_warehouse();"""
    run_commit_query_raise(conn1, query)
    # lg.dbinfo("#copy_tables_from_tmp_to_warehouse - success")


def copy_table_from_tmp_to_warehouse(conn1, table_name):
    lg.dbinfo("#copy_table_from_tmp_to_warehouse")
    query = f""" INSERT INTO warehouse.{table_name} SELECT * FROM tmp_{table_name} FOR UPDATE; """
    run_commit_query_raise(conn1, query)
    # lg.dbinfo("#copy_table_from_tmp_to_warehouse - success")


def load_archive(conn1, archive_number):
    lg.dbinfo("#load_archive")

    def load_files_to_tmp_tables(conn1, archive_number):
        lg.dbinfo("#load_files_to_tmp_tables")
        load_file_to_tmp_table(conn1, archive_number, 'suppliers')
        load_file_to_tmp_table(conn1, archive_number, 'supplies')
        load_file_to_tmp_table(conn1, archive_number, 'catalog')
        load_file_to_tmp_table(conn1, archive_number, 'package_states')
        load_file_to_tmp_table(conn1, archive_number, 'goods')
        load_file_to_tmp_table(conn1, archive_number, 'goods_supplies')
        load_file_to_tmp_table(conn1, archive_number, 'storage')
        load_file_to_tmp_table(conn1, archive_number, 'customers')
        load_file_to_tmp_table(conn1, archive_number, 'shipments')
        load_file_to_tmp_table(conn1, archive_number, 'goods_shipments')
        lg.dbinfo("#load_files_to_tmp_tables - success")

    reconnect_raise(conn1)
    # drop_temporary_tables(conn1)
    # проверить не запущена ли архивация или другой load from file процесс
    create_temporary_tables(conn1)
    load_files_to_tmp_tables(conn1, archive_number)
    # <--- check if files are correct should be here
    truncate_tables(conn1)
    # lock tables here
    copy_tables_from_tmp_to_warehouse(conn1)
    # unlock tables here
    drop_temporary_tables(conn1)
    lg.dbinfo("#load_archive - SUCCESS")
    conn1.disconnect()


# load_file_to_tmp_table()

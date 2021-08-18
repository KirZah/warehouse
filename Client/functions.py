from tkinter import TclError, Button
from loguru import logger as lg
from mysql.connector import Error
from datetime import datetime, timedelta
from tkinter import messagebox as mb


# from db import DbTables
def add_days_to_date(date, days):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    lg.debug(f"date={date}")
    lg.debug(f"days={days}")
    if days == '-' or days is None or days == 'None':
        return 'None'
    return str((date_obj + timedelta(days=int(days))).date())


# Проверки
def is_iterable(obj):
    try:
        iter(obj)
    except IndexError:  # Exception
        return False
    else:
        return True


def is_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        # raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return False
    else:
        return True



# string functions
def insert_new_line_symbols(str, max_chars=35, gap=16):
    s = ''
    i = 0
    for c in str:
        i += 1
        if c == '\n':
            i = 0
        elif i >= max_chars:  # if went too far
            s += c + '\n'
            i = 0
        elif i > max_chars-gap and c == ' ':  # if in gap
            s += '\n'
            i = 0
        else:
            s += c
    return s


def error_to_str(error) -> str:

    def parse_apostrophes(msg, apostrophe_num, char='\''):
        start = 0
        end = len(msg)
        for i in range(apostrophe_num):
            start = msg.find(char, start, end) + 1
        end = msg.find(char, start, end)
        return msg[start:end]
    def get_fisrt_word(msg):
        i = 0
        for c in msg:
            i += 1
            if not(c.isalpha()):
                break
        return msg[0:i]

    # s = errno_to_str(error.errno)
    errno = error.errno
    if errno is None:
        lg.debug("YOU PASSED 'NONE' TO FUNCTION 'error_to_str'")
        return "YOU PASSED 'NONE' TO FUNCTION 'error_to_str'"
    elif errno == 2003:
        # 2003 (None): Can't connect to MySQL server on 'warehouse:3306' (11001 getaddrinfo failed)
        address_info = parse_apostrophes(error.msg, 1)
        lg.error(f"ERROR (MySQL.Connector): Can't connect to MySQL server on '{address_info}'!")
        return f"Can't connect to MySQL server on '{address_info}'!"
    elif errno == 2005:
        lg.error('ERROR (MySQL.Connector): Host not found!')
        return 'Host not found!'
    elif errno == 1044:
        username = parse_apostrophes(error.msg, 1)
        host = parse_apostrophes(error.msg, 3)
        database = parse_apostrophes(error.msg, 5)
        lg.error(f"ERROR (MySQL.Connector): "
                 f"Error: 1044 (42000): Access denied for user '{username}'@'{host}' to database '{database}'")
        return f"Access denied for user '{username}' to database '{database}'"
    elif errno == 1045:  # 1045 (28000)
        lg.error('ERROR (MySQL.Connector): Incorrect User or Password!')
        return 'Incorrect User or Password!'
    elif errno == 1049:
        lg.error('ERROR (MySQL.Connector): Database not found!')
        return 'Database not found!'
    elif errno == 1146:  # 1146 (42S02)
        lg.error("ERROR (MySQL.Connector): Table doesn't exist!")
        return "Table doesn't exist!"
    elif errno == 1064:  # 1064 (42000)
        lg.error("ERROR (MySQL.Connector): You have an error in your SQL syntax! "
                 "(Tell the programmer that he's stupid)")
        return "You have an error in your SQL syntax! (Tell the programmer)"
    elif errno == 1054:  # 1054 (42S22)
        lg.error("ERROR (MySQL.Connector): You asked for Unknown column!")
        return "You asked for Unknown column!"
    elif errno == 1062:  # 1062 (23000)
        column_name = parse_apostrophes(error.msg, 3)
        lg.error(f"ERROR (MySQL.Connector): Duplicate entry for '{column_name}'!")
        return f"Duplicate entry for '{column_name}'!"
    elif errno == 1406:  # 1046 (22001)
        # lg.debug(f"error.msg={error.msg}")
        column_name = parse_apostrophes(error.msg, 1)
        lg.error(f"ERROR (MySQL.Connector):Data too long for '{column_name}'!")
        return f"Data too long for '{column_name}'!"
    elif errno == 1048:  # 1048 (23000)
        column_name = parse_apostrophes(error.msg, 1)
        lg.error(f"ERROR (MySQL.Connector): Column '{column_name}' cannot be null!")
        return f"Column '{column_name}' cannot be null!"
    elif errno == 1292:  # 1292 (22007)
        column_name = parse_apostrophes(error.msg, 3)
        lg.error(f"ERROR (MySQL.Connector): Incorrect date value for column '{column_name}'!")
        return f"Incorrect date value for column '{column_name}'!"
    elif errno == 1366:  # 1366 (HY000): Incorrect integer value: 'None' for column 'shelf_life' at row 1
        column_name = parse_apostrophes(error.msg, 3)
        lg.error(f"ERROR (MySQL.Connector): Incorrect integer value for column '{column_name}'!")
        if column_name == 'shelf_life':
            return f"Column '{column_name}' takes only integer numbers and '-' (for infinite)!"
        else:
            return f"Column '{column_name}' takes only integer numbers!"
    elif errno == 1264:  # 1264 (22003): Out of range value for column 'shelf_life'
        column_name = parse_apostrophes(error.msg, 1)
        lg.error(f"Out of range value for column '{column_name}'!")
        return f"Out of range value for column '{column_name}'!"
    elif errno == 1452:
        # 1452 (23000): Cannot add or update a child row: a foreign key constraint fails
        # (`warehouse`.`goods_shipments`, CONSTRAINT `goods_shipments_shipments_id_fk`
        # FOREIGN KEY (`shipments_id`) REFERENCES `shipments` (`id`))
        lg.error(f"ERROR (MySQL.Connector): Cannot add or update a child row!")
        return f"Cannot add or update a child row!"
    elif errno == 1451:
        # Error: 1451 (23000): Cannot delete or update a parent row: a foreign key
        # constraint fails (`warehouse`.`supplies`,
        # CONSTRAINT `supplies_suppliers_id_fk` FOREIGN KEY (`suppliers_id`)
        # REFERENCES `suppliers` (`id`))
        lg.error(f"ERROR (MySQL.Connector): Cannot delete or update a parent row!")
        return f"Cannot delete or update a parent row!"
    elif errno == 1142:  # 1142 (42000)
        # Error: 1142 (42000): SELECT command denied to user 'newuser'@'localhost' for table 'customers'
        username = parse_apostrophes(error.msg, 1)
        table = parse_apostrophes(error.msg, 5)
        cmd = get_fisrt_word(error.msg)
        lg.error(f'ERROR (MySQL): {cmd} command denied to user "{username}" for table "{table}"!')
        return f'ERROR (MySQL): {cmd} command denied to user "{username}" for table "{table}"!'

    elif errno == 1370:  # 1370 (42000)
        # Error: 1370 (42000): execute command denied to user 'warehouseman'@'localhost' for routine
        # 'warehouse.get_user_role'
        username = parse_apostrophes(error.msg, 1)
        host = parse_apostrophes(error.msg, 3)
        routine = parse_apostrophes(error.msg, 5)
        lg.error(f"ERROR (MySQL): execute command denied to user '{username}'@'{host}' for routine '{routine}'")
        return f"ERROR (MySQL): execute command denied to user '{username}'@'{host}' for routine '{routine}'"

    elif errno == 2068:  # 2068 (HY000)
        # Error: 2068 (HY000): LOAD DATA LOCAL INFILE file request rejected due to restrictions on access.
        lg.error(f"ERROR (MySQL): LOAD DATA LOCAL INFILE file request rejected due to restrictions on access.")
        return f"ERROR (MySQL): LOAD DATA LOCAL INFILE file request rejected due to restrictions on access."


    elif errno == 1701:  # 1701 (42000)
        # Error: 1701 (42000): Cannot truncate a table referenced in a
        # foreign key constraint (`warehouse`.`supplies`, CONSTRAINT `supplies_suppliers_id_fk`)
        database = parse_apostrophes(error.msg, 1, '`')
        table_name = parse_apostrophes(error.msg, 3, '`')
        foreign_key_name = parse_apostrophes(error.msg, 5, '`')
        lg.error(f"ERROR (MySQL): Cannot truncate a table referenced in a "
                 f"foreign key constraint (`{database}`.`{table_name}`, CONSTRAINT `{foreign_key_name}`)")
        return f"ERROR (MySQL): Cannot truncate a table referenced by `{foreign_key_name}`"

    # ERRORS DEFINED BY ME IN MYSQL ############
    elif errno == 9980:
        # Error message: User 'Chyvak88'@'localhost' doesn't exist (there's no record in 'mysql.User' table).
        username = parse_apostrophes(error.msg, 1)
        host = parse_apostrophes(error.msg, 3)
        lg.error(f"ERROR (MySQL - Chyvak88): User '{username}'@'{host}' doesn't exist "
                 f"(there's no record in 'mysql.User' table).")
        return f"ERROR: User '{username}'@'{host}' doesn't exist."

    elif errno == 9981:
        # Error: 9981 (ROLEF): User 'warehouseman'@'localhost' doesn't have any role assigned
        # (there's no record in 'mysql.role_edges' table).
        username = parse_apostrophes(error.msg, 1)
        host = parse_apostrophes(error.msg, 3)
        lg.error(f"ERROR (MySQL - Chyvak88): User '{username}'@'{host}' doesn't have any role assigned "
                 f"(there's no record in 'mysql.role_edges' table).")
        return f"ERROR: User '{username}'@'{host}' doesn't exist."

    elif errno == 9960:
        # Error: 9960 (ARHIV): Needed archive_number='1' is used already
        # (you might have added some files but not all that needed)
        archive_number = parse_apostrophes(error.msg, 1)
        lg.error(f"ERROR (MySQL - Chyvak88): Needed archive_number='{archive_number}' is used already "
                 f"(you might have added some files but not all that needed)")
        return f"ERROR: archive_number='{archive_number}' is used already. " \
               f"(you might have added some files but not all that needed)"

    elif errno == 9940:
        # Error: 9940 (STATE): Package #'2' has incorrect state for operation 'SELL PACKAGE'
        package_num = parse_apostrophes(error.msg, 1)
        operation = parse_apostrophes(error.msg, 3)
        lg.error(f"ERROR (MySQL - Chyvak88): Package #'{package_num}' has incorrect state for operation '{operation}'")
        return f"ERROR: Package #{package_num} has incorrect state for operation '{operation}'"
    # ERRORS DEFINED BY ME IN MYSQL ^^^^^^^^^^^^
    else:
        lg.error('ERROR (MySQL.Connector): Unknown (for me) Error!')
        return 'Unknown Error!'


# Treeview
def treeview_sort_column(treeview_obj, col, reverse):
    record_list = [(treeview_obj.set(k, col), k) for k in treeview_obj.get_children('')]
    if col in {'id', 'Package id', 'State'}:  # Если столбец из int
        record_list.sort(key=lambda t: int(t[0]), reverse=reverse)
        for index, (val, k) in enumerate(record_list):
            treeview_obj.move(k, '', index)
        treeview_obj.heading(col, command=lambda:  # reverse sort next time
                             treeview_sort_column(treeview_obj, col, not reverse))

    elif col == 'Price':  # Если столбец из float
        record_list.sort(key=lambda t: float(t[0]), reverse=reverse)
        for index, (val, k) in enumerate(record_list):
            treeview_obj.move(k, '', index)
        treeview_obj.heading(col, command=lambda:  # reverse sort next time
                             treeview_sort_column(treeview_obj, col, not reverse))
    else:  # остальные случаи
        record_list.sort(reverse=reverse)
        # rearrange items in sorted positions
        for index, (val, k) in enumerate(record_list):
            treeview_obj.move(k, '', index)
            # print(f'index={index};\t val={val};\t k={k};\t record_list={record_list};')
        treeview_obj.heading(col, command=lambda:  # reverse sort next time
                             treeview_sort_column(treeview_obj, col, not reverse))


def get_near_item(treeview, item):
    near_item = treeview.next(item)
    if near_item == '':
        near_item = treeview.prev(item)
    return near_item



# Обращение к MainWindow (Treeview)
def update_treeview(main_window):

    def get_treeview_selected_id(tree):
        selected_item = tree.selection()
        # lg.debug(f"selected_item={selected_item}")
        if selected_item == ():
            return None
        else:
            selected_item = selected_item[0]
            # lg.debug(f"selected_item={selected_item}")
            selected_id = tree.item(selected_item, "values")[0]
            # lg.debug(f"selected_id={selected_id}")
            return selected_id

    def set_treeview_selection(tree, selection_id):
        if not(selection_id is None):
            lg.debug(f"selection_id={selection_id}")
            children = tree.get_children()
            # tree.update_idletasks()
            for child in children:
                # lg.debug(f'id={tree.item(child, "values")[0]}')
                if int(tree.item(child, "values")[0]) == int(selection_id):
                    lg.debug(f"selection_id={selection_id} (inside)")
                    lg.debug(f"child={child}")
                    # tree.selection_remove(child)
                    # tree.update_idletasks()
                    tree.selection_set(child)
                    tree.see(child)
                    tree.focus(child)
                    # tree.update_idletasks()
                    break
        # else:   # потому что какого-то чёрта он стал останавливаться,
        #         # не доходя до первого элемента
        #     if len(children) > 0:
        #         child = children[1]
        #         # tree.selection_set(child)
        #         tree.see(child)
        #         # tree.focus(child)

    def press_chosen_button():
        # lg.debug(f'main_window.btn_showgoods["state"] = {main_window.btn_showgoods["state"]}')
        for child in main_window.frame_top.winfo_children():
            # lg.info(f"child={child}")
            if isinstance(child, Button):
                # lg.debug(f'main_window.child["state"] = {child["state"]}')
                if child["state"] == "disabled":
                    child["state"] = "normal"
                    child.invoke()
                    child["state"] = "disabled"
                    break

    lg.info("#update_treeview")
    selected_id = get_treeview_selected_id(main_window.tree)
    press_chosen_button()
    set_treeview_selection(main_window.tree, selected_id)


# window functions
def on_closing(window):  # maybe i should pass conn1 here
    #                 Upd: (no need cause I return conn1 only in ConnectionWindow)
    lg.info('#on_closing')
    # update_treeview(window.master)
    window.destroy()


def set_active(window):
    window.lift()
    window.focus_force()
    window.grab_set()
    # self.grab_release()


def set_parent_window_req_size(*frames, **kwargs):  # Считает frames в окне и сам их упаковывает (но пока не надо)
    lg.info("#set_parent_window_req_size")
    # Setting defaults
    resizeable = (0, 1)
    notifyspace = 70

    # Обработка kwargs
    kwargs_able = ("resizeable", "notifyspace")
    for arg in kwargs:
        lg.debug(f"arg = {arg}")
        if not (arg in kwargs_able):
            # CHECKING Error kwargs
            kwargs_able_str = ""
            i = 0
            while i + 1 < len(kwargs_able):
                kwargs_able_str = kwargs_able_str + ' -' + kwargs_able[i] + ','
                i += 1
            else:
                kwargs_able_str = kwargs_able_str + ' or -' + kwargs_able[i]
                raise TclError(f'Bad option: "-{arg}": must be{kwargs_able_str}')
        # Reading kwargs
        if arg == "resizeable":
            resizeable = kwargs[arg]
        elif arg == "notifyspace":
            notifyspace = kwargs[arg]

    width = 0
    height_max = 0
    for frame in frames:
        frame.update_idletasks()
        width += frame.winfo_reqwidth()
        height = frame.winfo_reqheight() + notifyspace
        lg.debug(f"width={width}")
        lg.debug(f"height={height}")
        if height > height_max:
            height_max = height
        # size = (frame.winfo_reqwidth() + width, frame.winfo_reqheight() + 50)
        # frame.parent.minsize(*size)
        # frame.parent.maxsize(*size)
        frame.master.minsize(width, height_max)
        # frame.parent.maxsize(width, height_max)
        frame.pack_propagate(0)  # Запретить виджетам изменять размер frame
        frame.master.resizable(*resizeable)


def place_tk_to_screen_center(window):
    lg.info("#place_tk_to_screen_center")
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    window.geometry(str(window_width) + 'x' + str(window_height))

    position_x = int(window.winfo_screenwidth() / 2 - window_width / 2)
    task_bar_height = 50  # высота панели задач
    window_cap_height = 30  # высота шапки окна
    window_height = window_height + window_cap_height + task_bar_height
    position_y = int((window.winfo_screenheight() - window_height) / 2)
    # lg.debug(f"tk_obj.__class__ = {window.__class__}")
    # lg.debug(f"tk_obj.wm_geometry() = {window.wm_geometry()}")
    # lg.info("position_x=", position_x, ";   position_y =", position_y)
    window.geometry("+{}+{}".format(position_x, position_y))  # Change window position


def place_window(window, *frames, **kwargs):
    set_parent_window_req_size(*frames, **kwargs)
    place_tk_to_screen_center(window)
    set_active(window)



# Validation
def on_validate_name(d, i, P, s, S, v, V, W, self=None):
    lg.info("#onValidate_product")
    # print("end", "\n\nOnValidate:")
    # print("end", f"d={d} - Type of action (1=insert, 0=delete, -1 for others)")
    # print("end", f"i={i} - index of char string to be inserted/deleted, or -1")
    # print("end", f"P={P} - value of the entry if the edit is allowed")
    # print("end", f"s={s} - value of entry prior to editing")
    # print("end", f"S={S} - the text string being inserted or deleted, if any")
    # print("end", f"v={v} - the type of validation that is currently set")
    # print("end", f"V={V} - the type of validation that triggered the callback (key, focusin, focusout, forced)")
    # print("end", f"W={W} - the tk name of the widget")

    # def run_func():
    #     if not(self is None):
    #         self.search_similar_product_name()

    lg.debug(f"func={self}")
    lg.debug(f"str={str(self)}")
    if '-1' == d:
        lg.debug("other action")
        # run_func()
        return True
    elif '0' == d:
        lg.debug("delete action")
        # run_func()
        return True
    else:
        lg.debug("insert action")

    if (S == '_') or (S == '%'):
        # self.bell()
        return False
    elif ('_' in P) or ('%' in P):
        # self.bell()
        return False
    else:
        # if self.btn_product_exists['state'] == 'disabled':
        #     self.searching_similar_product(P)
        # run_func()
        return True


def on_validate_date(d, i, P, s, S, v, V, W):
    lg.info("#onValidate_date")
    # lg.debug(f"\n\nOnValidate:")
    # lg.debug(f"d={d} - Type of action (1=insert, 0=delete, -1 for others)")
    # lg.debug(f"i={i} - index of char string to be inserted/deleted, or -1")
    # lg.debug(f"P={P} - value of the entry if the edit is allowed")
    lg.debug(f"s={s} - value of entry prior to editing")
    # lg.debug(f"S={S} - the text string being inserted or deleted, if any")
    # lg.debug(f"v={v} - the type of validation that is currently set")
    # lg.debug(f"V={V} - the type of validation that triggered the callback (key, focusin, focusout, forced)")
    # lg.debug(f"W={W} - the tk name of the widget")

    def count_dashes(str):
        k = 0
        pos = -1
        for n, c in enumerate(str):
            # lg.info(f"c={c}")
            if c == '-':
                k += 1
                pos = n
        return k, pos  # amount, last dash pos

    def count_numbers_after_dashes(str):
        # lg.debug(f"str='{str}'")
        i = 0
        for k in str:
            i += 1
        # lg.debug(f"i={i}")
        return i  # amount

    # lg.error("&&&")
    # lg.error(f"d={d}")
    # lg.error(f"d.__class__={d.__class__}")
    if '-1' == d:
        lg.debug("other action")
        return True
    if '0' == d:
        lg.debug("delete action")
        return True
    else:
        lg.debug("insert action")
        if not(S == '-') and not(S.isnumeric()):
            # self.bell()
            return False
        else:
            if S.isnumeric():
                dashes_amount, last_dash_pos = count_dashes(P)
                # lg.debug(f"P='{P}'")
                # lg.debug(f"last_dash_pos='{last_dash_pos}'")
                # lg.debug(f"P[last_dash_pos:]='{P[last_dash_pos+1:]}'")
                number_after_dashes = count_numbers_after_dashes(P[last_dash_pos+1:])
                # lg.debug(f"number_after_dashes = {number_after_dashes}")

                #  checking for correct work
                if dashes_amount == 0 and number_after_dashes > 4 or \
                        (dashes_amount == 1 or dashes_amount == 2) and number_after_dashes > 2:  #  or \
                        # s == '000' and S == '0':  # dashes_amount > 0 and number_after_dashes == 1 and S == '0' or \
                    # self.bell()
                    return False
                else:
                    return True
            elif S == '-':
                s_len = len(s)
                dash1_pos = s.find("-", 0, s_len)
                # lg.debug(f"n1_end={dash1_pos}")
                if (dash1_pos < s_len) and (dash1_pos != -1):
                    dash2_pos = s.find("-", dash1_pos + 1, s_len)
                    # lg.debug(f"n2_end={dash2_pos}")
                    if dash2_pos != -1:
                        # lg.debug(f"dash2_pos != 0")
                        # self.bell()
                        return False
            return True


def on_validate_naturalnumber(d, i, P, s, S, v, V, W):
    lg.info("#onValidate_product")
    # print("end", "\n\nOnValidate:")
    # print("end", f"d={d} - Type of action (1=insert, 0=delete, -1 for others)")
    # print("end", f"i={i} - index of char string to be inserted/deleted, or -1")
    # print("end", f"P={P} - value of the entry if the edit is allowed")
    # print("end", f"s={s} - value of entry prior to editing")
    # print("end", f"S={S} - the text string being inserted or deleted, if any")
    # print("end", f"v={v} - the type of validation that is currently set")
    # print("end", f"V={V} - the type of validation that triggered the callback (key, focusin, focusout, forced)")
    # print("end", f"W={W} - the tk name of the widget")
    if '-1' == d:
        lg.debug("other action")
        return True
    if '0' == d:
        lg.debug("delete action")
        return True
    else:
        lg.debug("insert action")
    if d == '0':
        return True

    if P.isnumeric():  # len(P) <= 4 and
        return True
        # n = int(P)
        # if 0 <= n <= 1000:
        #     return True
        # else:
        #     return False
    else:
        # self.bell()
        return False


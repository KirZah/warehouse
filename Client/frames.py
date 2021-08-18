import tkinter as tk
from tkinter import *
from tkinter import messagebox as mb
import tkinter.font as tkFont

from mysql.connector import Error

from loguru import logger as lg

from functions import is_date, is_iterable, insert_new_line_symbols, \
    set_active, set_parent_window_req_size, place_tk_to_screen_center, place_window,\
    on_validate_name, on_validate_date, on_validate_naturalnumber, \
    update_treeview, add_days_to_date, error_to_str
from db import Connection, DbTables, run_select_query, run_commit_query, add_records_to_cmb, get_next_id

import db
import exceptions

def connection_error_to_str(error):

    def parse_apostrophes(msg, apostrophe_num):
        start = 0
        end = len(msg)
        for i in range(apostrophe_num):
            start = msg.find("'", start, end) + 1
        end = msg.find("'", start, end)
        return msg[start:end]

    # s = errno_to_str(error.errno)
    errno = error.errno
    if errno is None:
        lg.info("GOOD, you've connected")
        return None

    elif errno == 2003:
        # 2003 (None): Can't connect to MySQL server on 'warehouse:3306' (11001 getaddrinfo failed)
        address_info = parse_apostrophes(error.msg, 2)
        lg.error(f"ERROR (MySQL.Connector): Can't connect to MySQL server on '{address_info}'!")
        return f"Can't connect \nto MySQL server \non '{address_info}'!"

    elif errno == 2005:
        lg.error('ERROR (MySQL.Connector): Host not found!')
        return 'Host not found!'

    elif errno == 1044:
        username = parse_apostrophes(error.msg, 1)
        host = parse_apostrophes(error.msg, 3)
        database = parse_apostrophes(error.msg, 5)
        lg.error(f"ERROR (MySQL.Connector): "
                 f"Error: 1044 (42000): Access denied for user '{username}'@'{host}' to database '{database}'")
        return f"Access denied!"

    elif errno == 1045: # (28000)
        lg.error('ERROR (MySQL.Connector): Incorrect User or Password!')
        return 'Incorrect User or Password!'

    elif errno == 1049:
        lg.error('ERROR (MySQL.Connector): Database not found!')
        return 'Database not found!'

    elif errno == 3118: # (HY000)
        username = parse_apostrophes(error.msg, 1)
        host = parse_apostrophes(error.msg, 3)
        lg.error(f"ERROR (MySQL.Connector): "
                 f"Error: 3118 (HY000): Access denied for user '{username}'@'{host}'. Account is locked.")
        return 'Access denied. Account is locked!'

    elif errno == 1370:  # 1370 (42000)
        # Error: 1370 (42000): execute command denied to user 'warehouseman'@'localhost' for routine
        # 'warehouse.get_user_role'
        username = parse_apostrophes(error.msg, 1)
        host = parse_apostrophes(error.msg, 3)
        routine = parse_apostrophes(error.msg, 5)
        lg.error(f"ERROR (MySQL): execute command denied to user '{username}'@'{host}' for routine '{routine}'")
        if username == 'mysql_select' : #and routine == 'warehouse.get_user_role':
            return f"ERROR (MySQL): Server error (can't get user's role)!"
        else:
            return f"ERROR (MySQL): execute command denied to user '{username}'@'{host}' for routine '{routine}'"

    # ERRORS DEFINED BY ME IN MYSQL ############
    elif errno == 9980:
        # Error message: User 'Chyvak88'@'localhost' doesn't exist (there's no record in 'mysql.User' table).
        username = parse_apostrophes(error.msg, 1)
        host = parse_apostrophes(error.msg, 3)
        lg.error(f"ERROR (MySQL - Chyvak88): User '{username}'@'{host}' doesn't exist (there's no record in 'mysql.User' table).")
        return f"ERROR: User '{username}'@'{host}' doesn't exist."
    elif errno == 9981:
        # Error: 9981 (ROLEF): User 'warehouseman'@'localhost' doesn't have any role assigned
        # (there's no record in 'mysql.role_edges' table).
        username = parse_apostrophes(error.msg, 1)
        host = parse_apostrophes(error.msg, 3)
        lg.error(f"User '{username}' doesn''t have any role assigned nor on host '{host}' nor for '%' (there''s no record in 'mysql.role_edges' table).")
        return f"ERROR: User '{username}'@'{host}' doesn't have any role assigned."
    # ERRORS DEFINED BY ME IN MYSQL ^^^^^^^^^^^^

    else:
        lg.error('ERROR (MySQL.Connector): Unknown (for me) Error!')
        return 'Unknown Connection Error!'


class ConnectionFrame(tk.Frame):
    def __init__(self, parent, conn1):
        lg.info("########   CREATING ConnectionFrame   ########")
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.conn1 = conn1

        # Placing frame on form
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.config(background="orange")

        # Creating Buttons
        # def connect_to_db():
        #     self.add_user('')
        self.btn_enter = tk.Button(self, text='Enter', command=lambda: self.connect_to_database(''))

        # Creating Labels
        self.lbl_title = tk.Label(self,     text='Connection',  background=self['background'])
        self.labelhost = tk.Label(self,     text='host:',       background=self['background'])
        self.labeldatabase = tk.Label(self, text='database:',   background=self['background'])
        self.labeluser = tk.Label(self,     text='user:',       background=self['background'])
        self.labelpassword = tk.Label(self, text='password:',   background=self['background'])
        self.lbl_notify = tk.Label(self,    text='notifier',    background=self['background'],
                                   font=('Calibri', 11, 'bold'), fg='black')

        # Creating Entry widgets
        self.entryhost = tk.Entry(self)
        self.entrydatabase = tk.Entry(self)
        self.entryuser = tk.Entry(self)
        self.entrypassword = tk.Entry(self, bd=5, show="*")

        # Creating String variables for Entry widgets
        self.entryhostvar = tk.StringVar()
        self.entrydatabasevar = tk.StringVar()
        self.entryuservar = tk.StringVar()
        self.entrypasswordvar = tk.StringVar()
        # Set them to some value.
        self.entryhostvar.set("localhost")
        self.entrydatabasevar.set("warehouse")

        # Tell the entry widget to watch this variable.
        self.entryhost["textvariable"] = self.entryhostvar
        self.entrydatabase["textvariable"] = self.entrydatabasevar
        self.entryuser["textvariable"] = self.entryuservar
        self.entrypassword["textvariable"] = self.entrypasswordvar

        # Bind widgets with events
        self.master.bind("<Key-Return>", self.connect_to_database)  # binding window
        def select_all(event):  # так выделяется ещё и если мышкой кликнуть. Почему? - Неясно, да и неважно
            self.entrypassword.selection_range(0, END)
        # self.entryhost.bind('<Key-Return>', self.add_user)
        self.entryhost.bind('<FocusIn>', self.entryhost.selection_range(0, END))
        # self.entry_role.bind('<Key-Return>', self.add_user)
        self.entrydatabase.bind('<FocusIn>', self.entrydatabase.selection_range(0, END))
        # self.entryuser.bind('<Key-Return>', self.add_user)
        self.entryuser.bind('<FocusIn>', self.entryuser.selection_range(0, END))
        # self.entrypassword.bind('<Key-Return>', self.add_user)
        self.entrypassword.bind('<FocusIn>', self.entrypassword.selection_range(0, END))
        self.entrypassword.bind('<FocusIn>', select_all)

        # Placing widgets
        self.lbl_title.grid(    row=0,  column=0, columnspan=2)
        self.labelhost.grid(    row=1,  column=0, padx=(10, 0))
        self.labeldatabase.grid(row=2,  column=0, padx=(10, 0))
        self.labeluser.grid(    row=3,  column=0, padx=(10, 0))
        self.labelpassword.grid(row=4,  column=0, padx=(10, 0))

        self.entryhost.grid(    row=1,  column=1, padx=(0, 10))
        self.entrydatabase.grid(row=2,  column=1, padx=(0, 10))
        self.entryuser.grid(    row=3,  column=1, padx=(0, 10))
        self.entrypassword.grid(row=4,  column=1, padx=(0, 10))
        self.btn_enter.grid(    row=5,  column=0, columnspan=2, pady=(5, 5))
        self.lbl_notify.grid(   row=6,  column=0, columnspan=2, pady=(5, 5))
        self.lbl_notify.grid_remove()

        lg.info(f'self.conn1 = {self.conn1}')
        self.fill_entries_with_current_connection()

        set_parent_window_req_size(self)
        place_tk_to_screen_center(self.parent)
        set_active(self)

        # # Временно #######################
        # self.entryuservar.set("warehouseman")
        # self.entrypasswordvar.set("warehouseman")
        # self.add_user("<Key-Return>")
        # # Временно #######################

    def connect_to_database(self, event):
        lg.info(f"#add_user('{self.entryhostvar.get()}', "
                f"'{self.entryuservar.get()}', "
                f"'{self.entrypasswordvar.get()}', "
                f"'{self.entrydatabasevar.get()}')"
                )
        # if self.entryuservar.get() == 'root':
        #     self.lbl_notify.config(fg='red', text="You can't login as 'root'")
        #     self.lbl_notify.grid()
        #     return
        self.conn1 = Connection(self.entryhostvar.get(),
                                self.entryuservar.get(),
                                self.entrypasswordvar.get(),
                                self.entrydatabasevar.get(),
                                )
        r = self.conn1.connect()
        if r is None:
            lg.info("Correct user and password")
            self.master.master.title(self.parent.master.main_window_title + " - " + self.conn1.get_role())
            self.lbl_notify.config(fg='green', text="Correct user and password")
            self.lbl_notify.grid()
            self.parent.master.conn1 = self.conn1
            self.parent.master.initialize_unknown_user_interface()
            self.parent.master.btnConnect.destroy()
            self.parent.master.initialize_user_interface()
            self.parent.master.resizable(True, True)
            self.parent.destroy()
        else:
            lg.info("Incorrect user or password!")
            self.master.master.title(self.parent.master.main_window_title)
            self.lbl_notify.config(fg='red', text=insert_new_line_symbols(connection_error_to_str(r), 29))
            self.lbl_notify.grid()
            self.parent.master.conn1 = self.conn1
            # try:
            #     self.parent.master.btnConnect.pack()
            # except TclError:
            #     lg.info("Button do not exist")
            #     # self.master.master.
            self.parent.master.initialize_unknown_user_interface()
            # else:
            #     lg.info("Button already exist")
        lg.debug('OK we can write even after class element gets destroyed! '
                 '(i suppose element lives till the end of function)')

    def fill_entries_with_current_connection(self):
        if not (self.conn1 is None) and not (self.conn1.get_connection() is None):
            self.entryhostvar.set(self.conn1.get_host())
            self.entrydatabasevar.set(self.conn1.get_database())
            self.entryuservar.set(self.conn1.get_username())
            self.entrypasswordvar.set(self.conn1.get_password())


class AddUserFrame(tk.Frame):
    def __init__(self, parent, conn1):
        lg.info("########   CREATING AddUserFrame   ########")
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.conn1 = conn1

        # Placing frame on form
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.config(background="orange")

        # Creating Buttons
        # def connect_to_db():
        #     self.add_user('')
        self.btn_enter = tk.Button(self, text='Enter', command=self.add_user)

        # Creating Labels
        self.lbl_title = tk.Label(self,     text='Add User',    background=self['background'])
        self.labelhost = tk.Label(self,     text='host:',       background=self['background'])
        self.lbl_role = tk.Label(self,      text='role:',       background=self['background'])
        self.labeluser = tk.Label(self,     text='user:',       background=self['background'])
        self.labelpassword = tk.Label(self, text='password:',   background=self['background'])
        # self.labelpassword2 = tk.Label(self, text='confirm password:',   background=self['background'])
        self.lbl_notify = tk.Label(self,    text='notifier',    background=self['background'],
                                   font=('Calibri', 11, 'bold'), fg='black')

        # Creating Entry widgets
        self.entryhost = tk.Entry(self)
        self.entry_role = tk.Entry(self)
        self.entryuser = tk.Entry(self)
        self.entrypassword = tk.Entry(self, bd=5, show="*")

        # Creating String variables for Entry widgets
        self.entryhostvar = tk.StringVar()
        self.entry_role_var = tk.StringVar()
        self.entryuservar = tk.StringVar()
        self.entrypasswordvar = tk.StringVar()
        # Set them to some value.
        self.entryhostvar.set("localhost")
        self.entry_role_var.set("warehouse")

        # Tell the entry widget to watch this variable.
        self.entryhost["textvariable"] = self.entryhostvar
        self.entry_role["textvariable"] = self.entry_role_var
        self.entryuser["textvariable"] = self.entryuservar
        self.entrypassword["textvariable"] = self.entrypasswordvar

        # Bind widgets with events
        self.master.bind("<Key-Return>", self.add_user)  # binding window
        def select_all(event):  # так выделяется ещё и если мышкой кликнуть. Почему? - Неясно, да и неважно
            self.entrypassword.selection_range(0, END)
        # self.entryhost.bind('<Key-Return>', self.add_user)
        self.entryhost.bind('<FocusIn>', self.entryhost.selection_range(0, END))
        # self.entry_role.bind('<Key-Return>', self.add_user)
        self.entry_role.bind('<FocusIn>', self.entry_role.selection_range(0, END))
        # self.entryuser.bind('<Key-Return>', self.add_user)
        self.entryuser.bind('<FocusIn>', self.entryuser.selection_range(0, END))
        # self.entrypassword.bind('<Key-Return>', self.add_user)
        self.entrypassword.bind('<FocusIn>', self.entrypassword.selection_range(0, END))
        self.entrypassword.bind('<FocusIn>', select_all)

        # Placing widgets
        self.lbl_title.grid(    row=0,  column=0, columnspan=2)
        self.labelhost.grid(    row=1,  column=0, padx=(10, 0))
        self.lbl_role.grid(row=2, column=0, padx=(10, 0))
        self.labeluser.grid(    row=3,  column=0, padx=(10, 0))
        self.labelpassword.grid(row=4,  column=0, padx=(10, 0))

        self.entryhost.grid(    row=1,  column=1, padx=(0, 10))
        self.entry_role.grid(row=2, column=1, padx=(0, 10))
        self.entryuser.grid(    row=3,  column=1, padx=(0, 10))
        self.entrypassword.grid(row=4,  column=1, padx=(0, 10))
        self.btn_enter.grid(    row=5,  column=0, columnspan=2, pady=(5, 5))
        self.lbl_notify.grid(   row=6,  column=0, columnspan=2, pady=(5, 5))
        self.lbl_notify.grid_remove()

        lg.info(f'self.conn1 = {self.conn1}')
        self.fill_entries_with_default()

        set_parent_window_req_size(self)
        place_tk_to_screen_center(self.parent)
        set_active(self)

        # # Временно #######################
        # self.entryuservar.set("warehouseman")
        # self.entrypasswordvar.set("warehouseman")
        # self.add_user("<Key-Return>")
        # # Временно #######################

    def add_user(self, event=''):
        lg.info(f"#add_user('{self.entryuservar.get()}', "
                f"'{self.entryhostvar.get()}', "
                f"'{self.entrypasswordvar.get()}', "
                f"'{self.entry_role_var.get()}')"
                )
        # query = """call add_user('%(username)s', '%(host)s', '%(password)s', '%(role)s')"""
        # parameters = ({'username': self.entryuservar.get(),
        #                'host': self.entryhostvar.get(),
        #                'password': self.entrypasswordvar.get(),
        #                'role': self.entry_role_var.get()
        #                })
        # db_rows = run_commit_query(self.conn1, query, parameters)
        username = self.entryuservar.get()
        host = self.entryhostvar.get()
        password = self.entrypasswordvar.get()
        role = self.entry_role_var.get()

        query = f"""call add_user('{username}', '{host}', '{password}', '{role}')"""
        db_rows = run_commit_query(self.conn1, query)

        if db_rows == -1:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
            self.lbl_notify.config(fg='red', text="Connection Error!")
            self.lbl_notify.grid()
        elif isinstance(db_rows, Error):
            error_msg = error_to_str(db_rows)
            lg.error(error_msg)
            self.lbl_notify.config(fg='red', text=insert_new_line_symbols(error_msg))
            self.lbl_notify.grid()
        elif db_rows is None:
            lg.info(f"New user added!")
            self.lbl_notify.config(fg='green', text='New user added!')
            self.lbl_notify.grid()
        else:
            lg.critical("received smth else")
            self.lbl_notify.config(fg='red', text='UNKNOWN CRITICAL ERROR!!!!')
            self.lbl_notify.grid()


    def fill_entries_with_default(self):
        if not (self.conn1 is None) and not (self.conn1.get_connection() is None):
            self.entryhostvar.set(self.conn1.get_host())
            self.entry_role_var.set("salesman")
            self.entryuservar.set("user")
            self.entrypasswordvar.set("")


class AboutFrame(tk.Frame):
    def __init__(self, parent):
        lg.info('########   CREATING AboutFrame   ########')
        tk.Frame.__init__(self, parent)
        self.parent = parent
        # Placing frame on form
        self.pack(side=tk.LEFT, fill=tk.Y)
        try:
            self.img = tk.PhotoImage(file='Slowpoke.PNG')
            self.canvas = tk.Canvas(self, width=self.img.width(), height=self.img.height())
            self.image = self.canvas.create_image(0, 0, anchor='nw', image=self.img)
            self.canvas.pack(side=tk.TOP, fill=tk.Y)
        except:
            mb.showerror('File not found!', 'File "Slowpoke.PNG" not found!')
            self.master.destroy()
        else:
            # pixelVirtual = tk.PhotoImage(width=1, height=1)
            # self.btn_exit = tk.Button(self, command=self.master.quit,
            #                             text="Close",
            #                             image=pixelVirtual,
            #                             width=self.img.width(),
            #                             height=20,
            #                             compound="c"
            #                           )
            # self.btn_exit.pack(side=tk.TOP, fill=tk.X)

            set_parent_window_req_size(self, notifyspace=0, resizeable=(0, 0))
            place_tk_to_screen_center(self.parent)
            set_active(self.parent)


class AssignShelfFrame(tk.Frame):

    def __init__(self, parent, conn1):
        self.parent = parent
        self.conn1 = conn1
        tk.Frame.__init__(self, parent)
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.parent.title('Assign Products with Shelves')
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)
        lg.info("########   CREATING ShelfAssignWindow  ########")
        self.goods_id = None

        def combobox_selected(event):
            lg.info("#combobox_selected")
            lg.info(f'you\'ve selected "{self.cmb_product_id.selection_get()}"')
            self.query = """
                           select price, shelf_life, description from catalog
                           where product_name = %(product_name)s
                           ORDER BY product_name ASC
                           """
            self.parameters = ({'product_name': self.cmb_product_id.selection_get()})
            self.show_chosen_product()

        def entprod(event):
            self.enter_product()

        frame = self
        # self.frame_product.pack(side=tk.LEFT, fill=tk.Y, expand=False, ipadx=5, ipady=5)
        self.config(background="orange")
        # Creating Button widgets
        self.btn_product_enter = tk.Button(frame, text="Enter", command=self.enter_product)
        self.btn_product_enter.bind('<Return>', entprod)

        # Creating Label widgets
        self.lbl_product = tk.Label(frame, text='Storage', background=frame['background'],
                                    font=('Calibri', 11, 'bold'))
        self.lbl_product_id = tk.Label(frame, text='Package id*', background=frame['background'])
        self.lbl_product_shelf = tk.Label(frame, text='Shelf*', background=frame['background'])
        self.lbl_product_notify = tk.Label(frame, text='notifier', background=frame['background'])
        # Creating Entry widgets
        vcmd = (self.register(self.on_validate_product_id),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        # vcmd2 = (self.register(self.on_validate_date),
        #          '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        # vcmd3 = (self.register(self.on_validate_naturalnumber),
        #          '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        # self.cmb_product_id = ttk.Combobox(frame, validate="key", validatecommand=vcmd)  # ComboBox
        self.entry_product_id = tk.Entry(frame, validate="key", validatecommand=vcmd)
        self.entry_product_shelf = tk.Entry(frame)
        self.entry_product_id.bind('<Return>', entprod)
        self.entry_product_shelf.bind('<Return>', entprod)

        # Creating Entry widgets's variables
        # self.cmb_product_id_var = tk.StringVar()
        self.entry_product_id_var = tk.StringVar()
        self.entry_product_shelf_var = tk.StringVar()
        #
        # Set widgets to some value.
        # self.cmb_product_id_var.set("")
        self.entry_product_id_var.set("")
        self.entry_product_shelf_var.set("")

        # Assigning variables to widgets    (Tell the widget to watch this variable.)
        # self.cmb_product_id["textvariable"] = self.cmb_product_id_var
        self.entry_product_id["textvariable"] = self.entry_product_id_var
        self.entry_product_shelf["textvariable"] = self.entry_product_shelf_var
        # Binding widgets with functions
        self.entry_product_id.bind('<FocusIn>', self.entry_product_id.selection_range(0, END))
        # self.cmb_product_id.bind('<FocusIn>', self.cmb_product_id.selection_range(0, END))
        # self.cmb_product_id.bind("<<ComboboxSelected>>", combobox_selected)
        self.entry_product_shelf.bind('<FocusIn>', self.entry_product_shelf.selection_range(0, END))

        # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
        self.lbl_product.grid(row=0, column=0, columnspan=2)  # sticky=N+S+W+E

        self.lbl_product_id.grid(row=2, column=0, padx=(5, 0), sticky='es')
        self.lbl_product_shelf.grid(row=3, column=0, sticky='e')

        # self.cmb_product_id.grid(row=2, column=1, padx=(5, 0), pady=(10, 0))
        self.entry_product_id.grid(row=2, column=1, padx=(15, 30), pady=(10, 0))
        self.entry_product_shelf.grid(row=3, column=1, padx=(15, 30))

        self.btn_product_enter.grid(row=10, column=0, columnspan=2, sticky='', pady=(5, 5))
        self.lbl_product_notify.grid(row=11, column=0, columnspan=2, sticky='', pady=(5, 5))

        self.lbl_product_notify.grid_remove()
        # self.cmb_product_id.grid_remove()
        # self.entry_product_id.grid_remove()

        # self.searching_similar_product_id(self.cmb_product_id_var.get())

        set_parent_window_req_size(self)
        place_tk_to_screen_center(self.parent)
        set_active(self.parent)

    def on_closing(self):
        lg.info("#on_closing")
        self.parent.destroy()

    def on_validate_product_id(self, d, i, P, s, S, v, V, W):
        lg.info("#on_validate_product_id")
        # print("end", "\n\nOnValidate:")
        # print("end", f"d={d} - Type of action (1=insert, 0=delete, -1 for others)")
        # print("end", f"i={i} - index of char string to be inserted/deleted, or -1")
        # print("end", f"P={P} - value of the entry if the edit is allowed")
        # print("end", f"s={s} - value of entry prior to editing")
        # print("end", f"S={S} - the text string being inserted or deleted, if any")
        # print("end", f"v={v} - the type of validation that is currently set")
        # print("end", f"V={V} - the type of validation that triggered the callback (key, focusin, focusout, forced)")
        # print("end", f"W={W} - the tk name of the widget")
        if d=='0' or P.isnumeric():
            return True
        else:
            return False

    def enter_product(self):
        lg.info("#change_package")
        self.lbl_product_notify.grid_remove()

        # def enter_product_exists():
        self.query = """
                        select id from goods
                        where id = %(id)s
                        """
        self.parameters = ({'id': self.entry_product_id_var.get()})
        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        # lg.info(f'db_rows={db_rows}')
        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
        elif db_rows == []:
            lg.error(f'db_rows={[]} (empty)')
            self.lbl_product_notify.config(fg='red', text="Package not found!\nCheck your Entry!")
            self.lbl_product_notify.grid()
            lg.error('Not found')
        elif is_iterable(db_rows):
            if False:
                lg.debug("Here should be check if 'goods_id' column is in 'goods_shipment' table")
            else:
                if self.entry_product_shelf_var.get() == '':
                    lg.info("You forgot to Enter shelf!")
                    self.lbl_product_notify.config(fg='red',
                                                   text=insert_new_line_symbols("You forgot to Enter shelf!"))
                    self.lbl_product_notify.grid()
                else:
                    lg.info('Product is chosen')
                    self.lbl_product_notify.config(fg='green', text="Chosen")
                    self.lbl_product_notify.grid()
                    self.goods_id = db_rows[0][0]
                    self.add_product_to_warehouse()
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')


        # if self.btn_product_exists['state'] == 'disabled':
        # enter_product_exists()
        # elif self.btn_product_new['state'] == 'disabled':
        #     enter_product_new()
        # else:
        #     lg.error("Button not chosen! ('New' or 'Exists')")

    def add_product_to_warehouse(self):
        lg.info("#add_product_to_warehouse")

        lg.debug(f"self.goods_id = {self.goods_id}")
        self.query = """INSERT INTO storage(goods_id, shelf) VALUES(%s, %s)"""
        self.parameters = (self.goods_id,
                           self.entry_product_shelf_var.get()
                           )
        db_rows = run_commit_query(self.conn1, self.query, self.parameters)

        # lg.debug(f"db_rows={db_rows}")
        # lg.debug(f"r=.__class__ = {db_rows.__class__}")
        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
            lg.error(error_to_str(db_rows))
            if db_rows.errno == 1062:
                self.lbl_product_notify.config(fg='darkred',
                                               text=insert_new_line_symbols("This id already exists in storage! "
                                                                            "Check your entry. "
                                                                            "(If your entry is correct then "
                                                                            "inform the management!!!)"))
                lg.error("This id already exists in table 'storage'!")
            else:
                self.lbl_product_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
            self.lbl_product_notify.grid()
        elif db_rows is None:
            self.lbl_product_notify.config(fg='green', text=f"Added package #{self.goods_id} to storage!")
            self.lbl_product_notify.grid()
            self.entry_product_id_var.set(str(self.goods_id + 1))
            if self.parent.master.table == DbTables.storage:
                values = (self.entry_product_id_var.get(), self.entry_product_shelf_var.get())
                self.parent.master.tree.insert("", 0, "", text='', values=values, tag='lightgray')
            # searching_similar_product_id(self.goods_id)
            # lg.debug(f"self.goods_id = {self.goods_id}")


class ChangePackageFrame(tk.Frame):
    # минусы: если кто-то произведёт изменение, пока это пытались сделать мы, то изменение
    # будет некорректно обработано. Как исправить (сузить время для возможного исправления):
    # Сразу перед запросом для изменения записи проверять совпадают ли изначально полученные данные
    # с теми, что в бд сейчас (существует ли ровно такая же запись).
    # Не особо важно исправлять, так как вероятность такого события очень мала,
    # если следовать логике проекта
    def __init__(self, parent, conn1, tree_item):
        lg.info("ChooseProductFrame")
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.conn1 = conn1
        self.item = tree_item
        self.goods_id = int(self.parent.master.tree.item(self.item, "values")[0])
        self.catalog_id = None

        def choosing_catalog_element():
            def change_button_selected():
                self.btn_new.config(relief=RAISED, state="normal")
                self.btn_exists.config(relief=SUNKEN, state="disabled")
                self.lbl_product_notify.grid_remove()

            def btn_exists_change_entries():
                self.cmb_product_name_var.set(self.entry_product_name_var.get())
                self.entry_product_price_var.set("")
                self.entry_product_shelf_life_var.set("")
                # self.entry_product_shelf_life_var.set(self.product_shelf_life)
                self.entry_product_description_var.set("")
                self.entry_product_description.config(state="disabled", fg="darkgreen")
                self.entry_product_shelf_life.config(state="disabled", fg="darkgreen")
                self.entry_product_price.config(state="disabled", fg="darkgreen")

            lg.info("#choosing_catalog_element")
            change_button_selected()
            btn_exists_change_entries()
            self.entry_product_name.grid_remove()
            self.cmb_product_name.grid()

            self.search_similar_product_name("")
            combobox_selected('', self.cmb_product_name_var.get())

        def adding_catalog_element():
            def btn_new_change_entries():
                self.entry_product_name_var.set(self.product_name)
                self.entry_product_price_var.set(self.product_price)
                self.entry_product_shelf_life_var.set(self.product_shelf_life)
                self.entry_product_description_var.set(self.product_description)
                self.entry_product_description.config(state="normal", fg="black")
                self.entry_product_shelf_life.config(state="normal", fg="black")
                self.entry_product_price.config(state="normal", fg="black")

            def change_button_selected():
                self.btn_exists.config(relief=RAISED, state="normal")
                self.btn_new.config(relief=SUNKEN, state="disabled")
                self.lbl_product_notify.grid_remove()

            lg.info("#adding_catalog_element")
            change_button_selected()
            btn_new_change_entries()
            self.cmb_product_name.grid_remove()
            self.entry_product_name.grid()

        def combobox_selected(event, str=None):
            lg.info("#combobox_selected")
            if str is None:
                str = self.cmb_product_name.selection_get()
            lg.info(f'you\'ve selected "{str}"')
            self.query = """
                               select price, shelf_life, description from catalog
                               where product_name = %(product_name)s
                               ORDER BY product_name ASC
                               """
            self.parameters = ({'product_name': str})
            self.show_chosen_catalog_element()

        frame = self
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.config(background="orange")
        # Creating Button widgets
        self.btn_new = tk.Button(frame, text="New Catalog el.", command=adding_catalog_element)
        self.btn_exists = tk.Button(frame, text="Catalog el. exists", command=choosing_catalog_element)
        self.btn_product_enter = tk.Button(frame, text="Change", command=self.change_package)
        # Creating Label widgets
        self.lbl_product = tk.Label(frame, text='Package', background=frame['background'],
                                    font=('Calibri', 11, 'bold'))
        self.lbl_product_name = tk.Label(frame, text='Product Name*', background=frame['background'])
        self.lbl_product_price = tk.Label(frame, text='price*', background=frame['background'])
        self.lbl_product_shelf_life = tk.Label(frame, text='shelf life*', background=frame['background'])
        self.lbl_product_description = tk.Label(frame, text='description', background=frame['background'])
        self.lbl_product_production_date = tk.Label(frame, text='production date*', background=frame['background'])
        self.lbl_product_note = tk.Label(frame, text='note', background=frame['background'])
        self.lbl_product_notify = tk.Label(frame, text='Product already exists!',
                                           background=frame['background'],
                                           font=('Calibri', 11, 'bold'), fg='red')

        # Creating validate commands
        vcmd = (self.register(self.on_validate_name),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd2 = (self.register(on_validate_date),
                 '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd3 = (self.register(on_validate_naturalnumber),
                 '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.cmb_product_name = ttk.Combobox(frame, validate="key", validatecommand=vcmd)
        # Creating Entry widgets
        self.entry_product_name = tk.Entry(frame)
        self.entry_product_price = tk.Entry(frame)
        self.entry_product_shelf_life = tk.Entry(frame)
        self.entry_product_description = tk.Entry(frame)
        self.entry_product_production_date = tk.Entry(frame, validate="key", validatecommand=vcmd2)
        self.entry_product_note = tk.Entry(frame)

        # Creating Entry widgets's variables
        self.cmb_product_name_var = tk.StringVar()
        self.entry_product_name_var = tk.StringVar()
        self.entry_product_price_var = tk.StringVar()
        self.entry_product_shelf_life_var = tk.StringVar()
        self.entry_product_description_var = tk.StringVar()
        self.entry_product_production_date_var = tk.StringVar()
        self.entry_product_note_var = tk.StringVar()

        # Set widgets to some value.
        self.cmb_product_name_var.set("")
        self.entry_product_name_var.set("")
        self.entry_product_price_var.set("")
        self.entry_product_shelf_life_var.set("")
        self.entry_product_description_var.set("")
        self.entry_product_production_date_var.set("")
        self.entry_product_note_var.set("")

        # Assigning variables to widgets    (Tell the widget to watch this variable.)
        self.cmb_product_name["textvariable"] = self.cmb_product_name_var
        self.entry_product_name["textvariable"] = self.entry_product_name_var
        self.entry_product_price["textvariable"] = self.entry_product_price_var
        self.entry_product_shelf_life["textvariable"] = self.entry_product_shelf_life_var
        self.entry_product_description["textvariable"] = self.entry_product_description_var
        self.entry_product_production_date["textvariable"] = self.entry_product_production_date_var
        self.entry_product_note["textvariable"] = self.entry_product_note_var

        # Binding widgets with functions
        self.cmb_product_name.bind("<<ComboboxSelected>>", combobox_selected)
        self.cmb_product_name.bind('<FocusIn>', self.cmb_product_name.selection_range(0, END))
        self.entry_product_name.bind('<FocusIn>', self.entry_product_name.selection_range(0, END))
        self.entry_product_price.bind('<FocusIn>', self.entry_product_price.selection_range(0, END))
        self.entry_product_shelf_life.bind('<FocusIn>', self.entry_product_shelf_life.selection_range(0, END))
        self.entry_product_description.bind('<FocusIn>', self.entry_product_description.selection_range(0, END))
        self.entry_product_production_date.bind('<FocusIn>', self.entry_product_production_date.selection_range(0, END))
        self.entry_product_note.bind('<FocusIn>', self.entry_product_note.selection_range(0, END))

        # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
        self.lbl_product.grid(row=0,                    column=0, columnspan=2)  # sticky=N+S+W+E,
        self.btn_new.grid(row=1,                        column=0, padx=(5, 0), pady=5, sticky='e')
        self.btn_exists.grid(row=1,                     column=1, padx=(5, 10), sticky='e')

        self.lbl_product_name.grid(row=2,               column=0, sticky='es')
        self.lbl_product_price.grid(row=3,              column=0, sticky='e')
        self.lbl_product_shelf_life.grid(row=4,         column=0, sticky='e')
        self.lbl_product_description.grid(row=5,        column=0, sticky='e')
        self.lbl_product_production_date.grid(row=6,    column=0, sticky='e', pady=(15, 0), padx=(5, 0))
        self.lbl_product_note.grid(row=7,               column=0, sticky='e')

        self.cmb_product_name.grid(row=2,               column=1, padx=(5, 0),   pady=(10, 0))
        self.entry_product_name.grid(row=2,             column=1, padx=(15, 30), pady=(10, 0))
        self.entry_product_price.grid(row=3,            column=1, padx=(15, 30))
        self.entry_product_shelf_life.grid(row=4,       column=1, padx=(15, 30))
        self.entry_product_description.grid(row=5,      column=1, padx=(15, 30))
        self.entry_product_production_date.grid(row=6,  column=1, padx=(15, 30), pady=(15, 0))
        self.entry_product_note.grid(row=7,             column=1, padx=(15, 30))

        self.btn_product_enter.grid(row=10,             column=0, columnspan=2, sticky='', pady=(5, 5))
        self.lbl_product_notify.grid(row=11,            column=0, columnspan=2, sticky='', pady=(5, 5))

        self.lbl_product_notify.grid_remove()
        self.entry_product_name.grid_remove()
        self.cmb_product_name.grid_remove()

        # adding_catalog_element()
        choosing_catalog_element()
        self.show_changing_package()
        self.search_similar_product_name("")
        # set_parent_window_req_size(self)
        # place_tk_to_screen_center(self)
        place_window(self.parent, self)

    def on_validate_name(self, d, i, P, s, S, v, V, W,):
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
            self.search_similar_product_name(P)
            return True
        elif '0' == d:
            lg.debug("delete action")
            self.search_similar_product_name(P)
            return True
        else:
            lg.debug("insert action")

        if (S == '_') or (S == '%'):
            self.bell()
            return False
        elif ('_' in P) or ('%' in P):
            self.bell()
            return False
        else:
            self.search_similar_product_name(P)
            return True

    def show_changing_package(self):
        lg.info("#show_changing_package")

        lg.info(f'you\'ve selected "{self.goods_id}"')
        self.query = """
                       select product_name, price, shelf_life, description,
                           production_date, note from goods
                            LEFT JOIN catalog ON goods.catalog_id = catalog.id
                       where goods.id = %(id)s
                       """
        self.parameters = ({'id': self.goods_id})
        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        lg.debug(f'db_rows={db_rows}')

        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
            self.lbl_product_notify.config(fg='red',
                                           text=insert_new_line_symbols(error_to_str(db_rows)))
        elif db_rows == []:
            lg.debug('Recieved empty array')
            self.lbl_product_notify.config(fg='red',
                                           text="While we were trying to get info from DB your chosen id disappeared")
            self.lbl_product_notify.grid()
        elif is_iterable(db_rows):
            for row in db_rows:
                # lg.info(f'self.entry_supply_address_var = "{self.entry_supply_address_var.get()}"')
                self.product_name = row[0]
                self.product_price = row[1]
                self.product_shelf_life = row[2]
                if self.product_shelf_life is None:
                    self.product_shelf_life = '-'
                self.product_description = row[3]
                self.product_production_date = row[4]
                self.product_note = row[5]

                self.cmb_product_name_var.set(self.product_name)
                self.entry_product_name_var.set(self.product_name)
                self.entry_product_price_var.set(self.product_price)
                self.entry_product_shelf_life_var.set(self.product_shelf_life)
                self.entry_product_description_var.set(self.product_description)
                self.entry_product_production_date_var.set(self.product_production_date)
                self.entry_product_note_var.set(self.product_note)
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')
        else:
            lg.debug("ok, wwat??")

    def show_chosen_catalog_element(self):
        lg.info("#show_changing_package")

        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        lg.debug(f'db_rows={db_rows}')

        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
        elif db_rows == []:
            lg.debug('Recieved empty array')
        elif is_iterable(db_rows):
            for row in db_rows:
                # lg.info(f'self.entry_supply_address_var = "{self.entry_supply_address_var.get()}"')
                # self.entry_product_id_var.set(row[0])
                self.entry_product_price_var.set(row[0])
                shelf_life = row[1]
                if shelf_life is None:
                    shelf_life = '-'
                self.entry_product_shelf_life_var.set(shelf_life)
                self.entry_product_description_var.set(row[2])
                # self.entry_product_production_date_var.set(row[4])
                # self.entry_product_note_var.set(row[5])
                self.lbl_product_notify.config(fg='green', text="Chosen")
                self.lbl_product_notify.grid()
                lg.info('Showing chosen Product')
                # self.create_frame_shipment()
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

    def search_similar_product_name(self, P):
        # if self.btn_new["state"] == "disabled":
        #     P = self.entry_product_name_var.get()
        # else:  # if exists
        if P is None:
            P = self.cmb_product_name_var.get()
        lg.info(f'#search_similar_product_name to "{P}"')
        self.query = """
                        SELECT product_name from catalog
                        WHERE product_name LIKE %(product_name)s
                        ORDER BY product_name ASC
                     """
        self.parameters = ({'product_name': P + '%'})
        self.cmb_product_name['values'] = ()
        add_records_to_cmb(self.conn1, self.query, self.parameters, self.cmb_product_name)

    def is_catalog_element_exists(self):
        if self.btn_new["state"] == "disabled":
            product_name = self.entry_product_name_var.get()
        else:
            product_name = self.cmb_product_name_var.get()
        self.query = """
                        select id from catalog
                        where product_name = %(product_name)s
                        """
        self.parameters = ({'product_name': product_name})
        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        # lg.info(f'db_rows={db_rows}')
        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
            return None
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
            self.lbl_product_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
            self.lbl_product_notify.grid()
            return None
        elif db_rows == []:
            lg.info("Catalog element doesn't exist")
            self.lbl_product_notify.config(fg='red', text="Catalog element doesn't exist")
            self.lbl_product_notify.grid()
            return False
        elif is_iterable(db_rows):
            lg.info("Catalog element exists")
            self.catalog_id = db_rows[0][0]
            return True
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

    def add_new_catalog_element(self):
        lg.info("#add_new_catalog_element")
        catalog_id = get_next_id(self.conn1, "catalog", self.lbl_product_notify)
        if catalog_id is None:
            return None
        self.catalog_id = catalog_id

        lg.debug(f"self.goods_id = {self.goods_id}")
        self.query = """INSERT INTO catalog(id, product_name, price, shelf_life, description) 
                                     VALUES(%s, %s, %s, %s, %s)"""

        shelf_life = self.entry_product_shelf_life_var.get()
        if shelf_life == '-':
            shelf_life = None
        self.parameters = (self.catalog_id,
                           self.entry_product_name_var.get(),
                           self.entry_product_price_var.get(),
                           shelf_life,
                           self.entry_product_description_var.get(),
                           )
        db_rows = run_commit_query(self.conn1, self.query, self.parameters)

        lg.debug(f"db_rows={db_rows}")
        # lg.debug(f"r=.__class__ = {db_rows.__class__}")
        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
            return None
        elif isinstance(db_rows, Error):
            # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
            lg.error(error_to_str(db_rows))
            self.lbl_product_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
            self.lbl_product_notify.grid()
            return None
        elif db_rows is None:
            # self.lbl_product_notify.config(fg='green', text="Added new catalog element")
            # self.lbl_product_notify.grid()
            lg.info("Added new catalog element")
            lg.info(f"self.goods_id = {self.goods_id}")
            return 0

    def change_package(self):
        lg.debug("#change_package")

        def update_package():
            lg.debug(f"self.goods_id = {self.goods_id}")
            # "UPDATE table_name SET field1 = new-value1, field2 = new-value2"
            self.query = """UPDATE goods SET 
                                        catalog_id = %(catalog_id)s, 
                                        production_date = %(production_date)s, 
                                        note = %(note)s
                                    WHERE goods.id = %(goods_id)s"""
            self.parameters = ({'catalog_id': self.catalog_id,
                                'production_date': self.entry_product_production_date_var.get(),
                                'note': self.entry_product_note_var.get(),
                                'goods_id': self.goods_id
                                })
            db_rows = run_commit_query(self.conn1, self.query, self.parameters)

            # lg.debug(f"db_rows={db_rows}")
            # lg.debug(f"r=.__class__ = {db_rows.__class__}")
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
                return None
            elif isinstance(db_rows, Error):
                # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
                lg.error(error_to_str(db_rows))
                self.lbl_product_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
                self.lbl_product_notify.grid()
                return None
            elif db_rows is None:
                # lg.debug(f"self.goods_id = {self.goods_id}")
                self.lbl_product_notify.config(fg='green', text="Package Changed!")
                self.lbl_product_notify.grid()
                # update_treeview(self.parent.master)
                return 0

        if not (is_date(self.entry_product_production_date_var.get())):
            self.lbl_product_notify.config(fg='red', text="Incorrect 'production date'!")
            self.lbl_product_notify.grid()
            lg.error("Incorrect 'production date'!")
            return
        else:
            lg.info("Date is correct!")

        # if self.selected_product_name == self.entry_product_name_var.get():
        #     # вы ввели то же имя (если вы хотите изменить атрибуты для всех товаров
        #     # с выбранным названием, то сделать это можно в таблице catalog)
        #     self.lbl_product_notify.config(fg='red',
        #                                    text=insert_new_line_symbols("You haven't changed name! "
        #                                                                 "(If you want to change other attributes "
        #                                                                 "you can do it in catalog table)", 50))
        #     self.lbl_product_notify.grid()
        #     return
        additional_info = ''
        el_exist = self.is_catalog_element_exists()
        if el_exist is None:  #если ошибка
            return
        if self.btn_new["state"] == "disabled":
            lg.debug("btn_new")
            if el_exist:
                # if not(self.goods_id is None):
                self.lbl_product_notify.config(fg='red',
                                               text=insert_new_line_symbols(
                                                   "This Product already exists! "
                                                   "(If you want to change Product attributes "
                                                   "you can do it in catalog table)", 50)
                                               )
                self.lbl_product_notify.grid()
                return
                # else:
                #     self.lbl_product_notify.config(fg='red',
                #                                    text=insert_new_line_symbols(
                #                                        "This Product already exists! "
                #                                        "(If you want to change 'production date' or "
                #                                        "'note' change button to "
                #                                        f"'{self.btn_exists.widgetName}')", 50)
                #                                    )
                #     self.lbl_product_notify.grid()
                #     lg.debug("Changing 'production date' or 'note'")
                #     return
            else:
                if self.add_new_catalog_element() is None:
                    return
                lg.debug("Changing Package & creating new catalog_element for it")
                additional_info = '\nA new catalog element was created for it.'
        else:  # self.btn_exists["state"] == "disabled"
            lg.debug("btn_exists")
            if el_exist:
                lg.debug("el_exist!!!!!!!!")
                if self.product_name == self.cmb_product_name_var.get():
                    lg.debug(f"SAME NAME")
                    lg.debug(f'SELF:  product_production_date={self.product_production_date.__class__};  '
                             f'product_note="{self.product_note.__class__}"')
                    lg.debug(f'ENTRY: product_production_date={self.entry_product_production_date_var.get().__class__};  '
                             f'product_note="{self.entry_product_note_var.get().__class__}"')
                    if (str(self.product_production_date) == self.entry_product_production_date_var.get()
                            and self.product_note == self.entry_product_note_var.get()):
                        lg.debug("You haven't changed anything!")
                        self.lbl_product_notify.config(fg='red',
                                                       text=insert_new_line_symbols(
                                                           "You haven't changed anything!", 50)
                                                       )
                        self.lbl_product_notify.grid()
                        return
                    else:
                        lg.debug("Package changed! ('production_date' or 'note')")
                        # self.lbl_product_notify.config(fg='green',
                        #                                text=insert_new_line_symbols(
                        #                                    "Package changed! ('production_date' "
                        #                                    "or 'note')", 50)
                        #                                )
                        # self.lbl_product_notify.grid()
                else:
                    lg.debug("Package changed! ('production_name' or 'production_date' or 'note')")
                    # self.lbl_product_notify.config(fg='green',
                    #                                text=insert_new_line_symbols(
                    #                                    "Package changed! ('production_name' "
                    #                                    "or 'production_date' or 'note')", 50)
                    #                                )
                    # self.lbl_product_notify.grid()
            else:
                lg.debug("Product name doesn't exist!")
                self.lbl_product_notify.config(fg='red',
                                               text=insert_new_line_symbols(
                                                   "Product name doesn't exist!", 50)
                                               )
                self.lbl_product_notify.grid()
                return

        if update_package() is None:
            return

        state = self.parent.master.tree.item(self.item, "values")[3]
        # lg.debug(f"state={state}")
        # self.parent.master.tree.delete(self.item)
        production_date = self.entry_product_production_date.get()
        shelf_life = self.entry_product_shelf_life_var.get()
        if shelf_life == '-':
            shelf_life = None
        # lg.debug(f"shelf_life={shelf_life}")
        if self.btn_new["state"] == 'disabled':
            product_name = self.entry_product_name_var.get()
        else:
            product_name = self.cmb_product_name_var.get()
        values = (self.goods_id,
                  product_name,  # name
                  self.entry_product_price_var.get(),  # price
                  state,
                  production_date,
                  add_days_to_date(production_date, shelf_life),  # Expiration_date
                  self.entry_product_description_var.get(),
                  self.entry_product_note_var.get())

        # lg.debug(f"{self.parent.master.tree.item(self.item)}")
        for i, value in enumerate(values):
            self.parent.master.tree.set(self.item,
                                        column=i,
                                        value=value)

        # lg.debug(f"{self.parent.master.tree.item(self.item)}")

        mb.showinfo("Record Changed!", "You've successfully changed package!" + additional_info)


        self.master.destroy()
        # self.parent.master.tree.see(self.item)
        # self.parent.master.tree.focus(self.item)


class ChangeCatalogFrame(tk.Frame):

    def __init__(self, parent, conn1, tree_item):
        lg.info("ChooseProductFrame")
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.conn1 = conn1
        self.item = tree_item
        self.catalog_id = int(self.parent.master.tree.item(self.item, "values")[0])

        frame = self
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.config(background="orange")
        # Creating Button widgets
        # self.btn_new = tk.Button(frame, text="New Catalog el.", command=adding_catalog_element)
        # self.btn_exists = tk.Button(frame, text="Catalog el. exists", command=choosing_catalog_element)
        self.btn_product_enter = tk.Button(frame, text="Change", command=self.change_catalog_element)
        # Creating Label widgets
        self.lbl_product = tk.Label(frame, text='Product', background=frame['background'],
                                    font=('Calibri', 11, 'bold'))
        self.lbl_product_name = tk.Label(frame, text='Product Name*', background=frame['background'])
        self.lbl_product_price = tk.Label(frame, text='price*', background=frame['background'])
        self.lbl_product_shelf_life = tk.Label(frame, text='shelf life*', background=frame['background'])
        self.lbl_product_description = tk.Label(frame, text='description', background=frame['background'])
        # self.lbl_product_production_date = tk.Label(frame, text='production date*', background=frame['background'])
        # self.lbl_product_note = tk.Label(frame, text='note', background=frame['background'])
        self.lbl_product_notify = tk.Label(frame, text='Product already exists!',
                                           background=frame['background'],
                                           font=('Calibri', 11, 'bold'), fg='red')

        # Creating validate commands
        vcmd = (self.register(on_validate_name),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd2 = (self.register(on_validate_date),
                 '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd3 = (self.register(on_validate_naturalnumber),
                 '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # self.cmb_product_name = ttk.Combobox(frame, validate="key", validatecommand=vcmd)
        # Creating Entry widgets
        self.entry_product_name = tk.Entry(frame)
        self.entry_product_price = tk.Entry(frame)
        self.entry_product_shelf_life = tk.Entry(frame, validate="key", validatecommand=vcmd3)
        self.entry_product_description = tk.Entry(frame)
        # self.entry_product_production_date = tk.Entry(frame, validate="key", validatecommand=vcmd2)
        # self.entry_product_note = tk.Entry(frame)

        # Creating Entry widgets's variables
        # self.cmb_product_name_var = tk.StringVar()
        self.entry_product_name_var = tk.StringVar()
        self.entry_product_price_var = tk.StringVar()
        self.entry_product_shelf_life_var = tk.StringVar()
        self.entry_product_description_var = tk.StringVar()
        # self.entry_product_production_date_var = tk.StringVar()
        # self.entry_product_note_var = tk.StringVar()

        # Set widgets to some value.
        # self.cmb_product_name_var.set("")
        self.entry_product_name_var.set("")
        self.entry_product_price_var.set("")
        self.entry_product_shelf_life_var.set("")
        self.entry_product_description_var.set("")
        # self.entry_product_production_date_var.set("")
        # self.entry_product_note_var.set("")

        # Assigning variables to widgets    (Tell the widget to watch this variable.)
        # self.cmb_product_name["textvariable"] = self.cmb_product_name_var
        self.entry_product_name["textvariable"] = self.entry_product_name_var
        self.entry_product_price["textvariable"] = self.entry_product_price_var
        self.entry_product_shelf_life["textvariable"] = self.entry_product_shelf_life_var
        self.entry_product_description["textvariable"] = self.entry_product_description_var
        # self.entry_product_production_date["textvariable"] = self.entry_product_production_date_var
        # self.entry_product_note["textvariable"] = self.entry_product_note_var

        # Binding widgets with functions
        # self.cmb_product_name.bind("<<ComboboxSelected>>", combobox_selected)
        # self.cmb_product_name.bind('<FocusIn>', self.cmb_product_name.selection_range(0, END))
        self.entry_product_name.bind('<FocusIn>', self.entry_product_name.selection_range(0, END))
        self.entry_product_price.bind('<FocusIn>', self.entry_product_price.selection_range(0, END))
        self.entry_product_shelf_life.bind('<FocusIn>', self.entry_product_shelf_life.selection_range(0, END))
        self.entry_product_description.bind('<FocusIn>', self.entry_product_description.selection_range(0, END))
        # self.entry_product_production_date.bind('<FocusIn>', self.entry_product_production_date.selection_range(0, END))
        # self.entry_product_note.bind('<FocusIn>', self.entry_product_note.selection_range(0, END))

        # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
        self.lbl_product.grid(row=0, column=0, columnspan=2)  # sticky=N+S+W+E,
        # self.btn_new.grid(row=1, column=0, padx=(5, 0), pady=5, sticky='e')
        # self.btn_exists.grid(row=1, column=1, padx=(5, 10), sticky='e')

        self.lbl_product_name.grid(row=2, column=0, sticky='es')
        self.lbl_product_price.grid(row=3, column=0, sticky='e')
        self.lbl_product_shelf_life.grid(row=4, column=0, sticky='e')
        self.lbl_product_description.grid(row=5, column=0, sticky='e')
        # self.lbl_product_production_date.grid(row=6, column=0, sticky='e', pady=(15, 0), padx=(5, 0))
        # self.lbl_product_note.grid(row=7, column=0, sticky='e')

        # self.cmb_product_name.grid(row=2, column=1, padx=(5, 0), pady=(10, 0))
        self.entry_product_name.grid(row=2, column=1, padx=(15, 30), pady=(10, 0))
        self.entry_product_price.grid(row=3, column=1, padx=(15, 30))
        self.entry_product_shelf_life.grid(row=4, column=1, padx=(15, 30))
        self.entry_product_description.grid(row=5, column=1, padx=(15, 30))
        # self.entry_product_production_date.grid(row=6, column=1, padx=(15, 30), pady=(15, 0))
        # self.entry_product_note.grid(row=7, column=1, padx=(15, 30))

        self.btn_product_enter.grid(row=10, column=0, columnspan=2, sticky='', pady=(5, 5))
        self.lbl_product_notify.grid(row=11, column=0, columnspan=2, sticky='', pady=(5, 5))

        self.lbl_product_notify.grid_remove()
        # self.entry_product_name.grid_remove()
        # self.cmb_product_name.grid_remove()

        self.show_changing_catalog_element()
        place_window(self.parent, self)
        #
        # self.entry_product_description.config(state="normal", fg="black")
        # self.entry_product_shelf_life.config(state="normal", fg="black")
        # self.entry_product_price.config(state="normal", fg="black")

    def show_changing_catalog_element(self):
        lg.info("#show_changing_catalog_element")

        lg.info(f'you\'ve selected "{self.catalog_id}"')
        self.query = """
                        select product_name, price, shelf_life, description
                            from catalog 
                        where catalog.id = %(id)s
                     """
        self.parameters = ({'id': self.catalog_id})

        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        lg.debug(f'db_rows={db_rows}')

        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
            self.lbl_product_notify.config(fg='red',
                                           text=insert_new_line_symbols(error_to_str(db_rows)))
        elif db_rows == []:
            lg.debug('Recieved empty array')
            self.lbl_product_notify.config(fg='red',
                                           text="While we were trying to get info from DB your chosen id disappeared")
            self.lbl_product_notify.grid()
        elif is_iterable(db_rows):
            for row in db_rows:
                # lg.info(f'self.entry_supply_address_var = "{self.entry_supply_address_var.get()}"')
                self.product_name = row[0]
                self.product_price = row[1]
                self.product_shelf_life = row[2]
                if self.product_shelf_life is None:
                    self.product_shelf_life = '-'
                self.product_description = row[3]

                # self.cmb_product_name_var.set(self.product_name)
                self.entry_product_name_var.set(self.product_name)
                self.entry_product_price_var.set(self.product_price)
                self.entry_product_shelf_life_var.set(self.product_shelf_life)
                self.entry_product_description_var.set(self.product_description)
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')
        else:
            lg.debug("ok, wwat??")

    def is_catalog_element_exists(self):
        lg.info("#is_catalog_element_exists")
        # if self.btn_new["state"] == "disabled":
        product_name = self.entry_product_name_var.get()
        # else:
        #     product_name = self.cmb_product_name_var.get()
        self.query = """
                        select id from catalog
                        where product_name = %(product_name)s
                        """
        self.parameters = ({'product_name': product_name})
        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        # lg.info(f'db_rows={db_rows}')
        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
            return None
        elif isinstance(db_rows, Error):
            error_msg = error_to_str(db_rows)
            lg.error(error_msg)
            self.lbl_product_notify.config(fg='red', text=insert_new_line_symbols(error_msg))
            self.lbl_product_notify.grid()
            return None
        elif db_rows == []:
            lg.info("Catalog element doesn't exist")
            # self.lbl_product_notify.config(fg='red', text="Catalog element doesn't exist")
            # self.lbl_product_notify.grid()
            return False
        elif is_iterable(db_rows):
            catalog_id_found = db_rows[0][0]
            if catalog_id_found != self.catalog_id:
                lg.info("Catalog element exists")
                return True
            else:
                lg.info("found changing catalog element")
                return False
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

    def change_catalog_element(self):
        lg.info("#archive")

        def is_able_to_change():
            if (str(self.product_name) == self.entry_product_name_var.get()
                    and str(self.product_price) == self.entry_product_price_var.get()
                    and str(self.product_shelf_life) == self.entry_product_shelf_life_var.get()
                    and str(self.product_description) == self.entry_product_description_var.get()):
                self.lbl_product_notify.config(fg='red',
                                               text=insert_new_line_symbols(
                                                   "You haven't changed anything!"))
                self.lbl_product_notify.grid()
                return False

            el_exists = self.is_catalog_element_exists()
            if el_exists is None:  # если ошибка
                return False
            elif el_exists:
                self.lbl_product_notify.config(fg='red',
                                               text=insert_new_line_symbols(
                                                   "Catalog element with that name already exists!"))
                self.lbl_product_notify.grid()
                return False

        def update_catalog_element(shelf_life):
            lg.debug(f"self.catalog_id = {self.catalog_id}")
            # "UPDATE table_name SET field1 = new-value1, field2 = new-value2"
            self.query = """UPDATE catalog SET 
                                        product_name = %(product_name)s, 
                                        price = %(price)s,
                                        shelf_life = %(shelf_life)s, 
                                        description = %(description)s
                                    WHERE catalog.id = %(catalog_id)s"""
            self.parameters = ({'product_name': self.entry_product_name_var.get(),
                                'price': self.entry_product_price_var.get(),
                                'shelf_life': shelf_life,
                                'description': self.entry_product_description_var.get(),
                                'catalog_id': self.catalog_id
                                })
            db_rows = run_commit_query(self.conn1, self.query, self.parameters)

            # lg.debug(f"db_rows={db_rows}")
            # lg.debug(f"r=.__class__ = {db_rows.__class__}")
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
                return -1
            elif isinstance(db_rows, Error):
                # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
                lg.error(error_to_str(db_rows))
                self.lbl_product_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
                self.lbl_product_notify.grid()
                return -2
            elif db_rows is None:
                # lg.debug(f"self.goods_id = {self.goods_id}")
                self.lbl_product_notify.config(fg='green', text=insert_new_line_symbols("Catalog Element Changed!"))
                self.lbl_product_notify.grid()
                # update_treeview(self.parent.master)
                return 0

        if not(is_able_to_change):
            return

        shelf_life = self.entry_product_shelf_life_var.get()
        if shelf_life == '-':
            shelf_life = None
        # lg.debug(f"shelf_life={shelf_life}")
        if update_catalog_element(shelf_life) != 0:
            return

        values = (self.catalog_id,
                  self.entry_product_name_var.get(),  # name
                  self.entry_product_price_var.get(),  # price
                  shelf_life,
                  self.entry_product_description_var.get()
                  )
        for i, value in enumerate(values):
            self.parent.master.tree.set(self.item,
                                        column=i,
                                        value=value)
        mb.showinfo("Record Changed!", "You've successfully changed Catalog Element!")
        self.parent.master.tree.see(self.item)
        self.parent.master.tree.focus(self.item)
        self.parent.master.tree.selection_set(self.item)
        self.master.destroy()


class ChangeShelfFrame(tk.Frame):

    def __init__(self, parent, conn1, tree_item):
        lg.info("ChangeShelfFrame")
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.conn1 = conn1
        self.item = tree_item
        self.goods_id = int(self.parent.master.tree.item(self.item, "values")[0])

        frame = self
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.config(background="orange")
        # Creating widgets
        self.btn_package_enter = tk.Button(frame, text="Change", command=self.change_shelf)
        # Creating Label widgets
        self.lbl_package = tk.Label(frame, text='Package', background=frame['background'], font=('Calibri', 11, 'bold'))
        self.lbl_package_id = tk.Label(frame, text='Package id', background=frame['background'])
        self.lbl_package_shelf = tk.Label(frame, text='Shelf', background=frame['background'])
        self.lbl_package_notify = tk.Label(frame, text='Package already exists!', background=frame['background'],
                                           font=('Calibri', 11, 'bold'), fg='red')

        # # Creating validate commands
        # vcmd = (self.register(on_validate_name),
        #         '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        # vcmd2 = (self.register(on_validate_date),
        #          '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        # vcmd3 = (self.register(on_validate_naturalnumber),
        #          '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # Creating Entry widgets
        self.entry_package_id = tk.Entry(frame, state="readonly")
        self.entry_package_shelf = tk.Entry(frame)

        # Creating Entry widgets's variables
        self.entry_package_id_var = tk.StringVar()
        self.entry_package_shelf_var = tk.StringVar()

        # Set widgets to some value.
        self.entry_package_id_var.set("")
        self.entry_package_shelf_var.set("")

        # Assigning variables to widgets    (Tell the widget to watch this variable.)
        self.entry_package_id["textvariable"] = self.entry_package_id_var
        self.entry_package_shelf["textvariable"] = self.entry_package_shelf_var

        # Binding widgets with functions
        self.entry_package_id.bind('<FocusIn>', self.entry_package_id.selection_range(0, END))
        self.entry_package_shelf.bind('<FocusIn>', self.entry_package_shelf.selection_range(0, END))

        # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
        self.lbl_package.grid(row=0, column=0, columnspan=2)  # sticky=N+S+W+E,

        self.lbl_package_id.grid(row=2, column=0, sticky='es')
        self.lbl_package_shelf.grid(row=3, column=0, sticky='e')

        # self.cmb_product_name.grid(row=2, column=1, padx=(5, 0), pady=(10, 0))
        self.entry_package_id.grid(row=2, column=1, padx=(15, 30), pady=(10, 0))
        self.entry_package_shelf.grid(row=3, column=1, padx=(15, 30))

        self.btn_package_enter.grid(row=10, column=0, columnspan=2, sticky='', pady=(5, 5))
        self.lbl_package_notify.grid(row=11, column=0, columnspan=2, sticky='', pady=(5, 5))

        self.lbl_package_notify.grid_remove()
        # self.entry_directory.grid_remove()
        # self.cmb_product_name.grid_remove()

        self.show_changing_package()
        place_window(self.parent, self)
        #
        # self.entry_product_description.config(state="normal", fg="black")
        # self.entry_product_shelf_life.config(state="normal", fg="black")
        # self.entry_archive_number.config(state="normal", fg="black")

    def show_changing_package(self):
        lg.info("#show_changing_package")

        lg.info(f'you\'ve selected "{self.goods_id}"')
        self.query = """
                        select goods_id, shelf from storage 
                        where goods_id = %(goods_id)s"""
        self.parameters = ({'goods_id': int(self.goods_id)})

        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        # lg.debug(f'db_rows={db_rows}')

        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
            self.lbl_package_notify.config(fg='red',
                                           text=insert_new_line_symbols(error_to_str(db_rows)))
        elif db_rows == []:
            lg.debug('Recieved empty array')
            self.lbl_package_notify.config(fg='red',
                                           text="While we were trying to get info from DB your chosen id disappeared")
            self.lbl_package_notify.grid()
        elif is_iterable(db_rows):
            for row in db_rows:
                # lg.info(f'self.entry_supply_address_var = "{self.entry_supply_address_var.get()}"')
                self.package_id = row[0]
                self.package_shelf = row[1]

                self.entry_package_id_var.set(self.package_id)
                self.entry_package_shelf_var.set(self.package_shelf)
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')
        else:
            lg.debug("ok, wwat??")

    def change_shelf(self):
        lg.info("#archive")

        def update_shelf():
            lg.debug(f"self.goods_id = {self.goods_id}")
            # "UPDATE table_name SET field1 = new-value1, field2 = new-value2"
            self.query = """UPDATE storage SET 
                                shelf = %(shelf)s
                            WHERE goods_id = %(goods_id)s"""
            self.parameters = ({
                'goods_id': self.entry_package_id_var.get(),
                'shelf': self.entry_package_shelf_var.get()
                })
            db_rows = run_commit_query(self.conn1, self.query, self.parameters)

            # lg.debug(f"db_rows={db_rows}")
            # lg.debug(f"r=.__class__ = {db_rows.__class__}")
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
                return None
            elif isinstance(db_rows, Error):
                # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
                lg.error(error_to_str(db_rows))
                self.lbl_package_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
                self.lbl_package_notify.grid()
                return None
            elif db_rows is None:
                # lg.debug(f"self.goods_id = {self.goods_id}")
                self.lbl_package_notify.config(fg='green', text=insert_new_line_symbols("Shelf Changed!"))
                self.lbl_package_notify.grid()
                # update_treeview(self.parent.master)
                return 0

        # el_exists = self.is_catalog_element_exists()
        # if el_exists is None:  #если ошибка
        #     return
        # elif el_exists:
        #     self.lbl_archive_notify.config(fg='red', text=insert_new_line_symbols("Catalog element already exists!"))
        #     self.lbl_archive_notify.grid()
        #     return

        # shelf_life = self.entry_product_shelf_life_var.get()
        # if shelf_life == '-':
        #     shelf_life = None
        # lg.debug(f"shelf_life={shelf_life}")
        if update_shelf() is None:
            return

        values = (self.goods_id,
                  self.entry_package_shelf_var.get(),
                  )
        for i, value in enumerate(values):
            self.parent.master.tree.set(self.item,
                                        column=i,
                                        value=value)
        mb.showinfo("Record Changed!", "You've successfully changed Catalog Element!")
        self.parent.master.tree.see(self.item)
        self.parent.master.tree.focus(self.item)
        self.parent.master.tree.selection_set(self.item)
        self.master.destroy()


class ArchiveFrame(tk.Frame):

    def __init__(self, parent, conn1):
        lg.info("__init__ 'ArchiveFrame'")
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.conn1 = conn1

        frame = self
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.config(background="orange")
        # Creating widgets
        self.btn_load_archive = tk.Button(frame, text="Load Database", command=self.load_archive)
        self.btn_archive = tk.Button(frame, text="Archive Database", command=self.archive)
        # Creating Label widgets
        self.lbl_archive = tk.Label(frame, text='Archive', background=frame['background'], font=('Calibri', 11, 'bold'))
        self.lbl_directory = tk.Label(frame, text='Directory', background=frame['background'])
        self.lbl_archive_number = tk.Label(frame, text='Archive Number', background=frame['background'])
        self.lbl_archive_notify = tk.Label(frame, text='Archive already exists!', background=frame['background'],
                                           font=('Calibri', 11, 'bold'), fg='red')

        # # Creating validate commands
        # vcmd = (self.register(on_validate_name),
        #         '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        # vcmd2 = (self.register(on_validate_date),
        #          '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        # vcmd3 = (self.register(on_validate_naturalnumber),
        #          '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # Creating Entry widgets
        self.entry_directory = tk.Entry(frame, state="readonly")
        self.entry_archive_number = tk.Entry(frame)

        # Creating Entry widgets's variables
        self.entry_directory_var = tk.StringVar()
        self.entry_archive_number_var = tk.StringVar()

        # Set widgets to some value.
        self.entry_directory_var.set("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/warehouse/archive/")
        self.entry_archive_number_var.set("")

        # Assigning variables to widgets    (Tell the widget to watch this variable.)
        self.entry_directory["textvariable"] = self.entry_directory_var
        self.entry_archive_number["textvariable"] = self.entry_archive_number_var

        # Binding widgets with functions
        self.entry_directory.bind('<FocusIn>', self.entry_directory.selection_range(0, END))
        self.entry_archive_number.bind('<FocusIn>', self.entry_archive_number.selection_range(0, END))

        # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
        self.lbl_archive.grid(row=0, column=0, columnspan=2)  # sticky=N+S+W+E,

        self.lbl_directory.grid(row=2, column=0, sticky='es')
        self.lbl_archive_number.grid(row=3, column=0, sticky='e')

        # self.cmb_product_name.grid(row=2, column=1, padx=(5, 0), pady=(10, 0))
        self.entry_directory.grid(row=2, column=1, padx=(15, 30), pady=(10, 0))
        self.entry_archive_number.grid(row=3, column=1, padx=(15, 30))

        self.btn_load_archive.grid(row=10, column=0, sticky='', pady=(5, 5))
        self.btn_archive.grid(row=10, column=1, sticky='', pady=(5, 5))
        self.lbl_archive_notify.grid(row=11, column=0, columnspan=2, sticky='', pady=(5, 5))

        self.lbl_archive_notify.grid_remove()
        # self.entry_directory.grid_remove()
        # self.cmb_product_name.grid_remove()

        place_window(self.parent, self)
        #
        # self.entry_product_description.config(state="normal", fg="black")
        # self.entry_product_shelf_life.config(state="normal", fg="black")
        # self.entry_archive_number.config(state="normal", fg="black")

    def archive(self):
        lg.info("#archive")

        lg.debug(f"self.archive_number = {self.entry_archive_number_var.get()}")
        self.query = f"""CALL archive(%(archive_number)s)"""
        self.parameters = ({
            'archive_number': self.entry_archive_number_var.get()
            })
        db_rows = run_commit_query(self.conn1, self.query, self.parameters)

        # lg.debug(f"db_rows={db_rows}")
        # lg.debug(f"r=.__class__ = {db_rows.__class__}")
        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
            return None
        elif isinstance(db_rows, Error):
            # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
            lg.error(error_to_str(db_rows))
            self.lbl_archive_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
            self.lbl_archive_notify.grid()
            return None
        elif db_rows is None:
            # lg.debug(f"self.goods_id = {self.goods_id}")
            self.lbl_archive_notify.config(fg='green', text=insert_new_line_symbols("Archived!"))
            self.lbl_archive_notify.grid()
            # update_treeview(self.parent.master)
            mb.showinfo("Archive Added!", "You've successfully created archive of a database!")
            self.master.destroy()
            return 0

    def load_archive(self):
        lg.info("#load_archive")
        self.lbl_archive_notify.config(fg='gray', text=insert_new_line_symbols("Loading database from archive... "
                                                                               "P.S. Don't close client untill it is "
                                                                               "loaded up", 40))
        self.lbl_archive_notify.grid()
        self.lbl_archive_notify.update_idletasks()
        lg.debug(f"self.archive_number = {self.entry_archive_number_var.get()}")
        # self.query = f"""CALL load_archive(%(archive_number)s)"""
        # self.parameters = ({
        #     'archive_number': self.entry_archive_number_var.get()
        #     })
        # db_rows = run_commit_query(self.conn1, self.query, self.parameters)
        try:
            feedback = db.load_archive(self.conn1, self.entry_archive_number_var.get())
        except exceptions.DBConnectionError:
            lg.debug("DBConnectionError")
            self.lbl_archive_notify.config(fg='red', text=insert_new_line_symbols(exceptions.DBConnectionError.msg))
            self.lbl_archive_notify.grid()
            self.conn1.disconnect()
            # mb.showerror(title="Connection Error!", message="Could not reconnect!")
        except exceptions.DBError:
            lg.debug("DBError")
            try:
                db.drop_temporary_tables(self.conn1)
            except exceptions.DBError:
                pass
            self.lbl_archive_notify.config(fg='red', text=insert_new_line_symbols(exceptions.DBError.msg))
            self.lbl_archive_notify.grid()
            self.conn1.disconnect()
            # mb.showerror(title="Database Error!", message=insert_new_line_symbols(exceptions.DBError.message))

        else:
            # elif isinstance(db_rows, Error):
            #     # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
            #     lg.error(error_to_str(db_rows))
            #     self.lbl_archive_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
            #     self.lbl_archive_notify.grid()
            #     return None

            self.lbl_archive_notify.config(fg='green', text=insert_new_line_symbols("Loaded up!"))
            self.lbl_archive_notify.grid()
            mb.showinfo("Loaded up!", "Database is loaded up from an archive!")
            # self.master.destroy()

            #     return 0





# class ChangePasswordFrame(tk.Frame):
#     def __init__(self, parent, conn1):
#         lg.info("########   CREATING ChangePasswordFrame   ########")
#         tk.Frame.__init__(self, parent)
#         self.parent = parent
#         self.conn1 = conn1
#
#         # Placing frame on form
#         self.pack(side=tk.LEFT, fill=tk.Y)
#         self.config(background="orange")
#
#         # Creating Buttons
#         # def connect_to_db():
#         #     self.add_user('')
#         self.btn_archive = tk.Button(self, text='Enter', command=lambda: self.add_user(''))
#
#         # Creating Labels
#         self.lbl_title = tk.Label(self,     text='Connection',  background=self['background'])
#         self.labelhost = tk.Label(self,     text='host:',       background=self['background'])
#         self.lbl_role = tk.Label(self, text='database:',   background=self['background'])
#         self.labeluser = tk.Label(self,     text='user:',       background=self['background'])
#         self.labelpassword = tk.Label(self, text='password:',   background=self['background'])
#         self.lbl_notify = tk.Label(self,    text='notifier',    background=self['background'],
#                                    font=('Calibri', 11, 'bold'), fg='black')
#
#         # Creating Entry widgets
#         self.entryhost = tk.Entry(self)
#         self.entry_role = tk.Entry(self)
#         self.entryuser = tk.Entry(self)
#         self.entrypassword = tk.Entry(self, bd=5, show="*")
#
#         # Creating String variables for Entry widgets
#         self.entryhostvar = tk.StringVar()
#         self.entry_role_var = tk.StringVar()
#         self.entryuservar = tk.StringVar()
#         self.entrypasswordvar = tk.StringVar()
#         # Set them to some value.
#         self.entryhostvar.set("localhost")
#         self.entry_role_var.set("warehouse")
#
#         # Tell the entry widget to watch this variable.
#         self.entryhost["textvariable"] = self.entryhostvar
#         self.entry_role["textvariable"] = self.entry_role_var
#         self.entryuser["textvariable"] = self.entryuservar
#         self.entrypassword["textvariable"] = self.entrypasswordvar
#
#         # Bind widgets with events
#         self.master.bind("<Key-Return>", self.add_user)  # binding window
#         def select_all(event):  # так выделяется ещё и если мышкой кликнуть. Почему? - Неясно, да и неважно
#             self.entrypassword.selection_range(0, END)
#         # self.entryhost.bind('<Key-Return>', self.add_user)
#         self.entryhost.bind('<FocusIn>', self.entryhost.selection_range(0, END))
#         # self.entry_role.bind('<Key-Return>', self.add_user)
#         self.entry_role.bind('<FocusIn>', self.entry_role.selection_range(0, END))
#         # self.entryuser.bind('<Key-Return>', self.add_user)
#         self.entryuser.bind('<FocusIn>', self.entryuser.selection_range(0, END))
#         # self.entrypassword.bind('<Key-Return>', self.add_user)
#         self.entrypassword.bind('<FocusIn>', self.entrypassword.selection_range(0, END))
#         self.entrypassword.bind('<FocusIn>', select_all)
#
#         # Placing widgets
#         self.lbl_title.grid(    row=0,  column=0, columnspan=2)
#         self.labelhost.grid(    row=1,  column=0, padx=(10, 0))
#         self.lbl_role.grid(row=2,  column=0, padx=(10, 0))
#         self.labeluser.grid(    row=3,  column=0, padx=(10, 0))
#         self.labelpassword.grid(row=4,  column=0, padx=(10, 0))
#
#         self.entryhost.grid(    row=1,  column=1, padx=(0, 10))
#         self.entry_role.grid(row=2,  column=1, padx=(0, 10))
#         self.entryuser.grid(    row=3,  column=1, padx=(0, 10))
#         self.entrypassword.grid(row=4,  column=1, padx=(0, 10))
#         self.btn_archive.grid(    row=5,  column=0, columnspan=2, pady=(5, 5))
#         self.lbl_notify.grid(   row=6,  column=0, columnspan=2, pady=(5, 5))
#         self.lbl_notify.grid_remove()
#
#         lg.info(f'self.conn1 = {self.conn1}')
#         self.fill_entries_with_default()
#
#         set_parent_window_req_size(self)
#         place_tk_to_screen_center(self.parent)
#         set_active(self)
#
#         # # Временно #######################
#         # self.entryuservar.set("Chyvak88")
#         # self.entrypasswordvar.set("Chyvak88")
#         # self.add_user("<Key-Return>")
#         # # Временно #######################
#
#     def add_user(self, event):
#         lg.info(f"#add_user('{self.entryhostvar.get()}', "
#                 f"'{self.entryuservar.get()}', "
#                 f"'{self.entrypasswordvar.get()}', "
#                 f"'{self.entry_role_var.get()}')"
#                 )
#         self.conn1 = Connection(self.entryhostvar.get(),
#                                 self.entryuservar.get(),
#                                 self.entrypasswordvar.get(),
#                                 self.entry_role_var.get(),
#                                 )
#         r = self.conn1.connect()
#         if r is None:
#             lg.info("Correct user and password")
#             self.lbl_notify.config(fg='green', text="Correct user and password")
#             self.lbl_notify.grid()
#             self.parent.master.conn1 = self.conn1
#             self.parent.master.btnConnect.destroy()
#             self.parent.master.initialize_user_interface()
#             self.parent.master.resizable(True, True)
#             self.parent.destroy()
#         else:
#             lg.info("Incorrect user or password!")
#             self.lbl_notify.config(fg='red', text=error_to_str(r))
#             self.lbl_notify.grid()
#             # self.parent.master.conn1 = self.conn1
#             # try:
#             #     self.parent.master.btnConnect.pack()
#             # except TclError:
#             #     lg.info("Button do not exist")
#             #     for child in self.parent.master.winfo_children():
#             #         if not(isinstance(child, Toplevel)) and not(isinstance(child, Menu)):
#             #             # lg.debug(f"child={child}")
#             #             child.destroy()
#             #     self.parent.master.initialize_unknown_user_interface()
#             # else:
#             #     lg.info("Button already exist")
#         lg.debug('OK we can write even after class element gets destroyed! '
#                  '(i suppose element lives till the end of function)')
#
#     def change_password(self):
#         lg.debug("#change_password")
#         lg.info(f"#add_user('{self.entryhostvar.get()}', "
#                 f"'{self.entryuservar.get()}', "
#                 f"'{self.entrypasswordvar.get()}', "
#                 f"'{self.entry_role_var.get()}')"
#                 )
#         self.query = f"""ALTER USER {self.entryuservar.get() + '@' + self.entryhostvar.get()}
#                          IDENTIFIED BY {self.entrypasswordvar.get()};"""
#
#         pass
#
#     def fill_entries_with_default(self):
#         if not (self.conn1 is None) and not (self.conn1.get_connection() is None):
#             self.entryhostvar.set(self.conn1.get_host())
#             self.entry_role_var.set(self.conn1.get_database())
#             self.entryuservar.set(self.conn1.get_username())
#             self.entrypasswordvar.set(self.conn1.get_password())


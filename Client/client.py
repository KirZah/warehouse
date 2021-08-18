#! /usr/bin/env python
# -*- coding: utf-8 -*-
	
"""
ТЗ на ЭТОТ проект:
    TO DO:
    - Слишком глобальные планы на проект свернуть, делать то что требуется (сервер не надо делать) 
            Вывод: всегда делать максимально точное ТЗ
    -- сделать одно представление таблицы внутри БД - готовую таблицу goods, отображать все поля
        можно сделать ещё для supplies и shipments.
    -- сделать триггеры чтобы при удалении поставки/отправки он удалял все товары связанные с ней
    -- ограничения целостности БД
        
    - Двойной клик ЛКМ - всегда только навигация (сделать чтобы storage и goods вели друг в друга)
    - Во всех неизвестных запросах выводить следующее: 
        lg.debug(f"UNKNOWN RETURN FROM DATABASE: db_rows={db_rows}")
    - вытащить on_closing из Frame-ов (только те которые используются одни в Toplevel), чтобы управлять сразу всеми
        
    DONE:
    - Реализовать просмотр записи в таблице goods. UPD: Не надо
    - Реализовать изменение записи во всех таблицах. UPD: В некоторых
    - Реализовать поиск по unique column в таблицах
    -- различные роли пользователей (Это в бд создать роли!)
    -- различные роли пользователей (GUI) (+- сделано)
    -- реализовать возможность создания архивных копий и восстановления данных из клиентского приложения
    -- добавить процедуры (нужно 6)
    - Реализовать удаление записи во всех таблицах. UPD: В некоторых
    - Проверить во всех SELECT запросах возвращение (db_rows[0][0] is None). 
        UPD: Только в случаях когда БД возвращает едиственное число (напр. "Max(id)+1")
    - при изменении в goods_id атрибута catalog_id (то есть в ChangePackage) проверять существуют ли ещё ссылки на 
        тот catalog_id котрый мы меняем и если их нету, то удаляем соответсвующий catalog_id 

    
"""
"""
https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html
Идеи по дальнейшему улучшению кода:
    На что стоит обратить внимание в превую очередь:
        На скопированное из course_work_12 (STD 1):
            - class MainTreeItemWindow
            - def on_validate_date

Некоторые пояснения:
    Выбор идёт по id специально. Так меньше значительно меньше вероятность ввести неправильные данные, 
    особенно в том, случае, когда существует много похожих названий, которые можно не так прочитать.
    Но, так менее удобно искать сущетвующий элемент. Возможно в будующем это стоит убрать...

ТЗ на случай развития проекта:
- При удалении record удалять все объекты связанные с ним:
    - Для удобства (Каждое удаление - отдельная функция, вот как они друг друга вызывают):
        1. record from suppliers: удаляем поставщика -> поставку -> товары из поставки -> (дальше  нет смысла)
        2. record from supplies: удаляем поставку -> товары из поставки -> (дальше  нет смысла)
        3. record from goods:
            сначала проверяем был ли отправлен этот товар клиенту и
            если да, то:
                запрещаем удаление записи
            если нет, то:
                удаляем товар .-> из поставки -> (дальше  нет смысла)
                              '-> (из отправки  нет смысла (т.к. если так то нарушается логика приложения ))
                                  (нельзя удалять отправленный товар, это портиворечит логике приложения)
                              '-> из хранилища
        4. record from catalog: удаляем вид товара .-> удаляем все товары данного вида -> (дальше  нет смысла)
        5. record from storage: удаляем товар из хранилища (это необходимо только если товар пропал или был удалён)
        6. record from customers: удаляем клиента -> отправку -> товары из отправки -> (дальше  нет смысла)
        7. record from shipments: удаляем отправку -> товары из отправки -> (дальше  нет смысла)
        8. record from goods_supplies
        9. record from goods_shipments

    - Для сохранения полноты отношений таблиц: ( "1:-> 2" - для каждой 2 из 1)
        1:-> 2:-> 8:-> 3:-> 5.
        2:-> 8:-> 3:-> 5.
        3:-> 8.
         '-> 5.
        4:-> 3:-> 8.
              '-> 5.
        5.
        6:-> 7:-> 9.
        7:-> 9.
    Затем можно удалить ВСЕ появивишиеся пустые поставки & отправки и ВСЕХ пустых поставщиков & клиентов
        Так же удалить  ВСЕ отсутствующие на складе виды продуктов

- Сделать свой класс Treeview унаследовав его от Tk.Treeview
    и работать с объектами Tk.Treeview через свой класс.
    Это нужно чтобы не дублировать инициализацию и схожие изменения в Treeview.

- Сделать обёртку для работы с БД, чтобы при смене используемой БД
    нужно было переписывать в разы меньше SQL запросов

- При добавлении новых товаров/покупок отображать уже существующие товары/покупки
    в соответствующей поставке/отправке

"""

import atexit

from tkinter.ttk import *
import tkinter as tk
# from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
import tkinter.font as tkFont
from tkinter import *
# from tkinter import TclError

import time

# import mysql
# import mysql.connector
# import mysql.connector.locales.eng
from mysql.connector import Error
# from mysql.connector import errorcode

from loguru import logger as lg

# from Connection import Connection
from windows import MainTreeItemWindow, AddNewProductWindow, ShipProductWindow
from frames import ConnectionFrame, AboutFrame, AssignShelfFrame, ChangePackageFrame, ChangeCatalogFrame, \
    ChangeShelfFrame, ArchiveFrame, AddUserFrame  # , ChangePasswordFrame  # , BaseWatchProductFrame
from functions import is_iterable, \
    set_active, place_tk_to_screen_center,\
    update_treeview, error_to_str, get_near_item, treeview_sort_column, on_closing
#   insert_new_line_symbols, is_date,
#   set_parent_window_req_size, place_window,
#   on_validate_name, on_validate_date, on_validate_naturalnumber, \
#   add_days_to_date,

from db import run_select_query, delete_table_records, DbRoles, DbTables


class MainWindow(tk.Tk):

    def __init__(self):
        lg.info('########   CREATING MAIN WINDOW   ########')
        tk.Tk.__init__(self)
        self.parent = self

        self.main_window_title = 'Warehouse Client'
        self.title(self.main_window_title)

        # Nulling some stuff (Just for the beauty)
        self.btnConnect = None
        # self.popupmenu = None
        self.columns = None
        self.query = None
        self.item = None
        self.frame_bot = None
        self.table = None

        # Nulling some stuff (Really needed)
        self.conn1 = None

        def initialize_menu():
            mainmenu = Menu(self)
            self.config(menu=mainmenu)

            file_menu = Menu(mainmenu, tearoff=0)
            file_menu.add_command(label="Database's Archive", command=self.create_archive_window)
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.quit)

            conn_menu = Menu(mainmenu, tearoff=0)
            conn_menu.add_command(label="Login", command=self.create_connection_window)
            # conn_menu.add_command(label="Change Password", command=self.create_change_password_window)
            conn_menu.add_separator()
            conn_menu.add_command(label="Add New User", command=self.create_add_user_window)
            # conn_menu.add_command(label="Delete User")

            help_menu = Menu(mainmenu, tearoff=0)
            # help_menu.add_command(label="Help")
            help_menu.add_separator()
            help_menu.add_command(label="About", command=self.create_about_window)

            mainmenu.add_cascade(label="File", menu=file_menu)
            mainmenu.add_cascade(label="Users", menu=conn_menu)
            mainmenu.add_cascade(label="Help", menu=help_menu)

        def initialize_styles():
            self.style1 = ttk.Style()
            self.style1.configure("mystyle.Treeview", highlightthickness=0, bd=0,
                                  font=('Calibri', 11))  # Modify the font of the body
            self.style1.configure("mystyle.Treeview.Heading",
                                  font=('Calibri', 13, 'bold'))  # Modify the font of the headings
            self.style1.layout("mystyle.Treeview",
                               [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

        def set_window_parameters():
            # self.minsize(int(self.parent.winfo_screenwidth() * 1 / 3),
            #              int(self.parent.winfo_screenheight() * 1 / 3))
            self.minsize(720, 300)
            self.maxsize(self.parent.winfo_screenwidth(), self.parent.winfo_screenheight())
            default_width = int(self.winfo_screenwidth() * 5 / 10)
            default_height = int(self.winfo_screenheight() * 5 / 10)
            self.geometry(str(default_width) + 'x' + str(default_height))
            self.resizable(True, True)

        # initializing window
        initialize_menu()
        initialize_styles()
        self.initialize_unknown_user_interface()
        set_window_parameters()

        # Placing window
        self.update_idletasks()
        place_tk_to_screen_center(self)

        self.create_connection_window()

    def initialize_unknown_user_interface(self):
        lg.info("#initialize_unknown_user_interface")
        # self.conn1 = None
        # try:
        for child in self.winfo_children():
            if not (isinstance(child, Toplevel)) and not (isinstance(child, Menu)):
                # lg.debug(f"child={child}")
                child.destroy()
        # except TclError:
        #     pass
        self.btnConnect = tk.Button(self,
                                    text="Установить соединение с БД",
                                    command=self.create_connection_window)
        self.btnConnect.pack()

    def initialize_user_interface(self):
        lg.info("#initialize_user_interface")

        def initialize_top_frame(user_role):
            self.frame_top = tk.Frame()
            self.frame_top.pack(side=tk.TOP, fill=tk.X, expand=False)
            self.frame_top.config(background="lavender")
            font_bold = tkFont.Font(font=('Calibri', 11, 'bold'))  # family="Lucida Grande", size=20

            able_tables = set()
            if user_role in {DbRoles.developer, DbRoles.administrator, DbRoles.director, DbRoles.boss,
                             DbRoles.pc_operator}:
                able_tables = {DbTables.suppliers, DbTables.supplies, DbTables.catalog, DbTables.goods,
                               DbTables.storage, DbTables.shipments, DbTables.customers}
            elif user_role == DbRoles.warehouseman:
                able_tables = {DbTables.catalog, DbTables.goods, DbTables.storage}
            elif user_role == DbRoles.salesman:
                able_tables = {DbTables.catalog, DbTables.goods, DbTables.customers}
            else:
                able_tables = {DbTables.suppliers, DbTables.supplies, DbTables.catalog, DbTables.goods,
                               DbTables.storage, DbTables.shipments, DbTables.customers}
                lg.debug(f"top_frame interface doesn't exist for user '{user_role}'")
                # self.quit()

            self.lbl_show = tk.Label(self.frame_top,            text="Tables:")
            self.btn_showgoods = tk.Button(self.frame_top,      text="Goods",       command=self.show_goods)
            self.btn_showcatalog = tk.Button(self.frame_top,    text="Catalog",     command=self.show_catalog)
            if DbTables.storage in able_tables:
                self.btn_showstorage = tk.Button(self.frame_top, text="Storage", command=self.show_storage)
            if DbTables.supplies in able_tables:
                self.btn_showsupplies = tk.Button(self.frame_top,   text="Supplies",    command=self.show_supplies)
            if DbTables.shipments in able_tables:
                self.btn_showshipments = tk.Button(self.frame_top,  text="Shipments",   command=self.show_shipments)
            if DbTables.suppliers in able_tables:
                self.btn_showsuppliers = tk.Button(self.frame_top,  text="Suppliers",   command=self.show_suppliers)
            if DbTables.customers in able_tables:
                self.btn_showcustomers = tk.Button(self.frame_top,  text="Customers",   command=self.show_customers)
            self.entry_search = tk.Entry(self.frame_top)

            # photo = tk.PhotoImage(file="search.PNG").subsample(3, 3)
            self.btn_search = tk.Button(self.frame_top,   text="\u2315", font=font_bold,
                                        command=self.search_row,
                                        fg='darkblue', bg=self.frame_top["background"],
                                        # image=photo,
                                        # width=10, height=15, compound="c"
                                        )  # ⌕
            # self.btn_search.bind("<Button-1>", self.search_row)

            self.btn_update_treeview = tk.Button(self.frame_top, text="\u21BB", command=lambda: update_treeview(self),
                                                 fg='darkblue', bg='yellow', font=('Calibri', 11, 'bold'))  # ↻

            # self.btn_exit = tk.Button(self, command=self.master.quit,
            #                           text="Close",
            #                           image=pixelVirtual,
            #                           width=15, height=20,
            #                           compound="c"
            #                           )

            self.entry_search_var = tk.StringVar()
            self.entry_search_var.set("")
            self.entry_search["textvariable"] = self.entry_search_var
            self.entry_search.bind("<Key-Return>", self.search_row)
            # self.entry_search.bind("<FocusOut>", self.search_row)

            def select_all(event):  # так выделяется ещё и если мышкой кликнуть. Почему? - Неясно, да и неважно
                self.entry_search.selection_range(0, END)
            self.entry_search.bind('<FocusIn>', self.entry_search.selection_range(0, END))
            self.entry_search.bind('<FocusIn>', select_all)

            self.lbl_show.pack(side=tk.LEFT,                padx=(5, 5))  # fill=tk.Y,     pady=5)
            self.btn_showgoods.pack(side=tk.LEFT,           padx=(5, 0))  # fill=tk.Y,    pady=(0, 5))
            self.btn_showcatalog.pack(side=tk.LEFT,         padx=(1, 0))  # fill=tk.Y,     pady=(0, 5))
            if DbTables.storage in able_tables:
                self.btn_showstorage.pack(side=tk.LEFT,         padx=(1, 0))  # fill=tk.Y,     pady=(0, 5))
            if DbTables.supplies in able_tables:
                self.btn_showsupplies.pack(side=tk.LEFT,        padx=(30, 0))  # fill=tk.Y,    pady=(0, 5))
            if DbTables.shipments in able_tables:
                self.btn_showshipments.pack(side=tk.LEFT,       padx=(1, 0))  # fill=tk.Y,     pady=(0, 5))
            if DbTables.suppliers in able_tables:
                self.btn_showsuppliers.pack(side=tk.LEFT,       padx=(30, 0))  # fill=tk.Y,    pady=(0, 5))
            if DbTables.customers in able_tables:
                self.btn_showcustomers.pack(side=tk.LEFT,       padx=(1, 0))  # fill=tk.Y,    pady=(0, 5))

            self.btn_update_treeview.pack(side=tk.RIGHT,    padx=(0, 0))  # fill=tk.Y, ,    pady=(0, 5))
            self.btn_search.pack(side=tk.RIGHT,              padx=(0, 20), fill=tk.Y,     pady=(5, 3))
            self.entry_search.pack(side=tk.RIGHT,            padx=(30, 0), fill=tk.Y,     pady=(5, 3))

        def initialize_bot_frame():
            self.frame_bot = tk.Frame(self.parent)
            self.frame_bot.config(background="dimgray")
            self.frame_bot.pack(side=tk.BOTTOM, fill=tk.X, expand=False)

            self.lbl_db_loadtime = tk.Label(self.frame_bot, text="Load Time: -", width=21)
            self.lbl_db_loadtime.pack(side=tk.RIGHT, fill=tk.Y)
            self.lbl_db_loadtime.config(background=self.frame_bot["background"])

            self.lbl_rows_amount = tk.Label(self.frame_bot, text="Rows Amount: -")
            self.lbl_rows_amount.pack(side=tk.LEFT, fill=tk.Y)
            self.lbl_rows_amount.config(background=self.frame_bot["background"])

        def initialize_right_frame(user_role):
            self.frame_right = tk.Frame()
            self.frame_right.pack(side=tk.RIGHT, fill=tk.Y)
            self.frame_right.config(background="darkgray")

            able_actions = set()
            if user_role in {DbRoles.administrator, DbRoles.developer, DbRoles.director, DbRoles.boss}:
                able_actions = {"add products", "assign shelf", "ship products"}
            elif user_role == DbRoles.pc_operator:
                able_actions = {"add products", "ship products"}
            elif user_role == DbRoles.warehouseman:
                able_actions = {"assign shelf"}
            elif user_role == DbRoles.salesman:
                able_actions = set() # {"add customers"}
            else:
                able_actions = {"add products", "assign shelf", "ship products"}
                lg.debug(f"right_frame Interface doesn't exist for user '{user_role}'")

            if able_actions != set():
                self.lbl_action = tk.Label(self.frame_right, text="Actions:")
            if "add products" in able_actions:
                self.btn_add_products = tk.Button(self.frame_right, text="Add Products",
                                                  command=lambda: AddNewProductWindow(self, self.conn1))
            if "assign shelf" in able_actions:
                self.btn_assign_shelf = tk.Button(self.frame_right, text="Assign Shelf",
                                                  command=self.create_assign_shelf_window)
            if "ship products" in able_actions:
                self.btn_ship_products = tk.Button(self.frame_right, text="Ship Products",
                                                   command=lambda: ShipProductWindow(self, self.conn1))
            # if "add customers" in able_actions:
            #     self.btn_add_customers = tk.Button(self.frame_right, text="Add Customers",
            #                                        command=self.create_add_customers_window)

            if able_actions != set():
                self.lbl_action.pack(side=tk.TOP, pady=(5, 5), expand=False)
            if "add products" in able_actions:
                self.btn_add_products.pack(side=tk.TOP, fill=tk.X, pady=(5, 0), expand=False)
            if "assign shelf" in able_actions:
                self.btn_assign_shelf.pack(side=tk.TOP, fill=tk.X, pady=(5, 0), expand=False)
            if "ship products" in able_actions:
                self.btn_ship_products.pack(side=tk.TOP, fill=tk.X, pady=(5, 0), expand=False)

        def initialize_tree():
            # Уже в self.columns нужно заносить те значения которые хотим отображать,
            # иначе сортировка изменит оглавления
            self.columns = ('default_column_name',)
            self.tree = ttk.Treeview(self.parent, columns=self.columns, style="mystyle.Treeview")
            self.tree['show'] = 'headings'  # Прячу первый столбец который text
            self.tree.bind("<Double-1>", self.on_double_click)
            self.tree.bind("<Button-3>", self.on_right_click)
            self.tree.tag_configure('gray', background='gray')
            self.tree.tag_configure('lightgray', background='lightgray')

            self.vsb = tk.Scrollbar(self, orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=self.vsb.set)
            self.vsb.pack(side="right", fill="y")

            self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
            self.tree.configure(xscrollcommand=self.hsb.set)
            self.hsb.pack(side="bottom", fill="x")

            self.tree.config(height=int(self.parent.winfo_screenheight() * 7 / 10))
            self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        user_role = self.conn1.get_role()
        # lg.debug(f"db_user={user_role}")
        initialize_top_frame(user_role)
        initialize_bot_frame()
        initialize_right_frame(user_role)
        initialize_tree()

        if user_role not in {DbRoles.developer, DbRoles.administrator, DbRoles.director, DbRoles.boss,
                             DbRoles.pc_operator, DbRoles.warehouseman, DbRoles.salesman}:
            mb.showwarning(f"Unknown user's role!",
                           f"Particular interface doesn't exist for user '{self.conn1.get_username()}'"
                           "You logged in successfully, but particular interface for this user does not exist yet! "
                           "Whole interface will be shown, but you might not be able to use part of it")

        self.popupmenu = Menu(self.tree, tearoff=0)
        self.show_goods()
        set_active(self)


    def search_row(self, event=''):
        lg.debug("#search_row")
        # self.btn_search.config(relief=SUNKEN)  # state="disabled",
        def get_btn_name_selected():
            for child in self.frame_top.winfo_children():
                # lg.info(f"child={child}")
                if isinstance(child, Button):
                    # lg.debug(f'main_window.child["state"] = {child["state"]}')
                    if child["state"] == "disabled":
                        return child["text"].lower()

        btn_name = get_btn_name_selected()
        lg.debug(f"btn_name={btn_name}")
        if btn_name == 'goods':
            self.query = """SELECT * FROM goods_view
                               WHERE id LIKE %(id)s
                               ;"""  # ORDER BY id DESC
            self.parameters = ({'id': self.entry_search_var.get() + '%'})
        elif btn_name == 'catalog':
            self.query = """
                          SELECT id, product_name, price, shelf_life, description FROM catalog
                           WHERE product_name LIKE %(product_name)s
                           ORDER BY product_name DESC;"""
            self.parameters = ({'product_name': self.entry_search_var.get() + '%'})
        elif btn_name == 'storage':
            self.query = """
                          SELECT goods_id, shelf FROM storage
                           WHERE goods_id LIKE %(goods_id)s
                           ORDER BY goods_id DESC;"""
            self.parameters = ({'goods_id': self.entry_search_var.get() + '%'})
        elif btn_name == 'suppliers':
            self.query = """
                          SELECT id, name, address, phone, email, note FROM suppliers
                          WHERE name LIKE %(name)s
                          ORDER BY name DESC;"""
            self.parameters = ({'name': self.entry_search_var.get() + '%'})
        elif btn_name == 'customers':
            self.query = """
                          SELECT id, name, address, phone, email, note FROM customers
                          WHERE name LIKE %(name)s
                          ORDER BY name DESC;"""
            self.parameters = ({'name': self.entry_search_var.get() + '%'})
        elif btn_name == 'supplies':
            self.query = """
                       SELECT supplies.id, name, date, delivery_note, supplies.note
                               FROM supplies LEFT JOIN suppliers ON supplies.suppliers_id = suppliers.id
                               WHERE delivery_note LIKE %(delivery_note)s
                       ORDER BY delivery_note DESC;"""
            self.parameters = ({'delivery_note': self.entry_search_var.get() + '%'})
        elif btn_name == 'shipments':
            self.query = """
                       SELECT shipments.id, name as "Customers Name", date, delivery_note, shipments.note
                               FROM shipments LEFT JOIN customers ON shipments.customers_id = customers.id
                               WHERE delivery_note LIKE %(delivery_note)s
                       ORDER BY delivery_note DESC;"""
            self.parameters = ({'delivery_note': self.entry_search_var.get() + '%'})
        else:
            lg.error(f"#CANT SEARCH button '{btn_name}'")

        self.viewing_table_records()
        # time.sleep(0.1)
        # self.btn_search.config(relief=RAISED)  # state="normal",

    def viewing_table_records(self):
        lg.info("#viewing_table_records")
        for element in self.tree.get_children():
            self.tree.delete(element)
        self.lbl_rows_amount.config(text=f"Rows Amount: ...")
        self.lbl_db_loadtime.config(text=f"Load Time: ...")
        self.frame_bot.update_idletasks()

        start_time = time.monotonic()
        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        # lg.debug(f"db_rows={db_rows}")
        mysql_request_time = time.monotonic() - start_time
        lg.info(f"Время получения результата Mysql Запроса: {str(mysql_request_time)[0:5]} sec.")
        if mysql_request_time > 10:
            lg.debug(f"Too long mysql_request_time (= {str(mysql_request_time)[0:5]} sec.)")
        start_time = time.monotonic()

        if db_rows == -1:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
            return
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
            if db_rows.errno == 1142:
                mb.showerror("Access denied", "You haven't got permission to watch this table")
        elif db_rows == []:
            lg.debug('Recieved empty array')
            load_time = time.monotonic() - start_time
            self.lbl_rows_amount.config(text=f"Rows Amount: 0")
            self.lbl_db_loadtime.config(text=f"Load Time: {str(load_time + mysql_request_time)[0:5]} sec.")
            mb.showinfo(title="Empty Table!", message="This table is empty!")
            return
        elif is_iterable(db_rows):
            rows_amount = len(db_rows)              # чтобы видеть загрузку
            freq = int(rows_amount / 10)            # чтобы видеть загрузку  130k rows loads in 3.7 - 3.8 sec. with
            i = 0                                   # чтобы видеть загрузку  130k rows loads in 3.4 - 3.5 sec. without
            for row in db_rows:
                if self.table == DbTables.goods and row[3] == 'sold':
                    self.tree.insert("", 0, "", text='', values=row, tag='gray')
                else:
                    self.tree.insert("", 0, "", text='', values=row, tag='lightgray')
                i += 1                              # чтобы видеть загрузку
                if i == freq:                       # чтобы видеть загрузку
                    i = 0                           # чтобы видеть загрузку
                    self.tree.update_idletasks()    # чтобы видеть загрузку

            load_time = time.monotonic() - start_time
            lg.info(f"Время вывода результата Mysql Запроса: {str(load_time)[0:5]} sec.")
            self.lbl_db_loadtime.config(text=f"Load Time: {str(load_time + mysql_request_time)[0:5]} sec.")
            self.lbl_rows_amount.config(text=f"Rows Amount: {rows_amount}")
            return
        elif db_rows is None:
            lg.critical('That line should be unreachable!')
        self.lbl_rows_amount.config(text=f"Rows Amount: -")
        self.lbl_db_loadtime.config(text=f"Load Time: -")

    def delete_table_records(self, table_name):

        near_item = get_near_item(self.tree, self.item)
        success_delete = delete_table_records(self.conn1, table_name,
                                              self.tree.item(self.item, "values")[0])
        if success_delete is None:
            return
        else:
            if near_item != '':
                self.tree.selection_set(near_item)
            # update_treeview(self)


    def change_btn_selected(self):
        lg.info("#change_btn_selected")
        self.tree.unbind("<Double-1>")  # Убрать в будущем
        try:
            self.frame_top.pack()
            for child in self.frame_top.winfo_children():
                if isinstance(child, Button):
                    # lg.debug(f"child={child}")
                    child.config(relief=RAISED, state="normal")
                    # Значения relief:  flat, groove, raised, ridge, solid, or sunken
                    # Значения  state:  active, disabled, or normal
        except TclError:
            lg.info("Frame do not exist")

        try:
            self.entry_search_var.set("")
        except BaseException:
            lg.info("search do not exist yet")

    def change_tree_columns(self):
        lg.info("#change_tree_columns")

        def set_treeview_column_defaults():
            for col in self.columns:
                self.tree.heading(col, anchor=tk.W)  # , text='default_column_heading'
                self.tree.column(col, width=100, minwidth=50, stretch=tk.NO)

        def enable_treeview_sorting():  # must do each time when columns change
            for col in self.columns:
                # SORTING COMMAND DELETED (MUST BE DONE IN QUERIES CAUSE IT'S NOT A TRIVIAL OPERATION)
                # self.tree.heading(col, text=col, command=lambda _col=col:
                #                   treeview_sort_column(self.tree, _col, False))
                self.tree.heading(col, text=col)

        self.tree.config(columns=self.columns)
        set_treeview_column_defaults()
        enable_treeview_sorting()


    def show_goods(self):
        lg.info('#show_goods')

        def change_tree_cols():
            self.change_tree_columns()
            # self.tree.column('#0', width=0, minwidth=0, stretch=tk.NO)
            self.tree.column('id', width=50, minwidth=40, stretch=tk.NO)
            self.tree.column('#2', width=150, minwidth=150, stretch=tk.NO)
            self.tree.column('#3', width=70, minwidth=70, stretch=tk.NO)
            self.tree.column('#4', width=45, minwidth=45, stretch=tk.NO)
            self.tree.column('#5', width=100, minwidth=100, stretch=tk.NO)
            self.tree.column('#6', width=100, minwidth=100, stretch=tk.NO)
            self.tree.column('#7', width=150, minwidth=150, stretch=tk.NO)
            self.tree.column('#8', width=150, minwidth=150, stretch=tk.NO)
        # Change chosen table
        self.change_btn_selected()
        self.btn_showgoods.config(relief=SUNKEN, state="disabled")
        self.table = DbTables.goods
        # Уже в self.columns нужно заносить те значения которые хотим отображать, иначе сортировка изменит оглавления
        # Хотя если вызвать self.enable_treeview_sorting() до обозначения имен столбцов и строк,
        # то можно установить дефолтные значения навсегда

        # Change Treeview
        # self.tree.bind("<Double-1>", self.on_double_click)
        self.columns = ('id', 'Product Name', 'Price', 'State', 'Production Date',
                        'Expiration Date', 'Description', 'Note')
        change_tree_cols()

        # Change popupmenu
        self.popupmenu.delete(0, END)
        self.popupmenu.add_command(label="Change record", command=self.create_change_product_window)
        self.popupmenu.add_command(label="Delete record",
                                   command=lambda:
                                   self.delete_table_records("goods"))
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label="Show Package Info")  # , command=self.show_goods_item)
        self.popupmenu.entryconfig("Show Package Info", state="disabled")
        # Change query
        self.query = """SELECT * FROM goods_view"""
        self.parameters = ()
        self.viewing_table_records()

    def show_catalog(self):
        lg.info('showing catalog')
        # Change chosen table
        self.change_btn_selected()
        self.btn_showcatalog.config(relief=SUNKEN, state="disabled")
        self.table = DbTables.catalog

        # Change Treeview
        self.columns = ('id', 'Product Name', 'Price', 'shelf_life', 'Description')
        self.change_tree_columns()
        self.tree.bind("<Double-1>", self.on_double_click)

        # Change popupmenu
        self.popupmenu.delete(0, END)
        self.popupmenu.add_command(label="Change record", command=self.create_change_catalog_frame)
        self.popupmenu.add_command(label="Delete record",
                                   command=lambda:
                                   self.delete_table_records("catalog"))
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label="Show Related Products", command=lambda: MainTreeItemWindow(self, self.conn1))
        # self.popupmenu.add_command(label="Show Product Info")

        # Change query
        self.query = """SELECT id, Product_name, Price, shelf_life, description FROM catalog
                           ORDER BY id DESC;"""
        self.parameters = ()
        self.viewing_table_records()

    def show_suppliers(self):
        lg.info('showing suppliers')
        # Change chosen table
        self.change_btn_selected()
        self.btn_showsuppliers.config(relief=SUNKEN, state="disabled")
        self.table = DbTables.suppliers

        # Change Treeview
        self.columns = ('id', "Supplier's Name", 'Address', 'Phone', 'Email', 'Note')
        self.change_tree_columns()
        self.tree.bind("<Double-1>", self.on_double_click)

        # Change popupmenu
        self.popupmenu.delete(0, END)
        self.popupmenu.add_command(label="Change record")
        self.popupmenu.add_command(label="Delete record",
                                   command=lambda:
                                   self.delete_table_records("suppliers"))
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label="Show Related Supplies", command=lambda: MainTreeItemWindow(self, self.conn1))
        # self.popupmenu.add_command(label="Show Supplier Info")
        self.popupmenu.entryconfig("Change record", state="disabled")

        # Change query
        self.query = """SELECT id, Name, Address, Phone, Email, Note FROM suppliers
                           ORDER BY id DESC;"""
        self.parameters = ()
        self.viewing_table_records()

    def show_supplies(self):
        lg.info('showing supplies')
        # Change chosen table
        self.change_btn_selected()
        self.btn_showsupplies.config(relief=SUNKEN, state="disabled")
        self.table = DbTables.supplies

        # Change Treeview
        self.columns = ('id', "Supplier's Name", 'Date', 'Delivery Note', 'Note')
        self.change_tree_columns()
        self.tree.bind("<Double-1>", self.on_double_click)

        # Change popupmenu
        self.popupmenu.delete(0, END)
        self.popupmenu.add_command(label="Change record")
        self.popupmenu.add_command(label="Delete record",
                                   command=lambda:
                                   self.delete_table_records("supplies"))
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label="Show Related Products", command=lambda: MainTreeItemWindow(self, self.conn1))
        # self.popupmenu.add_command(label="Show Supply Info")
        self.popupmenu.entryconfig("Change record", state="disabled")

        # Change query
        self.query = """SELECT supplies.id, name, date, delivery_note, supplies.note 
                               FROM supplies LEFT JOIN suppliers ON supplies.suppliers_id = suppliers.id
                               ORDER BY id DESC;"""
        self.parameters = ()
        self.viewing_table_records()

    def show_storage(self):
        lg.info('showing storage')
        # Change chosen table
        self.change_btn_selected()
        self.btn_showstorage.config(relief=SUNKEN, state="disabled")
        self.table = DbTables.storage

        # Change Treeview
        self.columns = ('Package id', 'Shelf')
        self.change_tree_columns()
        self.tree.bind("<Double-1>", self.on_double_click)

        # Change popupmenu
        self.popupmenu.delete(0, END)
        self.popupmenu.add_command(label="Change record", command=self.create_change_shelf_frame)
        self.popupmenu.add_command(label="Delete record",
                                   command=lambda:
                                   self.delete_table_records("storage"))
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label="Show Related Product", command=lambda: MainTreeItemWindow(self, self.conn1))
        # self.popupmenu.add_command(label="Show Storage Info")  # пригодится когда добавится вес товара
        # self.popupmenu.entryconfig("Change record", state="disabled")

        # Change query
        self.query = """SELECT goods_id, shelf FROM storage
                           ORDER BY goods_id DESC;"""
        self.parameters = ()
        self.viewing_table_records()

    def show_customers(self):
        lg.info('showing customers')
        # Change chosen table
        self.change_btn_selected()
        self.btn_showcustomers.config(relief=SUNKEN, state="disabled")
        self.table = DbTables.customers

        # Change Treeview
        self.columns = ('id', "Client's Name", 'Address', 'Phone', 'Email', 'Note')
        self.change_tree_columns()
        self.tree.bind("<Double-1>", self.on_double_click)

        # Change popupmenu
        self.popupmenu.delete(0, END)
        self.popupmenu.add_command(label="Change record")
        self.popupmenu.add_command(label="Delete record",
                                   command=lambda:
                                   self.delete_table_records("customers"))
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label="Show Related Shipments", command=lambda: MainTreeItemWindow(self, self.conn1))
        # self.popupmenu.add_command(label="Show Customer Info")
        self.popupmenu.entryconfig("Change record", state="disabled")

        # Change query
        self.query = """SELECT id, Name, Address, Phone, Email, Note FROM customers 
                        ORDER BY id DESC;"""
        self.parameters = ()
        self.viewing_table_records()

    def show_shipments(self):
        lg.info('showing shipments')
        # Change chosen table
        self.change_btn_selected()
        self.btn_showshipments.config(relief=SUNKEN, state="disabled")
        self.table = DbTables.shipments

        # Change Treeview
        self.columns = ('id', "Customer's Name", 'Date', 'Delivery Note', 'Note')
        self.change_tree_columns()
        self.tree.bind("<Double-1>", self.on_double_click)

        # Change popupmenu
        self.popupmenu.delete(0, END)
        self.popupmenu.add_command(label="Change record")
        self.popupmenu.add_command(label="Delete record",
                                   command=lambda:
                                   self.delete_table_records("shipments"))
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label="Show Related Products", command=lambda: MainTreeItemWindow(self, self.conn1))
        # self.popupmenu.add_command(label="Show Shipment Info")
        self.popupmenu.entryconfig("Change record", state="disabled")

        # Change query
        self.query = """
           SELECT shipments.id, name as "Customers Name", date, delivery_note, shipments.note
                   FROM shipments LEFT JOIN customers ON shipments.customers_id = customers.id
           ORDER BY id DESC;"""
        self.parameters = ()
        self.viewing_table_records()


    def on_double_click(self, event):
        self.item = self.tree.identify('item', event.x, event.y)
        lg.info(f"you clicked on self.item='{self.item}'")
        if not (self.item == ''):
            lg.info(f'you double-clicked on {self.tree.item(self.item, "values")[0]}')
            MainTreeItemWindow(self, self.conn1)
        else:
            lg.info(f"you double-clicked on header or non-exist row")

    def on_right_click(self, event):
        lg.info("#on_right_click")
        self.item = self.tree.identify('item', event.x, event.y)
        lg.info(f"you clicked on self.item='{self.item}'")
        if not (self.item == ''):
            lg.info(f'you right-clicked on {self.tree.item(self.item, "values")[0]}')
            # self.tree.focus(self.item)
            self.tree.selection_set(self.item)
            self.popupmenu.tk_popup(event.x_root, event.y_root, 0)
        else:
            lg.info(f"you right-clicked on header or non-exist row")


    def create_connection_window(self):
        lg.info("#create_connection_window")
        conn_window = tk.Toplevel(self)
        conn_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(conn_window))
        conn_window.title("Login")
        ConnectionFrame(conn_window, self.conn1)

    def create_add_user_window(self):
        lg.info("#create_add_user_window")
        add_user_window = tk.Toplevel(self)
        add_user_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(add_user_window))
        add_user_window.title("Add User")
        AddUserFrame(add_user_window, self.conn1)


    def create_archive_window(self):
        lg.info("#create_connection_window")
        conn_window = tk.Toplevel(self)
        conn_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(conn_window))
        conn_window.title("Warehouse Archive")
        ArchiveFrame(conn_window, self.conn1)

    # def create_change_password_window(self):
    #     lg.info("#create_change_password_window")
    #     conn_window = tk.Toplevel(self)
    #     conn_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(conn_window))
    #     conn_window.title(str(self.title()) + " - Change Password")
    #     ChangePasswordFrame(conn_window, self.conn1)

    def create_about_window(self):
        lg.info("#create_about_window")
        about_window = tk.Toplevel(self)
        about_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(about_window))
        about_window.title(self.main_window_title + " - About")
        AboutFrame(about_window)

    def create_assign_shelf_window(self):
        lg.info("#create_assign_shelf_window")
        assign_shelf_window = tk.Toplevel(self)
        assign_shelf_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(assign_shelf_window))
        assign_shelf_window.title("Assigning Shelf")
        AssignShelfFrame(assign_shelf_window, self.conn1)

    # def show_goods_item(self):  # UNUSED
    #     goods_id = self.tree.item(self.item, "values")[0]
    #     lg.info(f"#show_goods_item (self.item={self.item}, id = {goods_id})")
    #     watch_product_window = tk.Toplevel(self)
    #     watch_product_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(watch_product_window))
    #     watch_product_window.title("Package Info")
    #     BaseWatchProductFrame(watch_product_window, goods_id)

    def create_change_product_window(self):
        goods_id = self.tree.item(self.item, "values")[0]
        lg.info(f"#create_change_product_window (self.item={self.item}, id = {goods_id})")
        change_package_window = tk.Toplevel(self)
        change_package_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(change_package_window))
        change_package_window.title("Change Package")
        ChangePackageFrame(change_package_window, self.conn1, self.item)

    def create_change_catalog_frame(self):
        catalog_id = self.tree.item(self.item, "values")[0]
        lg.info(f"#create_change_catalog_frame (self.item={self.item}, id = {catalog_id})")
        change_product_window = tk.Toplevel(self)
        change_product_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(change_product_window))
        change_product_window.title("Change Product")
        ChangeCatalogFrame(change_product_window, self.conn1, self.item)

    def create_change_shelf_frame(self):
        goods_id = self.tree.item(self.item, "values")[0]
        lg.info(f"#create_change_catalog_frame (self.item={self.item}, id = {goods_id})")
        change_shelf_window = tk.Toplevel(self)
        change_shelf_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(change_shelf_window))
        change_shelf_window.title("Change Shelf")
        ChangeShelfFrame(change_shelf_window, self.conn1, self.item)


@atexit.register
def on_exit_client():
    lg.log("Client", "Client Closed!")


if __name__ == "__main__":
    new_level = lg.level("Client", no=38, color="<yellow>", icon="🐍")

    lg.log("Client", "Client Started!")
    root = MainWindow()
    root.mainloop()


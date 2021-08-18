import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb

from datetime import datetime

from mysql.connector import Error
from loguru import logger as lg

# from Frames import ConnectionFrame, AboutFrame
from functions import (is_date, is_iterable, insert_new_line_symbols,  # \
                       get_near_item,
                       set_active, set_parent_window_req_size, place_tk_to_screen_center,  # place_window, \
                       # on_validate_name, on_validate_date, on_validate_naturalnumber, add_days_to_date, \
                       update_treeview, error_to_str, treeview_sort_column)

from db import add_records_to_cmb, run_select_query, run_commit_query, delete_table_records


class AddNewProductWindow(tk.Toplevel):

    def __init__(self, parent, conn1):
        self.parent = parent
        self.conn1 = conn1
        tk.Toplevel.__init__(self, parent)

        self.parameters = None
        self.query = None

        self.frame_product = None
        self.frame_supply = None

        self.supplier_id = None
        self.supply_id = None
        self.catalog_id = None
        self.goods_id = None
        self.goods_supplies_id = None
        # self.conn1 = conn1
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        lg.debug('########   CREATING AddNewProductWindow  ########')
        self.title('Add Products')

        # self.minsize(int(self.parent.winfo_screenwidth() * 1.48 / 10),
        #              int(self.parent.winfo_screenheight() * 3.5 / 10))
        # self.maxsize(int(self.parent.winfo_screenwidth()), int(self.parent.winfo_screenheight()))
        #
        self.style1 = ttk.Style()
        self.style1.configure("mystyle.Treeview", highlightthickness=0, bd=0,
                              font=('Calibri', 11))  # Modify the font of the body
        self.style1.configure("mystyle.Treeview.Heading",
                              font=('Calibri', 13, 'bold'))  # Modify the font of the headings
        self.style1.layout("mystyle.Treeview",
                           [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

        # self.frame_top = tk.Frame(self)
        # self.frame_top.pack(side=tk.TOP, fill=tk.Y, expand=False)
        # self.frame_top.config(background="darkorange")
        #
        # # self.lbl_show = tk.Label(self.frame_top, text="Showing Supply #" + self.item_id)
        # self.lbl_show = tk.Label(self.frame_top, text="New supply")
        # self.lbl_show.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5, expand=False)

        def adding_supplier():
            lg.info("#adding_supplier")

            def clear_supplier_new():
                lg.info("#clear_supplier_new")
                self.entrysuppliernamevar.set(self.cmbsuppliernamevar.get())
                self.entrysuppliernamevar.set("")
                self.entry_supplier_address_var.set('')
                self.entry_supplier_phone_var.set('')
                self.entry_supplier_email_var.set('')
                self.entry_supplier_note_var.set('')
                self.lbl_supplier_notify.grid_remove()

            # self.entry_customer_name['state'] = 'normal'
            # self.cmb_customer_name['state'] = 'readonly'
            self.btn_supplier_new.config(relief=SUNKEN, state="disabled")
            self.btn_supplier_exists.config(relief=RAISED, state="normal")
            self.cmbsuppliername.grid_remove()
            self.entrysuppliername.grid()

            self.entry_supplier_address.config(state="normal")
            self.entry_supplier_phone.config(state="normal")
            self.entry_supplier_email.config(state="normal")
            self.entry_supplier_note.config(state="normal")
            clear_supplier_new()

        def choosing_supplier():
            lg.info("#choosing_supplier")

            def clear_supplier_exists():
                lg.info("#clear_supplier_exists")
                # self.cmb_customer_name_var.set(self.entry_customer_id_var.get())
                # self.cmb_customer_name_var.set('')
                self.entry_supplier_address_var.set('')
                self.entry_supplier_phone_var.set('')
                self.entry_supplier_email_var.set('')
                self.entry_supplier_note_var.set('')
                self.lbl_supplier_notify.grid_remove()

            # self.entry_customer_name['state'] = 'readonly'
            # self.cmb_customer_name['state'] = 'normal'
            self.btn_supplier_exists.config(relief=SUNKEN, state="disabled")
            self.btn_supplier_new.config(relief=RAISED, state="normal")
            self.entrysuppliername.grid_remove()
            self.cmbsuppliername.grid()

            self.entry_supplier_address.config(state="readonly")
            self.entry_supplier_phone.config(state="readonly")
            self.entry_supplier_email.config(state="readonly")
            self.entry_supplier_note.config(state="readonly")
            clear_supplier_exists()

            self.query = """
                           select address, phone, email, note from suppliers
                           where name = %(name)s
                           ORDER BY name ASC"""
            self.parameters = ({'name': self.cmbsuppliernamevar.get()})
            self.show_chosen_supplier()

        def combobox_selected(event):
            lg.info("#combobox_selected")
            lg.info(f'you\'ve selected "{self.cmbsuppliername.selection_get()}"')
            # self.parameters = ({'name': self.suppliernamevar.get()+'%'})
            self.parameters = ({'name': self.cmbsuppliername.selection_get()})
            self.query = """
                       select address, phone, email, note from suppliers
                       where name = %(name)s
                       ORDER BY name ASC
                       """
            self.show_chosen_supplier()

        self.frame_supplier = tk.Frame(self)
        self.frame_supplier.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_supplier.config(background="orange")

        # Creating Button widgets
        self.btn_supplier_enter = tk.Button(self.frame_supplier, text="Enter", command=self.enter_supplier)
        self.btn_supplier_new = tk.Button(self.frame_supplier, text="Add New", command=adding_supplier)
        self.btn_supplier_exists = tk.Button(self.frame_supplier, text="Already Exists", command=choosing_supplier)
        # Creating Label widgets
        self.lbl_supplier = tk.Label(self.frame_supplier, text='Supplier', background=self.frame_supplier['background'],
                                     font=('Calibri', 11, 'bold'))
        self.lbl_supplier_name = tk.Label(self.frame_supplier, text='name*', background=self.frame_supplier['background'])
        self.lbl_supplier_address = tk.Label(self.frame_supplier, text='address', background=self.frame_supplier['background'])
        self.lbl_supplier_phone = tk.Label(self.frame_supplier, text='phone*', background=self.frame_supplier['background'])
        self.lbl_supplier_email = tk.Label(self.frame_supplier, text='email*', background=self.frame_supplier['background'])
        self.lbl_supplier_note = tk.Label(self.frame_supplier, text='note', background=self.frame_supplier['background'])
        self.lbl_supplier_notify = tk.Label(self.frame_supplier, text='Supplier already exists!',
                                            background=self.frame_supplier['background'],
                                            font=('Calibri', 11, 'bold'), fg='red')
        # Creating Entry widgets
        vcmd = (self.register(self.on_validate_supplier_name),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.cmbsuppliername = ttk.Combobox(self.frame_supplier, validate="key", validatecommand=vcmd)  # ComboBox
        # , validatecommand=searching_similar_customer, validate='all'
        self.entrysuppliername = tk.Entry(self.frame_supplier, validate="key", validatecommand=vcmd)
        self.entry_supplier_address = tk.Entry(self.frame_supplier)
        self.entry_supplier_phone = tk.Entry(self.frame_supplier)
        self.entry_supplier_email = tk.Entry(self.frame_supplier)
        self.entry_supplier_note = tk.Entry(self.frame_supplier)
        # Creating Entry widgets's variables
        self.cmbsuppliernamevar = tk.StringVar()
        self.entrysuppliernamevar = tk.StringVar()
        self.entry_supplier_address_var = tk.StringVar()
        self.entry_supplier_phone_var = tk.StringVar()
        self.entry_supplier_email_var = tk.StringVar()
        self.entry_supplier_note_var = tk.StringVar()
        # Trace variables
        # self.suppliernamevar.trace('w', searching_similar_customer)
        # Set widgets to some value.
        self.cmbsuppliernamevar.set("")
        self.entrysuppliernamevar.set("")
        self.entry_supplier_address_var.set("")
        self.entry_supplier_phone_var.set("")
        self.entry_supplier_email_var.set("")
        self.entry_supplier_note_var.set("")
        # self.entry_supplier_address.delete(0, END)
        # self.entry_supplier_address.insert(0, row[0])

        # Assigning variables to widgets    (Tell the widget to watch this variable.)
        self.cmbsuppliername["textvariable"] = self.cmbsuppliernamevar
        self.entrysuppliername["textvariable"] = self.entrysuppliernamevar
        self.entry_supplier_address["textvariable"] = self.entry_supplier_address_var
        self.entry_supplier_phone["textvariable"] = self.entry_supplier_phone_var
        self.entry_supplier_email["textvariable"] = self.entry_supplier_email_var
        self.entry_supplier_note["textvariable"] = self.entry_supplier_note_var

        # Binding widgets with functions
        self.entrysuppliername.bind('<FocusIn>', self.entrysuppliername.selection_range(0, END))
        self.cmbsuppliername.bind('<FocusIn>', self.cmbsuppliername.selection_range(0, END))
        self.cmbsuppliername.bind("<<ComboboxSelected>>", combobox_selected)
        # self.cmb_customer_name.bind('<FocusIn>', self.searching_similar_customer(self.suppliernamevar.get()))
        # self.cmb_customer_name.bind('<Key>', searching_similar_customer)
        self.entry_supplier_address.bind('<FocusIn>', self.entry_supplier_address.selection_range(0, END))
        self.entry_supplier_phone.bind('<FocusIn>', self.entry_supplier_phone.selection_range(0, END))
        self.entry_supplier_email.bind('<FocusIn>', self.entry_supplier_email.selection_range(0, END))
        self.entry_supplier_note.bind('<FocusIn>', self.entry_supplier_note.selection_range(0, END))
        # self.btn_customer_exists.bind('<Button-1>', clear_supplier_exists)
        # self.btn_customer_new.bind('<Button-1>', clear_supplier_new)

        # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
        self.lbl_supplier.grid(         row=0,  column=0,  columnspan=2)  # sticky=N+S+W+E,
        self.btn_supplier_new.grid(     row=1,  column=0,  padx=5, pady=10, sticky='e')
        self.btn_supplier_exists.grid(  row=1,  column=1,  padx=(5, 10), sticky='e')

        self.lbl_supplier_name.grid(    row=2,  column=0,   sticky='es')
        self.lbl_supplier_address.grid( row=3,  column=0,   sticky='e')
        self.lbl_supplier_phone.grid(   row=4,  column=0,   sticky='e')
        self.lbl_supplier_email.grid(   row=5,  column=0,   sticky='e')
        self.lbl_supplier_note.grid(    row=6,  column=0,   sticky='e')

        self.cmbsuppliername.grid(          row=2,  column=1,   padx=(5, 0), pady=(10, 0))
        self.entrysuppliername.grid(        row=2,  column=1,   padx=(15, 30), pady=(10, 0))
        self.entry_supplier_address.grid(   row=3,  column=1,   padx=(15, 30))
        self.entry_supplier_phone.grid(     row=4,  column=1,   padx=(15, 30))
        self.entry_supplier_email.grid(     row=5,  column=1,   padx=(15, 30))
        self.entry_supplier_note.grid(      row=6,  column=1,   padx=(15, 30))

        self.btn_supplier_enter.grid(row=7, column=0, columnspan=2, sticky='', pady=(5, 5))
        # self.lbl_customer_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
        # self.lbl_customer_notify.grid_remove()
        # self.lbl_customer_notify.grid_propagate()

        self.searching_similar_supplier(self.cmbsuppliernamevar.get())

        # side=tk.LEFT, fill=tk.Y, expand=False,
        choosing_supplier()
        set_parent_window_req_size(self.frame_supplier)
        place_tk_to_screen_center(self)
        set_active(self)

    def on_closing(self):
        lg.info("#on_closing")
        update_treeview(self.parent)
        self.destroy()

    def create_frame_supply(self):
        lg.info("#create_frame_shipment")

        def adding_supply():
            lg.info("#adding_supply")

            def clear_supply_new():
                lg.info("#clear_supply_new")
                self.entry_supply_delivery_note_var.set("")
                self.entry_supply_date_var.set(datetime.date(datetime.now()))
                self.entry_supply_note_var.set("")
                # lg.debug(f"datetime.date(datetime.now())={datetime.date(datetime.now())}")
                self.lbl_supply_notify.grid_remove()

            self.btn_supply_new.config(relief=SUNKEN, state="disabled")
            self.btn_supply_exists.config(relief=RAISED, state="normal")
            self.cmb_supply_delivery_note.grid_remove()
            self.entry_supply_delivery_note.grid()

            # self.entry_shipment_delivery_note.config(state="disabled")
            self.entry_supply_date.config(state="normal")
            # self.entry_supply_email.config(state="normal")
            self.entry_supply_note.config(state="normal")
            clear_supply_new()

        def choosing_supply():
            lg.info("#choosing_supply")

            def clear_supply_exists():
                lg.info("#clear_supply_exists")
                # self.cmb_shipment_delivery_note_var.set("")
                self.entry_supply_date_var.set('')
                self.entry_supply_note_var.set('')
                self.lbl_supply_notify.grid_remove()
                self.entry_supply_delivery_note.grid_remove()

            self.btn_supply_exists.config(relief=SUNKEN, state="disabled")
            self.btn_supply_new.config(relief=RAISED, state="normal")
            # self.entry_shipment_delivery_note.grid_remove()
            self.cmb_supply_delivery_note.grid()

            self.entry_supply_date.config(state="readonly")
            # self.entry_supply_email.config(state="readonly")
            self.entry_supply_note.config(state="readonly")
            clear_supply_exists()

            self.query = """
                               select delivery_note, date, note from supplies
                               where delivery_note = %(delivery_note)s
                               ORDER BY delivery_note ASC"""
            self.parameters = ({'delivery_note': self.cmb_supply_delivery_note_var.get()})
            self.show_chosen_supply()

        def combobox_selected(event):
            lg.info("#combobox_selected")
            lg.info(f'you\'ve selected "{self.cmb_supply_delivery_note.selection_get()}"')
            self.query = """
                               select delivery_note, date, note from supplies
                               where delivery_note = %(delivery_note)s
                               ORDER BY delivery_note ASC
                               """
            self.parameters = ({'delivery_note': self.cmb_supply_delivery_note.selection_get()})
            self.show_chosen_supply()


        # Turning off frame_customer (supplier)
        self.frame_supplier.config(background='navajowhite')
        for child in self.frame_supplier.winfo_children():
            child.config(background='navajowhite')
            # lg.info(f'1) child={child}')
            child['state'] = 'disabled'
        self.btn_supplier_exists.unbind('<Button-1>')
        self.btn_supplier_new.unbind('<Button-1>')

        self.frame_supply = tk.Frame(self)
        frame = self.frame_supply
        frame.pack(side=tk.LEFT, fill=tk.Y)
        frame.config(background="orange")

        # Creating Button widgets
        self.btn_supply_enter = tk.Button(frame, text="Enter", command=self.enter_supply)
        self.btn_supply_new = tk.Button(frame, text="Add New", command=adding_supply)
        self.btn_supply_exists = tk.Button(frame, text="Already Exists", command=choosing_supply)
        # Creating Label widgets
        self.lbl_supply = tk.Label(frame, text='Supply', background=frame['background'],
                                   font=('Calibri', 11, 'bold'))
        self.lbl_supply_id = tk.Label(frame, text='delivery note*', background=frame['background'])
        self.lbl_supply_date = tk.Label(frame, text='date*', background=frame['background'])
        # self.lbl_supply_email = tk.Label(frame, text='email*', background=frame['background'])
        self.lbl_supply_note = tk.Label(frame, text='note', background=frame['background'])
        self.lbl_supply_notify = tk.Label(frame, text='Supply already exists!',
                                          background=frame['background'],
                                          font=('Calibri', 11, 'bold'), fg='red')
        # Creating Entry widgets
        vcmd = (self.register(self.on_validate_supply_delivery_note),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd2 = (self.register(self.on_validate_date),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.cmb_supply_delivery_note = ttk.Combobox(frame, validate="key", validatecommand=vcmd)  # ComboBox
        self.entry_supply_delivery_note = tk.Entry(frame, validate="key", validatecommand=vcmd)
        self.entry_supply_date = tk.Entry(frame, validate="key", validatecommand=vcmd2)
        # self.entry_supply_email = tk.Entry(frame)
        self.entry_supply_note = tk.Entry(frame)
        # Creating Entry widgets's variables
        self.cmb_supply_delivery_note_var = tk.StringVar()
        self.entry_supply_delivery_note_var = tk.StringVar()
        self.entry_supply_date_var = tk.StringVar()
        # self.entry_supply_email_var = tk.StringVar()
        self.entry_supply_note_var = tk.StringVar()
        # Set widgets to some value.
        self.cmb_supply_delivery_note_var.set("")
        self.entry_supply_delivery_note_var.set("")
        self.entry_supply_date_var.set("")
        # self.entry_supply_email_var.set("")
        self.entry_supply_note_var.set("")

        # Assigning variables to widgets    (Tell the widget to watch this variable.)
        self.cmb_supply_delivery_note["textvariable"] = self.cmb_supply_delivery_note_var
        self.entry_supply_delivery_note["textvariable"] = self.entry_supply_delivery_note_var
        self.entry_supply_date["textvariable"] = self.entry_supply_date_var
        # self.entry_supply_email["textvariable"] = self.entry_supply_email_var
        self.entry_supply_note["textvariable"] = self.entry_supply_note_var

        # Binding widgets with functions
        self.entry_supply_delivery_note.bind('<FocusIn>', self.entry_supply_delivery_note.selection_range(0, END))
        self.cmb_supply_delivery_note.bind('<FocusIn>', self.cmb_supply_delivery_note.selection_range(0, END))
        self.cmb_supply_delivery_note.bind("<<ComboboxSelected>>", combobox_selected)
        self.entry_supply_date.bind('<FocusIn>', self.entry_supply_date.selection_range(0, END))
        # self.entry_supply_email.bind('<FocusIn>', self.entry_supply_email.selection_range(0, END))
        self.entry_supply_note.bind('<FocusIn>', self.entry_supply_note.selection_range(0, END))
        # self.btn_shipment_exists.bind('<Button-1>', clear_supply_exists)

        # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
        self.lbl_supply.grid(                   row=0, column=0, columnspan=2)  # sticky=N+S+W+E,
        self.btn_supply_new.grid(               row=1, column=0, padx=(5, 0), pady=5, sticky='e')
        self.btn_supply_exists.grid(            row=1, column=1, padx=(5, 10), sticky='e')

        self.lbl_supply_id.grid(                row=2, column=0, sticky='es')
        self.lbl_supply_date.grid(              row=4, column=0, sticky='e')
        # self.lbl_supply_email.grid(           row=5, column=0, sticky='e')
        self.lbl_supply_note.grid(              row=6, column=0, sticky='e')

        self.cmb_supply_delivery_note.grid(     row=2, column=1, padx=(5, 0), pady=(10, 0))
        self.entry_supply_delivery_note.grid(   row=2, column=1, padx=(15, 30), pady=(10, 0))
        self.entry_supply_date.grid(            row=4, column=1, padx=(15, 30))
        # self.entry_supply_email.grid(         row=5, column=1, padx=(15, 30))
        self.entry_supply_note.grid(            row=6, column=1, padx=(15, 30))

        self.btn_supply_enter.grid(             row=7, column=0, columnspan=2, sticky='', pady=(5, 5))
        # self.lbl_shipment_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))

        self.entry_supply_delivery_note.grid_remove()
        self.cmb_supply_delivery_note.grid_remove()

        self.searching_similar_supply(self.cmb_supply_delivery_note_var.get())
        choosing_supply()
        set_parent_window_req_size(self.frame_supplier, self.frame_supply)
        # place_tk_to_screen_center(self)

    def create_frame_product(self):
        lg.info("create_frame_product")

        def adding_product():
            def clear_product_new():
                # self.entry_product_id_var.set("")
                self.entry_product_price_var.set("")
                self.entry_product_shelf_life_var.set("")
                self.entry_product_description_var.set("")
                self.lbl_product_notify.grid_remove()
                self.cmb_product_name.grid_remove()

            lg.info("#adding_product")

            self.btn_product_new.config(relief=SUNKEN, state="disabled")
            self.btn_product_exists.config(relief=RAISED, state="normal")

            # self.entry_product_id.config(state="disabled")
            self.entry_product_description.config(state="normal")
            self.entry_product_shelf_life.config(state="normal")
            self.entry_product_price.config(state="normal")
            self.entry_product_note.config(state="normal")
            clear_product_new()
            self.entry_product_name.grid()

        def choosing_product():
            def clear_product_exists():
                self.cmb_product_name_var.set("")
                self.entry_product_price_var.set('')
                self.entry_product_shelf_life_var.set('')
                self.entry_product_description_var.set('')
                self.entry_product_note_var.set('')
                self.lbl_product_notify.grid_remove()
                self.entry_product_name.grid_remove()

            lg.info("#choosing_product")
            self.btn_product_exists.config(relief=SUNKEN, state="disabled")
            self.btn_product_new.config(relief=RAISED, state="normal")

            self.entry_product_description.config(state="readonly")
            self.entry_product_shelf_life.config(state="readonly")
            self.entry_product_price.config(state="readonly")
            self.cmb_product_name.grid()
            clear_product_exists()

            # self.query = """
            #                select price, shelf_life, description from catalog
            #                where product_name = %(product_name)s
            #                ORDER BY product_name ASC"""
            # self.parameters = ({'product_name': self.cmb_product_id_var.get()})
            # self.show_changing_package()

            self.searching_similar_product(self.cmb_product_name_var.get())

        def combobox_selected(event):
            lg.info("#combobox_selected")
            lg.info(f'you\'ve selected "{self.cmb_product_name.selection_get()}"')
            self.query = """
                               select price, shelf_life, description from catalog
                               where product_name = %(product_name)s
                               ORDER BY product_name ASC
                               """
            self.parameters = ({'product_name': self.cmb_product_name.selection_get()})
            self.show_chosen_product()

        # Turning off frame_shipment
        self.frame_supply.config(background='navajowhite')
        for child in self.frame_supply.winfo_children():
            child.config(background='navajowhite')
            # lg.info(f'1) child={child}')
            child['state'] = 'disabled'
        self.btn_supply_exists.unbind('<Button-1>')
        self.btn_supply_new.unbind('<Button-1>')


        self.frame_product = tk.Frame(self)
        frame = self.frame_product
        self.frame_product.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_product.config(background="orange")
        # Creating Button widgets
        self.btn_product_enter = tk.Button(frame, text="Enter", command=self.enter_product)
        self.btn_product_new = tk.Button(frame, text="Add New", command=adding_product)
        self.btn_product_exists = tk.Button(frame, text="Already Exists", command=choosing_product)
        # Creating Label widgets
        self.lbl_product = tk.Label(frame, text='Product', background=frame['background'],
                                   font=('Calibri', 11, 'bold'))
        self.lbl_product_name = tk.Label(frame, text='Product Name*', background=frame['background'])
        self.lbl_product_price = tk.Label(frame, text='price*', background=frame['background'])
        self.lbl_product_shelf_life = tk.Label(frame, text='shelf life*', background=frame['background'])
        self.lbl_product_description = tk.Label(frame, text='description', background=frame['background'])
        self.lbl_product_production_date = tk.Label(frame, text='production date*', background=frame['background'])
        self.lbl_product_note = tk.Label(frame, text='note', background=frame['background'])
        self.lbl_product_amount = tk.Label(frame, text='Amount:', background=frame['background'])
        self.lbl_product_notify = tk.Label(frame, text='Product already exists!',
                                          background=frame['background'],
                                          font=('Calibri', 11, 'bold'), fg='red')
        # Creating Entry widgets
        vcmd = (self.register(self.on_validate_product_name),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd2 = (self.register(self.on_validate_date),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd3 = (self.register(self.on_validate_number),
                 '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.cmb_product_name = ttk.Combobox(frame, validate="key", validatecommand=vcmd)  # ComboBox
        self.entry_product_name = tk.Entry(frame, validate="key", validatecommand=vcmd)
        self.entry_product_price = tk.Entry(frame)
        self.entry_product_shelf_life = tk.Entry(frame)
        self.entry_product_description = tk.Entry(frame)
        self.entry_product_production_date = tk.Entry(frame, validate="key", validatecommand=vcmd2)
        self.entry_product_note = tk.Entry(frame)
        self.entry_product_amount = tk.Entry(frame, validate="key", validatecommand=vcmd3)

        # Creating Entry widgets's variables
        self.cmb_product_name_var = tk.StringVar()
        self.entry_product_name_var = tk.StringVar()
        self.entry_product_price_var = tk.StringVar()
        self.entry_product_shelf_life_var = tk.StringVar()
        self.entry_product_description_var = tk.StringVar()
        self.entry_product_production_date_var = tk.StringVar()
        self.entry_product_note_var = tk.StringVar()
        self.entry_product_amount_var = tk.StringVar()

        # Set widgets to some value.
        self.cmb_product_name_var.set("")
        self.entry_product_name_var.set("")
        self.entry_product_price_var.set("")
        self.entry_product_shelf_life_var.set("")
        self.entry_product_description_var.set("")
        self.entry_product_production_date_var.set("")
        self.entry_product_note_var.set("")
        self.entry_product_amount_var.set("1")

        # Assigning variables to widgets    (Tell the widget to watch this variable.)
        self.cmb_product_name["textvariable"] = self.cmb_product_name_var
        self.entry_product_name["textvariable"] = self.entry_product_name_var
        self.entry_product_price["textvariable"] = self.entry_product_price_var
        self.entry_product_shelf_life["textvariable"] = self.entry_product_shelf_life_var
        self.entry_product_description["textvariable"] = self.entry_product_description_var
        self.entry_product_production_date["textvariable"] = self.entry_product_production_date_var
        self.entry_product_note["textvariable"] = self.entry_product_note_var
        self.entry_product_amount["textvariable"] = self.entry_product_amount_var

        # Binding widgets with functions
        self.entry_product_name.bind('<FocusIn>', self.entry_product_name.selection_range(0, END))
        self.cmb_product_name.bind('<FocusIn>', self.cmb_product_name.selection_range(0, END))
        self.cmb_product_name.bind("<<ComboboxSelected>>", combobox_selected)
        self.entry_product_price.bind('<FocusIn>', self.entry_product_price.selection_range(0, END))
        self.entry_product_shelf_life.bind('<FocusIn>', self.entry_product_shelf_life.selection_range(0, END))
        self.entry_product_description.bind('<FocusIn>', self.entry_product_description.selection_range(0, END))
        self.entry_product_production_date.bind('<FocusIn>', self.entry_product_production_date.selection_range(0, END))
        self.entry_product_note.bind('<FocusIn>', self.entry_product_note.selection_range(0, END))
        self.entry_product_amount.bind('<FocusIn>', self.entry_product_amount.selection_range(0, END))

        # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
        self.lbl_product.grid(                  row=0,  column=0, columnspan=2)  # sticky=N+S+W+E,
        self.btn_product_new.grid(              row=1,  column=0, padx=5, pady=5, sticky='e')
        self.btn_product_exists.grid(           row=1,  column=1, padx=(5, 10), sticky='e')

        self.lbl_product_name.grid(             row=2,  column=0, sticky='es')
        self.lbl_product_price.grid(            row=3,  column=0, sticky='e')
        self.lbl_product_shelf_life.grid(       row=4,  column=0, sticky='e')
        self.lbl_product_description.grid(      row=5,  column=0, sticky='e')
        self.lbl_product_production_date.grid(  row=6,  column=0, sticky='e', pady=(15, 0), padx=(5, 0))
        self.lbl_product_note.grid(             row=7,  column=0, sticky='e')
        self.lbl_product_amount.grid(           row=8,  column=0, sticky='e', pady=(10, 0))

        self.cmb_product_name.grid(             row=2,  column=1, padx=(5, 0),   pady=(10, 0))
        self.entry_product_name.grid(           row=2,  column=1, padx=(15, 30), pady=(10, 0))
        self.entry_product_price.grid(          row=3,  column=1, padx=(15, 30))
        self.entry_product_shelf_life.grid(     row=4,  column=1, padx=(15, 30))
        self.entry_product_description.grid(    row=5,  column=1, padx=(15, 30))
        self.entry_product_production_date.grid(row=6,  column=1, padx=(15, 30), pady=(15, 0))
        self.entry_product_note.grid(           row=7,  column=1, padx=(15, 30))
        self.entry_product_amount.grid(         row=8,  column=1, padx=(15, 30), pady=(10, 0))

        self.btn_product_enter.grid(            row=10, column=0, columnspan=2, sticky='', pady=(5, 5))
        self.lbl_product_notify.grid(           row=11, column=0, columnspan=2, sticky='', pady=(5, 5))

        self.lbl_product_notify.grid_remove()
        self.cmb_product_name.grid_remove()
        self.entry_product_name.grid_remove()

        self.searching_similar_product(self.cmb_product_name_var.get())

        choosing_product()
        set_parent_window_req_size(self.frame_supplier, self.frame_supply, self.frame_product)
        # place_tk_to_screen_center(self)


    def show_chosen_supplier(self):
        lg.info("#show_chosen_customer")
        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        # lg.info(f'db_rows={db_rows}')

        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
        elif db_rows == []:
            lg.debug('Recieved empty array')
        elif is_iterable(db_rows):
            for row in db_rows:
                lg.info(f'self.entry_supplier_address_var = "{self.entry_supplier_address_var.get()}"')
                self.entry_supplier_address_var.set(row[0])
                self.entry_supplier_phone_var.set(row[1])
                self.entry_supplier_email_var.set(row[2])
                self.entry_supplier_note_var.set(row[3])
                self.lbl_supplier_notify.config(fg='green', text="Chosen")
                self.lbl_supplier_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.info('Showing chosen supplier')
                # self.create_frame_shipment()
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

    def show_chosen_supply(self):
        lg.info("#show_chosen_shipment")

        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        # lg.info(f'db_rows={db_rows}')

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
                self.entry_supply_delivery_note_var.set(row[0])
                self.entry_supply_date_var.set(row[1])
                self.entry_supply_note_var.set(row[2])
                self.lbl_supply_notify.config(fg='green', text="Chosen")
                self.lbl_supply_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.info('Showing chosen supply')
                # self.create_frame_shipment()
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

    def show_chosen_product(self):
        lg.info("#show_changing_package")

        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        # lg.info(f'db_rows={db_rows}')

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
                self.entry_product_shelf_life_var.set(row[1])
                self.entry_product_description_var.set(row[2])
                # self.entry_product_production_date_var.set(row[4])
                # self.entry_product_note_var.set(row[5])
                self.lbl_product_notify.config(fg='green', text="Chosen")
                self.lbl_product_notify.grid(row=11, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.info('Showing chosen Product')
                # self.create_frame_shipment()
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')


    def on_validate_supplier_name(self, d, i, P, s, S, v, V, W):
        lg.info("#on_validate_supplier_name")
        # print("end", "\n\nOnValidate:")
        # print("end", f"d={d} - Type of action (1=insert, 0=delete, -1 for others)")
        # print("end", f"i={i} - index of char string to be inserted/deleted, or -1")
        # print("end", f"P={P} - value of the entry if the edit is allowed")
        # print("end", f"s={s} - value of entry prior to editing")
        # print("end", f"S={S} - the text string being inserted or deleted, if any")
        # print("end", f"v={v} - the type of validation that is currently set")
        # print("end", f"V={V} - the type of validation that triggered the callback (key, focusin, focusout, forced)")
        # print("end", f"W={W} - the tk name of the widget")
        # Disallow _ and %
        if (S == '_') or (S == '%'):
            self.bell()
            return False
        elif ('_' in P) or ('%' in P):
            self.bell()
            # self.suppliernamevar.set('')
            return False
        else:
            if self.btn_supplier_exists['state'] == 'disabled':
                self.searching_similar_supplier(P)
            return True

    def on_validate_supply_delivery_note(self, d, i, P, s, S, v, V, W):
        lg.info("#on_validate_supply_delivery_note")
        # lg.debug("OnValidate:")
        # lg.debug(f"d={d} - Type of action (1=insert, 0=delete, -1 for others)")
        # lg.debug(f"i={i} - index of char string to be inserted/deleted, or -1")
        # lg.debug(f"P={P} - value of the entry if the edit is allowed")
        # lg.debug(f"s={s} - value of entry prior to editing")
        # lg.debug(f"S={S} - the text string being inserted or deleted, if any")
        # lg.debug(f"v={v} - the type of validation that is currently set")
        # lg.debug(f"V={V} - the type of validation that triggered the callback (key, focusin, focusout, forced)")
        # lg.debug(f"W={W} - the tk name of the widget")
        # if not (S.isnumeric()) and not (S == '-'):
        if (S == '_') or (S == '%'):
            self.bell()
            return False
        elif ('_' in P) or ('%' in P):
            self.bell()
            return False
        else:
            if self.btn_supply_exists['state'] == 'disabled':
                self.searching_similar_supply(P)
            return True

    def on_validate_date(self, d, i, P, s, S, v, V, W):
        lg.info("#on_validate_date")
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
            lg.info("other action")
            return True
        if '0' == d:
            lg.info("delete action")
            return True
        else:
            if not(S == '-') and not(S.isnumeric()):
                self.bell()
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
                        self.bell()
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
                            self.bell()
                            return False
                return True

    def on_validate_product_name(self, d, i, P, s, S, v, V, W):
        lg.info("#on_validate_product_name")
        # print("end", "\n\nOnValidate:")
        # print("end", f"d={d} - Type of action (1=insert, 0=delete, -1 for others)")
        # print("end", f"i={i} - index of char string to be inserted/deleted, or -1")
        # print("end", f"P={P} - value of the entry if the edit is allowed")
        # print("end", f"s={s} - value of entry prior to editing")
        # print("end", f"S={S} - the text string being inserted or deleted, if any")
        # print("end", f"v={v} - the type of validation that is currently set")
        # print("end", f"V={V} - the type of validation that triggered the callback (key, focusin, focusout, forced)")
        # print("end", f"W={W} - the tk name of the widget")
        if (S == '_') or (S == '%'):
            self.bell()
            return False
        elif ('_' in P) or ('%' in P):
            self.bell()
            return False
        else:
            if self.btn_product_exists['state'] == 'disabled':
                self.searching_similar_product(P)
            return True

    def on_validate_number(self, d, i, P, s, S, v, V, W):
        lg.info("#on_validate_number")
        # print("end", "\n\nOnValidate:")
        # print("end", f"d={d} - Type of action (1=insert, 0=delete, -1 for others)")
        # print("end", f"i={i} - index of char string to be inserted/deleted, or -1")
        # print("end", f"P={P} - value of the entry if the edit is allowed")
        # print("end", f"s={s} - value of entry prior to editing")
        # print("end", f"S={S} - the text string being inserted or deleted, if any")
        # print("end", f"v={v} - the type of validation that is currently set")
        # print("end", f"V={V} - the type of validation that triggered the callback (key, focusin, focusout, forced)")
        # print("end", f"W={W} - the tk name of the widget")

        if d == '0':
            return True
        if P.isnumeric():  # len(P) <= 4 and
            n = int(P)
            if 0 <= n <= 1000:
                return True
            else:
                return False
        else:
            self.bell()
            return False


    def searching_similar_supplier(self, P):  # (v, mode, callback):
        # print(f'searching_similar_customer to "{self.suppliernamevar.get()}"')
        lg.info(f'#searching_similar_supplier to "{P}"')
        self.query = """
           select name from suppliers
           where name LIKE %(name)s
           ORDER BY name ASC
           """
        # self.parameters = ({'name': self.suppliernamevar.get()+'%'})
        self.parameters = ({'name': P + '%'})
        self.cmbsuppliername['values'] = ()
        add_records_to_cmb(self.conn1, self.query, self.parameters, self.cmbsuppliername)

    def searching_similar_supply(self, P):  # (v, mode, callback):
        # print(f'searching_similar_shipment to "{self.supplyidvar.get()}"')
        lg.info(f'#searching_similar_supply to "{P}"')
        self.query = """
           select delivery_note from supplies
           where delivery_note LIKE %(delivery_note)s AND suppliers_id = %(suppliers_id)s
           ORDER BY delivery_note ASC
           """
        # self.parameters = ({'id': self.supplyidvar.get()+'%'})
        self.parameters = ({'delivery_note': P + '%',
                            'suppliers_id': self.supplier_id})
        self.cmb_supply_delivery_note['values'] = ()
        add_records_to_cmb(self.conn1, self.query, self.parameters, self.cmb_supply_delivery_note)

    def searching_similar_product(self, P):  # (v, mode, callback):
        # print(f'searching_similar_product_id to "{self.productidvar.get()}"')
        lg.info(f'#searching_similar_product to "{P}"')
        self.query = """
                   select product_name from catalog
                   where product_name LIKE %(product_name)s
                   ORDER BY product_name ASC
                   """
        self.parameters = ({'product_name': P + '%'})
        self.cmb_product_name['values'] = ()
        add_records_to_cmb(self.conn1, self.query, self.parameters, self.cmb_product_name)


    def enter_supplier(self):
        lg.info("#enter_customer")
        # lbl_customer_notify, cmb_customer_name_var, entry_customer_id_var
        # Те переменные, которые нужно проверить: entry_customer_id_var, entry_customer_phone_var,
        #                                         entry_customer_email_var

        # query, parameters,
        # btn_customer_exists, btn_customer_new
        # create_frame_shipment

        # devide into:  enter_supplier_exists + enter_supplier_new

        self.lbl_supplier_notify.grid_remove()
        self.query = """
                        select id from suppliers
                        where name = %(name)s
                        """

        def enter_supplier_exists():
            self.parameters = ({'name': self.cmbsuppliernamevar.get()})
            db_rows = run_select_query(self.conn1, self.query, self.parameters)
            lg.info(f'um db_rows={db_rows}')
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
            elif isinstance(db_rows, Error):
                lg.error(error_to_str(db_rows))
            elif db_rows == []:
                lg.error(f'db_rows={[]} (empty)')
                self.lbl_supplier_notify.config(fg='red', text="Supplier not found!\nCheck your Entry!")
                self.lbl_supplier_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.error('Not found')
            elif is_iterable(db_rows):
                # for row in db_rows:
                #     lg.info(f'row={row}')
                #     lg.info(f"row[0]={row[0]}")
                self.supplier_id = db_rows[0][0]
                self.lbl_supplier_notify.config(fg='green', text="Chosen")
                self.lbl_supplier_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.info('Chosen (after "enter_customer")')
                self.create_frame_supply()
            elif db_rows is None:
                lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

        def enter_supplier_new():
            lg.debug("\t\tself.btn_customer_new['state'] == 'disabled':")
            # checking if supplier exists already
            self.parameters = ({'name': self.entrysuppliernamevar.get()})
            db_rows = run_select_query(self.conn1, self.query, self.parameters)
            # lg.info(f'db_rows={db_rows}')
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
            elif isinstance(db_rows, Error):
                lg.error(error_to_str(db_rows))
            elif db_rows == []:
                lg.info(f"ok we havent found anything with parameters={self.parameters} (that's a good thing)")
                if self.entrysuppliernamevar.get() == '' or self.entry_supplier_phone_var.get() == '' or \
                        self.entry_supplier_email_var.get() == '':
                    self.lbl_supplier_notify.config(fg='red', text="Required fields\ncan't be empty!")
                    self.lbl_supplier_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                else:
                    self.add_new_supplier()
            elif is_iterable(db_rows):
                # for row in db_rows:
                # lg.info(f'row={row}')
                # lg.info(f"row[0]={row[0]}")
                self.lbl_supplier_notify.config(fg='red', text="Supplier already exists!")
                self.lbl_supplier_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.error('Supplier already exists')
            elif db_rows is None:
                lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

        if self.btn_supplier_exists['state'] == 'disabled':
            enter_supplier_exists()
        elif self.btn_supplier_new['state'] == 'disabled':
            enter_supplier_new()
        else:
            lg.error("Button not chosen! ('New' or 'Exists')")

    def enter_supply(self):
        lg.info("#enter_shipment")

        def enter_supply_exists():
            self.query = """
                            select id from supplies
                            where delivery_note = %(delivery_note)s
                            """
            self.parameters = ({'delivery_note': self.cmb_supply_delivery_note.get()})
            db_rows = run_select_query(self.conn1, self.query, self.parameters)
            # lg.info(f'db_rows={db_rows}')
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
            elif isinstance(db_rows, Error):
                lg.error(error_to_str(db_rows))
            elif db_rows == []:
                lg.error(f'db_rows={[]} (empty)')
                self.lbl_supply_notify.config(fg='red', text="Supply not found!\nCheck your Entry!")
                self.lbl_supply_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.error('Not found')
            elif is_iterable(db_rows):
                # for row in db_rows:
                #     lg.info(f'row={row}')
                #     lg.info(f"row[0]={row[0]}")
                self.lbl_supply_notify.config(fg='green', text="Chosen")
                self.lbl_supply_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                self.supply_id = db_rows[0][0]
                lg.info('Supply is chosen')
                self.create_frame_product()
            elif db_rows is None:
                lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

        def enter_supply_new():
            lg.debug("\t\tself.btn_shipment_new['state'] == 'disabled':")
            # checking if supply exists already
            self.query = """
                        select id from supplies
                        where suppliers_id = %(suppliers_id)s AND delivery_note = %(delivery_note)s
                        """
            self.parameters = ({'suppliers_id': self.supplier_id,
                                'delivery_note': self.entry_supply_delivery_note_var.get()
                                })

            db_rows = run_select_query(self.conn1, self.query, self.parameters)
            # lg.info(f'db_rows={db_rows}')
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
            elif isinstance(db_rows, Error):
                lg.error(error_to_str(db_rows))
            elif db_rows == []:
                lg.info(f"ok we havent found anything with parameters={self.parameters} (that's a good thing)")
                if self.entry_supply_date.get() == '' or self.entry_supply_delivery_note_var.get() == '':
                    self.lbl_supply_notify.config(fg='red', text="Required fields\ncan't be empty!")
                    self.lbl_supply_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                else:
                    self.add_new_supply()
            elif is_iterable(db_rows):
                # for row in db_rows:
                # lg.info(f'row={row}')
                # lg.info(f"row[0]={row[0]}")
                self.lbl_supply_notify.config(fg='red', text="Supply already exists!")
                self.lbl_supply_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.error('Supply already exists')
            elif db_rows is None:
                lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

        self.lbl_supply_notify.grid_remove()
        if self.btn_supply_exists['state'] == 'disabled':
            enter_supply_exists()
        elif self.btn_supply_new['state'] == 'disabled':
            enter_supply_new()
        else:
            lg.error("Button not chosen! ('New' or 'Exists')")

    def enter_product(self):
        lg.info("#change_package")

        def enter_product_exists():
            self.query = """
                            select id from catalog
                            where product_name = %(product_name)s
                            """
            self.parameters = ({'product_name': self.cmb_product_name_var.get()})
            db_rows = run_select_query(self.conn1, self.query, self.parameters)
            # lg.info(f'db_rows={db_rows}')
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
            elif isinstance(db_rows, Error):
                lg.error(error_to_str(db_rows))
            elif db_rows == []:
                lg.error(f'db_rows={[]} (empty)')
                self.lbl_product_notify.config(fg='red', text="Product not found!\nCheck your Entry!")
                self.lbl_product_notify.grid()
                lg.error('Not found')
            elif is_iterable(db_rows):
                # for row in db_rows:
                #     lg.info(f'row={row}')
                #     lg.info(f"row[0]={row[0]}")

                self.lbl_product_notify.config(fg='green', text="Chosen")
                self.lbl_product_notify.grid()
                lg.info('Product is chosen')
                self.catalog_id = db_rows[0][0]
                self.add_new_product()
            elif db_rows is None:
                lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

        def enter_product_new():
            lg.debug("\t\tself.btn_product_new['state'] == 'disabled':")
            # checking if product exists already
            self.query = """
                        select id from catalog
                        where product_name = %(product_name)s
                        """
            self.parameters = ({'product_name': self.entry_product_name_var.get()})

            db_rows = run_select_query(self.conn1, self.query, self.parameters)
            # lg.info(f'db_rows={db_rows}')
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
            elif isinstance(db_rows, Error):
                lg.error(error_to_str(db_rows))
            elif db_rows == []:
                lg.info(f"ok we havent found anything with parameters={self.parameters} (that's a good thing)")
                if (self.entry_product_name_var.get() == '' or self.entry_product_price_var.get() == ''
                        or self.entry_product_shelf_life_var.get() == ''
                        or self.entry_product_production_date_var.get() == ''):
                    self.lbl_product_notify.config(fg='red', text="Required fields\ncan't be empty!")
                    self.lbl_product_notify.grid()
                else:
                    self.add_new_product()
            elif is_iterable(db_rows):
                # for row in db_rows:
                # lg.info(f'row={row}')
                # lg.info(f"row[0]={row[0]}")
                self.lbl_product_notify.config(fg='red', text="Catalog element already exists!")
                self.lbl_product_notify.grid()
                lg.error('Catalog element already exists')
            elif db_rows is None:
                lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

        self.lbl_product_notify.grid_remove()
        if self.btn_product_exists['state'] == 'disabled':
            enter_product_exists()
        elif self.btn_product_new['state'] == 'disabled':
            enter_product_new()
        else:
            lg.error("Button not chosen! ('New' or 'Exists')")


    def get_next_id(self, table_name, lbl_notify):
        lg.info("#get_next_supplier_id")
        self.query = """ select MAX(id)+1 from """ + table_name
        self.parameters = ()
        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        if db_rows.__class__ is int:
            lg.error(f"Didn't get id from database!")
            lg.error(f"Could not reconnect to database!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
            lbl_notify.config(fg='green', text="Could not reconnect to database!")
            lbl_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
            return None
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
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


    def add_new_supplier(self):
        lg.info("#add_new_customer")
        supplier_id = self.get_next_id("suppliers", self.lbl_supplier_notify)
        if supplier_id is None:
            lg.error(f"customer_id is None")
            return None
        self.supplier_id = supplier_id
        lg.debug(f"self.customer_id = {self.supplier_id}")
        self.query = """INSERT INTO suppliers(id, name, address, phone, email, note) 
                                       VALUES(%s, %s, %s, %s, %s, %s)"""
        self.parameters = (self.supplier_id,
                           self.entrysuppliernamevar.get(),
                           self.entry_supplier_address_var.get(),
                           self.entry_supplier_phone_var.get(),
                           self.entry_supplier_email_var.get(),
                           self.entry_supplier_note_var.get()
                           )
        db_rows = run_commit_query(self.conn1, self.query, self.parameters)

        lg.info(f"r={db_rows}")
        # lg.debug(f"r=.__class__ = {db_rows.__class__}")
        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
            lg.error(error_to_str(db_rows))
            self.lbl_supplier_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
            self.lbl_supplier_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
        elif db_rows is None:
            self.lbl_supplier_notify.config(fg='green', text="Added new supplier!")
            self.lbl_supplier_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
            self.create_frame_supply()

    def add_new_supply(self):
        lg.info("#add_new_shipment")
        supply_id = self.get_next_id("supplies", self.lbl_supply_notify)
        if supply_id is None:
            return None
        self.supply_id = supply_id
        # lg.debug(f"self.customer_id = {self.customer_id}")
        lg.debug(f"self.shipment_id = {self.supply_id}")
        self.query = """INSERT INTO supplies(id, suppliers_id, delivery_note, date, note) 
                                               VALUES(%s, %s, %s, %s, %s)"""
        self.parameters = (self.supply_id,
                           self.supplier_id,
                           self.entry_supply_delivery_note_var.get(),
                           self.entry_supply_date_var.get(),
                           self.entry_supply_note_var.get(),
                           )
        db_rows = run_commit_query(self.conn1, self.query, self.parameters)

        lg.debug(f"db_rows={db_rows}")
        # lg.debug(f"r=.__class__ = {db_rows.__class__}")
        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
            lg.error(error_to_str(db_rows))
            self.lbl_supply_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
            self.lbl_supply_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
        elif db_rows is None:
            self.lbl_supply_notify.config(fg='green', text="Added new supply!")
            self.lbl_supply_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
            lg.info(f"self.shipment_id = {self.supply_id}")
            self.create_frame_product()

    def add_new_catalog_element(self):
        catalog_id = self.get_next_id("catalog", self.lbl_product_notify)
        if catalog_id is None:
            return None
        self.catalog_id = catalog_id

        lg.debug(f"self.catalog_id = {self.catalog_id}")
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
            self.lbl_product_notify.config(fg='green', text="Added new catalog element!")
            self.lbl_product_notify.grid()
            lg.info(f"self.goods_id = {self.goods_id}")
            # self.create_frame_product()
            return 0

    def add_new_product(self):
        lg.info("#add_new_product")

        def is_correct_date():
            if not (is_date(self.entry_product_production_date_var.get())):
                self.lbl_product_notify.config(fg='red', text="Incorrect 'production date'!")
                self.lbl_product_notify.grid()
                lg.error("Incorrect 'production date'!")
                return False
            else:
                lg.info("Date is correct!")
                return True

        def get_amount():
            amount_str = self.entry_product_amount_var.get()
            if amount_str == '':
                self.lbl_product_notify.config(fg='red', text="Enter Amount of products!")
                self.lbl_product_notify.grid()
                return None
            amount = int(amount_str)
            if amount <= 0:
                self.lbl_product_notify.config(fg='red', text="Amount must be more than zero!")
                self.lbl_product_notify.grid()
                lg.error("Amount must be more than zero!")
                return None
            return amount



            if not (is_correct_date(self.entry_product_production_date_var.get())):
                return False
            if is_correct_amount() is False:
                return False

        if is_correct_date() is False:
            return
        amount = get_amount()
        if amount is None:
            return

        if self.btn_product_new['state'] == 'disabled':
            if self.add_new_catalog_element() is None:
                return

        self.btn_product_enter.config(relief=SUNKEN, state="disabled")
        self.btn_product_enter.update_idletasks()
        self.btn_product_enter.grid_remove()
        self.btn_product_enter.update_idletasks()
        self.frame_product.update_idletasks()

        # pb = ttk.Progressbar(self.frame_product, orient=HORIZONTAL, length=200, mode='determinate')
        # pb.grid(row=11, column=0, columnspan=2)
        # pb['value'] = 0
        # a = 100 / amount

        # pb = ttk.Progressbar(self.frame_product, orient=HORIZONTAL, length=200, mode='determinate')
        # pb.grid(row=10, column=0, columnspan=2)
        # lg.debug(f"type(pb['value'])={type(pb['value'])}")
        # for i in range(1):  # amount
        #     pb['value'] += a
            # pb['value'] += 1
            # pb.update_idletasks()
        product_id = self.get_next_id("goods", self.lbl_product_notify)
        if product_id is None:
            self.btn_product_enter.config(relief=RAISED, state="normal")
            self.btn_product_enter.grid()
            return
        self.goods_id = product_id
        lg.debug(f"self.catalog_id = {self.catalog_id}")
        # self.query = """INSERT INTO goods(id, catalog_id, state, production_date, note)
        #                                        VALUES(%s, %s, %s, %s, %s)"""
        # self.parameters = (self.goods_id,
        #                    self.catalog_id,
        #                    0,
        #                    self.entry_product_production_date_var.get(),
        #                    self.entry_product_note_var.get(),
        #                    )
        # db_rows = run_commit_query(self.conn1, self.query, self.parameters)
        catalog_id = self.catalog_id
        production_date = self.entry_product_production_date_var.get()
        note = self.entry_product_note_var.get()

        self.query = f"""call add_goods({amount}, {int(catalog_id)}, '{production_date}', '{str(note)}' );"""
        lg.debug(f'self.query="{self.query}"')
        self.parameters = ()
        # self.parameters = ({'amount':           amount,
        #                     'catalog_id':       self.catalog_id,
        #                     'production_date':  self.entry_product_production_date_var.get(),
        #                     'note':             self.entry_product_note_var.get()
        #                     })

        db_rows = run_commit_query(self.conn1, self.query)

        # lg.debug(f"db_rows={db_rows}")
        # lg.debug(f"r=.__class__ = {db_rows.__class__}")
        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
            self.btn_product_enter.config(relief=RAISED, state="normal")
            self.btn_product_enter.grid()
        elif isinstance(db_rows, Error):
            # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
            lg.error(error_to_str(db_rows))
            self.lbl_product_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
            self.lbl_product_notify.grid()
            self.btn_product_enter.config(relief=RAISED, state="normal")
            self.btn_product_enter.grid()
        elif db_rows is None:
            self.add_to_goods_supplies_table()
            # lg.debug(f"self.goods_id = {self.goods_id}")
            # if i == amount - 1:
            if amount == 1:
                self.lbl_product_notify.config(fg='green', text="Added new product!")
                # pb.grid_remove()
            else:
                self.lbl_product_notify.config(fg='green', text=f"Added ({amount}) new products!")
                # pb.grid_remove()
            self.lbl_product_notify.grid()
            self.btn_product_enter.config(relief=RAISED, state="normal")
            self.btn_product_enter.grid()

    def add_to_goods_supplies_table(self):
        lg.info("#delete_product_from_storage")
        # если возникнет ошибка, здесь, надо будет удалить последний добавленный товар и
        #       если нажата кнопка New, то удалить последний добавленный элемент из каталога
        self.query = """INSERT INTO goods_supplies(goods_id, supplies_id) 
                                                       VALUES(%s, %s)"""
        # lg.debug(f"goods_id = {self.goods_id}")
        # lg.debug(f"shipment_id = {self.shipment_id}")
        self.parameters = (self.goods_id,
                           self.supply_id
                           )
        db_rows = run_commit_query(self.conn1, self.query, self.parameters)

        # lg.debug(f"db_rows={db_rows}")
        # lg.debug(f"db_rows.__class__ = {db_rows.__class__}")
        if db_rows.__class__ is int:
            lg.critical(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            lg.error(f"db_rows IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
            lg.critical(error_to_str(db_rows))
            self.lbl_product_notify.config(fg='darkred', text="CRITICAL ERROR!!!\n" +
                                                              insert_new_line_symbols(error_to_str(db_rows)))
            self.bell()
            self.lbl_product_notify.grid()
        elif db_rows is None:
            # self.lbl_product_notify.config(fg='green', text="Added new product !")
            # self.lbl_product_notify.grid()
            lg.info("Product added to goods+supplies table")
            lg.info(f"self.goods_id = {self.goods_id}")


class ShipProductWindow(tk.Toplevel):

    def __init__(self, parent, conn1):
        self.parent = parent
        self.conn1 = conn1
        tk.Toplevel.__init__(self, parent)

        self.parameters = None
        self.query = None

        self.frame_product = None
        self.frame_shipment = None

        self.customer_id = None
        self.shipment_id = None
        self.catalog_id = None
        self.goods_id = None
        self.goods_supplies_id = None
        # self.conn1 = conn1
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        lg.debug('########   CREATING AddNewProductWindow  ########')
        self.title('Ship Products')

        self.style1 = ttk.Style()
        self.style1.configure("mystyle.Treeview", highlightthickness=0, bd=0,
                              font=('Calibri', 11))  # Modify the font of the body
        self.style1.configure("mystyle.Treeview.Heading",
                              font=('Calibri', 13, 'bold'))  # Modify the font of the headings
        self.style1.layout("mystyle.Treeview",
                           [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

        def adding_customer():
            lg.info("#adding_customer")

            def clear_customer_new():
                lg.info("#clear_customer_new")
                self.entry_customer_id_var.set(self.cmb_customer_name_var.get())
                self.entry_customer_id_var.set("")
                self.entry_customer_address_var.set('')
                self.entry_customer_phone_var.set('')
                self.entry_customer_email_var.set('')
                self.entry_customer_note_var.set('')
                self.lbl_customer_notify.grid_remove()

            # self.entry_customer_name['state'] = 'normal'
            # self.cmb_customer_name['state'] = 'readonly'
            self.btn_customer_new.config(relief=SUNKEN, state="disabled")
            self.btn_customer_exists.config(relief=RAISED, state="normal")
            self.cmb_customer_name.grid_remove()
            self.entry_customer_name.grid()

            self.entry_customer_address.config(state="normal")
            self.entry_customer_phone.config(state="normal")
            self.entry_customer_email.config(state="normal")
            self.entry_customer_note.config(state="normal")
            clear_customer_new()

        def choosing_customer():
            lg.info("#choosing_customer")

            def clear_customer_exists():
                lg.info("#clear_customer_exists")
                # self.cmb_customer_name_var.set(self.entry_customer_id_var.get())
                # self.cmb_customer_name_var.set('')
                self.entry_customer_address_var.set('')
                self.entry_customer_phone_var.set('')
                self.entry_customer_email_var.set('')
                self.entry_customer_note_var.set('')
                self.lbl_customer_notify.grid_remove()

            # self.entry_customer_name['state'] = 'readonly'
            # self.cmb_customer_name['state'] = 'normal'
            self.btn_customer_exists.config(relief=SUNKEN, state="disabled")
            self.btn_customer_new.config(relief=RAISED, state="normal")
            self.entry_customer_name.grid_remove()
            self.cmb_customer_name.grid()

            self.entry_customer_address.config(state="readonly")
            self.entry_customer_phone.config(state="readonly")
            self.entry_customer_email.config(state="readonly")
            self.entry_customer_note.config(state="readonly")
            clear_customer_exists()

            self.query = """
                           select address, phone, email, note from customers
                           where name = %(name)s
                           ORDER BY name ASC"""
            self.parameters = ({'name': self.cmb_customer_name_var.get()})
            self.show_chosen_customer()

        def combobox_selected(event):
            lg.info("#combobox_selected")
            lg.info(f'you\'ve selected "{self.cmb_customer_name.selection_get()}"')
            # self.parameters = ({'name': self.customernamevar.get()+'%'})
            self.parameters = ({'name': self.cmb_customer_name.selection_get()})
            self.query = """
                       select address, phone, email, note from customers
                       where name = %(name)s
                       ORDER BY name ASC
                       """
            self.show_chosen_customer()

        self.frame_customer = tk.Frame(self)
        self.frame_customer.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_customer.config(background="orange")

        # Creating Button widgets
        self.btn_customer_enter = tk.Button(self.frame_customer, text="Enter", command=self.enter_customer)
        self.btn_customer_new = tk.Button(self.frame_customer, text="Add New", command=adding_customer)
        self.btn_customer_exists = tk.Button(self.frame_customer, text="Already Exists", command=choosing_customer)
        # Creating Label widgets
        self.lbl_customer = tk.Label(self.frame_customer, text='Customer', background=self.frame_customer['background'],
                                     font=('Calibri', 11, 'bold'))
        self.lbl_customer_name = tk.Label(self.frame_customer, text='name*', background=self.frame_customer['background'])
        self.lbl_customer_address = tk.Label(self.frame_customer, text='address', background=self.frame_customer['background'])
        self.lbl_customer_phone = tk.Label(self.frame_customer, text='phone*', background=self.frame_customer['background'])
        self.lbl_customer_email = tk.Label(self.frame_customer, text='email*', background=self.frame_customer['background'])
        self.lbl_customer_note = tk.Label(self.frame_customer, text='note', background=self.frame_customer['background'])
        self.lbl_customer_notify = tk.Label(self.frame_customer, text='Customer already exists!',
                                            background=self.frame_customer['background'],
                                            font=('Calibri', 11, 'bold'), fg='red')
        # Creating Entry widgets
        vcmd = (self.register(self.on_validate_customer_name),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.cmb_customer_name = ttk.Combobox(self.frame_customer, validate="key", validatecommand=vcmd)  # ComboBox
        # , validatecommand=searching_similar_customer, validate='all'
        self.entry_customer_name = tk.Entry(self.frame_customer, validate="key", validatecommand=vcmd)
        self.entry_customer_address = tk.Entry(self.frame_customer)
        self.entry_customer_phone = tk.Entry(self.frame_customer)
        self.entry_customer_email = tk.Entry(self.frame_customer)
        self.entry_customer_note = tk.Entry(self.frame_customer)
        # Creating Entry widgets's variables
        self.cmb_customer_name_var = tk.StringVar()
        self.entry_customer_id_var = tk.StringVar()
        self.entry_customer_address_var = tk.StringVar()
        self.entry_customer_phone_var = tk.StringVar()
        self.entry_customer_email_var = tk.StringVar()
        self.entry_customer_note_var = tk.StringVar()
        # Trace variables
        # self.customernamevar.trace('w', searching_similar_customer)
        # Set widgets to some value.
        self.cmb_customer_name_var.set("")
        self.entry_customer_id_var.set("")
        self.entry_customer_address_var.set("")
        self.entry_customer_phone_var.set("")
        self.entry_customer_email_var.set("")
        self.entry_customer_note_var.set("")
        # self.entry_customer_address.delete(0, END)
        # self.entry_customer_address.insert(0, row[0])

        # Assigning variables to widgets    (Tell the widget to watch this variable.)
        self.cmb_customer_name["textvariable"] = self.cmb_customer_name_var
        self.entry_customer_name["textvariable"] = self.entry_customer_id_var
        self.entry_customer_address["textvariable"] = self.entry_customer_address_var
        self.entry_customer_phone["textvariable"] = self.entry_customer_phone_var
        self.entry_customer_email["textvariable"] = self.entry_customer_email_var
        self.entry_customer_note["textvariable"] = self.entry_customer_note_var

        # Binding widgets with functions
        self.entry_customer_name.bind('<FocusIn>', self.entry_customer_name.selection_range(0, END))
        self.cmb_customer_name.bind('<FocusIn>', self.cmb_customer_name.selection_range(0, END))
        self.cmb_customer_name.bind("<<ComboboxSelected>>", combobox_selected)
        # self.cmb_customer_name.bind('<FocusIn>', self.searching_similar_customer(self.customernamevar.get()))
        # self.cmb_customer_name.bind('<Key>', searching_similar_customer)
        self.entry_customer_address.bind('<FocusIn>', self.entry_customer_address.selection_range(0, END))
        self.entry_customer_phone.bind('<FocusIn>', self.entry_customer_phone.selection_range(0, END))
        self.entry_customer_email.bind('<FocusIn>', self.entry_customer_email.selection_range(0, END))
        self.entry_customer_note.bind('<FocusIn>', self.entry_customer_note.selection_range(0, END))
        # self.btn_customer_exists.bind('<Button-1>', clear_customer_exists)
        # self.btn_customer_new.bind('<Button-1>', clear_customer_new)

        # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
        self.lbl_customer.grid(         row=0,  column=0,  columnspan=2)  # sticky=N+S+W+E,
        self.btn_customer_new.grid(row=1, column=0, padx=5, pady=10, sticky='e')
        self.btn_customer_exists.grid(row=1, column=1, padx=(5, 10), sticky='e')

        self.lbl_customer_name.grid(    row=2,  column=0,   sticky='es')
        self.lbl_customer_address.grid( row=3,  column=0,   sticky='e')
        self.lbl_customer_phone.grid(   row=4,  column=0,   sticky='e')
        self.lbl_customer_email.grid(   row=5,  column=0,   sticky='e')
        self.lbl_customer_note.grid(    row=6,  column=0,   sticky='e')

        self.cmb_customer_name.grid(row=2, column=1, padx=(5, 0), pady=(10, 0))
        self.entry_customer_name.grid(row=2, column=1, padx=(15, 30), pady=(10, 0))
        self.entry_customer_address.grid(   row=3,  column=1,   padx=(15, 30))
        self.entry_customer_phone.grid(     row=4,  column=1,   padx=(15, 30))
        self.entry_customer_email.grid(     row=5,  column=1,   padx=(15, 30))
        self.entry_customer_note.grid(      row=6,  column=1,   padx=(15, 30))

        self.btn_customer_enter.grid(row=7, column=0, columnspan=2, sticky='', pady=(5, 5))
        # self.lbl_customer_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
        # self.lbl_customer_notify.grid_remove()
        # self.lbl_customer_notify.grid_propagate()

        self.searching_similar_customer(self.cmb_customer_name_var.get())

        # side=tk.LEFT, fill=tk.Y, expand=False,
        choosing_customer()
        set_parent_window_req_size(self.frame_customer)
        place_tk_to_screen_center(self)
        set_active(self)

    def on_closing(self):
        lg.info("#on_closing")
        update_treeview(self.parent)
        self.destroy()

    def create_frame_shipment(self):
        lg.info("#create_frame_shipment")

        def adding_shipment():
            lg.info("#adding_shipment")

            def clear_shipment_new():
                lg.info("#clear_shipment_new")
                self.entry_shipment_delivery_note_var.set("")
                self.entry_shipment_date_var.set(datetime.date(datetime.now()))
                self.entry_shipment_note_var.set("")
                # lg.debug(f"datetime.date(datetime.now())={datetime.date(datetime.now())}")
                self.lbl_shipment_notify.grid_remove()

            self.btn_shipment_new.config(relief=SUNKEN, state="disabled")
            self.btn_shipment_exists.config(relief=RAISED, state="normal")
            self.cmb_shipment_delivery_note.grid_remove()
            self.entry_shipment_delivery_note.grid()

            # self.entry_shipment_delivery_note.config(state="disabled")
            self.entry_shipment_date.config(state="normal")
            # self.entry_shipment_email.config(state="normal")
            self.entry_shipment_note.config(state="normal")
            clear_shipment_new()

        def choosing_shipment():
            lg.info("#choosing_shipment")

            def clear_shipment_exists():
                lg.info("#clear_shipment_exists")
                # self.cmb_shipment_delivery_note_var.set("")
                self.entry_shipment_date_var.set('')
                self.entry_shipment_note_var.set('')
                self.lbl_shipment_notify.grid_remove()
                self.entry_shipment_delivery_note.grid_remove()

            self.btn_shipment_exists.config(relief=SUNKEN, state="disabled")
            self.btn_shipment_new.config(relief=RAISED, state="normal")
            # self.entry_shipment_delivery_note.grid_remove()
            self.cmb_shipment_delivery_note.grid()

            self.entry_shipment_date.config(state="readonly")
            # self.entry_shipment_email.config(state="readonly")
            self.entry_shipment_note.config(state="readonly")
            clear_shipment_exists()

            self.query = """
                               select delivery_note, date, note from shipments
                               where delivery_note = %(delivery_note)s
                               ORDER BY delivery_note ASC"""
            self.parameters = ({'delivery_note': self.cmb_shipment_delivery_note_var.get()})
            self.show_chosen_shipment()

        def combobox_selected(event):
            lg.info("#combobox_selected")
            lg.info(f'you\'ve selected "{self.cmb_shipment_delivery_note.selection_get()}"')
            self.query = """
                               select delivery_note, date, note from shipments
                               where delivery_note = %(delivery_note)s
                               ORDER BY delivery_note ASC
                               """
            self.parameters = ({'delivery_note': self.cmb_shipment_delivery_note.selection_get()})
            self.show_chosen_shipment()


        # Turning off frame_customer (customer)
        self.frame_customer.config(background='navajowhite')
        for child in self.frame_customer.winfo_children():
            child.config(background='navajowhite')
            # lg.info(f'1) child={child}')
            child['state'] = 'disabled'
        self.btn_customer_exists.unbind('<Button-1>')
        self.btn_customer_new.unbind('<Button-1>')

        self.frame_shipment = tk.Frame(self)
        frame = self.frame_shipment
        frame.pack(side=tk.LEFT, fill=tk.Y)
        frame.config(background="orange")

        # Creating Button widgets
        self.btn_shipment_enter = tk.Button(frame, text="Enter", command=self.enter_shipment)
        self.btn_shipment_new = tk.Button(frame, text="Add New", command=adding_shipment)
        self.btn_shipment_exists = tk.Button(frame, text="Already Exists", command=choosing_shipment)
        # Creating Label widgets
        self.lbl_shipment = tk.Label(frame, text='Shipment', background=frame['background'],
                                   font=('Calibri', 11, 'bold'))
        self.lbl_shipment_id = tk.Label(frame, text='delivery note*', background=frame['background'])
        self.lbl_shipment_date = tk.Label(frame, text='date*', background=frame['background'])
        # self.lbl_shipment_email = tk.Label(frame, text='email*', background=frame['background'])
        self.lbl_shipment_note = tk.Label(frame, text='note', background=frame['background'])
        self.lbl_shipment_notify = tk.Label(frame, text='Shipment already exists!',
                                            background=frame['background'],
                                            font=('Calibri', 11, 'bold'), fg='red')
        # Creating Entry widgets
        vcmd = (self.register(self.on_validate_shipment_delivery_note),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd2 = (self.register(self.on_validate_date),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.cmb_shipment_delivery_note = ttk.Combobox(frame, validate="key", validatecommand=vcmd)  # ComboBox
        self.entry_shipment_delivery_note = tk.Entry(frame, validate="key", validatecommand=vcmd)
        self.entry_shipment_date = tk.Entry(frame, validate="key", validatecommand=vcmd2)
        # self.entry_shipment_email = tk.Entry(frame)
        self.entry_shipment_note = tk.Entry(frame)
        # Creating Entry widgets's variables
        self.cmb_shipment_delivery_note_var = tk.StringVar()
        self.entry_shipment_delivery_note_var = tk.StringVar()
        self.entry_shipment_date_var = tk.StringVar()
        # self.entry_shipment_email_var = tk.StringVar()
        self.entry_shipment_note_var = tk.StringVar()
        # Set widgets to some value.
        self.cmb_shipment_delivery_note_var.set("")
        self.entry_shipment_delivery_note_var.set("")
        self.entry_shipment_date_var.set("")
        # self.entry_shipment_email_var.set("")
        self.entry_shipment_note_var.set("")

        # Assigning variables to widgets    (Tell the widget to watch this variable.)
        self.cmb_shipment_delivery_note["textvariable"] = self.cmb_shipment_delivery_note_var
        self.entry_shipment_delivery_note["textvariable"] = self.entry_shipment_delivery_note_var
        self.entry_shipment_date["textvariable"] = self.entry_shipment_date_var
        # self.entry_shipment_email["textvariable"] = self.entry_shipment_email_var
        self.entry_shipment_note["textvariable"] = self.entry_shipment_note_var

        # Binding widgets with functions
        self.entry_shipment_delivery_note.bind('<FocusIn>', self.entry_shipment_delivery_note.selection_range(0, END))
        self.cmb_shipment_delivery_note.bind('<FocusIn>', self.cmb_shipment_delivery_note.selection_range(0, END))
        self.cmb_shipment_delivery_note.bind("<<ComboboxSelected>>", combobox_selected)
        self.entry_shipment_date.bind('<FocusIn>', self.entry_shipment_date.selection_range(0, END))
        # self.entry_shipment_email.bind('<FocusIn>', self.entry_shipment_email.selection_range(0, END))
        self.entry_shipment_note.bind('<FocusIn>', self.entry_shipment_note.selection_range(0, END))
        # self.btn_shipment_exists.bind('<Button-1>', clear_shipment_exists)

        # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
        self.lbl_shipment.grid(                   row=0, column=0, columnspan=2)  # sticky=N+S+W+E,
        self.btn_shipment_new.grid(row=1, column=0, padx=(5, 0), pady=5, sticky='e')
        self.btn_shipment_exists.grid(row=1, column=1, padx=(5, 10), sticky='e')

        self.lbl_shipment_id.grid(                row=2, column=0, sticky='es')
        self.lbl_shipment_date.grid(              row=4, column=0, sticky='e')
        # self.lbl_shipment_email.grid(           row=5, column=0, sticky='e')
        self.lbl_shipment_note.grid(              row=6, column=0, sticky='e')

        self.cmb_shipment_delivery_note.grid(row=2, column=1, padx=(5, 0), pady=(10, 0))
        self.entry_shipment_delivery_note.grid(row=2, column=1, padx=(15, 30), pady=(10, 0))
        self.entry_shipment_date.grid(row=4, column=1, padx=(15, 30))
        # self.entry_shipment_email.grid(         row=5, column=1, padx=(15, 30))
        self.entry_shipment_note.grid(            row=6, column=1, padx=(15, 30))

        self.btn_shipment_enter.grid(             row=7, column=0, columnspan=2, sticky='', pady=(5, 5))
        # self.lbl_shipment_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))

        self.entry_shipment_delivery_note.grid_remove()
        self.cmb_shipment_delivery_note.grid_remove()

        self.searching_similar_shipment(self.cmb_shipment_delivery_note_var.get())
        choosing_shipment()
        set_parent_window_req_size(self.frame_customer, self.frame_shipment)
        # place_tk_to_screen_center(self)

    def create_frame_product(self):
        lg.info("create_frame_product")

        def adding_product():
            def clear_product_new():
                # self.entry_product_id_var.set("")
                self.entry_product_price_var.set("")
                self.entry_product_shelf_life_var.set("")
                self.entry_product_description_var.set("")
                self.lbl_product_notify.grid_remove()
                self.cmb_product_id.grid_remove()

            lg.info("#adding_product")

            # self.btn_product_new.config(relief=SUNKEN, state="disabled")
            self.btn_product_exists.config(relief=RAISED, state="normal")

            # self.entry_product_id.config(state="disabled")
            self.entry_product_description.config(state="normal")
            self.entry_product_shelf_life.config(state="normal")
            self.entry_product_price.config(state="normal")
            self.entry_product_note.config(state="normal")
            clear_product_new()
            self.entry_product_id.grid()

        def choosing_product():
            def clear_product_exists():
                self.cmb_product_id_var.set("")
                self.entry_product_price_var.set('')
                self.entry_product_shelf_life_var.set('')
                self.entry_product_description_var.set('')
                self.entry_product_note_var.set('')
                self.lbl_product_notify.grid_remove()
                self.entry_product_id.grid_remove()

            lg.info("#choosing_product")
            self.btn_product_exists.config(relief=SUNKEN, state="disabled")
            # self.btn_product_new.config(relief=RAISED, state="normal")

            self.entry_product_description.config(state="readonly")
            self.entry_product_shelf_life.config(state="readonly")
            self.entry_product_price.config(state="readonly")
            self.entry_product_name.config(state="readonly")
            self.entry_product_production_date.config(state="readonly")
            self.entry_product_note.config(state="readonly")
            self.cmb_product_id.grid()
            clear_product_exists()

            self.query = """
                            SELECT product_name, price, shelf_life, description, production_date, note 
                                    FROM goods LEFT JOIN catalog c on goods.catalog_id = c.id
                            WHERE goods.id = %(goods_id)s
                         """
            self.parameters = ({'goods_id': self.cmb_product_id_var.get()})
            self.show_chosen_product()
            # self.searching_similar_product_id(self.cmb_product_id_var.get())

        def combobox_selected(event):
            lg.info("#combobox_selected")
            lg.info(f'you\'ve selected "{self.cmb_product_id.selection_get()}"')
            self.query = """
                            SELECT product_name, price, shelf_life, description, production_date, note 
                                    FROM goods LEFT JOIN catalog c on goods.catalog_id = c.id
                            WHERE goods.id = %(goods_id)s
                         """
            self.parameters = ({'goods_id': self.cmb_product_id.selection_get()})
            self.show_chosen_product()

        # Turning off frame_shipment
        self.frame_shipment.config(background='navajowhite')
        for child in self.frame_shipment.winfo_children():
            child.config(background='navajowhite')
            # lg.info(f'1) child={child}')
            child['state'] = 'disabled'
        self.btn_shipment_exists.unbind('<Button-1>')
        self.btn_shipment_new.unbind('<Button-1>')


        self.frame_product = tk.Frame(self)
        frame = self.frame_product
        self.frame_product.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_product.config(background="orange")
        # Creating Button widgets
        self.btn_product_enter = tk.Button(frame, text="Enter", command=self.enter_product)
        # self.btn_product_new = tk.Button(frame, text="Add New", command=adding_product)
        self.btn_product_exists = tk.Button(frame, text="Already Exists", command=choosing_product)
        # Creating Label widgets
        self.lbl_product = tk.Label(frame, text='Product', background=frame['background'],
                                   font=('Calibri', 11, 'bold'))
        self.lbl_product_id = tk.Label(frame, text='id*', background=frame['background'])
        self.lbl_product_name = tk.Label(frame, text='Product Name:', background=frame['background'])
        self.lbl_product_price = tk.Label(frame, text='price*', background=frame['background'])
        self.lbl_product_shelf_life = tk.Label(frame, text='shelf life*', background=frame['background'])
        self.lbl_product_description = tk.Label(frame, text='description', background=frame['background'])
        self.lbl_product_production_date = tk.Label(frame, text='production date*', background=frame['background'])
        self.lbl_product_note = tk.Label(frame, text='note', background=frame['background'])
        self.lbl_product_notify = tk.Label(frame, text='Product already exists!',
                                          background=frame['background'],
                                          font=('Calibri', 11, 'bold'), fg='red')
        # Creating Entry widgets
        vcmd = (self.register(self.on_validate_product_id),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd2 = (self.register(self.on_validate_date),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd3 = (self.register(self.on_validate_number),
                 '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.cmb_product_id = ttk.Combobox(frame, validate="key", validatecommand=vcmd)  # ComboBox
        self.entry_product_id = tk.Entry(frame, validate="key", validatecommand=vcmd)
        self.entry_product_price = tk.Entry(frame)
        self.entry_product_shelf_life = tk.Entry(frame)
        self.entry_product_description = tk.Entry(frame)
        self.entry_product_production_date = tk.Entry(frame, validate="key", validatecommand=vcmd2)
        self.entry_product_note = tk.Entry(frame)
        self.entry_product_name = tk.Entry(frame, validate="key", validatecommand=vcmd3)

        # Creating Entry widgets's variables
        self.cmb_product_id_var = tk.StringVar()
        self.entry_product_id_var = tk.StringVar()
        self.entry_product_price_var = tk.StringVar()
        self.entry_product_shelf_life_var = tk.StringVar()
        self.entry_product_description_var = tk.StringVar()
        self.entry_product_production_date_var = tk.StringVar()
        self.entry_product_note_var = tk.StringVar()
        self.entry_product_name_var = tk.StringVar()

        # Set widgets to some value.
        self.cmb_product_id_var.set("")
        self.entry_product_id_var.set("")
        self.entry_product_price_var.set("")
        self.entry_product_shelf_life_var.set("")
        self.entry_product_description_var.set("")
        self.entry_product_production_date_var.set("")
        self.entry_product_note_var.set("")
        self.entry_product_name_var.set("1")

        # Assigning variables to widgets    (Tell the widget to watch this variable.)
        self.cmb_product_id["textvariable"] = self.cmb_product_id_var
        self.entry_product_id["textvariable"] = self.entry_product_id_var
        self.entry_product_price["textvariable"] = self.entry_product_price_var
        self.entry_product_shelf_life["textvariable"] = self.entry_product_shelf_life_var
        self.entry_product_description["textvariable"] = self.entry_product_description_var
        self.entry_product_production_date["textvariable"] = self.entry_product_production_date_var
        self.entry_product_note["textvariable"] = self.entry_product_note_var
        self.entry_product_name["textvariable"] = self.entry_product_name_var

        # Binding widgets with functions
        self.entry_product_id.bind('<FocusIn>', self.entry_product_id.selection_range(0, END))
        self.cmb_product_id.bind('<FocusIn>', self.cmb_product_id.selection_range(0, END))
        self.cmb_product_id.bind("<<ComboboxSelected>>", combobox_selected)
        self.entry_product_price.bind('<FocusIn>', self.entry_product_price.selection_range(0, END))
        self.entry_product_shelf_life.bind('<FocusIn>', self.entry_product_shelf_life.selection_range(0, END))
        self.entry_product_description.bind('<FocusIn>', self.entry_product_description.selection_range(0, END))
        self.entry_product_production_date.bind('<FocusIn>', self.entry_product_production_date.selection_range(0, END))
        self.entry_product_note.bind('<FocusIn>', self.entry_product_note.selection_range(0, END))
        self.entry_product_name.bind('<FocusIn>', self.entry_product_name.selection_range(0, END))

        # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
        self.lbl_product.grid(                  row=0,  column=0, columnspan=2)  # sticky=N+S+W+E,
        # self.btn_product_new.grid(              row=1,  column=0, padx=5, pady=5, sticky='e')
        self.btn_product_exists.grid(           row=1,  column=1, padx=(5, 10), sticky='e')

        self.lbl_product_id.grid(               row=2,  column=0, sticky='es')
        self.lbl_product_name.grid(row=3, column=0, sticky='e', pady=(10, 0))
        self.lbl_product_price.grid(            row=4,  column=0, sticky='e')
        self.lbl_product_shelf_life.grid(       row=5,  column=0, sticky='e')
        self.lbl_product_description.grid(      row=6,  column=0, sticky='e')
        self.lbl_product_production_date.grid(  row=7,  column=0, sticky='e', pady=(15, 0), padx=(5, 0))
        self.lbl_product_note.grid(             row=8,  column=0, sticky='e')

        self.cmb_product_id.grid(               row=2,  column=1, padx=(5, 0), pady=(10, 0))
        self.entry_product_id.grid(             row=2,  column=1, padx=(15, 30), pady=(10, 0))
        self.entry_product_name.grid(           row=3, column=1, padx=(15, 30), pady=(10, 0))
        self.entry_product_price.grid(          row=4,  column=1, padx=(15, 30))
        self.entry_product_shelf_life.grid(     row=5,  column=1, padx=(15, 30))
        self.entry_product_description.grid(    row=6,  column=1, padx=(15, 30))
        self.entry_product_production_date.grid(row=7,  column=1, padx=(15, 30), pady=(15, 0))
        self.entry_product_note.grid(           row=8,  column=1, padx=(15, 30))

        self.btn_product_enter.grid(            row=10, column=0, columnspan=2, sticky='', pady=(5, 5))
        self.lbl_product_notify.grid(           row=11, column=0, columnspan=2, sticky='', pady=(5, 5))

        self.lbl_product_notify.grid_remove()
        self.cmb_product_id.grid_remove()
        self.entry_product_id.grid_remove()

        self.searching_similar_product(self.cmb_product_id_var.get())

        choosing_product()
        set_parent_window_req_size(self.frame_customer, self.frame_shipment, self.frame_product)
        # place_tk_to_screen_center(self)

    def show_chosen_customer(self):
        lg.info("#show_chosen_customer")
        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        # lg.info(f'db_rows={db_rows}')

        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
        elif db_rows == []:
            lg.debug('Recieved empty array')
        elif is_iterable(db_rows):
            for row in db_rows:
                lg.info(f'self.entry_customer_address_var = "{self.entry_customer_address_var.get()}"')
                self.entry_customer_address_var.set(row[0])
                self.entry_customer_phone_var.set(row[1])
                self.entry_customer_email_var.set(row[2])
                self.entry_customer_note_var.set(row[3])
                self.lbl_customer_notify.config(fg='green', text="Chosen")
                self.lbl_customer_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.info('Showing chosen customer')
                # self.create_frame_shipment()
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

    def show_chosen_shipment(self):
        lg.info("#show_chosen_shipment")

        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        # lg.info(f'db_rows={db_rows}')

        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
        elif db_rows == []:
            lg.debug('Recieved empty array')
        elif is_iterable(db_rows):
            for row in db_rows:
                # lg.info(f'self.entry_shipment_address_var = "{self.entry_shipment_address_var.get()}"')
                self.entry_shipment_delivery_note_var.set(row[0])
                self.entry_shipment_date_var.set(row[1])
                self.entry_shipment_note_var.set(row[2])
                self.lbl_shipment_notify.config(fg='green', text="Chosen")
                self.lbl_shipment_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.info('Showing chosen shipment')
                # self.create_frame_shipment()
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

    def show_chosen_product(self):
        lg.info("#show_changing_package")

        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        # lg.info(f'db_rows={db_rows}')

        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
        elif db_rows == []:
            lg.debug('Recieved empty array')
        elif is_iterable(db_rows):
            for row in db_rows:
                self.entry_product_name_var.set(row[0])
                self.entry_product_price_var.set(row[1])
                self.entry_product_shelf_life_var.set(row[2])
                self.entry_product_description_var.set(row[3])
                self.entry_product_production_date_var.set(row[4])
                self.entry_product_note_var.set(row[5])
                self.lbl_shipment_notify.config(fg='green', text="Chosen")
                self.lbl_shipment_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.info('Showing chosen Product')
                # self.create_frame_shipment()
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')


    def on_validate_customer_name(self, d, i, P, s, S, v, V, W):
        lg.info("#on_validate_customer_name")
        # print("end", "\n\nOnValidate:")
        # print("end", f"d={d} - Type of action (1=insert, 0=delete, -1 for others)")
        # print("end", f"i={i} - index of char string to be inserted/deleted, or -1")
        # print("end", f"P={P} - value of the entry if the edit is allowed")
        # print("end", f"s={s} - value of entry prior to editing")
        # print("end", f"S={S} - the text string being inserted or deleted, if any")
        # print("end", f"v={v} - the type of validation that is currently set")
        # print("end", f"V={V} - the type of validation that triggered the callback (key, focusin, focusout, forced)")
        # print("end", f"W={W} - the tk name of the widget")
        # Disallow _ and %
        if (S == '_') or (S == '%'):
            self.bell()
            return False
        elif ('_' in P) or ('%' in P):
            self.bell()
            # self.customernamevar.set('')
            return False
        else:
            if self.btn_customer_exists['state'] == 'disabled':
                self.searching_similar_customer(P)
            return True

    def on_validate_shipment_delivery_note(self, d, i, P, s, S, v, V, W):
        lg.info("#on_validate_shipment_delivery_note")
        # lg.debug("OnValidate:")
        # lg.debug(f"d={d} - Type of action (1=insert, 0=delete, -1 for others)")
        # lg.debug(f"i={i} - index of char string to be inserted/deleted, or -1")
        # lg.debug(f"P={P} - value of the entry if the edit is allowed")
        # lg.debug(f"s={s} - value of entry prior to editing")
        # lg.debug(f"S={S} - the text string being inserted or deleted, if any")
        # lg.debug(f"v={v} - the type of validation that is currently set")
        # lg.debug(f"V={V} - the type of validation that triggered the callback (key, focusin, focusout, forced)")
        # lg.debug(f"W={W} - the tk name of the widget")
        # if not (S.isnumeric()) and not (S == '-'):
        if (S == '_') or (S == '%'):
            self.bell()
            return False
        elif ('_' in P) or ('%' in P):
            self.bell()
            return False
        else:
            if self.btn_shipment_exists['state'] == 'disabled':
                self.searching_similar_shipment(P)
            return True

    def on_validate_date(self, d, i, P, s, S, v, V, W):
        lg.info("#on_validate_date")
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
            lg.info("other action")
            return True
        if '0' == d:
            lg.info("delete action")
            return True
        else:
            if not(S == '-') and not(S.isnumeric()):
                self.bell()
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
                        self.bell()
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
                            self.bell()
                            return False
                return True

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
        if (S == '_') or (S == '%'):
            self.bell()
            return False
        elif ('_' in P) or ('%' in P):
            self.bell()
            return False
        else:
            if self.btn_product_exists['state'] == 'disabled':
                self.searching_similar_product(P)
            return True

    def on_validate_number(self, d, i, P, s, S, v, V, W):
        lg.info("#on_validate_number")
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
            n = int(P)
            if 0 <= n <= 1000:
                return True
            else:
                return False
        else:
            self.bell()
            return False

    def searching_similar_customer(self, P):  # (v, mode, callback):
        # print(f'searching_similar_customer to "{self.customernamevar.get()}"')
        lg.info(f'#searching_similar_customer to "{P}"')
        self.query = """
           select name from customers
           where name LIKE %(name)s
           ORDER BY name ASC
           """
        # self.parameters = ({'name': self.customernamevar.get()+'%'})
        self.parameters = ({'name': P + '%'})
        self.cmb_customer_name['values'] = ()
        add_records_to_cmb(self.conn1, self.query, self.parameters,  self.cmb_customer_name)

    def searching_similar_shipment(self, P):  # (v, mode, callback):
        # print(f'searching_similar_shipment to "{self.shipmentidvar.get()}"')
        lg.info(f'#searching_similar_shipment to "{P}"')
        self.query = """
           select delivery_note from shipments
           where delivery_note LIKE %(delivery_note)s AND customers_id = %(customers_id)s
           ORDER BY delivery_note ASC
           """
        # self.parameters = ({'id': self.shipmentidvar.get()+'%'})
        self.parameters = ({'delivery_note': P + '%',
                            'customers_id': self.customer_id})
        self.cmb_shipment_delivery_note['values'] = ()
        add_records_to_cmb(self.conn1, self.query, self.parameters, self.cmb_shipment_delivery_note)

    def searching_similar_product(self, P):  # (v, mode, callback):
        # print(f'searching_similar_product_id to "{self.productidvar.get()}"')
        lg.info(f'#searching_similar_product to "{P}"')
        self.query = """
                   select goods.id from goods
                   where goods.id LIKE %(id)s
                   ORDER BY goods.id ASC
                   LIMIT 100
                   """
        self.parameters = ({'id': P + '%'})
        self.cmb_product_id['values'] = ()
        add_records_to_cmb(self.conn1, self.query, self.parameters, self.cmb_product_id)


    def enter_customer(self):
        lg.info("#enter_customer")
        # lbl_customer_notify, cmb_customer_name_var, entry_customer_id_var
        # Те переменные, которые нужно проверить: entry_customer_id_var, entry_customer_phone_var,
        #                                         entry_customer_email_var

        # query, parameters,
        # btn_customer_exists, btn_customer_new
        # create_frame_shipment

        # devide into:  enter_customer_exists + enter_customer_new

        self.lbl_customer_notify.grid_remove()
        self.query = """
                        select id from customers
                        where name = %(name)s
                        """

        def enter_customer_exists():
            self.parameters = ({'name': self.cmb_customer_name_var.get()})
            db_rows = run_select_query(self.conn1, self.query, self.parameters)
            lg.info(f'um db_rows={db_rows}')
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
            elif isinstance(db_rows, Error):
                lg.error(error_to_str(db_rows))
            elif db_rows == []:
                lg.error(f'db_rows={[]} (empty)')
                self.lbl_customer_notify.config(fg='red', text="customer not found!\nCheck your Entry!")
                self.lbl_customer_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.error('Not found')
            elif is_iterable(db_rows):
                # for row in db_rows:
                #     lg.info(f'row={row}')
                #     lg.info(f"row[0]={row[0]}")
                self.customer_id = db_rows[0][0]
                self.lbl_customer_notify.config(fg='green', text="Chosen")
                self.lbl_customer_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.info('Chosen (after "enter_customer")')
                self.create_frame_shipment()
            elif db_rows is None:
                lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

        def enter_customer_new():
            lg.debug("\t\tself.btn_customer_new['state'] == 'disabled':")
            # checking if customer exists already
            self.parameters = ({'name': self.entry_customer_id_var.get()})
            db_rows = run_select_query(self.conn1, self.query, self.parameters)
            # lg.info(f'db_rows={db_rows}')
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
            elif isinstance(db_rows, Error):
                lg.error(error_to_str(db_rows))
            elif db_rows == []:
                lg.info(f"ok we havent found anything with parameters={self.parameters} (that's a good thing)")
                if self.entry_customer_id_var.get() == '' or self.entry_customer_phone_var.get() == '' or \
                        self.entry_customer_email_var.get() == '':
                    self.lbl_customer_notify.config(fg='red', text="Required fields\ncan't be empty!")
                    self.lbl_customer_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                else:
                    self.add_new_customer()
            elif is_iterable(db_rows):
                # for row in db_rows:
                # lg.info(f'row={row}')
                # lg.info(f"row[0]={row[0]}")
                self.lbl_customer_notify.config(fg='red', text="customer already exists!")
                self.lbl_customer_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.error('customer already exists')
            elif db_rows is None:
                lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

        if self.btn_customer_exists['state'] == 'disabled':
            enter_customer_exists()
        elif self.btn_customer_new['state'] == 'disabled':
            enter_customer_new()
        else:
            lg.error("Button not chosen! ('New' or 'Exists')")

    def enter_shipment(self):
        lg.info("#enter_shipment")

        def enter_shipment_exists():
            self.query = """
                            select id from shipments
                            where delivery_note = %(delivery_note)s
                            """
            self.parameters = ({'delivery_note': self.cmb_shipment_delivery_note.get()})
            db_rows = run_select_query(self.conn1, self.query, self.parameters)
            # lg.info(f'db_rows={db_rows}')
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
            elif isinstance(db_rows, Error):
                lg.error(error_to_str(db_rows))
            elif db_rows == []:
                lg.error(f'db_rows={[]} (empty)')
                self.lbl_shipment_notify.config(fg='red', text="Shipment not found!\nCheck your Entry!")
                self.lbl_shipment_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.error('Not found')
            elif is_iterable(db_rows):
                # for row in db_rows:
                #     lg.info(f'row={row}')
                #     lg.info(f"row[0]={row[0]}")
                self.lbl_shipment_notify.config(fg='green', text="Chosen")
                self.lbl_shipment_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                self.shipment_id = db_rows[0][0]
                lg.info('Shipment is chosen')
                self.create_frame_product()
            elif db_rows is None:
                lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

        def enter_shipment_new():
            lg.debug("\t\tself.btn_shipment_new['state'] == 'disabled':")
            # checking if shipment exists already
            self.query = """
                        select id from shipments
                        where customers_id = %(customers_id)s AND delivery_note = %(delivery_note)s
                        """
            self.parameters = ({'customers_id': self.customer_id,
                                'delivery_note': self.entry_shipment_delivery_note_var.get()
                                })

            db_rows = run_select_query(self.conn1, self.query, self.parameters)
            lg.debug(f'db_rows={db_rows}')
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
            elif isinstance(db_rows, Error):
                lg.error(error_to_str(db_rows))
            elif db_rows == []:
                lg.info(f"ok we havent found anything with parameters={self.parameters} (that's a good thing)")
                if self.entry_shipment_date.get() == '' or self.entry_shipment_delivery_note_var.get() == '':
                    self.lbl_shipment_notify.config(fg='red', text="Required fields\ncan't be empty!")
                    self.lbl_shipment_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                else:
                    self.add_new_shipment()
            elif is_iterable(db_rows):
                # for row in db_rows:
                # lg.info(f'row={row}')
                # lg.info(f"row[0]={row[0]}")
                self.lbl_shipment_notify.config(fg='red', text="Shipment already exists!")
                self.lbl_shipment_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
                lg.error('Shipment already exists')
            elif db_rows is None:
                lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

        self.lbl_shipment_notify.grid_remove()
        if self.btn_shipment_exists['state'] == 'disabled':
            enter_shipment_exists()
        elif self.btn_shipment_new['state'] == 'disabled':
            enter_shipment_new()
        else:
            lg.error("Button not chosen! ('New' or 'Exists')")

    def enter_product(self):
        lg.info("#change_package")

        def enter_product_exists():
            self.query = """
                            select goods.id from goods
                            where goods.id = %(id)s
                            """
            self.parameters = ({'id': self.cmb_product_id_var.get()})
            db_rows = run_select_query(self.conn1, self.query, self.parameters)
            # lg.info(f'db_rows={db_rows}')
            if db_rows.__class__ is int:
                lg.error(f"Could not reconnect!")
                mb.showerror(title="Connection Error!", message="Could not reconnect!")
            elif isinstance(db_rows, Error):
                lg.error(error_to_str(db_rows))
            elif db_rows == []:
                lg.error(f'db_rows={[]} (empty)')
                self.lbl_product_notify.config(fg='red', text="Product not found!\nCheck your Entry!")
                self.lbl_product_notify.grid()
                lg.error('Not found')
            elif is_iterable(db_rows):
                self.lbl_product_notify.config(fg='green', text="Chosen")
                self.lbl_product_notify.grid()
                lg.info('Product is chosen')
                self.goods_id = db_rows[0][0]
                self.add_new_product_to_shipment()
            elif db_rows is None:
                lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

        self.lbl_product_notify.grid_remove()
        enter_product_exists()


    def get_next_id(self, table_name, lbl_notify):
        lg.info("#get_next_customer_id")
        self.query = """ select MAX(id)+1 from """ + table_name
        self.parameters = ()
        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        lg.debug(f"db_rows={db_rows}")
        if db_rows.__class__ is int:
            lg.error(f"Didn't get id from database!")
            lg.error(f"Could not reconnect to database!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
            lbl_notify.config(fg='green', text="Could not reconnect to database!")
            lbl_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
            return None
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
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


    def add_new_customer(self):
        lg.info("#add_new_customer")
        customer_id = self.get_next_id("customers", self.lbl_customer_notify)
        if customer_id is None:
            lg.error(f"customer_id is None")
            return None
        self.customer_id = customer_id
        lg.debug(f"self.customer_id = {self.customer_id}")
        self.query = """INSERT INTO customers(id, name, address, phone, email, note) 
                                       VALUES(%s, %s, %s, %s, %s, %s)"""
        self.parameters = (self.customer_id,
                           self.entry_customer_id_var.get(),
                           self.entry_customer_address_var.get(),
                           self.entry_customer_phone_var.get(),
                           self.entry_customer_email_var.get(),
                           self.entry_customer_note_var.get()
                           )
        db_rows = run_commit_query(self.conn1, self.query, self.parameters)

        lg.info(f"r={db_rows}")
        # lg.debug(f"r=.__class__ = {db_rows.__class__}")
        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
            lg.error(error_to_str(db_rows))
            self.lbl_customer_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
            self.lbl_customer_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
        elif db_rows is None:
            self.lbl_customer_notify.config(fg='green', text="Added new customer!")
            self.lbl_customer_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
            self.create_frame_shipment()

    def add_new_shipment(self):
        lg.info("#add_new_shipment")
        shipment_id = self.get_next_id("shipments", self.lbl_shipment_notify)
        if shipment_id is None:
            lg.debug("shipment_id IS NONE!")
            return None
        self.shipment_id = shipment_id
        lg.debug(f"self.customer_id = {self.customer_id}")
        lg.debug(f"self.shipment_id = {self.shipment_id}")
        self.query = """INSERT INTO shipments(id, customers_id, delivery_note, date, note) 
                                               VALUES(%s, %s, %s, %s, %s)"""
        self.parameters = (self.shipment_id,
                           self.customer_id,
                           self.entry_shipment_delivery_note_var.get(),
                           self.entry_shipment_date_var.get(),
                           self.entry_shipment_note_var.get(),
                           )
        db_rows = run_commit_query(self.conn1, self.query, self.parameters)

        lg.debug(f"db_rows={db_rows}")
        # lg.debug(f"r=.__class__ = {db_rows.__class__}")
        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
            lg.error(error_to_str(db_rows))
            self.lbl_shipment_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
            self.lbl_shipment_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
        elif db_rows is None:
            self.lbl_shipment_notify.config(fg='green', text="Added new shipment!")
            self.lbl_shipment_notify.grid(row=8, column=0, columnspan=2, sticky='', pady=(5, 5))
            lg.info(f"self.shipment_id = {self.shipment_id}")
            self.create_frame_product()

    def add_new_product_to_shipment(self):
        lg.info("#add_new_product_to_shipment")

        lg.debug(f"self.goods_id = {self.goods_id}")
        # self.query = """INSERT INTO goods_shipments(goods_id, shipments_id)
        #                                      VALUES(%s, %s)"""
        # self.parameters = (self.goods_id,
        #                    self.shipment_id
        #                    )
        # db_rows = run_commit_query(self.conn1, self.query, self.parameters)
        self.query = f"""CALL sell_package({self.goods_id}, {self.shipment_id})"""
        db_rows = run_commit_query(self.conn1, self.query)

        # lg.debug(f"db_rows={db_rows}")
        # lg.debug(f"r=.__class__ = {db_rows.__class__}")
        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            # lg.error(f"res IS ERROR:  isinstance(res, {Error}) = {isinstance(db_rows, Error)}")
            if db_rows.errno == 1062:
                lg.info("Package is already in another shipment!")
                self.lbl_product_notify.config(fg='red', text=insert_new_line_symbols(
                                                         "Package is already in another shipment!"))
                self.lbl_product_notify.grid()
            else:
                lg.error(error_to_str(db_rows))
                self.lbl_product_notify.config(fg='red', text=insert_new_line_symbols(error_to_str(db_rows)))
                self.lbl_product_notify.grid()

        elif db_rows is None:
            # lg.debug(f"self.goods_id = {self.goods_id}")
            self.lbl_product_notify.config(fg='green', text="Added new product to shipment!")

class MainTreeItemWindow(tk.Toplevel):

    def __init__(self, parent, conn1):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.conn1 = conn1

        self.parameters = ()
        self.label_str = ''
        lg.info('########   CREATING MainTreeItemWindow  ########')
        self.title('Database Workplace - Item info')

        # self.parent.geometry('567x300')
        self.minsize(int(self.parent.winfo_screenwidth() * 2 / 10), int(self.parent.winfo_screenheight() * 3 / 10))
        self.maxsize(int(self.parent.winfo_screenwidth()), int(self.parent.winfo_screenheight()))
        # self.resizable(False, False)
        place_tk_to_screen_center(self)

        self.frame1 = tk.Frame(self)
        self.frame1.pack(side=tk.TOP, fill=tk.X, expand=False)
        self.frame1.config(background="purple")

        self.item = self.parent.tree.item(self.parent.item, "values")
        self.item_id = self.parent.tree.item(self.parent.item, "values")[0]
        # lg.info(f'self.item_id={self.item_id}')
        # self.lbl_show = tk.Label(self.frame_top, text="Showing Supply #" + self.item_id)
        self.label1 = tk.Label(self.frame1, text="THIS IS LABEL FOR ID =" + self.item_id)
        self.label1.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5, expand=False)

        # Set the treeview
        # Уже в self.columns нужно заносить те значения которые хотим отображать, иначе сортировка изменит оглавления
        self.columns = ''
        self.tree = ttk.Treeview(self, columns=self.columns, style="mystyle.Treeview")
        self.tree['show'] = 'headings'  # Прячу первый столбец который text

        self.tree.bind("<Button-3>", self.on_right_click)

        self.tree.tag_configure('orange', background='orange')
        self.tree.tag_configure('purple', background='purple')
        # #f0f0f0
        self.tree.tag_configure('grey', background='grey')
        self.tree.tag_configure('lightgrey', background='lightgrey')

        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.hsb.set)
        self.hsb.pack(side="bottom", fill="x")
        self.tree.config(height=int(self.parent.winfo_screenheight() * 7 / 10))
        # print(f'int(self.parent.winfo_screenheight()*7/10) = {int(self.parent.winfo_screenheight()*7/10)}')
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        self.popupmenu = Menu(self.tree, tearoff=0)
        # self.popupmenu.add_command(label="Delete record from supply",
        #                            command=lambda: self.delete_table_records("goods_supplies"))

        # Understanding what we need to show
        if self.parent.table == 'supplies':  # delete from goods_supplies  =  delete from goods
            self.popupmenu.add_command(label="Delete record", command=lambda: self.delete_table_records("goods"))
            self.show_supplies_items()

        elif self.parent.table == 'catalog':
            self.popupmenu.add_command(label="Delete record", command=lambda: self.delete_table_records("goods"))
            self.show_catalog_items()

        elif self.parent.table == 'suppliers':
            self.show_suppliers_items()

        elif self.parent.table == 'storage':
            self.show_storage_items()

        elif self.parent.table == 'customers':
            self.show_customers_items()

        elif self.parent.table == 'shipments':
            self.popupmenu.add_command(label="Return package",
                                       command=lambda: self.delete_table_records("goods_shipments"))
            self.show_shipments_items()

        set_active(self)


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

    def delete_table_records(self, table_name):

        near_item = get_near_item(self.tree, self.item)
        success_delete = delete_table_records(self.conn1, table_name,
                                              self.tree.item(self.item, "values")[0])
        if success_delete is None:
            return
        if near_item != '':
            self.tree.selection_set(near_item)

        # update_treeview(self)
        self.viewing_records()


    def show_supplies_items(self):
        self.show = 'show_supplies_items'
        # Change Label
        self.label_str = 'Showing supply'
        self.label1.config(text=self.label_str + ' #' + self.item_id)

        # Change Treeview
        self.columns = (
        'id', "Product Name", 'Price', "State", 'Production Date', 'Expiration_Date', 'Description', 'Note')
        self.change_tree_columns()
        self.tree.bind("<Double-1>", self.on_double_click)

        # Set query
        self.query = """
        SELECT * FROM goods_view
        WHERE goods_view.id IN (SELECT goods_id FROM goods_supplies
                WHERE supplies_id = %(supplies_id)s)
        ORDER BY goods_view.id DESC;"""
        self.parameters = ({'supplies_id': self.item_id})
        self.viewing_records()

    def show_catalog_items(self):
        self.show = 'show_catalog_items'
        # Change Label
        self.label_str = 'Showing goods related to Catalog item_id'
        self.label1.config(text=self.label_str + ' #' + self.item_id)

        # Change Treeview
        self.columns = ('Product id', "State", 'Production Date', 'Expiration_Date', 'Note')
        self.change_tree_columns()
        self.tree.bind("<Double-1>", self.on_double_click)

        # Set query
        self.query = """
                SELECT goods.id, package_states.state, Production_Date,
                       IF(ISNULL(shelf_life), NULL, DATE_ADD(production_date, INTERVAL shelf_life DAY)) as Expiration_Date, Note
                FROM goods 
                        left join catalog on goods.catalog_id = catalog.id     
                        Left join package_states  ON goods.state_id   = package_states.id
                WHERE catalog_id = %(catalog_id)s
                ORDER BY id DESC;
                """
        self.parameters = ({'catalog_id': self.item_id})
        self.viewing_records()

    def show_suppliers_items(self):
        self.show = 'show_suppliers_items'
        # Change Label
        self.label_str = "Showing supplier's"
        self.label1.config(text=self.label_str + '#' + self.item_id + ' supplies')

        # Change Treeview
        self.columns = ('id', 'Date', 'Delivery Note', 'Note')
        self.change_tree_columns()
        self.tree.bind("<Double-1>", self.on_double_click)

        # Change query
        self.query = """
        SELECT id, date, delivery_note, note FROM supplies
        WHERE suppliers_id = %(suppliers_id)s
        ORDER BY id DESC;"""
        self.parameters = ({'suppliers_id': self.item_id})
        self.viewing_records()

    def show_storage_items(self):
        self.show = 'show_storage_items'
        # Change Label
        self.label_str = "Showing storaged Product"
        self.label1.config(text=self.label_str + ' #' + self.item_id)

        # Change Treeview
        self.columns = (
        'id', 'Shelf', 'Product Name', 'Price', 'Production Date', 'Expiration Date', 'Description', 'Note')
        self.change_tree_columns()
        self.tree.bind("<Double-1>", self.on_double_click)

        # Change query
        self.query = """
        SELECT goods_id, shelf, product_name, price, production_date,
                IF(ISNULL(shelf_life), NULL, DATE_ADD(production_date, INTERVAL shelf_life DAY)) as Expiration_Date,
                description, note
        FROM storage LEFT JOIN goods on storage.goods_id = goods.id LEFT JOIN catalog on goods.catalog_id = catalog.id
        WHERE goods_id = %(goods_id)s
        ORDER BY goods_id DESC;"""
        self.parameters = ({'goods_id': self.item_id})
        self.viewing_records()

    def show_customers_items(self):
        self.show = 'show_customers_items'
        # Change Label
        self.label_str = "Showing Customer's"
        self.label1.config(text=self.label_str + '#' + self.item_id + ' shipments')

        # Change Treeview
        self.columns = ('id', 'Date', 'Delivery Note', 'Note')
        self.change_tree_columns()
        self.tree.bind("<Double-1>", self.on_double_click)
        # Change query
        self.query = """
                SELECT shipments.id, date, delivery_note, shipments.note FROM shipments
                WHERE customers_id = %(customers_id)s
                ORDER BY id DESC;"""
        self.parameters = ({'customers_id': self.item_id})
        self.viewing_records()

    def show_shipments_items(self):
        self.show = 'show_shipments_items'
        # Change Label
        self.label_str = "Showing shipment"
        self.label1.config(text=self.label_str + ' #' + self.item_id)

        # Change Treeview
        self.columns = ('id', "Product Name", 'Price', 'Production Date', 'Expiration_Date', 'Description', 'Note')
        self.change_tree_columns()
        self.tree.bind("<Double-1>", self.on_double_click)

        # Set query
        self.query = """
                SELECT goods.id as id, Product_name, Price, Production_Date,
                   IF(ISNULL(shelf_life), NULL, DATE_ADD(production_date, INTERVAL shelf_life DAY)) as Expiration_Date,
                   description, Note
                FROM goods Left join catalog ON goods.catalog_id = catalog.id
                WHERE goods.id IN (SELECT goods_id FROM goods_shipments
                        WHERE shipments_id = %(shipments_id)s)
                ORDER BY goods.id DESC;"""
        self.parameters = ({'shipments_id': self.item_id})
        self.viewing_records()

    def on_double_click(self, event):
        self.item = self.tree.identify('item', event.x, event.y)
        # lg.info(f"you clicked on self.item='{self.item}'")
        if not (self.item == ''):
            self.item_id_clicked = self.tree.item(self.item, "values")[0]
            lg.info("you clicked on Item #", self.item_id_clicked)

            def show_clicked_item():
                treechildren = self.parent.tree.get_children()
                child_select = None
                for child in treechildren:
                    if self.parent.tree.item(child, "values")[0] == self.item_id_clicked:
                        child_select = child
                        break
                if child_select is None:
                    lg.error('ERROR: GOODS DISAPPEARED!!!')
                else:
                    lg.info(f"child_select={child_select}")
                    self.parent.tree.focus(child_select)
                    self.parent.tree.selection_set(child_select)
                    self.parent.tree.see(child_select)
                    self.destroy()

            if self.show == 'show_supplies_items':
                self.parent.show_goods()
                show_clicked_item()
            elif self.show == 'show_catalog_items':
                self.parent.show_goods()
                show_clicked_item()
            elif self.show == 'show_suppliers_items':
                self.parent.show_supplies()
                show_clicked_item()
            elif self.show == 'show_storage_items':
                self.parent.show_goods()
                show_clicked_item()
            elif self.show == 'show_customers_items':
                self.parent.show_shipments()
                show_clicked_item()
            elif self.show == 'show_shipments_items':
                self.parent.show_goods()
                show_clicked_item()
            else:  # в принципе не нужно, но вдруг..
                lg.critical(f"Impossible happened: unknown self.show={self.show}")

    def change_tree_columns(self):
        def enable_treeview_sorting():
            # columns = ('name', 'age')
            # self.treeview = ttk.TreeView(root, columns=columns, show='headings')   # Interesting

            # for col in self.columns:
            #     self.tree.heading(col, text=col, command=lambda: treeview_sort_column(self.tree, col, False))
            for col in self.columns:
                self.tree.heading(col, text=col,
                                  command=lambda _col=col: treeview_sort_column(self.tree, _col, False))

        self.tree.config(columns=self.columns)
        self.tree.heading('#0', anchor=tk.W, text='LOL THIS IS HIDDEN FOREVER ))')
        self.tree.column('#0', width=0, minwidth=0, stretch=tk.NO)
        for col in self.columns:
            self.tree.heading(col, anchor=tk.W, text='lul default')
            self.tree.column(col, width=100, minwidth=50, stretch=tk.NO)
        enable_treeview_sorting()

    def viewing_records(self):
        lg.info("#viewing_table_records")
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)

        db_rows = run_select_query(self.conn1, self.query, self.parameters)
        # lg.info(f'db_rows={db_rows}')

        if db_rows.__class__ is int:
            lg.error(f"Could not reconnect!")
            mb.showerror(title="Connection Error!", message="Could not reconnect!")
        elif isinstance(db_rows, Error):
            lg.error(error_to_str(db_rows))
            if db_rows.errno == 1142:
                mb.showerror("Access denied", "You haven't got permission to watch this table")
        elif db_rows == []:
            lg.debug('Recieved empty array')
        elif is_iterable(db_rows):
            for row in db_rows:
                if (self.show == 'show_supplies_items' and row[3] == 'sold') or \
                        (self.show == 'show_catalog_items' and row[1] == 'sold'):
                    self.tree.insert("", 0, "", text='', values=row, tag='grey')
                else:
                    self.tree.insert("", 0, "", text='', values=row, tag='lightgrey')
        elif db_rows is None:
            lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')


class BaseProductFrame(tk.Frame):
    """ 3 Варианта:
    1. Сразу добавляем всё что нужно и в заисимости от вызова... - вариант не очень
       UPD: ITS THE BEST VARIANT FOR CHOOSE AND ENTER
    2. Делаем минимальный класс и добавляем в классы-наследники от этого
        то чего не хватает, однако при использовании .pack() встаёт вопрос:
        Как это изобразить правильно? (Так как важен поядок добавления объектов)
        Ответ: разделить инициализацию объектов с их прорисовкой и делать это
            в классе-наследнике
    3. То же что и 2-ой вариант, но использовать .grid, он сам выстраивает
        порядок объектов и добавит промежуточные при необходимости - лучший вариант

    Возможные наследники:
    просмтор:
    добавление:
    продажа:
    изм_выбор:
    изм_ввод:
    """
    """ Порядок:
    0 : label                           - просмтор, добавление, продажа, изм_выбор, изм_ввод, удаление
    1 : btn_new, btn_exists (may везде) -           добавление,
    2 : cmb_id                          -                       продажа, изм_выбор,
    2 : entry_id                        - просмтор,                                           удаление
    3 : cmb_name                        -           добавление,
    3 : entry_name                      - просмтор, добавление, продажа, изм_выбор, изм_ввод, удаление
    6 : price, shelf_life, description  - просмтор, добавление, продажа, изм_выбор, изм_ввод, удаление
    8 : production_date, note           - просмтор, добавление, продажа, изм_выбор, изм_ввод, удаление
    9 : amount                          -           добавление,
    10: btn_archive                       -           добавление, продажа, изм_выбор, изм_ввод, удаление
    11: lbl_notify                      - просмтор, добавление, продажа, изм_выбор, изм_ввод, удаление
    """
    """ BaseProduct (for просмтор, добавление, продажа, изм_выбор, изм_ввод)
    0 : label
    3 : entry_name
    4 : price
    5 : shelf_life
    6 : description
    7 : production_date
    8 : note
    11: lbl_notify
    """
    def __init__(self, parent, color):
        lg.info('########   CREATING BaseProductFrame   ########')
        tk.Frame.__init__(self, parent)
        self.parent = parent
        # Placing frame on form
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.config(background=color)

        self.frame = self
        frame = self
        # Creating Button widgets
        # self.btn_product_enter = tk.Button(frame, text="Enter", command=self.change_package)
        # self.btn_product_new = tk.Button(frame, text="Add New", command=adding_product)
        # self.btn_product_exists = tk.Button(frame, text="Already Exists", command=choosing_product)
        # Creating Label widgets
        self.lbl_product = tk.Label(frame, text='Product', background=frame['background'],
                                    font=('Calibri', 11, 'bold'))
        self.lbl_product_name = tk.Label(frame, text='Product Name*', background=frame['background'])
        self.lbl_product_price = tk.Label(frame, text='price*', background=frame['background'])
        self.lbl_product_shelf_life = tk.Label(frame, text='shelf life*', background=frame['background'])
        self.lbl_product_description = tk.Label(frame, text='description', background=frame['background'])
        self.lbl_product_production_date = tk.Label(frame, text='production date*', background=frame['background'])
        self.lbl_product_note = tk.Label(frame, text='note', background=frame['background'])
        self.lbl_product_notify = tk.Label(frame, text='lbl_product_notify',
                                           background=frame['background'],
                                           font=('Calibri', 11, 'bold'), fg='black')
        # Creating Entry widgets
        vcmd = (self.register(on_validate_name),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd2 = (self.register(on_validate_date),
                 '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.vcmd3 = (self.register(on_validate_naturalnumber),
                 '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        # self.cmb_product_id = ttk.Combobox(frame, validate="key", validatecommand=vcmd3)  # ComboBox
        self.entry_product_name = tk.Entry(frame, validate="key", validatecommand=vcmd)
        self.entry_product_price = tk.Entry(frame)
        self.entry_product_shelf_life = tk.Entry(frame)
        self.entry_product_description = tk.Entry(frame)
        self.entry_product_production_date = tk.Entry(frame, validate="key", validatecommand=vcmd2)
        self.entry_product_note = tk.Entry(frame)

        # Creating Entry widgets's variables
        # self.cmb_product_id_var = tk.StringVar()
        self.entry_product_name_var = tk.StringVar()
        self.entry_product_price_var = tk.StringVar()
        self.entry_product_shelf_life_var = tk.StringVar()
        self.entry_product_description_var = tk.StringVar()
        self.entry_product_production_date_var = tk.StringVar()
        self.entry_product_note_var = tk.StringVar()

        # Set widgets to some value.
        # self.cmb_product_id_var.set("")
        self.entry_product_name_var.set("")
        self.entry_product_price_var.set("")
        self.entry_product_shelf_life_var.set("")
        self.entry_product_description_var.set("")
        self.entry_product_production_date_var.set("")
        self.entry_product_note_var.set("")

        # Assigning variables to widgets    (Tell the widget to watch this variable.)
        # self.cmb_product_id["textvariable"] = self.cmb_product_id_var
        self.entry_product_name["textvariable"] = self.entry_product_name_var
        self.entry_product_price["textvariable"] = self.entry_product_price_var
        self.entry_product_shelf_life["textvariable"] = self.entry_product_shelf_life_var
        self.entry_product_description["textvariable"] = self.entry_product_description_var
        self.entry_product_production_date["textvariable"] = self.entry_product_production_date_var
        self.entry_product_note["textvariable"] = self.entry_product_note_var

        # Binding widgets with functions
        # self.cmb_product_id.bind('<FocusIn>', self.cmb_product_id.selection_range(0, END))
        # self.cmb_product_id.bind("<<ComboboxSelected>>", combobox_selected)
        self.entry_product_name.bind('<FocusIn>', self.entry_product_name.selection_range(0, END))
        self.entry_product_price.bind('<FocusIn>', self.entry_product_price.selection_range(0, END))
        self.entry_product_shelf_life.bind('<FocusIn>', self.entry_product_shelf_life.selection_range(0, END))
        self.entry_product_description.bind('<FocusIn>', self.entry_product_description.selection_range(0, END))
        self.entry_product_production_date.bind('<FocusIn>', self.entry_product_production_date.selection_range(0, END))
        self.entry_product_note.bind('<FocusIn>', self.entry_product_note.selection_range(0, END))

        self.lbl_product_notify.grid_remove()
        # self.cmb_product_id.grid_remove()
        # self.entry_product_id.grid_remove()

    def place_base_product_widgedts(self):
        # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
        self.lbl_product.grid(row=0, column=0, columnspan=2)  # sticky=N+S+W+E,
        # self.btn_product_new.grid(              row=1,  column=0, padx=5, pady=5, sticky='e')
        # self.btn_product_exists.grid(row=1, column=1, padx=(5, 10), sticky='e')

        # self.lbl_product_id.grid(row=2, column=0, sticky='es')
        self.lbl_product_name.grid(row=3, column=0, sticky='e', pady=(10, 0))
        self.lbl_product_price.grid(row=4, column=0, sticky='e')
        self.lbl_product_shelf_life.grid(row=5, column=0, sticky='e')
        self.lbl_product_description.grid(row=6, column=0, sticky='e')
        self.lbl_product_production_date.grid(row=7, column=0, sticky='e', pady=(15, 0), padx=(5, 0))
        self.lbl_product_note.grid(row=8, column=0, sticky='e')

        # self.cmb_product_id.grid(row=2, column=1, padx=(5, 0), pady=(10, 0))

        self.entry_product_name.grid(row=3, column=1, padx=(15, 30), pady=(10, 0))
        self.entry_product_price.grid(row=4, column=1, padx=(15, 30))
        self.entry_product_shelf_life.grid(row=5, column=1, padx=(15, 30))
        self.entry_product_description.grid(row=6, column=1, padx=(15, 30))
        self.entry_product_production_date.grid(row=7, column=1, padx=(15, 30), pady=(15, 0))
        self.entry_product_note.grid(row=8, column=1, padx=(15, 30))

        # self.btn_product_enter.grid(row=10, column=0, columnspan=2, sticky='', pady=(5, 5))
        self.lbl_product_notify.grid(row=11, column=0, columnspan=2, sticky='', pady=(5, 5))
pass
# class ChooseProductFrame(BaseProductFrame):
#     "Choose существуют разные. Есть окошко в котором реализовано и Choose и Enter New"
#     def __init__(self, parent, goods_id):
#         color = "lightgray"
#         super().__init__(parent, color)
#         lg.info('########   CREATING BaseChooseProductFrame   ########')
#
#         self.goods_id = int(goods_id)
#
#         frame = self
#         self.lbl_product_id = tk.Label(frame, text='id*', background=frame['background'])
#         self.lbl_storage_shelf = tk.Label(frame, text='Storage Shelf', background=frame['background'])
#
#         self.entry_product_id = tk.Entry(frame)
#         self.entry_storage_shelf = tk.Entry(frame)
#
#         self.entry_product_id_var = tk.StringVar()
#         self.entry_storage_shelf_var = tk.StringVar()
#         self.entry_product_id_var.set(self.goods_id)
#         self.entry_storage_shelf_var.set("")
#
#         self.entry_product_id["textvariable"] = self.entry_product_id_var
#         self.entry_storage_shelf["textvariable"] = self.entry_storage_shelf_var
#
#         self.entry_product_id.bind('<FocusIn>', self.entry_product_id.selection_range(0, END))
#         self.entry_storage_shelf.bind('<FocusIn>', self.entry_storage_shelf.selection_range(0, END))
#
#         def place_widgedts():
#             self.place_base_product_widgedts()
#             self.lbl_product_id.grid(row=2, column=0, pady=(10, 0), sticky='e')
#             self.lbl_storage_shelf.grid(row=9, column=0, pady=(10, 0), sticky='e')
#             self.entry_product_id.grid(row=2, column=1, padx=(15, 30), pady=(10, 0))
#             self.entry_storage_shelf.grid(row=9, column=1, padx=(15, 30), pady=(10, 0))
#
#         def turn_off_frame(*args):
#             # # Turning off frame_shipment
#             # # self.config(background='navajowhite')
#             # for child in self.winfo_children():
#             #     # child.config(background='navajowhite')
#             #     lg.debug(f'1) child={child}')
#             #     child.config(state = 'disabled', )
#             # # self.btn_supply_exists.unbind('<Button-1>')
#             # # self.btn_supply_new.unbind('<Button-1>')
#
#             for child in self.winfo_children():
#                 # lg.debug(f"child={child}")
#                 if isinstance(child, Entry) and Entry in args:  # turning off Entry
#                     child.config(relief=SUNKEN, state="readonly")
#
#         place_widgedts()
#         turn_off_frame(Entry)
#         place_window(self.parent, self)



# UNUSED CLASS
pass
class BaseWatchProductFrame(BaseProductFrame):
    """Отобразить товар, Поставку, Поставщика, Отправку, Покупателя"""
    def __init__(self, parent, goods_id):
        color = "lightgray"
        super().__init__(parent, color)
        lg.info('########   CREATING WatchProductFrame   ########')

        self.goods_id = int(goods_id)

        frame = self
        self.lbl_product_id = tk.Label(frame, text='id*', background=frame['background'])
        self.lbl_storage_shelf = tk.Label(frame, text='Storage Shelf', background=frame['background'])

        self.entry_product_id = tk.Entry(frame)
        self.entry_storage_shelf = tk.Entry(frame)

        self.entry_product_id_var = tk.StringVar()
        self.entry_storage_shelf_var = tk.StringVar()
        self.entry_product_id_var.set(self.goods_id)
        self.entry_storage_shelf_var.set("")

        self.entry_product_id["textvariable"] = self.entry_product_id_var
        self.entry_storage_shelf["textvariable"] = self.entry_storage_shelf_var

        self.entry_product_id.bind('<FocusIn>', self.entry_product_id.selection_range(0, END))
        self.entry_storage_shelf.bind('<FocusIn>', self.entry_storage_shelf.selection_range(0, END))

        def place_widgedts():
            self.place_base_product_widgedts()
            self.lbl_product_id.grid(row=2, column=0, pady=(10, 0), sticky='e')
            self.lbl_storage_shelf.grid(row=9, column=0, pady=(10, 0), sticky='e')
            self.entry_product_id.grid(row=2, column=1, padx=(15, 30), pady=(10, 0))
            self.entry_storage_shelf.grid(row=9, column=1, padx=(15, 30), pady=(10, 0))

        def turn_off_frame(*args):
            # # Turning off frame_shipment
            # # self.config(background='navajowhite')
            # for child in self.winfo_children():
            #     # child.config(background='navajowhite')
            #     lg.debug(f'1) child={child}')
            #     child.config(state = 'disabled', )
            # # self.btn_supply_exists.unbind('<Button-1>')
            # # self.btn_supply_new.unbind('<Button-1>')

            for child in self.winfo_children():
                # lg.debug(f"child={child}")
                if isinstance(child, Entry) and Entry in args:  # turning off Entry
                    child.config(relief=SUNKEN, state="readonly")

        place_widgedts()
        turn_off_frame(Entry)
        place_window(self.parent, self)

# Supplier
pass
# class BaseSupplierFrame(tk.Frame):  # передавать kwargs, для упаковки (в далёком будущем)
#
#     def __init__(self, parent, color):
#         lg.info('########   CREATING BaseSupplierFrame   ########')
#         tk.Frame.__init__(self, parent)
#         self.parent = parent
#         # Placing frame on form
#         self.pack(side=tk.LEFT, fill=tk.Y, background=color)
#
#         self.frame = self
#         frame = self
#         # Creating Button widgets
#         # self.btn_supplier_enter = tk.Button(frame, text="Enter", command=self.enter_supplier)
#         # self.btn_supplier_new = tk.Button(frame, text="Add New", command=adding_supplier)
#         # self.btn_supplier_exists = tk.Button(frame, text="Already Exists", command=choosing_supplier)
#         # Creating Label widgets
#         self.lbl_supplier = tk.Label(frame, text='Supplier', background=frame['background'],
#                                      font=('Calibri', 11, 'bold'))
#         self.lbl_supplier_name = tk.Label(frame, text='Supplier Name*', background=frame['background'])
#         self.lbl_product_price = tk.Label(frame, text='price*', background=frame['background'])
#         self.lbl_product_shelf_life = tk.Label(frame, text='shelf life*', background=frame['background'])
#         self.lbl_product_description = tk.Label(frame, text='description', background=frame['background'])
#         self.lbl_product_production_date = tk.Label(frame, text='production date*', background=frame['background'])
#         self.lbl_product_note = tk.Label(frame, text='note', background=frame['background'])
#         self.lbl_product_notify = tk.Label(frame, text='Product already exists!',
#                                            background=frame['background'],
#                                            font=('Calibri', 11, 'bold'), fg='red')
#         # Creating Entry widgets
#         vcmd = (self.register(widget_on_validate_name),
#                 '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
#         vcmd2 = (self.register(on_validate_date),
#                  '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
#         self.vcmd3 = (self.register(on_validate_naturalnumber),
#                  '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
#         # self.cmb_product_id = ttk.Combobox(frame, validate="key", validatecommand=vcmd3)  # ComboBox
#         self.entry_supplier_name = tk.Entry(frame, validate="key", validatecommand=vcmd)
#         self.entry_product_price = tk.Entry(frame)
#         self.entry_product_shelf_life = tk.Entry(frame)
#         self.entry_product_description = tk.Entry(frame)
#         self.entry_product_production_date = tk.Entry(frame, validate="key", validatecommand=vcmd2)
#         self.entry_product_note = tk.Entry(frame)
#
#         # Creating Entry widgets's variables
#         # self.cmb_product_id_var = tk.StringVar()
#         self.entry_supplier_name_var = tk.StringVar()
#         self.entry_product_price_var = tk.StringVar()
#         self.entry_product_shelf_life_var = tk.StringVar()
#         self.entry_product_description_var = tk.StringVar()
#         self.entry_product_production_date_var = tk.StringVar()
#         self.entry_product_note_var = tk.StringVar()
#
#         # Set widgets to some value.
#         # self.cmb_product_id_var.set("")
#         self.entry_supplier_name_var.set("")
#         self.entry_product_price_var.set("")
#         self.entry_product_shelf_life_var.set("")
#         self.entry_product_description_var.set("")
#         self.entry_product_production_date_var.set("")
#         self.entry_product_note_var.set("")
#
#         # Assigning variables to widgets    (Tell the widget to watch this variable.)
#         # self.cmb_product_id["textvariable"] = self.cmb_product_id_var
#         self.entry_supplier_name["textvariable"] = self.entry_supplier_name_var
#         self.entry_product_price["textvariable"] = self.entry_product_price_var
#         self.entry_product_shelf_life["textvariable"] = self.entry_product_shelf_life_var
#         self.entry_product_description["textvariable"] = self.entry_product_description_var
#         self.entry_product_production_date["textvariable"] = self.entry_product_production_date_var
#         self.entry_product_note["textvariable"] = self.entry_product_note_var
#
#         # Binding widgets with functions
#         # self.cmb_product_id.bind('<FocusIn>', self.cmb_product_id.selection_range(0, END))
#         # self.cmb_product_id.bind("<<ComboboxSelected>>", combobox_selected)
#         self.entry_supplier_name.bind('<FocusIn>', self.entry_supplier_name.selection_range(0, END))
#         self.entry_product_price.bind('<FocusIn>', self.entry_product_price.selection_range(0, END))
#         self.entry_product_shelf_life.bind('<FocusIn>', self.entry_product_shelf_life.selection_range(0, END))
#         self.entry_product_description.bind('<FocusIn>', self.entry_product_description.selection_range(0, END))
#         self.entry_product_production_date.bind('<FocusIn>', self.entry_product_production_date.selection_range(0, END))
#         self.entry_product_note.bind('<FocusIn>', self.entry_product_note.selection_range(0, END))
#
#         # Locating widgets  (anchor: n, ne, e, se, s, sw, w, nw, or center)
#         self.lbl_supplier.grid(row=0, column=0, columnspan=2)  # sticky=N+S+W+E,
#         # self.btn_product_new.grid(              row=1,  column=0, padx=5, pady=5, sticky='e')
#         # self.btn_product_exists.grid(row=1, column=1, padx=(5, 10), sticky='e')
#
#         # self.lbl_product_id.grid(row=2, column=0, sticky='es')
#         self.lbl_supplier_name.grid(row=3, column=0, sticky='e', pady=(10, 0))
#         self.lbl_product_price.grid(row=4, column=0, sticky='e')
#         self.lbl_product_shelf_life.grid(row=5, column=0, sticky='e')
#         self.lbl_product_description.grid(row=6, column=0, sticky='e')
#         self.lbl_product_production_date.grid(row=7, column=0, sticky='e', pady=(15, 0), padx=(5, 0))
#         self.lbl_product_note.grid(row=8, column=0, sticky='e')
#
#         # self.cmb_product_id.grid(row=2, column=1, padx=(5, 0), pady=(10, 0))
#
#         self.entry_supplier_name.grid(row=3, column=1, padx=(15, 30), pady=(10, 0))
#         self.entry_product_price.grid(row=4, column=1, padx=(15, 30))
#         self.entry_product_shelf_life.grid(row=5, column=1, padx=(15, 30))
#         self.entry_product_description.grid(row=6, column=1, padx=(15, 30))
#         self.entry_product_production_date.grid(row=7, column=1, padx=(15, 30), pady=(15, 0))
#         self.entry_product_note.grid(row=8, column=1, padx=(15, 30))
#
#         # self.btn_product_enter.grid(row=10, column=0, columnspan=2, sticky='', pady=(5, 5))
#         self.lbl_product_notify.grid(row=11, column=0, columnspan=2, sticky='', pady=(5, 5))
#
#         self.lbl_product_notify.grid_remove()
#         # self.cmb_product_id.grid_remove()
#         # self.entry_product_id.grid_remove()

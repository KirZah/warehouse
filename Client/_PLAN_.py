""""
changes:

поменять
"""

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
        self.entry_package_id = tk.Entry(frame)
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
                        where storage.goods_id = %(goods_id)s
                     """
        self.parameters = ({'goods_id': self.goods_id})

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

    # def is_catalog_element_exists(self):
    #     lg.info("#is_catalog_element_exists")
    #     # if self.btn_new["state"] == "disabled":
    #     product_name = self.entry_directory_var.get()
    #     # else:
    #     #     package_id = self.cmb_product_name_var.get()
    #     self.query = """
    #                     select id from catalog
    #                     where package_id = %(package_id)s
    #                     """
    #     self.parameters = ({'package_id': product_name})
    #     db_rows = run_select_query(self.conn1, self.query, self.parameters)
    #     lg.info(f'db_rows={db_rows}')
    #     if db_rows.__class__ is int:
    #         lg.error(f"Could not reconnect!")
    #         mb.showerror(title="Connection Error!", message="Could not reconnect!")
    #         return None
    #     elif isinstance(db_rows, Error):
    #         error_msg = error_to_str(db_rows)
    #         lg.error(error_msg)
    #         self.lbl_archive_notify.config(fg='red', text=insert_new_line_symbols(error_msg))
    #         self.lbl_archive_notify.grid()
    #         return None
    #     elif db_rows == []:
    #         lg.info("Catalog element doesn't exist")
    #         # self.lbl_archive_notify.config(fg='red', text="Catalog element doesn't exist")
    #         # self.lbl_archive_notify.grid()
    #         return False
    #     elif is_iterable(db_rows):
    #         lg.info("Catalog element exists")
    #
    #         self.goods_id = db_rows[0][0]
    #         return True
    #     elif db_rows is None:
    #         lg.debug('OMG WHAT THE HELL? WHY I RECIEVED "None"????')

    def change_shelf(self):
        lg.info("#archive")

        def update_shelf():
            lg.debug(f"self.goods_id = {self.goods_id}")
            # "UPDATE table_name SET field1 = new-value1, field2 = new-value2"
            self.query = """UPDATE storage SET shelf = %(shelf)s,
                            WHERE storage.goods_id = %(goods_id)s"""
            self.parameters = ({
                'goods_id': self.entry_package_id_var.get(),
                'shelf': self.entry_package_shelf_var.get()
                })
            db_rows = run_change_query(self.conn1, self.query, self.parameters)

            # lg.info(f"db_rows={db_rows}")
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

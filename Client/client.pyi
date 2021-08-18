import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import *
#
# import time
#
# # import mysql
# # import mysql.connector
# # import mysql.connector.locales.eng
# from mysql.connector import Error
# # from mysql.connector import errorcode
#
# # from loguru import logger as lg
#
# # from Connection import Connection
# from Frames import ConnectionFrame, AboutFrame
# from Functions import *

class MainWindow(tk.Tk):
    tree: ttk.Treeview
    popup : tk.Menu
    # def __init__(self) -> None:
    #     super().__init__()
    #     self.tree: ttk.Treeview

    def initialize_user_interface(self) -> None: ...


    # def on_right_click(self, event) -> None:
    #     self.item: ttk.Treeview


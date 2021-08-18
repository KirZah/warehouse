# imports
from tkinter import *
from tkinter.ttk import *
from tkinter.font import *

# subclass treeview for the convenience of overriding the column method
class ScrollableTV(Treeview):
  def __init__(self, master, **kw):
    super().__init__(master, **kw)
    self.columns=[]

  # column now records the name and details of each column in the TV just before they're added
  def column(self, column, **kw):
    if column not in [column[0] for column in self.columns]:
      self.columns.append((column, kw))
    super().column(column, **kw)

  # keep a modified, heavier version of Style around that you can use in cases where ScrollableTVs are involved
  class ScrollableStyle(Style):
    def __init__(self, tv, *args, **kw):
      super().__init__(*args, **kw)
      self.tv = tv

    # override Style's configure method to reset all its TV's columns to their initial settings before it returns into TtkResizeWidget(). since we undo the TV's automatic changes before the screen redraws, there's no need to cause flickering by redrawing a second time after the width is reset
    def configure(self, item, **kw):
      super().configure(item, **kw)
      for column in self.tv.columns:
        name, kw = column
        self.tv.column(name, **kw)

# root
root=Tk()

# font config
ff10=Font(family="Consolas", size=10)
ff10b=Font(family="Consolas", size=10, weight=BOLD)

# init a scrollabletv
tv=ScrollableTV(root, selectmode=BROWSE, height=8, show="tree headings", columns=("key", "value"), style="Foo2.Treeview")
tv.heading("key", text="Key", anchor=W)
tv.heading("value", text="Value", anchor=W)
tv.column("#0", width=0, stretch=False)
tv.column("key", width=78, stretch=False)
tv.column("value", minwidth=372, width=232, stretch=True)
tv.grid(padx=8, pady=(8,0))

# style config. use a ScrollableStyle and pass in the ScrollableTV whose configure needs to be managed. if you had more than one ScrollableTV, you could modify ScrollableStyle to store a list of them and operate configure on each of them
s=ScrollableTV.ScrollableStyle(tv)
s.configure("Foo2.Treeview", font=ff10, padding=1)
s.configure("Foo2.Treeview.Heading", font=ff10b, padding=1)

# init a scrollbar
sb=Scrollbar(root, orient=HORIZONTAL)
sb.grid(row=1, sticky=EW, padx=8, pady=(0,8))
tv.configure(xscrollcommand=sb.set)
sb.configure(command=tv.xview)

# insert a row that has data longer than the initial column width and
# then update width/minwidth to activate the scrollbar.
tv.insert("", END, values=("foobar", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"))
# we don't need to meddle with the stretch and minwidth values here

#click in the TV to test
def conf(event):
  s.configure("Foo2.TCheckbutton", foreground="red")
tv.bind("<Button-1>", conf, add="+")
root.mainloop()
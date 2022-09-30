# https://www.pythontutorial.net/tkinter/tkinter-treeview/
import tkinter.ttk as ttk
import tkinter as tk
from tkinter.messagebox import showinfo
import sqlite3


# create a db with a new table (if not exists)
conn = sqlite3.connect("students.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE if not exists student (First TEXT, Last TEXT, Email TEXT PRIMARY KEY)")
conn.commit()

# populate the table with initial values if empty
if cursor.execute("SELECT COUNT(*) from student").fetchone()[0] == 0:
    for n in range(1, 10):
        values = (f'first {n}', f'last {n}', f'email{n}@example.com')
        cursor.execute("INSERT INTO student VALUES {}".format(values))
    conn.commit()

# Initialize the Tkinter root
root = tk.Tk()
root.title('Registration Form')
root.geometry('600x600')

# Widget Treeview + a bit of style
tree = ttk.Treeview(root)
s = ttk.Style()
s.theme_use('clam')
s.configure('Treeview.Heading', background="green3", font=('Bold', 13))
tree.pack(fill=tk.X, pady=5)
tree['column'] = ["First","Last","Email"]
tree.column('#0', anchor=tk.W, width=0, stretch=tk.NO)
tree.column('First', anchor=tk.W, width=200)
tree.column('Last', anchor=tk.W, width=200)
tree.column('Email', anchor=tk.W, width=200)
tree.heading('First', text='First')
tree.heading('Last', text='Last')
tree.heading('Email', text='Email')

# populate tree fields fetching data from database
rows = cursor.execute("SELECT * FROM student order by First").fetchall()
for row in rows:
    tree.insert('', tk.END, values=row)

# Functions
row = ''
record = []
def clean_entries():
    first_entry.delete(0, tk.END)
    last_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
def populate_entries(v1, v2, v3):
    first_entry.insert(0, v1)
    last_entry.insert(0, v2)
    email_entry.insert(0, v3)
def item_selected(event):
    for selected_item in tree.selection():
        global row
        row = selected_item
        item = tree.item(selected_item)
        global record
        record = item['values']
        clean_entries()
        populate_entries(record[0], record[1], record[2])
tree.bind('<<TreeviewSelect>>', item_selected)
def delete_tree():
    global row
    if row == '':
        showinfo(title='Error', message='Select one row')
        return
    lst_items = []
    for r in tree.get_children():
        lst_items.append(r)
    if row not in lst_items:
        showinfo(title='Error', message='Select one row')
    else:
        tree.delete(row)
        sql = "DELETE from student where Email = ?"
        cursor.execute(sql, (email_entry.get(),))
        conn.commit()
        clean_entries()
        row=''
def update_tree():
    global row
    if row == '':
        showinfo(title='Error', message='Insert new data')
        return
    lst=[]
    for i in tree.get_children():
        lst.append(i)
    tree.delete(row)
    values=(first_entry.get(),last_entry.get(), email_entry.get())
    tree.insert('', lst.index(row), values=values)
    sql = "Insert or replace into student values {}".format(values)
    cursor.execute(sql)
    conn.commit()
    clean_entries()
    row=''
def insert_tree():
    global row
    values = (first_entry.get(),last_entry.get(), email_entry.get())
    if ''.join(values)=='':
        showinfo(title='Error', message='Populate Fields')
        return
    lst_emails = []
    for line in tree.get_children():
        email = tree.item(line)['values'][2]
        lst_emails.append(email)
    if values[2] in lst_emails:
         showinfo(title='Error', message='Email already listed')
         return
    tree.insert('', 0, values=values)
    sql = "INSERT or REPLACE into student values {}".format(values)
    cursor.execute(sql)
    conn.commit()
    clean_entries()
    row=''
def filter_df():
    choice = clicked.get()
    filter = search_entry.get()
    match choice:
        case "First":
            sql = "Select * from student where First = ?"
            rows = cursor.execute(sql, (filter, )).fetchall()
        case "Last":
            sql = "Select * from student where Last = ?"
            rows = cursor.execute(sql, (filter, )).fetchall()
        case "Email":
            sql = "Select * from student where Email = ?"
            rows = cursor.execute(sql, (filter, )).fetchall()
        case "ALL":
            sql = "Select * from student"
            rows = cursor.execute(sql).fetchall()
    for child in tree.get_children():
        tree.delete(child)
    for row in rows:
        tree.insert('', tk.END, values=row)

# Delete / Update / Insert buttons widgets
delete_btn = tk.Button(root, text='Delete', font=('Bold', 16), command=delete_tree)
delete_btn.place(x=50, y=240, width=100)
update_btn = tk.Button(root, text='Update', font=('Bold', 16), command=update_tree)
update_btn.place(x=200, y=240, width=100)
insert_btn = tk.Button(root, text='Insert', font=('Bold', 16), command=insert_tree)
insert_btn.place(x=350, y=240, width=100)

# labels and Entry widgets
low_frame = tk.Frame(root)

first_lb = tk.Label(low_frame, text='First:', font=('Bold', 12)).place(x=10, y=30, width=50)
last_lb = tk.Label(low_frame, text='Last:', font=('Bold', 12)).place(x=10, y=80, width=50)
email_lb = tk.Label(low_frame, text='Email:', font=('Bold', 12)).place(x=10, y=130, width=50)
first_entry = tk.Entry(low_frame, font=('Bold',12))
first_entry.place(x=100, y=30, width=200)
last_entry = tk.Entry(low_frame, font=('Bold',12))
last_entry.place(x=100, y=80, width=200)
email_entry = tk.Entry(low_frame, font=('Bold',12))
email_entry.place(x=100, y=130, width=200)

low_frame.pack(side=tk.BOTTOM, pady=10)
low_frame.pack_propagate(False)
low_frame.configure(width=600, height=300)

# Search Widget
east_frame = tk.Frame(low_frame)
search_lb = tk.Label(east_frame, text='Filter by:', font=('Bold', 12)).pack(side=tk.TOP, pady=10)
clicked = tk.StringVar(east_frame)
clicked.set("First")
options = ["First", "Last", "Email", "ALL"]
drop = tk.OptionMenu(east_frame, clicked , *options )
drop.pack(side=tk.TOP)
search_entry = tk.Entry(east_frame, font=('Bold', 12))
search_entry.pack(anchor='n', expand=True, pady=10)
dwnd = tk.PhotoImage(file='search-bar.png')
search_bt = tk.Button(east_frame, image=dwnd, command = filter_df, borderwidth=0).pack(pady=10)

east_frame.pack(side=tk.RIGHT)
east_frame.pack_propagate(False)
east_frame.configure(width=200, height=200)

# Exit Button 
exit = tk.Button(low_frame, text = "Exit Program", bg='yellow', font=('Bold',10), command=root.destroy)
exit.pack(side=tk.BOTTOM, pady=50)

root.mainloop()

from tkinter import *
from tkinter.ttk import Combobox
from tkinter import messagebox
import openpyxl
from openpyxl import Workbook
import pathlib

# Constants
FILE_PATH = 'data.xlsx'
WINDOW_TITLE = "Data Entry"
WINDOW_SIZE = '700x412'
WINDOW_POSITION = '+300+200'
BG_COLOR = "#5277ff"
BUTTON_COLOR = '#5e17eb'
TEXT_COLOR = '#fff'

# Initialize Tkinter window
root = Tk()
root.title(WINDOW_TITLE)
root.geometry(WINDOW_SIZE + WINDOW_POSITION)
root.resizable(False, False)
root.configure(bg=BG_COLOR)

# Check if file exists, otherwise create it
file = pathlib.Path(FILE_PATH)
if not file.exists():
    wb = Workbook()
    sheet = wb.active
    sheet.append(["Full Name", "Phone Number", "Age", "Gender", "Address"])
    wb.save(FILE_PATH)

# Clear input fields
def clear():
    NameValue.set('')
    ContactValue.set('')
    AgeValue.set('')
    gender_combobox.set('Male')  # Reset gender combobox
    addressEntry.delete(1.0, END)

# Validate input fields
def validate_inputs():
    name = NameValue.get().strip()
    contact = ContactValue.get().strip()
    age = AgeValue.get().strip()

    if not name:
        messagebox.showerror('Error', 'Name is required')
        return False
    if not contact.isdigit() or len(contact) != 10:  # Optional: Enforce 10-digit phone numbers
        messagebox.showerror('Error', 'A valid 10-digit phone number is required')
        return False
    if not age.isdigit() or not (0 < int(age) < 150):
        messagebox.showerror('Error', 'Valid age between 1 and 149 is required')
        return False
    if not addressEntry.get(1.0, END).strip():
        messagebox.showerror('Error', 'Address is required')
        return False
    return True

# Submit data
def submit():
    if not validate_inputs():
        return
    name = NameValue.get()
    contact = ContactValue.get()
    age = AgeValue.get()
    gender = gender_combobox.get()
    address = addressEntry.get(1.0, END).strip()

    try:
        wb = openpyxl.load_workbook(FILE_PATH)
        sheet = wb.active
        sheet.append([name, contact, age, gender, address])
        wb.save(FILE_PATH)
        messagebox.showinfo('Info', 'Details added successfully!')
        clear()
    except Exception as e:
        messagebox.showerror('Error', f'An error occurred: {str(e)}')

# Create labels
Label(root, text="Please fill out this form:", font="calibri 14 bold", bg=BG_COLOR, fg=TEXT_COLOR).place(x=50, y=20)
Label(root, text='Name', font="calibri 14 bold", bg=BG_COLOR, fg=TEXT_COLOR).place(x=50, y=100)
Label(root, text='Phone Number', font="calibri 14 bold", bg=BG_COLOR, fg=TEXT_COLOR).place(x=50, y=150)
Label(root, text='Age', font="calibri 14 bold", bg=BG_COLOR, fg=TEXT_COLOR).place(x=50, y=200)
Label(root, text='Gender', font="calibri 14 bold", bg=BG_COLOR, fg=TEXT_COLOR).place(x=360, y=200)
Label(root, text='Address', font="calibri 14 bold", bg=BG_COLOR, fg=TEXT_COLOR).place(x=50, y=250)

# Create entry fields
NameValue = StringVar()
ContactValue = StringVar()
AgeValue = StringVar()

Entry(root, textvariable=NameValue, width=45, bd=2, font=('calibri', 12)).place(x=200, y=100)
Entry(root, textvariable=ContactValue, width=45, bd=2, font=('calibri', 12)).place(x=200, y=150)
Entry(root, textvariable=AgeValue, width=15, bd=2, font=('calibri', 12)).place(x=200, y=200)

# Create gender combobox
gender_combobox = Combobox(root, values=['Male', 'Female'], font=('calibri', 12), state='readonly', width=14)
gender_combobox.place(x=440, y=200)
gender_combobox.set('Male')

# Create address entry
addressEntry = Text(root, width=50, height=4, bd=4, font=('calibri', 12))
addressEntry.place(x=200, y=250)

# Create buttons
Button(root, text='Submit', bg=BUTTON_COLOR, fg='white', font=('calibri', 10, 'bold'), width=15, height=2, command=submit).place(x=200, y=350)
Button(root, text='Clear', bg=BUTTON_COLOR, fg='white', font=('calibri', 10, 'bold'), width=15, height=2, command=clear).place(x=340, y=350)
Button(root, text='Exit', bg=BUTTON_COLOR, fg='white', font=('calibri', 10, 'bold'), width=15, height=2, command=root.destroy).place(x=480, y=350)

root.mainloop()
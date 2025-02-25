import tkinter as tk
from tkinter import messagebox, ttk
import json
import logging
from typing import Callable

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Set up logging
logging.basicConfig(filename='calculator.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class WithdrawalCalculator:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Withdrawal Calculator")
        self.master.geometry("550x400")
        self.master.configure(bg=config['colors']['light']['bg'])

        self.setup_variables()
        self.create_widgets()
        self.setup_layout()
        self.create_tooltips()
        self.bind_shortcuts()

    def setup_variables(self) -> None:
        self.amount_var = tk.StringVar()
        self.fee_var = tk.StringVar()
        self.currency_var = tk.StringVar(value="$")
        self.result_var = tk.StringVar()

    def create_widgets(self) -> None:
        self.header_label = ttk.Label(self.master, text="Enter desired amount:", font=("Arial", 12, "bold"))
        self.amount_entry = ttk.Entry(self.master, textvariable=self.amount_var, validate="key", 
                                      validatecommand=(self.master.register(self.validate_input), '%P'))
        
        self.fee_label = ttk.Label(self.master, text="Enter bank fee percentage (%):", font=("Arial", 12))
        self.fee_entry = ttk.Entry(self.master, textvariable=self.fee_var, validate="key", 
                                   validatecommand=(self.master.register(self.validate_fee), '%P'))
        
        self.currency_menu = ttk.OptionMenu(self.master, self.currency_var, "$", *config['currencies'])
        
        self.calculate_button = ttk.Button(self.master, text="Calculate", command=self.calculate_with_custom_fee)
        self.clear_button = ttk.Button(self.master, text="Clear", command=self.clear_fields)
        self.save_button = ttk.Button(self.master, text="Save Results", command=self.save_results)
        
        self.result_label = ttk.Label(self.master, textvariable=self.result_var, font=("Arial", 10))
        
        self.mode_button = ttk.Button(self.master, text="Switch to Dark Mode", command=self.toggle_mode)
        
        self.history_button = ttk.Button(self.master, text="View History", command=self.view_history)

    def setup_layout(self) -> None:
        for widget in (self.header_label, self.amount_entry, self.fee_label, self.fee_entry, 
                       self.currency_menu, self.calculate_button, self.clear_button, 
                       self.save_button, self.result_label, self.mode_button, self.history_button):
            widget.pack(pady=5)

    def create_tooltips(self) -> None:
        self.create_tooltip(self.amount_entry, "Enter the amount you want to receive.")
        self.create_tooltip(self.fee_entry, "Enter the bank fee percentage.")
        self.create_tooltip(self.currency_menu, "Choose your currency.")

    def bind_shortcuts(self) -> None:
        self.master.bind('<Return>', lambda event: self.calculate_with_custom_fee())
        self.master.bind('<Escape>', lambda event: self.clear_fields())
        self.master.bind('<Control-s>', lambda event: self.save_results())

    def validate_input(self, value: str) -> bool:
        return value == "" or (value.replace('.', '', 1).isdigit() and float(value) > 0)

    def validate_fee(self, value: str) -> bool:
        return value == "" or (value.replace('.', '', 1).isdigit() and 0 <= float(value) < 100)

    def calculate_with_custom_fee(self) -> None:
        try:
            desired_amount = float(self.amount_var.get())
            fee_percentage = float(self.fee_var.get()) / 100
            
            if fee_percentage == 1:
                raise ValueError("Fee percentage cannot be 100%")
            
            actual_withdrawal = desired_amount / (1 - fee_percentage)
            bank_fee = actual_withdrawal * fee_percentage
            
            result = (f"You need to withdraw: {self.currency_var.get()}{actual_withdrawal:.2f}\n"
                      f"Bank fee ({fee_percentage*100}%): {self.currency_var.get()}{bank_fee:.2f}\n"
                      f"You will receive: {self.currency_var.get()}{desired_amount:.2f}")
            
            self.result_var.set(result)
            logging.info(f"Calculation performed: {result}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            logging.error(f"Calculation error: {str(e)}")

    def clear_fields(self) -> None:
        self.amount_var.set("")
        self.fee_var.set("")
        self.result_var.set("")
        logging.info("Fields cleared")

    def save_results(self) -> None:
        with open("withdrawal_results.txt", "a") as file:
            file.write(self.result_var.get() + "\n")
        messagebox.showinfo("Saved", "Results saved to withdrawal_results.txt")
        logging.info("Results saved to file")

    def create_tooltip(self, widget: tk.Widget, text: str) -> None:
        tooltip = tk.Label(self.master, text=text, bg="yellow", fg="black", wraplength=150)
        
        def show_tooltip(event):
            tooltip.place(x=event.x_root - self.master.winfo_x(), y=event.y_root - self.master.winfo_y())
        
        def hide_tooltip(event):
            tooltip.place_forget()
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def toggle_mode(self) -> None:
        current_mode = 'light' if self.master.cget("bg") == config['colors']['light']['bg'] else 'dark'
        new_mode = 'dark' if current_mode == 'light' else 'light'
        
        self.master.configure(bg=config['colors'][new_mode]['bg'])
        self.mode_button.config(text=f"Switch to {'Light' if new_mode == 'dark' else 'Dark'} Mode")
        
        logging.info(f"Switched to {new_mode} mode")

    def view_history(self) -> None:
        history_window = tk.Toplevel(self.master)
        history_window.title("Calculation History")
        
        with open("withdrawal_results.txt", "r") as file:
            history = file.read()
        
        history_text = tk.Text(history_window, wrap=tk.WORD)
        history_text.insert(tk.END, history)
        history_text.pack(expand=True, fill=tk.BOTH)
        
        logging.info("Viewed calculation history")

if __name__ == "__main__":
    root = tk.Tk()
    app = WithdrawalCalculator(root)
    root.mainloop()
import tkinter as tk
from tkinter import messagebox
import string
import secrets
import pyperclip
import zxcvbn
from cryptography.fernet import Fernet
import json
import os

class PasswordGeneratorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Password Generator")
        self.root.configure(bg="lightgray")

        # Initialize variables and widgets
        self.initialize_variables()
        self.create_widgets()

        # Load encryption key and password vault
        self.load_encryption_key()
        self.password_vault = self.load_password_vault()

    def initialize_variables(self):
        # Password history and strength labels
        self.password_history = []
        self.password_strength_labels = {
            0: ("Very Weak", "#FF6347"),  # Tomato
            1: ("Weak", "#FF6347"),
            2: ("Fair", "#FFD700"),  # Gold
            3: ("Strong", "#32CD32"),  # LimeGreen
            4: ("Very Strong", "#32CD32"),
        }

        # GUI variables
        self.var_length = tk.IntVar(value=12)
        self.var_lower = tk.BooleanVar(value=True)
        self.var_upper = tk.BooleanVar(value=True)
        self.var_digits = tk.BooleanVar(value=True)
        self.var_symbols = tk.BooleanVar(value=True)

    def load_encryption_key(self):
        """Load encryption key from file or generate a new one."""
        if os.path.exists("key.key"):
            with open("key.key", "rb") as key_file:
                self.password_key = key_file.read()
        else:
            self.password_key = Fernet.generate_key()
            with open("key.key", "wb") as key_file:
                key_file.write(self.password_key)
        self.cipher_suite = Fernet(self.password_key)

    def load_password_vault(self):
        """Load encrypted passwords from file."""
        if os.path.exists("passwords.json"):
            try:
                with open("passwords.json", "r") as f:
                    encrypted_passwords = json.load(f)
                # Decrypt passwords
                return [self.cipher_suite.decrypt(ep.encode()).decode() for ep in encrypted_passwords]
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load password vault: {str(e)}")
        return []

    def save_password_vault(self):
        """Encrypt and save passwords to file."""
        try:
            encrypted_passwords = [self.cipher_suite.encrypt(p.encode()).decode() for p in self.password_vault]
            with open("passwords.json", "w") as f:
                json.dump(encrypted_passwords, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save password vault: {str(e)}")

    def create_widgets(self):
        frame = tk.Frame(self.root, padx=20, pady=20, bg="lightgray")
        frame.grid(row=0, column=0, padx=10, pady=10)

        # Password Length
        label_length = tk.Label(frame, text="Password Length:", bg="lightgray")
        label_length.grid(row=0, column=0, sticky="w", pady=(0, 10))
        entry_length = tk.Entry(frame, textvariable=self.var_length)
        entry_length.grid(row=0, column=1, padx=10, pady=(0, 10))

        # Character Types
        characters_frame = tk.LabelFrame(frame, text="Character Types", bg="lightgray")
        characters_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="we")

        checkbox_lower = tk.Checkbutton(characters_frame, text="Include lowercase letters", variable=self.var_lower, bg="lightgray")
        checkbox_lower.pack(anchor="w", padx=10)
        checkbox_upper = tk.Checkbutton(characters_frame, text="Include uppercase letters", variable=self.var_upper, bg="lightgray")
        checkbox_upper.pack(anchor="w", padx=10)
        checkbox_digits = tk.Checkbutton(characters_frame, text="Include digits", variable=self.var_digits, bg="lightgray")
        checkbox_digits.pack(anchor="w", padx=10)
        checkbox_symbols = tk.Checkbutton(characters_frame, text="Include symbols", variable=self.var_symbols, bg="lightgray")
        checkbox_symbols.pack(anchor="w", padx=10)

        # Generate Password Button
        generate_button = tk.Button(frame, text="Generate Password", command=self.generate_password)
        generate_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Password Strength Label
        self.strength_label = tk.Label(frame, text="Password Strength:", bg="lightgray")
        self.strength_label.grid(row=3, column=0, columnspan=2, pady=5)

        # Generated Password Label
        self.result_label = tk.Label(frame, text="", wraplength=300, bg="lightgray")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)

        # Copy to Clipboard Button
        copy_button = tk.Button(frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_button.grid(row=5, column=0, columnspan=2, pady=5)

        # Save Password Button
        save_button = tk.Button(frame, text="Save Password", command=self.save_password)
        save_button.grid(row=6, column=0, columnspan=2, pady=5)

        # Password History Button
        history_button = tk.Button(frame, text="Password History", command=self.show_password_history)
        history_button.grid(row=7, column=0, columnspan=2, pady=5)

    def generate_password(self):
        try:
            length = self.var_length.get()
            use_lower = self.var_lower.get()
            use_upper = self.var_upper.get()
            use_digits = self.var_digits.get()
            use_symbols = self.var_symbols.get()

            chars = ""
            if use_lower:
                chars += string.ascii_lowercase
            if use_upper:
                chars += string.ascii_uppercase
            if use_digits:
                chars += string.digits
            if use_symbols:
                chars += string.punctuation

            if not chars:
                messagebox.showwarning("Warning", "Please select at least one character type")
                return

            password = ''.join(secrets.choice(chars) for _ in range(length))
            self.display_password(password)
            self.evaluate_password_strength(password)
            self.password_history.append(password)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for password length")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def display_password(self, password: str):
        self.result_label.config(text=f"Generated password: {password}")

    def evaluate_password_strength(self, password: str):
        result = zxcvbn.zxcvbn(password)
        score = result['score']
        feedback = result['feedback']['suggestions']
        self.strength_label.config(
            text=f"Password Strength: {self.password_strength_labels[score][0]}",
            fg=self.password_strength_labels[score][1],
        )
        messagebox.showinfo("Password Strength", "\n".join(feedback))

    def copy_to_clipboard(self):
        password = self.result_label.cget("text").split(": ")[1]
        pyperclip.copy(password)
        messagebox.showinfo("Success", "Password copied to clipboard")

    def save_password(self):
        password = self.result_label.cget("text").split(": ")[1]
        self.password_vault.append(password)
        self.save_password_vault()
        messagebox.showinfo("Success", "Password saved to vault")

    def show_password_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Password History")

        scrollbar = tk.Scrollbar(history_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(history_window, yscrollcommand=scrollbar.set)
        for password in self.password_history:
            listbox.insert(tk.END, password)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=listbox.yview)

def main():
    root = tk.Tk()
    app = PasswordGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
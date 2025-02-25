import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import matplotlib.pyplot as plt


class FinancialPlannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Monthly Financial Planner (Ksh)")
        self.month_data = []  # Store data for each month

        # Theme settings: fixed Light theme for consistency
        self.theme = "Light"
        self.colors = {
            "bg": "#F5F5DC",      # parchment-like beige
            "fg": "#000000",
            "entry_bg": "#FFFFFF",
            "button_bg": "#E6E6FA"  # soft lavender
        }
        self.font = ("Times New Roman", 12)

        self.create_widgets()
        self.update_theme()

    def create_widgets(self):
        # --- Month Label ---
        month_frame = tk.Frame(self.root)
        month_frame.pack(pady=5, padx=10, fill="x")
        tk.Label(month_frame, text="Month (e.g., March 2025):", font=self.font, anchor="w", width=30).pack(side=tk.LEFT)
        self.month_entry = tk.Entry(month_frame, font=self.font)
        self.month_entry.pack(side=tk.LEFT, fill="x", expand=True)

        # --- Portfolios Container ---
        portfolios_frame = tk.Frame(self.root)
        portfolios_frame.pack(padx=10, pady=10, fill="both")
        self.entries = {}  # Dictionary to store all entry widgets

        # Row 0: Chumz, Cash, Crypto
        self.create_portfolio_frame(portfolios_frame, "Chumz", 0, 0, [
            ("Emergency Fares (Ksh):", ""),
            ("Quick Savings (Ksh):", ""),
            ("Chumz Monthly Savings (Ksh):", ""),
            ("Chumz Expenses (Ksh):", ""),
            ("Chumz Crypto Capital (Ksh):", "")
        ])
        self.create_portfolio_frame(portfolios_frame, "Cash", 0, 1, [
            ("Cash (Ksh):", "")
        ])
        self.create_portfolio_frame(portfolios_frame, "Crypto", 0, 2, [
            ("Crypto (Ksh):", "")
        ])

        # Row 1: Etica, Ziidi (Ziidi spans one column here)
        self.create_portfolio_frame(portfolios_frame, "Etica", 1, 0, [
            ("Etica Investment (Ksh):", "")
        ])
        self.create_portfolio_frame(portfolios_frame, "Ziidi", 1, 1, [
            ("Ziidi Shopping (Ksh):", ""),
            ("Ziidi Weekly Savings (Ksh):", ""),
            ("Ziidi Liquid Expenses (Ksh):", "")
        ])

        # --- Action Buttons ---
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Add Month Data", command=self.add_month_data, font=self.font,
                  bg=self.colors["button_bg"]).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Plot Monthly Breakdown", command=self.plot_monthly_breakdown, font=self.font,
                  bg=self.colors["button_bg"]).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="View Progress Over Time", command=self.open_progress_window, font=self.font,
                  bg=self.colors["button_bg"]).pack(side=tk.LEFT, padx=5)

    def create_portfolio_frame(self, parent, portfolio_name, row, col, fields):
        """
        Create a frame with input fields for a given portfolio.
        Each field is a tuple: (label_text, default_value)
        """
        frame = tk.Frame(parent, bd=2, relief="groove", padx=5, pady=5, bg=self.colors["bg"])
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        tk.Label(frame, text=portfolio_name + " Portfolio", font=(self.font[0], 14, "bold"),
                 bg=self.colors["bg"], fg=self.colors["fg"]).pack(pady=(0, 5))
        for label_text, default in fields:
            row_frame = tk.Frame(frame, bg=self.colors["bg"])
            row_frame.pack(fill="x", pady=2)
            tk.Label(row_frame, text=label_text, anchor="w", width=25, font=self.font,
                     bg=self.colors["bg"], fg=self.colors["fg"]).pack(side=tk.LEFT)
            entry = tk.Entry(row_frame, font=self.font, bg=self.colors["entry_bg"], fg=self.colors["fg"])
            entry.pack(side=tk.LEFT, fill="x", expand=True)
            # Construct a unique key by stripping the unit from the label (everything after ' (')
            key = f"{portfolio_name}_{label_text.split(' (')[0].strip()}"
            self.entries[key] = entry

    def update_theme(self):
        # This function applies the fixed light theme to all widgets.
        self.root.configure(bg=self.colors["bg"])
        self.recursive_config(self.root)

    def recursive_config(self, widget):
        try:
            widget.configure(bg=self.colors["bg"], fg=self.colors["fg"], font=self.font)
        except tk.TclError:
            pass
        # Special handling for some widget types:
        if isinstance(widget, tk.Entry):
            widget.configure(bg=self.colors["entry_bg"], fg=self.colors["fg"])
        elif isinstance(widget, tk.Button):
            widget.configure(bg=self.colors["button_bg"], fg=self.colors["fg"])
        elif isinstance(widget, tk.Radiobutton):
            widget.configure(bg=self.colors["bg"], fg=self.colors["fg"], selectcolor=self.colors["bg"])
        for child in widget.winfo_children():
            self.recursive_config(child)

    def get_float(self, field_name, entry_widget):
        """
        Retrieve a non-negative float from an entry.
        Accepts zero but rejects negatives.
        """
        try:
            value = float(entry_widget.get())
            if value < 0:
                raise ValueError
            return value
        except ValueError:
            messagebox.showerror("Invalid Input", f"Enter a valid non-negative number for {field_name}.")
            raise

    def add_month_data(self):
        month_label = self.month_entry.get().strip()
        if not month_label:
            messagebox.showerror("Invalid Input", "Please enter a valid month label (e.g., 'March 2025').")
            return

        try:
            # --- Chumz Portfolio ---
            chumz_fields = [
                "Emergency Fares",
                "Quick Savings",
                "Chumz Monthly Savings",
                "Chumz Expenses",
                "Chumz Crypto Capital"
            ]
            chumz_values = {}
            for field in chumz_fields:
                key = f"Chumz_{field}"
                if key not in self.entries:
                    raise KeyError(f"Missing entry for {field} in Chumz portfolio.")
                chumz_values[field] = self.get_float(f"Chumz {field}", self.entries[key])
            total_chumz = sum(chumz_values.values())

            # --- Cash Portfolio ---
            key_cash = "Cash_Cash"
            if key_cash not in self.entries:
                raise KeyError("Missing entry for Cash.")
            cash_value = self.get_float("Cash", self.entries[key_cash])
            total_cash = cash_value

            # --- Crypto Portfolio ---
            key_crypto = "Crypto_Crypto"
            if key_crypto not in self.entries:
                raise KeyError("Missing entry for Crypto.")
            crypto_value = self.get_float("Crypto", self.entries[key_crypto])
            total_crypto = crypto_value

            # --- Etica Portfolio ---
            key_etica = "Etica_Etica Investment"
            if key_etica not in self.entries:
                raise KeyError("Missing entry for Etica Investment.")
            etica_value = self.get_float("Etica Investment", self.entries[key_etica])
            total_etica = etica_value

            # --- Ziidi Portfolio ---
            ziidi_fields = ["Ziidi Shopping", "Ziidi Weekly Savings", "Ziidi Liquid Expenses"]
            ziidi_values = {}
            for field in ziidi_fields:
                key = f"Ziidi_{field}"
                if key not in self.entries:
                    raise KeyError(f"Missing entry for {field} in Ziidi portfolio.")
                ziidi_values[field.replace("Ziidi ", "")] = self.get_float(field.replace("Ziidi ", ""), self.entries[key])
            total_ziidi = sum(ziidi_values.values())

        except Exception as e:
            # The error message has already been shown by get_float or KeyError
            return

        month_entry = {
            "month": month_label,
            "Chumz": {
                "fields": chumz_values,
                "total": total_chumz
            },
            "Cash": {
                "value": cash_value,
                "total": total_cash
            },
            "Crypto": {
                "value": crypto_value,
                "total": total_crypto
            },
            "Etica": {
                "investment": etica_value,
                "total": total_etica
            },
            "Ziidi": {
                "fields": ziidi_values,
                "total": total_ziidi
            }
        }
        self.month_data.append(month_entry)
        messagebox.showinfo("Success", f"Data for {month_label} added successfully!")
        self.clear_fields()

    def clear_fields(self):
        self.month_entry.delete(0, tk.END)
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def plot_monthly_breakdown(self):
        if not self.month_data:
            messagebox.showerror("No Data", "Please add at least one month's data first.")
            return

        data = self.month_data[-1]
        month_label = data["month"]
        portfolio_list = [
            ("Chumz", data["Chumz"].get("fields", {})),
            ("Cash", {"Cash": data["Cash"]["value"]}),
            ("Crypto", {"Crypto": data["Crypto"]["value"]}),
            ("Etica", {"Investment": data["Etica"]["investment"]}),
            ("Ziidi", data["Ziidi"].get("fields", {}))
        ]

        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        axes = axes.flatten()
        for i, (name, fields) in enumerate(portfolio_list):
            ax = axes[i]
            if fields:
                labels = list(fields.keys())
                sizes = list(fields.values())
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            else:
                ax.text(0.5, 0.5, "No Data", ha="center", va="center")
            ax.set_title(f"{name} Breakdown ({month_label})", fontsize=14)
            ax.axis('equal')

        for j in range(len(portfolio_list), len(axes)):
            axes[j].axis('off')

        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.001)

    def open_progress_window(self):
        if not self.month_data:
            messagebox.showerror("No Data", "Please add at least one month's data first.")
            return

        progress_win = tk.Toplevel(self.root)
        progress_win.title("Progress Over Time")
        progress_win.configure(bg=self.colors["bg"])
        tk.Label(progress_win, text="Enter month(s) to compare (comma separated).\nLeave empty to compare all months:",
                 font=self.font, bg=self.colors["bg"], fg=self.colors["fg"]).pack(padx=10, pady=5)
        months_entry = tk.Entry(progress_win, font=self.font, width=40, bg=self.colors["entry_bg"], fg=self.colors["fg"])
        months_entry.pack(padx=10, pady=5)
        tk.Button(progress_win, text="Plot Progress", font=self.font, bg=self.colors["button_bg"], fg=self.colors["fg"],
                  command=lambda: self.plot_progress(months_entry.get().strip(), progress_win)
                  ).pack(padx=10, pady=10)

    def plot_progress(self, months_input, window):
        window.destroy()
        if months_input:
            selected = [m.strip().lower() for m in months_input.split(",") if m.strip()]
            filtered_data = [d for d in self.month_data if d["month"].lower() in selected]
            if not filtered_data:
                messagebox.showerror("No Data", "No matching month(s) found.")
                return
        else:
            filtered_data = self.month_data

        months = [d["month"] for d in filtered_data]
        fig, axs = plt.subplots(5, 1, figsize=(12, 20))
        portfolio_names = ["Chumz", "Cash", "Crypto", "Etica", "Ziidi"]

        for i, portfolio in enumerate(portfolio_names):
            ax = axs[i]
            if portfolio in ["Chumz", "Ziidi"]:
                # Multi-field portfolios: assume each month has the same fields as the first
                field_names = filtered_data[0][portfolio].get("fields", {}).keys()
                for field in field_names:
                    try:
                        values = [month[portfolio]["fields"][field] for month in filtered_data]
                    except KeyError:
                        values = []
                    ax.plot(months, values, marker='o', label=field)
            else:
                if portfolio == "Cash":
                    values = [month["Cash"]["value"] for month in filtered_data]
                elif portfolio == "Crypto":
                    values = [month["Crypto"]["value"] for month in filtered_data]
                elif portfolio == "Etica":
                    values = [month["Etica"]["investment"] for month in filtered_data]
                ax.plot(months, values, marker='o', label=portfolio)

            ax.set_title(f"{portfolio} Progress Over Time", fontsize=14)
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount (Ksh)")
            ax.legend()
            ax.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = FinancialPlannerGUI(root)
    root.mainloop()
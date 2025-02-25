"""
Financial Planner App – Old Money Edition
This application tracks monthly portfolio data across several sections:
  - Chumz (with multiple fields, including Emergency Fares, Quick Savings,
    Chumz Monthly Savings, Chumz Expenses, and Chumz Crypto Capital)
  - Cash (standalone)
  - Crypto (standalone)
  - Etica (Investment)
  - Ziidi (with Shopping, Weekly Savings, and Liquid Expenses)
It supports:
  - Data entry via a Tkinter GUI with a classic “old money” aesthetic.
  - A menu bar with File (New, Export, Import, Exit), Edit (Undo/Redo),
    and Help (About) options.
  - Persistent JSON storage so data isn’t lost between sessions.
  - Logging of events and errors.
  - A summary table of month data (via ttk.Treeview).
  - Monthly breakdown plotting as pie charts (responsive to screen size) and progress-over‑time
    plotting with both Matplotlib (synchronous) and Plotly (if installed, interactive).
  - Undo/Redo support and versioning of monthly data.
  - Tooltips, keyboard shortcuts, and accessibility improvements.
  - Input validation with custom exceptions.
  - Dynamic field generation and input history/autofill stubs.
Author: Nova’s Developer (2025)
"""
import os
import re
import json
import logging
import threading
import copy
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, List, Optional
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import matplotlib.pyplot as plt

# Try to import plotly for interactive plotting; if not, fallback to matplotlib
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# Global Portfolio Definitions (Dynamic Field Management)
PORTFOLIO_DEFINITIONS = {
    "Chumz": ["Emergency Fares", "Quick Savings", "Chumz Monthly Savings", "Chumz Expenses", "Chumz Crypto Capital"],
    "Cash": ["Cash"],
    "Crypto": ["Crypto"],
    "Etica": ["Etica Investment"],
    "Ziidi": ["Ziidi Shopping", "Ziidi Weekly Savings", "Ziidi Liquid Expenses"]
}

# Fixed Light Theme Settings
LIGHT_THEME = {
    "bg": "#F0F0F0",  # Light grey background
    "fg": "#000000",  # Black text
    "entry_bg": "#FFFFFF",  # White entries
    "button_bg": "#DADADA",  # Light button background
    "font_family": "Times New Roman",
    "font_size": 13
}

# Logging Configuration
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    filename="financial_planner.log",
                    filemode="a")
logger = logging.getLogger(__name__)

# Custom Exceptions
class InputValidationError(Exception):
    """Exception raised for errors in the input."""
    pass

# Data Models using dataclasses
@dataclass
class PortfolioData:
    fields: Dict[str, float] = field(default_factory=dict)
    version: int = 1

    def total(self) -> float:
        return sum(self.fields.values())


@dataclass
class SingleValueData:
    value: float = 0.0
    version: int = 1


@dataclass
class MonthData:
    month: str
    chumz: PortfolioData
    cash: SingleValueData
    crypto: SingleValueData
    etica: SingleValueData
    ziidi: PortfolioData
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# Configuration (from file or defaults)
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "storage_file": "month_data.json"
}


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                logger.info("Configuration loaded from file.")
                return config
        except Exception as e:
            logger.error("Failed to load config, using defaults: %s", e)
    logger.info("Using default configuration.")
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    logger.info("Configuration saved.")


# Model: Handles data persistence, undo/redo, versioning, etc.
class FinancialPlannerModel:
    def __init__(self, storage_file: str):
        self.storage_file = storage_file
        self.months: List[MonthData] = []
        self.undo_stack: List[List[MonthData]] = []
        self.redo_stack: List[List[MonthData]] = []
        self.load_data()

    def add_month(self, month_data: MonthData):
        self.undo_stack.append(copy.deepcopy(self.months))
        self.redo_stack.clear()
        self.months.append(month_data)
        logger.info("Added month data for %s", month_data.month)
        self.save_data()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(copy.deepcopy(self.months))
            self.months = self.undo_stack.pop()
            logger.info("Undo performed")
            self.save_data()
        else:
            raise InputValidationError("Nothing to undo.")

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(copy.deepcopy(self.months))
            self.months = self.redo_stack.pop()
            logger.info("Redo performed")
            self.save_data()
        else:
            raise InputValidationError("Nothing to redo.")

    def export_data(self, filepath: str):
        try:
            data = [asdict(md) for md in self.months]
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
            logger.info("Data exported to %s", filepath)
        except Exception as e:
            logger.error("Export failed: %s", e)
            raise

    def import_data(self, filepath: str):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            self.months = []
            for entry in data:
                md = MonthData(
                    month=entry["month"],
                    chumz=PortfolioData(fields=entry["chumz"]["fields"], version=entry["chumz"].get("version", 1)),
                    cash=SingleValueData(value=entry["cash"]["value"], version=entry["cash"].get("version", 1)),
                    crypto=SingleValueData(value=entry["crypto"]["value"], version=entry["crypto"].get("version", 1)),
                    etica=SingleValueData(value=entry["etica"]["value"] if "value" in entry["etica"] else entry["etica"]["investment"],
                                          version=entry["etica"].get("version", 1)),
                    ziidi=PortfolioData(fields=entry["ziidi"]["fields"], version=entry["ziidi"].get("version", 1)),
                    timestamp=entry.get("timestamp", datetime.now().isoformat())
                )
                self.months.append(md)
            logger.info("Data imported from %s", filepath)
        except Exception as e:
            logger.error("Import failed: %s", e)
            raise

    def save_data(self):
        try:
            data = [asdict(md) for md in self.months]
            with open(self.storage_file, "w") as f:
                json.dump(data, f, indent=4)
            logger.info("Data saved to %s", self.storage_file)
        except Exception as e:
            logger.error("Save data failed: %s", e)

    def load_data(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r") as f:
                    data = json.load(f)
                self.months = []
                for entry in data:
                    md = MonthData(
                        month=entry["month"],
                        chumz=PortfolioData(fields=entry["chumz"]["fields"], version=entry["chumz"].get("version", 1)),
                        cash=SingleValueData(value=entry["cash"]["value"], version=entry["cash"].get("version", 1)),
                        crypto=SingleValueData(value=entry["crypto"]["value"], version=entry["crypto"].get("version", 1)),
                        etica=SingleValueData(value=entry["etica"]["value"] if "value" in entry["etica"] else entry["etica"]["investment"],
                                              version=entry["etica"].get("version", 1)),
                        ziidi=PortfolioData(fields=entry["ziidi"]["fields"], version=entry["ziidi"].get("version", 1)),
                        timestamp=entry.get("timestamp", datetime.now().isoformat())
                    )
                    self.months.append(md)
                logger.info("Data loaded from %s", self.storage_file)
            except Exception as e:
                logger.error("Failed to load data: %s", e)
                self.months = []
        else:
            logger.info("No storage file found. Starting with empty data.")


# Controller: Bridges the Model and the View
class FinancialPlannerController:
    def __init__(self, model: FinancialPlannerModel, view: 'FinancialPlannerView'):
        self.model = model
        self.view = view

    def validate_numeric_field(self, value: str, field_name: str) -> float:
        try:
            return float(value)
        except ValueError:
            raise InputValidationError(f"Invalid number for {field_name}: {value}")

    def add_month_data(self, data: dict):
        try:
            month = data.get("month", "").strip()
            if not month:
                raise InputValidationError("Month label cannot be empty.")
            chumz_fields = {key: self.validate_numeric_field(val, key)
                            for key, val in data.get("Chumz", {}).items()}
            cash_val = self.validate_numeric_field(data.get("Cash", "0"), "Cash")
            crypto_val = self.validate_numeric_field(data.get("Crypto", "0"), "Crypto")
            etica_val = self.validate_numeric_field(data.get("Etica", "0"), "Etica Investment")
            ziidi_fields = {key: self.validate_numeric_field(val, key)
                            for key, val in data.get("Ziidi", {}).items()}
            month_data = MonthData(
                month=month,
                chumz=PortfolioData(fields=chumz_fields),
                cash=SingleValueData(value=cash_val),
                crypto=SingleValueData(value=crypto_val),
                etica=SingleValueData(value=etica_val),
                ziidi=PortfolioData(fields=ziidi_fields)
            )
            self.model.add_month(month_data)
            self.view.show_info(f"Data for {month} added successfully!")
            self.view.update_summary_table(self.model.months)
        except Exception as e:
            logger.error("Error adding month data: %s", e)
            self.view.show_error(str(e))

    def undo(self):
        try:
            self.model.undo()
            self.view.update_summary_table(self.model.months)
            self.view.show_info("Undo successful.")
        except Exception as e:
            self.view.show_error(str(e))

    def redo(self):
        try:
            self.model.redo()
            self.view.update_summary_table(self.model.months)
            self.view.show_info("Redo successful.")
        except Exception as e:
            self.view.show_error(str(e))

    def export_data(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON Files", "*.json")])
        if filepath:
            try:
                self.model.export_data(filepath)
                self.view.show_info(f"Data exported to {filepath}")
            except Exception as e:
                self.view.show_error(str(e))

    def import_data(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath:
            try:
                self.model.import_data(filepath)
                self.view.update_summary_table(self.model.months)
                self.view.show_info("Data imported successfully.")
            except Exception as e:
                self.view.show_error(str(e))

    def plot_monthly_breakdown(self):
        if not self.model.months:
            self.view.show_error("No data to plot.")
            return
        month_data = self.model.months[-1]
        threading.Thread(target=self._plot_monthly_breakdown_thread, args=(month_data,), daemon=True).start()

    def _plot_monthly_breakdown_thread(self, month_data: MonthData):
        try:
            screen_width = self.view.winfo_screenwidth()
            screen_height = self.view.winfo_screenheight()
            fig_width = min(18, screen_width / 100)
            fig_height = min(10, screen_height / 100)
            portfolios = {
                "Chumz": month_data.chumz.fields,
                "Cash": {"Cash": month_data.cash.value},
                "Crypto": {"Crypto": month_data.crypto.value},
                "Etica": {"Investment": month_data.etica.value},
                "Ziidi": month_data.ziidi.fields
            }
            fig, axes = plt.subplots(2, 3, figsize=(fig_width, fig_height))
            axes = axes.flatten()
            for i, (name, fields) in enumerate(portfolios.items()):
                ax = axes[i]
                if fields:
                    labels = list(fields.keys())
                    sizes = list(fields.values())
                    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                else:
                    ax.text(0.5, 0.5, "No Data", ha="center", va="center")
                ax.set_title(f"{name} Breakdown ({month_data.month})", fontsize=14)
                ax.axis('equal')
            for j in range(len(portfolios), len(axes)):
                axes[j].axis('off')
            plt.tight_layout()
            if messagebox.askyesno("Export Graph?", "Do you want to export the monthly breakdown as an image?"):
                export_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                           filetypes=[("PNG Files", "*.png")])
                if export_path:
                    plt.savefig(export_path)
                    logger.info("Graph exported to %s", export_path)
            plt.show(block=False)
            plt.pause(0.001)
        except Exception as e:
            logger.error("Plot monthly breakdown error: %s", e)

    def plot_progress_over_time(self, selected_months: Optional[List[str]] = None, interactive: bool = False):
        if not self.model.months:
            self.view.show_error("No data available.")
            return
        filtered = ([md for md in self.model.months if md.month.lower() in selected_months]
                    if selected_months else self.model.months)
        if not filtered:
            self.view.show_error("No matching months found.")
            return
        months = [md.month for md in filtered]
        fig, axs = plt.subplots(5, 1, figsize=(12, 20))
        portfolios = {
            "Chumz": lambda md: md.chumz.fields,
            "Cash": lambda md: {"Cash": md.cash.value},
            "Crypto": lambda md: {"Crypto": md.crypto.value},
            "Etica": lambda md: {"Investment": md.etica.value},
            "Ziidi": lambda md: md.ziidi.fields
        }
        for i, (port_name, getter) in enumerate(portfolios.items()):
            ax = axs[i]
            sample = getter(filtered[0])
            for field in sample.keys():
                values = [getter(md).get(field, 0) for md in filtered]
                ax.plot(months, values, marker='o', label=field)
            ax.set_title(f"{port_name} Progress Over Time", fontsize=14)
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount (Ksh)")
            ax.legend()
            ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        if interactive and HAS_PLOTLY:
            interactive_fig = px.line(title="Interactive Progress Over Time")
            for port_name, getter in portfolios.items():
                sample = getter(filtered[0])
                for field in sample.keys():
                    values = [getter(md).get(field, 0) for md in filtered]
                    interactive_fig.add_scatter(x=months, y=values, mode="lines+markers", name=f"{port_name} {field}")
            interactive_fig.show()
        else:
            plt.show()


# Single Definition of CreateToolTip
class CreateToolTip:
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Times New Roman", 10))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


# View: The Tkinter GUI (Using Only Light Theme)
class FinancialPlannerView(tk.Tk):
    def __init__(self, config: dict):
        super().__init__()
        self.controller = None  # To be set later via set_controller()
        self.config_data = config
        self.portfolio_definitions = PORTFOLIO_DEFINITIONS.copy()
        self.entries = {}  # All entry widgets keyed by "Portfolio_Field"
        self.title("Monthly Financial Planner (Ksh) - Old Money Edition")
        self.geometry("1200x800")
        self.apply_theme()  # Always use the light theme
        self.create_main_widgets()
        self.create_summary_table()
        self.bind_shortcuts()

    def get_font(self):
        return (LIGHT_THEME["font_family"], LIGHT_THEME["font_size"])

    def set_controller(self, controller):
        self.controller = controller
        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self)
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.clear_all)
        file_menu.add_command(label="Export Data", command=lambda: self.controller.export_data() if self.controller else None)
        file_menu.add_command(label="Import Data", command=lambda: self.controller.import_data() if self.controller else None)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=lambda: self.controller.undo() if self.controller else None, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=lambda: self.controller.redo() if self.controller else None, accelerator="Ctrl+Y")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    def create_main_widgets(self):
        font = self.get_font()
        frame = tk.Frame(self, bg=LIGHT_THEME["bg"])
        frame.pack(pady=10)
        tk.Label(frame, text="Month (e.g., March 2025):", font=font, bg=LIGHT_THEME["bg"], fg=LIGHT_THEME["fg"]).pack(side=tk.LEFT)
        self.month_entry = tk.Entry(frame, font=font, bg=LIGHT_THEME["entry_bg"], fg=LIGHT_THEME["fg"])
        self.month_entry.pack(side=tk.LEFT, padx=5)
        CreateToolTip(self.month_entry, "Enter the month label.")
        self.portfolio_frames = {}
        container = tk.Frame(self, bg=LIGHT_THEME["bg"])
        container.pack(pady=10, fill=tk.BOTH, expand=True)
        row = 0
        col = 0
        for port, fields in self.portfolio_definitions.items():
            frame = tk.LabelFrame(container, text=f"{port} Portfolio", font=font, padx=5, pady=5,
                                  bg=LIGHT_THEME["bg"], fg=LIGHT_THEME["fg"])
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.portfolio_frames[port] = frame
            for field in fields:
                self._create_portfolio_field(frame, port, field)
            col += 1
            if col > 2:
                col = 0
                row += 1
        btn_frame = tk.Frame(self, bg=LIGHT_THEME["bg"])
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add Month Data", command=self.add_month_data, font=font,
                  bg=LIGHT_THEME["button_bg"], fg=LIGHT_THEME["fg"]).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Plot Monthly Breakdown",
                  command=lambda: self.controller.plot_monthly_breakdown() if self.controller else messagebox.showerror("Error", "Controller not set"),
                  font=font, bg=LIGHT_THEME["button_bg"], fg=LIGHT_THEME["fg"]).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="View Progress Over Time", command=self.open_progress_dialog, font=font,
                  bg=LIGHT_THEME["button_bg"], fg=LIGHT_THEME["fg"]).pack(side=tk.LEFT, padx=5)

    def _create_portfolio_field(self, parent, portfolio: str, field: str):
        font = self.get_font()
        subframe = tk.Frame(parent, bg=LIGHT_THEME["bg"])
        subframe.pack(fill=tk.X, pady=2)
        lbl = tk.Label(subframe, text=f"{field} (Ksh):", font=font, width=25, anchor="w",
                       bg=LIGHT_THEME["bg"], fg=LIGHT_THEME["fg"])
        lbl.pack(side=tk.LEFT)
        ent = tk.Entry(subframe, font=font, bg=LIGHT_THEME["entry_bg"], fg=LIGHT_THEME["fg"])
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
        key = f"{portfolio}_{field}"
        self.entries[key] = ent
        CreateToolTip(ent, f"Enter amount for {field}.")

    def create_summary_table(self):
        self.summary_frame = tk.Frame(self, bg=LIGHT_THEME["bg"])
        self.summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ("Month", "Chumz Total", "Cash", "Crypto", "Etica", "Ziidi Total", "Timestamp")
        self.tree = ttk.Treeview(self.summary_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def update_summary_table(self, months: List[MonthData]):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for md in months:
            self.tree.insert("", tk.END, values=(
                md.month,
                f"{md.chumz.total():.2f}",
                f"{md.cash.value:.2f}",
                f"{md.crypto.value:.2f}",
                f"{md.etica.value:.2f}",
                f"{md.ziidi.total():.2f}",
                md.timestamp.split("T")[0]
            ))

    def add_month_data(self):
        data = {"month": self.month_entry.get().strip(), "Chumz": {}, "Cash": "", "Crypto": "", "Etica": "", "Ziidi": {}}
        for key, entry in self.entries.items():
            try:
                port, field = key.split("_", 1)
                value = entry.get().strip()
                if port in ["Chumz", "Ziidi"]:
                    data[port][field] = value if value != "" else "0"
                elif port in ["Cash", "Crypto", "Etica"]:
                    data[port] = value if value != "" else "0"
            except Exception as e:
                logger.error("Error processing entry %s: %s", key, e)
        self.controller.add_month_data(data)
        self.clear_fields()

    def clear_fields(self):
        self.month_entry.delete(0, tk.END)
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def open_progress_dialog(self):
        months_str = simpledialog.askstring("Progress Over Time",
                                            "Enter month(s) to compare (comma separated) or leave empty for all:")
        if months_str is not None:
            selected = None if months_str.strip() == "" else [m.strip().lower() for m in months_str.split(",")]
            interactive = False
            if HAS_PLOTLY and messagebox.askyesno("Interactive Plot?", "Use interactive plot (Plotly)?"):
                interactive = True
            self.controller.plot_progress_over_time(selected_months=selected, interactive=interactive)

    def bind_shortcuts(self):
        self.bind("<Control-z>", lambda e: self.controller.undo() if self.controller else None)
        self.bind("<Control-y>", lambda e: self.controller.redo() if self.controller else None)

    def clear_all(self):
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all data?"):
            self.controller.model.months = []
            self.update_summary_table(self.controller.model.months)

    def show_about(self):
        messagebox.showinfo("About", "Personal Financial Planner App\nVersion 2.0")

    def show_error(self, msg: str):
        messagebox.showerror("Error", msg)

    def show_info(self, msg: str):
        messagebox.showinfo("Info", msg)

    def apply_theme(self):
        # Set default options for consistency
        self.option_add("*Background", LIGHT_THEME["bg"])
        self.option_add("*Foreground", LIGHT_THEME["fg"])
        self.option_add("*ActiveBackground", LIGHT_THEME["button_bg"])
        self.configure(bg=LIGHT_THEME["bg"])
        self.update_theme_recursive(self, LIGHT_THEME["bg"], LIGHT_THEME["fg"])
        # Update ttk styles
        style = ttk.Style(self)
        style.theme_use('default')
        style.configure("Treeview", background=LIGHT_THEME["bg"], fieldbackground=LIGHT_THEME["bg"], foreground=LIGHT_THEME["fg"])
        style.configure("Treeview.Heading", background=LIGHT_THEME["button_bg"], foreground=LIGHT_THEME["fg"])
        style.configure("TButton", background=LIGHT_THEME["button_bg"], foreground=LIGHT_THEME["fg"])
        style.configure("TLabel", background=LIGHT_THEME["bg"], foreground=LIGHT_THEME["fg"])
        style.configure("TEntry", fieldbackground=LIGHT_THEME["entry_bg"], foreground=LIGHT_THEME["fg"])
        style.configure("TMenubutton", background=LIGHT_THEME["button_bg"], foreground=LIGHT_THEME["fg"])

    def update_theme_recursive(self, widget, bg, fg):
        try:
            widget.configure(bg=bg, fg=fg)
        except Exception:
            pass
        for child in widget.winfo_children():
            self.update_theme_recursive(child, bg, fg)


# Main: Initialize everything and start the app
def main():
    config = load_config()
    storage_file = config.get("storage_file", "month_data.json")
    model = FinancialPlannerModel(storage_file=storage_file)
    app = FinancialPlannerView(config=config)
    controller = FinancialPlannerController(model=model, view=app)
    app.set_controller(controller)
    app.update_summary_table(model.months)
    app.mainloop()


if __name__ == "__main__":
    main()
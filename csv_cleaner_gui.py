"""
CSV / Excel Cleaner - GUI Version
----------------------------------
Same cleaning logic as csv_cleaner.py, but with a simple graphical
interface so you can pick your file with a "Browse" button instead
of typing the full path in a terminal.

Cleans a CSV/Excel file by:
  - Removing completely blank rows
  - Stripping extra whitespace from every cell
  - Standardizing column headers (lowercase, no spaces)
  - Removing duplicate rows
  - Filling remaining missing values with a placeholder

HOW TO RUN:
1. Install Python (if not already installed): https://www.python.org/downloads/
2. Install the required library (only once):
       pip install pandas
   (tkinter comes built-in with Python on Windows/Mac)
3. Double-click this file, or run in a terminal:
       python csv_cleaner_gui.py

The cleaned file is saved next to your original file with "_cleaned"
added to the name. Your original file is never modified.
"""

import os
import warnings
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd

warnings.filterwarnings("ignore")


def clean_headers(columns):
    """Lowercase, strip spaces, replace spaces with underscores."""
    return [str(c).strip().lower().replace(" ", "_") for c in columns]


def clean_dataframe(df, fill_placeholder=None):
    """Runs the full cleaning pipeline on a DataFrame and returns
    (cleaned_df, stats_dict)."""
    original_rows = len(df)

    # Standardize headers
    df.columns = clean_headers(df.columns)

    # Strip whitespace, treat empty/whitespace-only cells as truly blank
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(r"^(nan)?$", pd.NA, regex=True)

    # Remove fully blank rows
    df = df.dropna(how="all")
    after_blank_removal = len(df)

    # Remove duplicates
    df = df.drop_duplicates()
    after_dedup = len(df)

    # Optionally fill remaining missing values
    if fill_placeholder is not None and fill_placeholder != "":
        df = df.fillna(fill_placeholder)

    stats = {
        "original_rows": original_rows,
        "blank_rows_removed": original_rows - after_blank_removal,
        "duplicates_removed": after_blank_removal - after_dedup,
        "final_rows": len(df),
        "columns": list(df.columns),
    }
    return df, stats


class CsvCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV / Excel Cleaner")
        self.root.geometry("620x480")
        self.root.minsize(560, 400)
        self.root.resizable(True, True)

        self.file_path = tk.StringVar()
        self.fill_enabled = tk.BooleanVar(value=True)
        self.placeholder_text = tk.StringVar(value="N/A")

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 16, "pady": 8}

        title = tk.Label(
            self.root, text="CSV / Excel Cleaner",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=(16, 4))

        subtitle = tk.Label(
            self.root,
            text="Removes blank rows, duplicates, and messy formatting.",
            font=("Segoe UI", 9), fg="#555555"
        )
        subtitle.pack(pady=(0, 12))

        # File selection row
        file_frame = tk.Frame(self.root)
        file_frame.pack(fill="x", **pad)

        tk.Label(file_frame, text="File:", font=("Segoe UI", 10)).pack(side="left")
        file_entry = tk.Entry(file_frame, textvariable=self.file_path)
        file_entry.pack(side="left", padx=8, fill="x", expand=True)
        browse_btn = tk.Button(file_frame, text="Browse...", command=self.browse_file)
        browse_btn.pack(side="left")

        # Fill placeholder options
        options_frame = tk.Frame(self.root)
        options_frame.pack(fill="x", **pad)

        fill_check = tk.Checkbutton(
            options_frame, text="Fill empty cells with placeholder:",
            variable=self.fill_enabled
        )
        fill_check.pack(side="left")
        placeholder_entry = tk.Entry(options_frame, textvariable=self.placeholder_text, width=10)
        placeholder_entry.pack(side="left", padx=8)

        # Run button
        run_btn = tk.Button(
            self.root, text="Clean File", font=("Segoe UI", 11, "bold"),
            bg="#2e7d32", fg="white", padx=20, pady=8,
            command=self.run_cleaning
        )
        run_btn.pack(pady=16)

        # Progress bar (indeterminate, shown briefly during processing)
        self.progress = ttk.Progressbar(self.root, mode="indeterminate", length=300)

        # Results box
        result_label = tk.Label(self.root, text="Summary:", font=("Segoe UI", 10, "bold"))
        result_label.pack(anchor="w", padx=16)

        result_frame = tk.Frame(self.root)
        result_frame.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side="right", fill="y")

        self.result_box = tk.Text(result_frame, height=10, state="disabled",
                                   bg="#f5f5f5", font=("Consolas", 9),
                                   wrap="word", yscrollcommand=scrollbar.set)
        self.result_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.result_box.yview)

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select a CSV or Excel file",
            filetypes=[("CSV and Excel files", "*.csv *.xlsx *.xls"), ("All files", "*.*")]
        )
        if path:
            self.file_path.set(path)

    def set_result_text(self, text):
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, text)
        self.result_box.config(state="disabled")

    def run_cleaning(self):
        path = self.file_path.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Error", "Please select a valid file first.")
            return

        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".csv":
                df = pd.read_csv(path)
            elif ext in (".xlsx", ".xls"):
                df = pd.read_excel(path)
            else:
                messagebox.showerror("Error", "Only .csv, .xlsx, or .xls files are supported.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{e}")
            return

        self.progress.pack(pady=(0, 8))
        self.progress.start(10)
        self.root.update_idletasks()

        placeholder = self.placeholder_text.get() if self.fill_enabled.get() else None
        cleaned_df, stats = clean_dataframe(df, fill_placeholder=placeholder)

        base, _ = os.path.splitext(path)
        output_path = f"{base}_cleaned.csv"
        cleaned_df.to_csv(output_path, index=False)

        self.progress.stop()
        self.progress.pack_forget()

        summary = (
            f"Original rows:          {stats['original_rows']}\n"
            f"Blank rows removed:     {stats['blank_rows_removed']}\n"
            f"Duplicate rows removed: {stats['duplicates_removed']}\n"
            f"Final rows:             {stats['final_rows']}\n"
            f"Columns standardized:   {stats['columns']}\n\n"
            f"Cleaned file saved to:\n{output_path}"
        )
        self.set_result_text(summary)
        messagebox.showinfo("Done", f"Cleaned file saved to:\n{output_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CsvCleanerApp(root)
    root.mainloop()
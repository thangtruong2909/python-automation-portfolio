"""
Simple Web Scraper - GUI Version
-----------------------------------
Same scraping logic as web_scraper.py, but with a simple graphical
interface so you can type the URL and CSS selector into text boxes
instead of a terminal, and save the result with a file save dialog.

HOW TO RUN:
1. Install Python (if not already installed): https://www.python.org/downloads/
2. Install the required libraries (only once):
       pip install requests beautifulsoup4
   (tkinter comes built-in with Python on Windows/Mac)
3. Double-click this file, or run in a terminal:
       python web_scraper_gui.py

IMPORTANT - USE RESPONSIBLY:
  - Only scrape publicly accessible pages you have the right to
    collect data from.
  - Always check the site's robots.txt and Terms of Service before
    scraping.
  - This tool is for educational/demo purposes on public data
    (e.g. practice/sandbox sites like quotes.toscrape.com).
"""

import csv
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import requests
from bs4 import BeautifulSoup


def fetch_page(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text


def extract_items(html, selector):
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.select(selector)
    return [el.get_text(strip=True) for el in elements]


class WebScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Web Scraper")
        self.root.geometry("640x520")
        self.root.minsize(560, 420)
        self.root.resizable(True, True)

        self.url_var = tk.StringVar()
        self.selector_var = tk.StringVar()
        self.column_var = tk.StringVar(value="value")
        self.scraped_items = []

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 16, "pady": 6}

        tk.Label(self.root, text="Simple Web Scraper",
                 font=("Segoe UI", 16, "bold")).pack(pady=(16, 2))
        tk.Label(self.root, text="Extracts text from a page using a CSS selector.",
                 font=("Segoe UI", 9), fg="#555555").pack(pady=(0, 12))

        # URL input
        url_frame = tk.Frame(self.root)
        url_frame.pack(fill="x", **pad)
        tk.Label(url_frame, text="Page URL:", width=12, anchor="w").pack(side="left")
        tk.Entry(url_frame, textvariable=self.url_var).pack(side="left", fill="x", expand=True)

        # Selector input
        selector_frame = tk.Frame(self.root)
        selector_frame.pack(fill="x", **pad)
        tk.Label(selector_frame, text="CSS Selector:", width=12, anchor="w").pack(side="left")
        tk.Entry(selector_frame, textvariable=self.selector_var).pack(side="left", fill="x", expand=True)
        tk.Label(self.root, text="Example: '.price', 'h2 a', '.quote-text'",
                 font=("Segoe UI", 8), fg="#777777").pack(anchor="w", padx=16)

        # Column name input
        col_frame = tk.Frame(self.root)
        col_frame.pack(fill="x", **pad)
        tk.Label(col_frame, text="CSV Column Name:", width=16, anchor="w").pack(side="left")
        tk.Entry(col_frame, textvariable=self.column_var, width=20).pack(side="left")

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=12)
        self.scrape_btn = tk.Button(
            btn_frame, text="Scrape Page", font=("Segoe UI", 11, "bold"),
            bg="#2e7d32", fg="white", padx=16, pady=6,
            command=self.start_scrape
        )
        self.scrape_btn.pack(side="left", padx=6)

        self.save_btn = tk.Button(
            btn_frame, text="Save as CSV...", font=("Segoe UI", 10),
            padx=16, pady=6, state="disabled",
            command=self.save_csv
        )
        self.save_btn.pack(side="left", padx=6)

        self.progress = ttk.Progressbar(self.root, mode="indeterminate", length=300)

        # Results
        tk.Label(self.root, text="Results:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16)

        result_frame = tk.Frame(self.root)
        result_frame.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side="right", fill="y")

        self.result_box = tk.Text(result_frame, height=12, state="disabled",
                                   bg="#f5f5f5", font=("Consolas", 9),
                                   wrap="word", yscrollcommand=scrollbar.set)
        self.result_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.result_box.yview)

    def set_result_text(self, text):
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, text)
        self.result_box.config(state="disabled")

    def start_scrape(self):
        url = self.url_var.get().strip()
        selector = self.selector_var.get().strip()

        if not url.startswith(("http://", "https://")):
            messagebox.showerror("Error", "Please enter a full URL starting with http:// or https://")
            return
        if not selector:
            messagebox.showerror("Error", "Please enter a CSS selector.")
            return

        self.scrape_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.progress.pack(pady=(0, 8))
        self.progress.start(10)
        self.set_result_text("Fetching page, please wait...")

        # Run the network request in a background thread so the GUI
        # doesn't freeze while waiting for the page to load.
        thread = threading.Thread(target=self._scrape_worker, args=(url, selector), daemon=True)
        thread.start()

    def _scrape_worker(self, url, selector):
        try:
            html = fetch_page(url)
            items = extract_items(html, selector)
        except requests.exceptions.RequestException as e:
            self.root.after(0, self._scrape_error, f"Error fetching the page:\n{e}")
            return
        except Exception as e:
            self.root.after(0, self._scrape_error, f"Unexpected error:\n{e}")
            return

        self.root.after(0, self._scrape_done, items, selector)

    def _scrape_error(self, message):
        self.progress.stop()
        self.progress.pack_forget()
        self.scrape_btn.config(state="normal")
        self.set_result_text(message)
        messagebox.showerror("Error", message)

    def _scrape_done(self, items, selector):
        self.progress.stop()
        self.progress.pack_forget()
        self.scrape_btn.config(state="normal")
        self.scraped_items = items

        if not items:
            text = (
                f"No elements found matching selector '{selector}'.\n\n"
                "Tip: open the page in your browser, right-click the data "
                "you want, choose 'Inspect', and check the element's class name."
            )
            self.set_result_text(text)
            return

        preview = "\n".join(f"- {item}" for item in items[:20])
        more = f"\n... and {len(items) - 20} more" if len(items) > 20 else ""
        self.set_result_text(f"Found {len(items)} item(s):\n\n{preview}{more}")
        self.save_btn.config(state="normal")

    def save_csv(self):
        if not self.scraped_items:
            messagebox.showwarning("Nothing to save", "Scrape a page first.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Save scraped data as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not output_path:
            return

        column_name = self.column_var.get().strip() or "value"
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([column_name])
            for item in self.scraped_items:
                writer.writerow([item])

        messagebox.showinfo("Saved", f"Saved {len(self.scraped_items)} row(s) to:\n{output_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()
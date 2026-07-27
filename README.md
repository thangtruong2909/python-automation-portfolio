# python-automation-portfolio
Sample scripts demonstrating Python automation solutions for common 
business tasks — available in both command-line and graphical (GUI) 
versions. Available for freelance work on Fiverr.

## Scripts

### batch_file_renamer.py
Renames all files in a folder using a customizable pattern — add 
prefixes, today's date, and sequence numbers. Includes a preview 
step before any files are actually renamed, so nothing changes 
unless you confirm.

**How to run:**
python batch_file_renamer.py
Then follow the on-screen prompts.

### csv_cleaner_gui.py
A CSV/Excel cleaning tool with a simple graphical interface — no need 
to use the terminal. Select a file with the Browse button, and the 
tool automatically removes blank rows, removes duplicates, standardizes 
column headers, and fills empty cells with a placeholder of your choice. 
Results are shown directly in the app, and the cleaned file is saved 
as a new file (your original is never modified).

**How to run:**
pip install pandas
python csv_cleaner_gui.py

### web_scraper_gui.py
A web scraping tool with a graphical interface for extracting public 
data from any web page. Enter a URL and a CSS selector (e.g. `.price`, 
`h2 a`) to pull matching text from the page, preview the results, and 
export them to a CSV file with one click. Runs scraping in the 
background so the interface stays responsive while the page loads.

**How to run:**
pip install requests beautifulsoup4
python web_scraper_gui.py

---
📩 Need a custom script for your task? [Contact me on Fiverr](https://www.fiverr.com/matt_thangt/write-a-custom-python-script-to-automate-your-repetitive-task)

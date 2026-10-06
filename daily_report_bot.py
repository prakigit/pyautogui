import pyautogui
import pyperclip
import pandas as pd
import subprocess
import time
from datetime import datetime


# =========================================================
# SETTINGS
# =========================================================

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

print("Open the Chrome Browser...")
time.sleep(4)

pyautogui.hotkey('command', 'space', interval=0.2)
time.sleep(1)
pyautogui.typewrite('chrome', interval=0.2)
time.sleep(1)
pyautogui.press('enter', interval=0.2)
time.sleep(1)

print("Step 2: GO TO THE WEBSITE...")
pyautogui.hotkey('command', 'l', interval=0.2)
time.sleep(1)
pyautogui.typewrite('https://www.screener.in/company/504918/#peers"', interval=0.2)
time.sleep(1)
pyautogui.press('enter', interval=0.2)
time.sleep(5)


# =========================================================
# REQUIRED EXCEL COLUMNS
# =========================================================

REQUIRED_COLUMNS = [
    "S.No.",
    "Company",
    "CMP Rs.",
    "P/E",
    "Mar Cap Rs.Cr.",
    "Div Yld %",
    "NP Qtr Rs.Cr.",
    "Qtr Profit Var %",
    "Sales Qtr Rs.Cr.",
    "Qtr Sales Var %",
    "ROCE %"
]


# =========================================================
# STEP 1: OPEN / ACTIVATE CHROME
# =========================================================

print("Step 1: Opening Chrome...")

subprocess.run([
    "osascript",
    "-e",
    'tell application "Google Chrome" to activate'
])

time.sleep(3)


# =========================================================
# STEP 2: OPEN SCREENER WEBSITE
# =========================================================

print("Step 2: Opening Screener...")

pyautogui.hotkey("command", "l")
time.sleep(1)

pyautogui.typewrite(
    'https://www.screener.in/company/504918/#peers"',
    interval=0.01
)

pyautogui.press("enter")

print("Waiting for Screener to load...")

time.sleep(1)


# =========================================================
# STEP 3: EXTRACT PEER COMPARISON TABLE
# =========================================================

print("Step 3: Extracting Peer Comparison table...")


# JavaScript executed inside Chrome.
#
# It:
# 1. Finds the Peer Comparison section
# 2. Finds its table
# 3. Reads every row
# 4. Converts the table to tab-separated text
# 5. Copies the result to the clipboard

javascript_code = r'''javascript:(async()=>{let t=document.querySelector('#peers table');if(!t){let s=document.querySelector('#peers');if(s)s.scrollIntoView();await new Promise(r=>setTimeout(r,3000));t=document.querySelector('#peers table')}if(!t){alert('Peer comparison table not found. Please wait for the table to load and run again.');return}let rows=[...t.querySelectorAll('tr')].map(r=>[...r.querySelectorAll('th,td')].map(c=>c.innerText.trim()));let txt=rows.map(r=>r.join('\t')).join('\n');let ta=document.createElement('textarea');ta.value=txt;document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();alert('Peer table copied: '+rows.length+' rows');})()'''


# Make sure Chrome is active
subprocess.run([
    "osascript",
    "-e",
    'tell application "Google Chrome" to activate'
])

time.sleep(1)


# Open Chrome address bar
pyautogui.hotkey(
    "command",
    "l"
)

time.sleep(1)


# Type JavaScript
pyautogui.write(
    javascript_code,
    interval=0.001
)

pyautogui.press("enter")

time.sleep(4)


# =========================================================
# STEP 4: READ CLIPBOARD
# =========================================================

print("Step 4: Reading Peer Comparison data...")

clipboard_text = pyperclip.paste()


if not clipboard_text.strip():

    print("\nERROR: Clipboard is empty.")

    print(
        "The Peer Comparison table may not have loaded."
    )

    raise SystemExit


print(
    "Characters copied:",
    len(clipboard_text)
)


# =========================================================
# STEP 5: CONVERT CLIPBOARD TO DATAFRAME
# =========================================================

print("Step 5: Converting table to DataFrame...")

from io import StringIO


try:

    df = pd.read_csv(
        StringIO(clipboard_text),
        sep="\t",
        dtype=str
    )

except Exception as e:

    print("\nERROR while reading clipboard:")
    print(e)

    print("\nRaw clipboard data:")
    print(clipboard_text)

    raise SystemExit


# =========================================================
# STEP 6: DISPLAY ORIGINAL HEADERS
# =========================================================

print("\nOriginal Screener headers:")

for column in df.columns:

    print(
        repr(column)
    )


# =========================================================
# STEP 7: CLEAN COLUMN NAMES
# =========================================================

df.columns = [
    str(column)
    .replace("\n", " ")
    .replace("\xa0", " ")
    .strip()
    for column in df.columns
]


# =========================================================
# STEP 8: MAP SCREENER HEADERS
# =========================================================

column_mapping = {}


for column in df.columns:

    clean = column.lower().strip()


    # Serial number
    if clean in [
        "s.no.",
        "s.no",
        "s no",
        "s. no.",
        "rank"
    ]:

        column_mapping[column] = "S.No."


    # Company
    elif clean in [
        "name",
        "company"
    ]:

        column_mapping[column] = "Company"


    # CMP
    elif "cmp" in clean:

        column_mapping[column] = "CMP Rs."


    # P/E
    elif clean in [
        "p/e",
        "pe"
    ]:

        column_mapping[column] = "P/E"


    # Market Cap
    elif "mar cap" in clean:

        column_mapping[column] = "Mar Cap Rs.Cr."


    # Dividend Yield
    elif (
        "div yld" in clean
        or "dividend yield" in clean
    ):

        column_mapping[column] = "Div Yld %"


    # Net Profit Quarterly
    elif "np qtr" in clean:

        column_mapping[column] = "NP Qtr Rs.Cr."


    # Quarterly Profit Variation
    elif "qtr profit var" in clean:

        column_mapping[column] = "Qtr Profit Var %"


    # Quarterly Sales
    elif "sales qtr" in clean:

        column_mapping[column] = "Sales Qtr Rs.Cr."


    # Quarterly Sales Variation
    elif "qtr sales var" in clean:

        column_mapping[column] = "Qtr Sales Var %"


    # ROCE
    elif (
        clean == "roce %"
        or clean == "roce"
    ):

        column_mapping[column] = "ROCE %"


# Rename columns
df = df.rename(
    columns=column_mapping
)


# =========================================================
# STEP 9: CHECK REQUIRED COLUMNS
# =========================================================

missing_columns = [
    column
    for column in REQUIRED_COLUMNS
    if column not in df.columns
]


if missing_columns:

    print("\nERROR:")
    print("Some required columns were not found.")

    print("\nMissing columns:")

    for column in missing_columns:

        print(
            "-",
            column
        )


    print("\nColumns received from Screener:")

    for column in df.columns:

        print(
            "-",
            column
        )


    raise SystemExit


# =========================================================
# STEP 10: KEEP ONLY REQUIRED COLUMNS
# =========================================================

df = df[
    REQUIRED_COLUMNS
].copy()


# =========================================================
# STEP 11: REMOVE EMPTY ROWS
# =========================================================

df = df.dropna(
    how="all"
)


# =========================================================
# STEP 12: REMOVE MEDIAN ROW
# =========================================================

df = df[
    ~df["Company"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("median")
]


# =========================================================
# STEP 13: RESET INDEX
# =========================================================

df = df.reset_index(
    drop=True
)


# =========================================================
# STEP 14: ADD DATE & TIME AS FIRST COLUMN
# =========================================================

current_datetime = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)


df.insert(
    0,
    "Date & Time",
    current_datetime
)


# =========================================================
# STEP 15: SAVE TO EXCEL
# =========================================================

print("\nStep 6: Creating Excel file...")


# Timestamp for filename
timestamp = datetime.now().strftime(
    "%Y-%m-%d_%H-%M-%S"
)


filename = (
    f"screener_peer_comparison_{timestamp}.xlsx"
)


df.to_excel(
    filename,
    index=False
)


# =========================================================
# STEP 16: DISPLAY FINAL RESULT
# =========================================================

print("\n")
print("=" * 70)
print("SUCCESS!")
print("=" * 70)


print("\nExcel file created:")

print(
    filename
)


print("\nFinal columns:")

for column in df.columns:

    print(
        "-",
        column
    )


print("\nPeer Comparison Data:")

print(
    df.to_string(
        index=False
    )
)


print("\nNumber of companies:")

print(
    len(df)
)


print("\nNumber of columns:")

print(
    len(df.columns)
)


print("\nDate & Time of extraction:")

print(
    current_datetime
)


print("\nDone!")
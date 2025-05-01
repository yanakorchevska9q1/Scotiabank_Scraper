import os
import json
import requests
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials

# Save Google credentials from GitHub Actions secret
credentials_path = 'credentials.json'
with open(credentials_path, 'w') as f:
    f.write(os.environ['GOOGLE_CREDENTIALS_JSON'])

# Define scopes for Google Sheets access
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Authenticate with service account
creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
gc = gspread.authorize(creds)

# Open the Google Sheet by URL
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1DE2yw5TUfglpcR_RC_chlJINU54vCMSix8TR7_zKUC8"
spreadsheet = gc.open_by_url(spreadsheet_url)

# Select the correct worksheet/tab
worksheet = spreadsheet.worksheet("Sheet1")

# Fetch data from the ScotiaBank API
api_url = 'https://dmtsms.scotiabank.com/api/rates/fxr'
response = requests.get(api_url)
data = response.json()

# Find the USD rate
usd_data = next((item for item in data['data'] if item['CURRENCY_CODE'] == 'USD'), None)

# Print it for debugging
print(usd_data)

# Create a row for the sheet
row = {
    "Effective Date": usd_data["EFFECTIVE_DATE"],
    "Country": "United States",
    "Currency/Code": usd_data["CURRENCY_CODE"],
    "Client Buys (Pays Canadian)": usd_data["CLIENT_BUY"],
    "Client Sells (Receives Canadian)": usd_data["CLIENT_SELL"]
}

# Convert to DataFrame
df = pd.DataFrame([row])

# Determine next empty row in the sheet
existing = worksheet.get_all_values()
next_row = len(existing) + 1  # Append after existing rows

# Write new row to sheet
set_with_dataframe(worksheet, df, row=next_row, include_column_header=False)

print("Completed!")

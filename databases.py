import pandas as pd
import sqlite3

# Define the file path to the Excel file
excel_file = 'DataBases.xlsx'

# Read all sheets from the Excel file into a dictionary of DataFrames
dfs = pd.read_excel(excel_file, sheet_name=None)

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('your_database.db')

# Iterate over the dictionary and write each DataFrame to a separate table
for sheet_name, df in dfs.items():
    # Use the sheet name as the table name
    df.to_sql(sheet_name, conn, if_exists='replace', index=False)

# Close the connection
conn.close()



 
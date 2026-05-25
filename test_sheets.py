import gspread

gc = gspread.service_account(filename="credentials.json")

spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1Yu0KC5PH8rvGd520grm-_GMn-5LcuBX5Lx1tmjuO1oo/edit?gid=566375627#gid=566375627")

clients_sheet = spreadsheet.worksheet("clients")

rows = clients_sheet.get_all_records()

print(rows)
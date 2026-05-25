import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
gc = gspread.authorize(credentials)

spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1Yu0KC5PH8rvGd520grm-_GMn-5LcuBX5Lx1tmjuO1oo/edit?gid=566375627#gid=566375627")

clients_sheet = spreadsheet.worksheet("clients")

rows = clients_sheet.get_all_records()

print(rows)
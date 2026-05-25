import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

PRICE_PER_CLIENT = 25.00
COST_PER_CLIENT = 10.00

service_account_info = dict(st.secrets["gcp_service_account"])

service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")

credentials = Credentials.from_service_account_info(
    service_account_info
)

gc = gspread.authorize(credentials)

spreadsheet = gc.open("subscription_sales")
clients_sheet = spreadsheet.worksheet("clients")

st.set_page_config(page_title="TV Plan Dashboard", layout="wide")

page = st.sidebar.radio(
    "Menu",
    ["Register Client", "Dashboard", "Clients List"]
)

def load_clients():
    data = clients_sheet.get_all_records()
    return pd.DataFrame(data)

if page == "Register Client":
    st.title("Register Client")

    with st.form("client_form"):
        name = st.text_input("Client Name")
        whatsapp = st.text_input("WhatsApp")
        plan = st.selectbox("Plan", ["TV Plan"])
        submitted = st.form_submit_button("Register Client")

        if submitted:
            clients = clients_sheet.get_all_records()
            client_id = len(clients) + 1

            expiration_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            clients_sheet.append_row([
                client_id,
                name,
                whatsapp,
                plan,
                expiration_date,
                created_at
            ])

            st.success("Client registered successfully!")

if page == "Dashboard":
    st.title("TV Plan Subscription Dashboard")

    df = load_clients()

    if df.empty:
        st.warning("No clients registered yet.")
        st.stop()

    df["expiration_date"] = pd.to_datetime(df["expiration_date"])
    df["created_at"] = pd.to_datetime(df["created_at"])

    today = pd.Timestamp(datetime.now().date())

    df["status"] = df["expiration_date"].apply(
        lambda x: "active" if x >= today else "expired"
    )

    active_clients = df[df["status"] == "active"]
    expired_clients = df[df["status"] == "expired"]

    monthly_revenue = len(active_clients) * PRICE_PER_CLIENT
    monthly_cost = len(active_clients) * COST_PER_CLIENT
    monthly_profit = monthly_revenue - monthly_cost

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Active Clients", len(active_clients))
    col2.metric("Monthly Revenue", f"R$ {monthly_revenue:.2f}")
    col3.metric("Monthly Cost", f"R$ {monthly_cost:.2f}")
    col4.metric("Monthly Profit", f"R$ {monthly_profit:.2f}")

    st.subheader("Active vs Expired")

    status_chart = df["status"].value_counts().reset_index()
    status_chart.columns = ["status", "clients"]

    fig_status = px.pie(
        status_chart,
        names="status",
        values="clients",
        title="Client Status"
    )

    st.plotly_chart(fig_status, use_container_width=True)

    st.subheader("Monthly Sales")

    df["month"] = df["created_at"].dt.strftime("%Y-%m")

    monthly_sales = df.groupby("month").size().reset_index(name="sales")
    monthly_sales["revenue"] = monthly_sales["sales"] * PRICE_PER_CLIENT
    monthly_sales["cost"] = monthly_sales["sales"] * COST_PER_CLIENT
    monthly_sales["profit"] = monthly_sales["revenue"] - monthly_sales["cost"]

    fig = px.bar(
        monthly_sales,
        x="month",
        y=["revenue", "cost", "profit"],
        title="Revenue, Cost and Profit by Month",
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)

if page == "Clients List":
    st.title("Clients List")

    df = load_clients()

    if df.empty:
        st.warning("No clients registered yet.")
        st.stop()

    df["expiration_date"] = pd.to_datetime(df["expiration_date"])
    today = pd.Timestamp(datetime.now().date())

    df["status"] = df["expiration_date"].apply(
        lambda x: "active" if x >= today else "expired"
    )

    st.dataframe(df)
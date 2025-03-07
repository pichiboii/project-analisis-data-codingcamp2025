import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv", parse_dates=[
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ])
    return df

def filter_data(df):
    st.sidebar.header("Filter")
    
    # Filter berdasarkan status order
    status_filter = st.sidebar.multiselect("Pilih Status Order", df["order_status"].unique(), default=df["order_status"].unique())
    
    # Filter berdasarkan rentang waktu
    min_date = df["order_purchase_timestamp"].min().date()
    max_date = df["order_purchase_timestamp"].max().date()
    date_range = st.sidebar.date_input("Pilih Rentang Waktu", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    df_filtered = df[df["order_status"].isin(status_filter)]
    df_filtered = df_filtered[(df_filtered["order_purchase_timestamp"].dt.date >= date_range[0]) & (df_filtered["order_purchase_timestamp"].dt.date <= date_range[1])]
    
    return df_filtered

def display_metrics(df):
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", len(df))
    avg_delivery_time = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days.mean()
    col2.metric("Rata-rata Waktu Pengiriman", f"{avg_delivery_time:.2f} hari")
    on_time_percentage = 100 * (df["order_delivered_customer_date"] <= df["order_estimated_delivery_date"]).mean()
    col3.metric("% Order Tepat Waktu", f"{on_time_percentage:.2f}%")

def plot_order_status(df):
    st.subheader("📊 Distribusi Status Order")
    fig, ax = plt.subplots()
    status_counts = df["order_status"].value_counts()
    ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
    ax.set_title("Distribusi Status Order")
    st.pyplot(fig)

def plot_daily_orders(df):
    st.subheader("📈 Tren Order Harian")
    df_daily_orders = df.groupby(df["order_purchase_timestamp"].dt.date).size()
    st.line_chart(df_daily_orders)

def plot_delivery_delay(df):
    st.subheader("📦 Analisis Keterlambatan Pengiriman")
    df_copy = df.copy()
    df_copy["delay_days"] = (df_copy["order_delivered_customer_date"] - df_copy["order_estimated_delivery_date"]).dt.days
    df_copy = df_copy.dropna(subset=["delay_days"])
    
    fig, ax = plt.subplots()
    ax.boxplot(df_copy["delay_days"], vert=False, patch_artist=True, boxprops=dict(facecolor='#66b3ff'))
    ax.set_xlabel("Hari Keterlambatan")
    ax.set_title("Distribusi Keterlambatan Pengiriman")
    ax.grid(True, linestyle='--', alpha=0.6)
    
    st.pyplot(fig)

st.title("📦 Dashboard Order Analysis")
df = load_data()
df_filtered = filter_data(df)
display_metrics(df_filtered)
plot_order_status(df_filtered)
plot_daily_orders(df_filtered)
plot_delivery_delay(df_filtered)

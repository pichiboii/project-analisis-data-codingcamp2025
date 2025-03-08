import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# judul dashboard
st.title("📦E-Commerce Business Insights Dashboard📦")

# load dataset
@st.cache_data

# Debugging - Cek apakah file CSV tersedia
st.write("📌 Current working directory:", os.getcwd())
st.write("📌 Files in directory:", os.listdir("."))

orders_df = pd.read_csv("orders_df.csv", parse_dates=['order_purchase_timestamp'])
seller_df = pd.read_csv("seller_df.csv")
rfm_df = pd.read_csv("rfm_df.csv")
sellers_geolocation_df = pd.read_csv("sellers_geolocation_df.csv")

# sidebar untuk filter tanggal
st.sidebar.header("Filter Waktu")
min_date = orders_df['order_purchase_timestamp'].min()
max_date = orders_df['order_purchase_timestamp'].max()

start_date, end_date = st.sidebar.date_input(
    "Pilih Rentang Tanggal", 
    [min_date, max_date], 
    min_value=min_date, 
    max_value=max_date
)

# ---visualisasi untuk pertanyaan no 1 : Bagaimana tren jumlah pesanan pada e-commerce?---

# fungsi untuk menampilkan tren jumlah pesanan
def plot_order_trend(start_date, end_date):
    st.subheader("1. Bagaimana tren jumlah pesanan pada e-commerce?")
    
    # memfilter data berdasarkan rentang waktu
    mask = (orders_df['order_purchase_timestamp'] >= pd.Timestamp(start_date)) & \
           (orders_df['order_purchase_timestamp'] <= pd.Timestamp(end_date))
    filtered_orders = orders_df[mask]
    
    # memfilter hanya pesanan yang Completed
    completed_orders = filtered_orders[filtered_orders['order_status_category'] == 'Completed']
    
    # group by bulan
    monthly_orders = completed_orders.groupby(completed_orders['order_purchase_timestamp'].dt.to_period('M')).size()
    monthly_orders.index = monthly_orders.index.to_timestamp()
    
    # group by hari
    daily_orders = completed_orders.groupby(completed_orders['order_purchase_timestamp'].dt.to_period('D')).size()
    daily_orders.index = daily_orders.index.to_timestamp()
    
    # plot grafik per bulan
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(x=monthly_orders.index, y=monthly_orders.values, marker='o', color='#0d88e6', linewidth=2.5, markersize=10, ax=ax)
    
    ax.set_xlabel("Bulan", fontsize=12)
    ax.set_ylabel("Jumlah Pesanan", fontsize=12)
    ax.set_title("Tren Jumlah Pesanan per Bulan", fontsize=14)
    ax.set_xticks(monthly_orders.index)
    ax.set_xticklabels(monthly_orders.index.strftime('%B'), rotation=45)
    ax.grid(True)
    
    st.pyplot(fig)
    
    # tambahan insight
    st.markdown("""
### 🔍 Insight Tambahan :
Berdasarkan analisis tren jumlah pesanan e-commerce pada tahun 2018, terjadi fluktuasi signifikan dalam beberapa bulan terakhir. 
- **Penurunan tajam** terjadi pada bulan **Februari** dan **Juni**.
- **Peningkatan signifikan** tercatat pada **Maret** dibandingkan bulan sebelumnya.
- **Jumlah pesanan tertinggi** sepanjang tahun 2018 terjadi pada bulan **Januari**.
- **Jumlah pesanan terendah** tercatat pada bulan **Juni**.
""")
    
    # plot grafik per hari
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(x=daily_orders.index, y=daily_orders.values, marker='o', color='#0d88e6', linewidth=2.5, markersize=5, ax=ax)
    
    ax.set_xlabel("Tanggal", fontsize=12)
    ax.set_ylabel("Jumlah Pesanan", fontsize=12)
    ax.set_title("Tren Jumlah Pesanan per Hari", fontsize=14)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True)
    
    st.pyplot(fig)

# ---visualisasi untuk pertanyaan no 2 : Bagaimana performa seller berdasarkan jumlah pesanan dan rating pelanggan?---

# fungsi untuk menampilkan distribusi seller berdasarkan kategori
def plot_seller_category():
    st.subheader("2. Bagaimana performa seller berdasarkan jumlah pesanan dan rating pelanggan?")
    
    colors = ["#22a7f0", "#63bff0", "#e1a692", "#e14b31"]
    category_counts = seller_df['seller_category'].value_counts()
    category_order = ["Elite Seller", "Growing Seller", "At-Risk Seller", "Dormant Seller"]
    
    category_counts = category_counts.reindex(category_order, fill_value=0)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=category_counts.values, y=category_counts.index, palette=colors, ax=ax)
    ax.set_xlabel("Jumlah Seller")
    ax.set_ylabel("Kategori Seller")
    ax.set_title("Distribusi Seller Berdasarkan Kategori")
    
    st.pyplot(fig)
    
    # tambahan insight
    st.markdown("""
### 🔍 Insight Tambahan :
Berdasarkan analisis clustering dengan manual grouping, performa seller dapat dikategorikan ke dalam empat kelompok utama :
- **Elite Seller (34.44%)** merupakan kelompok dengan performa terbaik, memiliki jumlah pesanan tinggi serta rating pelanggan yang tinggi
- **Growing Seller (29.92%)** menunjukkan potensi pertumbuhan karena meskipun jumlah pesanannya masih rendah, mereka memiliki rating pelanggan yang tinggi
- **At-Risk Seller (18.93%)** memiliki jumlah pesanan tinggi tetapi rating rendah, yang menunjukkan adanya risiko dalam kualitas layanan mereka
- **Dormant Seller (16.71%)** merupakan kelompok dengan performa paling rendah, dengan jumlah pesanan dan rating yang sama-sama rendah
""")

# fungsi untuk menampilkan RFM analysis
def plot_rfm_analysis():
    st.subheader("Best Sellers Based on RFM Parameters")
    
    fig, ax = plt.subplots(1, 3, figsize=(18, 6))
    colors_g = ["#72BCD4"] * top_n
    
    # plot Recency (terbaru = nilai kecil)
    sns.barplot(y="Recency", x="seller_id", 
                data=rfm_df.nsmallest(top_n, "Recency"), 
                palette=colors_g, ax=ax[0])
    ax[0].set_title(f"{top_n} Seller dengan Pesanan Terbaru (Recency)")
    ax[0].set_xlabel(None)
    ax[0].set_ylabel("Recency (Hari)")
    ax[0].tick_params(axis="x", rotation=90)
    
    # plot Frequency (terbanyak = nilai besar)
    sns.barplot(y="Frequency", x="seller_id", 
                data=rfm_df.nlargest(top_n, "Frequency"), 
                palette=colors_g, ax=ax[1])
    ax[1].set_title(f"{top_n} Seller dengan Pesanan Terbanyak (Frequency)")
    ax[1].set_xlabel(None)
    ax[1].set_ylabel("Jumlah Pesanan")
    ax[1].tick_params(axis="x", rotation=90)
    
    # plot Monetary (tertinggi = nilai besar)
    sns.barplot(y="Monetary", x="seller_id", 
                data=rfm_df.nlargest(top_n, "Monetary"), 
                palette=colors_g, ax=ax[2])
    ax[2].set_title(f"{top_n} Seller dengan Rating Tertinggi (Monetary)")
    ax[2].set_xlabel(None)
    ax[2].set_ylabel("Rata-rata Rating")
    ax[2].tick_params(axis="x", rotation=90)
    
    st.pyplot(fig)
    
    # Insight 
    st.markdown("""
### 🔍 Kenapa RFM Analysis?
RFM (Recency, Frequency, Monetary) adalah metode analisis pelanggan yang digunakan untuk mengelompokkan seller berdasarkan perilaku transaksi mereka. Dengan RFM, kita dapat mengidentifikasi seller yang paling aktif dan bernilai tinggi, serta seller yang berisiko tidak aktif. RFM di sini memiliki komponen :
- Recency (R - Seberapa Baru?) : mengukur kapan terakhir kali seorang seller menerima pesanan
- Frequency (F - Seberapa Sering?) : mengukur jumlah pesanan yang sudah diterima oleh seller
- Monetary (M - Seberapa Besar?) : mengukur rata-rata rating yang diterima seller
""")

# ---visualisasi untuk pertanyaan no 3 :     

def plot_seller_distribution(sellers_geolocation_df, num_states=5):
    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(24, 12))
    st.subheader("3. Bagaimana distribusi geografis seller?")
    
    colors_b = ["#72BCD4"] * num_states  # warna untuk grafik terbanyak
    colors_s = ["#e1a692"] * num_states  # warna untuk grafik tersedikit

    # --- ROW 1: Seller per STATE ---
    state_counts = sellers_geolocation_df["seller_state"].value_counts().reset_index()
    state_counts.columns = ["seller_state", "count"]

    sns.barplot(x="count", y="seller_state", data=state_counts.head(num_states), palette=colors_b, ax=ax[0, 0])
    ax[0, 0].set_ylabel(None)
    ax[0, 0].set_xlabel(None)
    ax[0, 0].set_title("State dengan Seller Terbanyak", loc="center", fontsize=20)
    ax[0, 0].tick_params(axis="y", labelsize=15)
    ax[0, 0].tick_params(axis="x", labelsize=15)

    sns.barplot(
        x="count",
        y="seller_state",
        data=state_counts.sort_values(by="count", ascending=True).head(num_states),
        palette=colors_s,
        ax=ax[0, 1]
    )
    ax[0, 1].set_ylabel(None)
    ax[0, 1].set_xlabel(None)
    ax[0, 1].invert_xaxis()
    ax[0, 1].yaxis.set_label_position("right")
    ax[0, 1].yaxis.tick_right()
    ax[0, 1].set_title("State dengan Seller Tersedikit", loc="center", fontsize=20)
    ax[0, 1].tick_params(axis="y", labelsize=15)
    ax[0, 1].tick_params(axis="x", labelsize=15)

    # --- ROW 2: Seller per CITY ---
    city_counts = sellers_geolocation_df["seller_city"].value_counts().reset_index()
    city_counts.columns = ["seller_city", "count"]

    sns.barplot(x="count", y="seller_city", data=city_counts.head(num_states), palette=colors_b, ax=ax[1, 0])
    ax[1, 0].set_ylabel(None)
    ax[1, 0].set_xlabel(None)
    ax[1, 0].set_title("City dengan Seller Terbanyak", loc="center", fontsize=20)
    ax[1, 0].tick_params(axis="y", labelsize=15)
    ax[1, 0].tick_params(axis="x", labelsize=15)

    sns.barplot(
        x="count",
        y="seller_city",
        data=city_counts.sort_values(by="count", ascending=True).head(num_states),
        palette=colors_s,
        ax=ax[1, 1]
    )
    ax[1, 1].set_ylabel(None)
    ax[1, 1].set_xlabel(None)
    ax[1, 1].invert_xaxis()
    ax[1, 1].yaxis.set_label_position("right")
    ax[1, 1].yaxis.tick_right()
    ax[1, 1].set_title("City dengan Seller Tersedikit", loc="center", fontsize=20)
    ax[1, 1].tick_params(axis="y", labelsize=15)
    ax[1, 1].tick_params(axis="x", labelsize=15)

    fig.suptitle("Distribusi Seller Berdasarkan State dan City", fontsize=20)
    plt.subplots_adjust(hspace=0.4)  # Memberikan jarak antar baris
    st.pyplot(fig)
    
    # tambahan insight
    st.markdown("""
### 🔍 Insight Tambahan :
Distribusi geografis seller menunjukkan bahwa **sebagian besar seller terpusat di State São Paulo (SP)**, menjadikannya wilayah dengan jumlah seller terbanyak. Sebaliknya, **State Piauí (PI) memiliki jumlah seller paling sedikit**. <br>
Pada tingkat kota, **São Paulo menjadi kota dengan konsentrasi seller tertinggi, sementara Ferraz de Vasconcelos memiliki jumlah seller paling sedikit**.<br>
Distribusi ini mencerminkan bahwa **aktivitas e-commerce lebih terkonsentrasi di wilayah dengan pusat ekonomi besar** seperti São Paulo, sementara **daerah dengan aktivitas bisnis yang lebih rendah memiliki jumlah seller yang lebih sedikit**.
""")

# membuat filter berapa state/city yang ingin ditampilkan
st.sidebar.header("Filter")
top_n = st.sidebar.slider("Pilih jumlah seller teratas", min_value=3, max_value=10, value=5)
num_states = st.sidebar.slider("Jumlah State/City yang Ditampilkan", min_value=1, max_value=10, value=5)


# Tampilkan visualisasi di Streamlit
plot_order_trend(start_date, end_date)
plot_seller_category()
plot_rfm_analysis()
plot_seller_distribution(sellers_geolocation_df, num_states)

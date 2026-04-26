import streamlit as st
import pandas as pd
import requests
import sqlite3
import plotly.graph_objects as go
from datetime import datetime

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="علم أثير - Aether Science", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0F172A; color: white; }
    h1, h2 { color: #00D4AA !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. دوال جلب البيانات (نسخة تجاوز الحظر) ---
def get_live_data(symbol):
    coin_map = {"BTCUSDT": "bitcoin", "ETHUSDT": "ethereum", "SOLUSDT": "solana"}
    coin_id = coin_map.get(symbol, "bitcoin")
    try:
        # محاولة عبر Binance US أولاً
        res = requests.get(f"https://api.binance.us/api/v3/ticker/price?symbol={symbol}", timeout=5)
        if res.status_code == 200:
            return float(res.json()['price'])
        # محاولة عبر CoinGecko كبديل عالمي
        res_alt = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd", timeout=5)
        return float(res_alt.json()[coin_id]['usd'])
    except:
        return None

def get_chart_data(symbol):
    try:
        url = f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=50"
        data = requests.get(url, timeout=5).json()
        df = pd.DataFrame(data, columns=['time','o','h','l','c','v','ct','qv','t','bt','ab','ai'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        for col in ['o','h','l','c','v']: df[col] = pd.to_numeric(df[col])
        return df
    except:
        return None

# --- 3. الواجهة الرئيسية ---
st.markdown("# 🛡️ علم أثير - AETHER SCIENCE")

symbol = st.selectbox("اختر العملة", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
price = get_live_data(symbol)

if price:
    st.success(f"✅ السعر المباشر: ${price:,.2f}")
else:
    st.warning("⚠️ جاري تحديث البيانات من الخادم البديل...")

# الرسم البياني
df = get_chart_data(symbol)
if df is not None:
    fig = go.Figure(data=[go.Candlestick(x=df['time'], open=df['o'], high=df['h'], low=df['l'], close=df['c'])])
    fig.update_layout(template='plotly_dark', height=400)
    st.plotly_chart(fig, use_container_width=True)

# --- 4. سجل العمليات (إصلاح خطأ صورة 3460) ---
st.markdown("---")
st.markdown("### 📋 سجل العمليات النشطة")

try:
    conn = sqlite3.connect("aether.db")
    conn.execute("CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, symbol TEXT, side TEXT, price REAL)")
    df_trades = pd.read_sql_query("SELECT * FROM trades", conn)
    
    if not df_trades.empty:
        st.dataframe(df_trades, use_container_width=True)
    else:
        st.info("لا توجد صفقات نشطة حالياً. النظام جاهز.")
except:
    st.info("النظام في وضع الاستعداد.")

st.markdown("<p style='text-align:center;'>🛡️ إمبراطورية بايا © 2026</p>", unsafe_allow_html=True)

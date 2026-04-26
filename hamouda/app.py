import streamlit as st
import pandas as pd
import requests
import sqlite3
import plotly.graph_objects as go
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Baya Empire Pro", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; }
    .stApp { background: #0b0f19; color: #ffffff; }
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00D4AA;
    }
    h1 { color: #00D4AA; text-align: center; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

# --- 2. محرك البيانات ---
def get_crypto_data(symbol):
    try:
        url = f"https://api.binance.us/api/v3/ticker/24hr?symbol={symbol}"
        data = requests.get(url, timeout=5).json()
        return {
            "price": float(data['lastPrice']),
            "change": float(data['priceChangePercent']),
            "high": float(data['highPrice']),
            "low": float(data['lowPrice'])
        }
    except: return None

def get_candles(symbol):
    try:
        url = f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=30"
        data = requests.get(url, timeout=5).json()
        df = pd.DataFrame(data, columns=['time','o','h','l','c','v','ct','qv','t','bt','ab','ai'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        for col in ['o','h','l','c']: df[col] = pd.to_numeric(df[col])
        return df
    except: return None

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect("aether.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, side TEXT, price REAL, amount REAL, time TEXT)")

# --- 4. الواجهة الرئيسية ---
st.markdown("<h1>🛡️ BAYA EMPIRE PRO</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### الإعدادات")
    symbol = st.selectbox("زوج التداول", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    st.divider()
    st.info("حالة النظام: متصل 🟢")

info = get_crypto_data(symbol)

if info:
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'>💰 السعر<br><h2>${info['price']:,.2f}</h2></div>", unsafe_allow_html=True)
    with c2: 
        color = "#00D4AA" if info['change'] >= 0 else "#FF4B4B"
        st.markdown(f"<div class='metric-card'>📈 التغير<br><h2 style='color:{color}'>{info['change']}%</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'>🔥 الأعلى<br><h2>${info['high']:,.1f}</h2></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='metric-card'>❄️ الأدنى<br><h2>${info['low']:,.1f}</h2></div>", unsafe_allow_html=True)

    df = get_candles(symbol)
    if df is not None:
        fig = go.Figure(data=[go.Candlestick(x=df['time'], open=df['o'], high=df['h'], low=df['l'], close=df['c'])])
        fig.update_layout(template='plotly_dark', height=400, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### ⚡ مركز العمليات")
    col_t1, col_t2 = st.columns([1, 2])
    with col_t1:
        side = st.radio("نوع العملية", ["BUY", "SELL"])
        amount = st.number_input("الكمية", value=0.1)
        if st.button("🚀 تنفيذ المهمة", use_container_width=True):
            conn.execute("INSERT INTO trades (symbol, side, price, amount, time) VALUES (?,?,?,?,?)",
                         (symbol, side, info['price'], amount, datetime.now().strftime("%H:%M:%S")))
            conn.commit()
            st.toast("تمت العملية بنجاح!")

    with col_t2:
        st.markdown("#### 📜 سجل العمليات")
        history = pd.read_sql_query("SELECT side, price, amount, time FROM trades ORDER BY id DESC LIMIT 5", conn)
        st.table(history) if not history.empty else st.info("السجل فارغ")
else:
    st.error("فشل في جلب البيانات. يرجى المحاولة لاحقاً.")

st.markdown("<p style='text-align:center; opacity:0.3;'>🛡️ إمبراطورية بايا 2026</p>", unsafe_allow_html=True)

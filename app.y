import streamlit as st
import pandas as pd
import requests
import sqlite3
import plotly.graph_objects as go
from datetime import datetime

# --- 1. الإعدادات الجمالية ---
st.set_page_config(page_title="Baya Empire Pro", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; }
    .stApp { background: #0b0f19; color: #ffffff; }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00D4AA;
        margin-bottom: 10px;
    }
    h1 { color: #00D4AA; text-align: center; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

# --- 2. محرك جلب البيانات ---
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

# --- 3. إدارة قاعدة البيانات (المصادقة) ---
def init_db():
    conn = sqlite3.connect("aether.db", check_same_thread=False)
    # التأكد من وجود الجدول بالأعمدة الصحيحة
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            symbol TEXT, 
            side TEXT, 
            price REAL, 
            amount REAL, 
            time TEXT
        )
    """)
    conn.commit()
    return conn

conn = init_db()

# --- 4. الواجهة الرئيسية ---
st.markdown("<h1>🛡️ BAYA EMPIRE PRO</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    symbol = st.selectbox("زوج التداول", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    st.divider()
    st.success("النظام نشط 🟢")

info = get_crypto_data(symbol)

if info:
    # عرض البطاقات (كما في صورتك الجميلة 3478)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'>💰 السعر<br><h2>${info['price']:,.2f}</h2></div>", unsafe_allow_html=True)
    with c2: 
        color = "#00D4AA" if info['change'] >= 0 else "#FF4B4B"
        st.markdown(f"<div class='metric-card'>📈 التغير<br><h2 style='color:{color}'>{info['change']}%</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'>🔥 الأعلى<br><h2>${info['high']:,.1f}</h2></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='metric-card'>❄️ الأدنى<br><h2>${info['low']:,.1f}</h2></div>", unsafe_allow_html=True)

    # مركز العمليات (صورة 3477)
    st.markdown("### ⚡ مركز العمليات")
    col_t1, col_t2 = st.columns([1, 2])
    
    with col_t1:
        side = st.radio("نوع العملية", ["BUY", "SELL"])
        amount = st.number_input("الكمية", value=0.10, step=0.01)
        if st.button("🚀 تنفيذ المهمة", use_container_width=True):
            conn.execute("INSERT INTO trades (symbol, side, price, amount, time) VALUES (?,?,?,?,?)",
                         (symbol, side, info['price'], amount, datetime.now().strftime("%H:%M:%S")))
            conn.commit()
            st.toast("✅ تم تسجيل العملية في الإمبراطورية!")

    with col_t2:
        st.markdown("#### 📜 سجل العمليات")
        try:
            history = pd.read_sql_query("SELECT side, price, amount, time FROM trades ORDER BY id DESC LIMIT 5", conn)
            if not history.empty:
                st.dataframe(history, use_container_width=True)
            else:
                st.info("لا توجد عمليات مسجلة حالياً.")
        except:
            st.warning("جاري تهيئة السجل...")
else:
    st.error("فشل الاتصال بالخادم الرئيسي.")

st.markdown("<p style='text-align:center; opacity:0.3;'>🛡️ إمبراطورية بايا © 2026</p>", unsafe_allow_html=True)

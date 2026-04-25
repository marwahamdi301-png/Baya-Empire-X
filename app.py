import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="علم أثير - Aether Science", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); }
h1, h2, h3 { color: #00D4AA !important; }
.stButton > button { background: linear-gradient(135deg, #00D4AA, #10B981) !important; color: white; border-radius: 12px; padding: 12px; }
</style>
""", unsafe_allow_html=True)

class AetherDB:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized: return
        self.db_name = "aether.db"
        self._initialized = True
        self.setup()
    
    def setup(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, side TEXT, entry_price REAL, exit_price REAL, amount REAL, profit REAL, status TEXT DEFAULT 'OPEN', timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            conn.commit()
    
    def log_trade(self, symbol, side, price, amount):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("INSERT INTO trades (symbol, side, entry_price, amount) VALUES (?, ?, ?, ?)", (symbol, side, price, amount))
    
    def get_open_trades(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            return pd.read_sql_query("SELECT * FROM trades WHERE status='OPEN'", conn)
    
    def get_all_trades(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            return pd.read_sql_query("SELECT * FROM trades ORDER BY timestamp DESC", conn)
    
    def get_stats(self):
        df = self.get_all_trades()
        if df.empty: return {"win_rate": 0, "total_profit": 0, "trade_count": 0}
        closed = df[df['status']=='CLOSED'] if 'CLOSED' in df['status'].values else pd.DataFrame()
        if closed.empty: return {"win_rate": 0, "total_profit": 0, "trade_count": 0}
        wins = len(closed[closed['profit']>0]) if 'profit' in closed.columns else 0
        return {"win_rate": (wins/len(closed))*100, "total_profit": closed['profit'].sum() if 'profit' in closed.columns else 0, "trade_count": len(closed), "winners": wins}

def get_price(symbol):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=5)
        return float(r.json()['price']) if r.status_code == 200 else None
    except: return None

def get_klines(symbol, interval="1h", limit=100):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            df = pd.DataFrame(data, columns=['time','o','h','l','c','v','ct','qv','t','bt','ab','ai'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            for col in ['o','h','l','c','v']: df[col] = pd.to_numeric(df[col])
            return df
    except: return None

def calc_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta>0,0).rolling(period).mean()
    loss = (-delta.where(delta<0,0)).rolling(period).mean()
    rs = gain/loss
    return 100-(100/(1+rs))

db = AetherDB()

st.markdown("# 🛡️ علم أثير - AETHER SCIENCE")
st.markdown("### نظام التداول الذكي المدعوم بالذكاء الاصطناعي")

symbols = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT","AVAXUSDT","MATICUSDT"]
symbol = st.selectbox("اختر الرمز", symbols)

price = get_price(symbol)
if price:
    st.success(f"✅ السعر الحالي: ${price:,.2f}")
else:
    st.error("❌ تعذر جلب السعر")

stats = db.get_stats()
col1, col2, col3 = st.columns(3)
col1.metric("💰 إجمالي الربح", f"${stats['total_profit']:.2f}")
col2.metric("🎯 نسبة الفوز", f"{stats['win_rate']:.1f}%")
col3.metric("📊 عدد الصفقات", stats['trade_count'])

st.markdown("---")
st.markdown("### 📊 التحليل الفني")

df = get_klines(symbol)
if df is not None and len(df) > 0:
    rsi = calc_rsi(df['c'])
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df['time'], open=df['o'], high=df['h'], low=df['l'], close=df['c'], name='السعر'))
    fig.update_layout(template='plotly_dark', height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"RSI: {rsi.iloc[-1]:.1f}")
else:
    st.error("تعذر جلب البيانات")

st.markdown("---")
st.markdown("### 💹 فتح صفقة")

col1, col2 = st.columns(2)
with col1:
    side = st.radio("الاتجاه", ["BUY", "SELL"], horizontal=True)
    entry = st.number_input("سعر الدخول", value=float(price) if price else 50000.0)
    amount = st.number_input("الكمية", value=0.001)
with col2:
    if st.button("🚀 فتح الصفقة", use_container_width=True):
        db.log_trade(symbol, side, entry, amount)
        st.success(f"✅ تم فتح صفقة {side}!")

st.markdown("### 📋 الصفقات المفتوحة")
trades = db.get_open_trades()
if not trades.empty:
    st.dataframe(trades, use_container_width=True)
else:
    st.info("لا توجد صفقات مفتوحة")

st.markdown("---")
st.markdown("**🛡️ علم أثير - Aether Science | © 2024 Jamel Chaabani**")

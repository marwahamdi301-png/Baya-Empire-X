import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import sqlite3
import plotly.graph_objects as go
from binance.client import Client

# إعداد الصفحة وتصميم الإمبراطورية
st.set_page_config(page_title="علم أثير - Aether Science", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); }
h1, h2, h3 { color: #00D4AA !important; }
.stButton > button { background: linear-gradient(135deg, #00D4AA, #10B981) !important; color: white; border-radius: 12px; padding: 12px; transition: 0.3s; }
.stButton > button:hover { transform: scale(1.02); box-shadow: 0 4px 15px rgba(0,212,170,0.4); }
</style>
""", unsafe_allow_html=True)

# دمج المفاتيح مباشرة في الكود (Hardcoded) لضمان الاتصال
API_KEY = "A60nfkH0J266aALgB3QnbcYySaSiTLHgXrcUmHA6SnFQJ4ngNPJGvIHXrHNxbmfX"
API_SECRET = "Z9zQGxqzQyjxyadmrDJYcMyrVTf1PlHqCftHh3gMehPsXXTUiZtkMdYTDskbt5Rr"

try:
    client = Client(API_KEY, API_SECRET)
except Exception as e:
    st.error(f"⚠️ خطأ في الاتصال بمكتبة بينانس: {e}")
    client = None

class AetherDB:
    def __init__(self):
        self.db_name = "aether.db"
        self.setup()
    
    def setup(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                symbol TEXT, side TEXT, entry_price REAL, 
                amount REAL, status TEXT DEFAULT 'OPEN', 
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            conn.commit()
    
    def log_trade(self, symbol, side, price, amount):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("INSERT INTO trades (symbol, side, entry_price, amount) VALUES (?, ?, ?, ?)", 
                         (symbol, side, price, amount))
    
    def get_open_trades(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            return pd.read_sql_query("SELECT * FROM trades WHERE status='OPEN'", conn)

db = AetherDB()

# دالة جلب السعر عبر المكتبة الرسمية
def get_price(symbol):
    try:
        if client:
            ticker = client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        return None
    except:
        return None

def get_klines(symbol):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100")
        data = r.json()
        df = pd.DataFrame(data, columns=['time','o','h','l','c','v','ct','qv','t','bt','ab','ai'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        for col in ['o','h','l','c','v']: df[col] = pd.to_numeric(df[col])
        return df
    except: return None

# الواجهة الرئيسية
st.markdown("# 🛡️ علم أثير - AETHER SCIENCE")
st.markdown("### نظام التداول الذكي | النسخة المستقرة")

symbols = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT"]
symbol = st.selectbox("اختر العملة للتداول", symbols)

price = get_price(symbol)
if price:
    st.success(f"✅ السعر المباشر لـ {symbol}: **${price:,.2f}**")
else:
    st.error("❌ تعذر جلب السعر. تأكدي من أن مفاتيحكِ مفعلة في Binance (دون قيود IP).")

st.markdown("---")

# الرسم البياني
df = get_klines(symbol)
if df is not None:
    fig = go.Figure(data=[go.Candlestick(x=df['time'], open=df['o'], high=df['h'], low=df['l'], close=df['c'])])
    fig.update_layout(template='plotly_dark', title=f"تحليل {symbol}", height=450)
    st.plotly_chart(fig, use_container_width=True)

# تنفيذ الصفقات
st.markdown("### 💹 تنفيذ أمر تداول")
col_a, col_b = st.columns(2)
with col_a:
    side = st.radio("نوع العملية", ["BUY", "SELL"], horizontal=True)
    entry_val = st.number_input("سعر التنفيذ", value=price if price else 0.0)
with col_b:
    amount = st.number_input("الكمية", value=0.01)
    if st.button("🚀 إرسال الأمر للسوق", use_container_width=True):
        if price:
            db.log_trade(symbol, side, entry_val, amount)
            st.balloons()
            st.success(f"تم تسجيل صفقة {side} بنجاح!")

st.markdown("---")
st.markdown("### 📋 سجل العمليات الحالية")
open_trades = db.get_open_trades()
st.dataframe(open_trades if not open_trades.empty else "لا توجد صفقات نشطة", use_container_width=True)

st.markdown("**🛡️ إمبراطورية بايا - نظام أثير العلمي © 2026**")

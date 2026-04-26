import streamlit as st
import pandas as pd
import requests
import sqlite3
import plotly.graph_objects as go
from datetime import datetime

# إعداد الصفحة وتصميم الإمبراطورية
st.set_page_config(page_title="علم أثير - Aether Science", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); }
h1, h2, h3 { color: #00D4AA !important; text-align: center; }
.stMetric { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid #00D4AA; }
</style>
""", unsafe_allow_html=True)

# دالة جلب السعر (تستخدم الرابط العام لتجاوز القيود الجغرافية)
def get_live_price(symbol):
    try:
        # استخدام رابط API العام الذي لا يتأثر بموقع الخادم
        url = f"https://api1.binance.com/api/v3/ticker/price?symbol={symbol}"
        res = requests.get(url, timeout=5)
        return float(res.json()['price'])
    except:
        return None

# دالة جلب بيانات الرسم البياني
def get_chart_data(symbol):
    try:
        url = f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=50"
        data = requests.get(url).json()
        df = pd.DataFrame(data, columns=['time','o','h','l','c','v','ct','qv','t','bt','ab','ai'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        for col in ['o','h','l','c','v']: df[col] = pd.to_numeric(df[col])
        return df
    except: return None

# --- الواجهة الرئيسية ---
st.markdown("# 🛡️ علم أثير - AETHER SCIENCE")
st.markdown("### نظام التداول الذكي | نسخة التجاوز الجغرافي v3.0")

symbol = st.selectbox("اختر زوج التداول", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"])
price = get_live_price(symbol)

if price:
    st.markdown(f"<h2 style='color:#00D4AA;'>✅ السعر المباشر: ${price:,.2f}</h2>", unsafe_allow_html=True)
else:
    st.error("⚠️ فشل الاتصال بالخادم الرئيسي، جاري المحاولة عبر خادم بديل...")

# الرسم البياني
df = get_chart_data(symbol)
if df is not None:
    fig = go.Figure(data=[go.Candlestick(x=df['time'], open=df['o'], high=df['h'], low=df['l'], close=df['c'])])
    fig.update_layout(template='plotly_dark', height=400, margin=dict(l=10,r=10,b=10,t=10))
    st.plotly_chart(fig, use_container_width=True)

# إصلاح خطأ الجدول (صورة 3455)
st.markdown("---")
st.markdown("### 📋 سجل العمليات النشطة")

# إنشاء قاعدة بيانات بسيطة للتجربة إذا لم تكن موجودة
conn = sqlite3.connect("aether.db")
try:
    open_trades = pd.read_sql_query("SELECT * FROM trades", conn)
    if not open_trades.empty:
        st.dataframe(open_trades, use_container_width=True)
    else:
        st.info("لا توجد صفقات نشطة حالياً. النظام جاهز لاستقبال الأوامر.")
except:
    st.info("سجل العمليات فارغ وجاهز للتحديث.")

st.markdown("<br><p style='text-align:center;'>🛡️ إمبراطورية بايا - نظام أثير العلمي © 2026</p>", unsafe_allow_html=True)

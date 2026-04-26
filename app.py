لواجهة الرئيسية ---
n("# 🛡️ علم أثير - AETHER SCIENCE")
symbol = st.selectbox("اختر العملة", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
import streamlit as st
import pandas as pd
import requests
import sqlite3
import plotly.graph_objects as go
from datetime import datetime

# --- 1. إعدادات الصفحة والجمالية ---
st.set_page_config(page_title="Baya Empire Pro", page_icon="🛡️", layout="wide")

# CSS متقدم لإضافة الرونق والجمالية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    * { font-family: 'Cairo', sans-serif; }
    .stApp { background: #0b0f19; color: #ffffff; }
    
    /* تصميم البطاقات */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00D4AA;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* تخصيص العناوين */
    h1 {
        background: -webkit-linear-gradient(#00D4AA, #00A382);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* تخصيص الأزرار */
    .stButton>button {
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px #00D4AA;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. محرك البيانات المتقدم ---
def get_crypto_data(symbol):
    try:
        # جلب السعر ومعلومات إضافية
        url = f"https://api.binance.us/api/v3/ticker/24hr?symbol={symbol}"
        data = requests.get(url, timeout=5).json()
        return {
            "price": float(data['lastPrice']),
            "change": float(data['priceChangePercent']),
            "high": float(data['highPrice']),
            "low": float(data['lowPrice']),
            "volume": float(data['volume'])
        }
    except: return None

def get_candles(symbol):
    try:
        url = f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=30"
        data = requests.get(url).json()
        return pd.DataFrame(data, columns=['time','o','h','l','c','v','ct','qv','t','bt','ab','ai'])
    except: return None

# --- 3. إدارة قاعدة البيانات ---
conn = sqlite3.connect("aether.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, side TEXT, price REAL, amount REAL, time TEXT)")

# --- 4. الهيكل البصري للتطبيق ---

# العنوان العلوي
st.markdown("<h1>🛡️ BAYA EMPIRE PRO | الإمبراطورية</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>نظام أثير للتحليل المالي المتقدم</p>", unsafe_allow_html=True)

# شريط الأدوات الجانبي
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2091/2091665.png", width=100)
    st.markdown("### الإعدادات")
    symbol = st.selectbox("زوج التداول", ["BTCUSDT", "ETHUSDT", "SOLUSDT"], index=0)
    st.divider()
    st.markdown("#### حالة النظام: 🟢 متصل")

# جلب البيانات
info = get_crypto_data(symbol)

if info:
    # عرض الإحصائيات في بطاقات جميلة
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card'>💰 السعر<br><h2>${info['price']:,.2f}</h2></div>", unsafe_allow_html=True)
    with c2:
        color = "#00D4AA" if info['change'] >= 0 else "#FF4B4B"
        st.markdown(f"<div class='metric-card'>📈 تغير 24h<br><h2 style='color:{color}'>{info['change']}%</h2></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'>🔥 أعلى سعر<br><h2>${info['high']:,.1f}</h2></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'>❄️ أدنى سعر<br><h2>${info['low']:,.1f}</h2></div>", unsafe_allow_html=True)

    # الرسم البياني الاحترافي
    st.markdown("### 📊 تحليل السوق")
    df = get_candles(symbol)
    if df is not None:
        fig = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df['time'], unit='ms'),
                        open=df['o'], high=df['h'], low=df['l'], close=df['c'],
                        increasing_line_color= '#00D4AA', decreasing_line_color= '#FF4B4B')])
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450)
        st.plotly_chart(fig, use_container_width=True)

    # لوحة التحكم في العمليات
    st.markdown("### ⚡ مركز العمليات")
    col_trade1, col_trade2 = st.columns([1, 2])
    
    with col_trade1:
        trade_side = st.radio("نوع العملية", ["شراء (BUY)", "بيع (SELL)"], horizontal=True)
        trade_amount = st.number_input("الكمية", min_value=0.001, value=0.1)
        if st.button("🚀 تنفيذ المهمة", use_container_width=True):
            side_eng = "BUY" if "شراء" in trade_side else "SELL"
            conn.execute("INSERT INTO trades (symbol, side, price, amount, time) VALUES (?,?,?,?,?)",
                         (symbol, side_eng, info['price'], trade_amount, datetime.now().strftime("%H:%M:%S")))
            conn.commit()
            st.toast(f"تمت العملية بنجاح على {symbol}", icon='✅')

    with col_trade2:
        # عرض آخر 5 عمليات فقط بشكل أنيق
        st.markdown("#### 📜 سجل العمليات الأخيرة")
        history = pd.read_sql_query("SELECT side, price, amount, time FROM trades ORDER BY id DESC LIMIT 5", conn)
        if not history.empty:
            st.table(history)
        else:
            st.info("لا توجد عمليات مسجلة اليوم.")

else:
    st.error("⚠️ فشل في جلب بيانات السوق الحية.")

st.markdown("---")
st.markdown("<p style='text-align:center; opacity:0.3;'>🛡️ إمبراطورية بايا - جميع الحقوق محفوظة 2026</p>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import numpy as np
import requests
import sqlite3
import plotly.graph_objects as go
from datetime import datetime

# --- 1. إعداد الصفحة والتصميم ---
st.set_page_config(page_title="علم أثير - Aether Science", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); color: white; }
    h1, h2, h3 { color: #00D4AA !important; text-align: center; font-family: 'Cairo', sans-serif; }
    .stMetric { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid #00D4AA; }
    .stButton > button { 
        background: linear-gradient(135deg, #00D4AA, #10B981) !important; 
        color: white; border-radius: 12px; width: 100%; border: none; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. محرك جلب البيانات (تجاوز القيود الجغرافية) ---
def get_live_data(symbol):
    """جلب السعر باستخدام روابط متعددة لضمان العمل في المناطق المحظورة"""
    # تحويل الرموز لمصادر بديلة
    coin_map = {"BTCUSDT": "bitcoin", "ETHUSDT": "ethereum", "SOLUSDT": "solana", "BNBUSDT": "binancecoin"}
    coin_id = coin_map.get(symbol, "bitcoin")
    
    try:
        # المحاولة الأولى: رابط Binance US (غالباً لا يُحظر في خوادم السحاب)
        res = requests.get(f"https://api.binance.us/api/v3/ticker/price?symbol={symbol}", timeout=5)
        if res.status_code == 200:
            return float(res.json()['price'])
        
        # المحاولة الثانية: مصدر CoinGecko العالمي
        res_alt = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd", timeout=5)
        return float(res_alt.json()[coin_id]['usd'])
    except:
        return None

def get_chart_data(symbol):
    """جلب بيانات الشموع من رابط API بديل"""
    try:
        url = f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=50"
        data = requests.get(url, timeout=5).json()
        df = pd.DataFrame(data, columns=['time','o','h','l','c','v','ct','qv','t','bt','ab','ai'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        for col in ['o','h','l','c','v']: df[col] = pd.to_numeric(df[col])
        return df
    except:


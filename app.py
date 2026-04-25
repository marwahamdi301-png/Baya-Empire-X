import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

st.set_page_config(page_title="Baya Empire", page_icon="🛡️", layout="wide")

class BayaDatabase:
    def __init__(self, db_name="baya_empire.db"):
        self.db_name = db_name
        self.setup_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name, check_same_thread=False)

    def setup_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT, side TEXT, entry_price REAL,
                    exit_price REAL, amount REAL, profit REAL,
                    status TEXT, timestamp DATETIME
                )
            ''')
            conn.commit()

    @staticmethod
    def get_instance():
        if not hasattr(BayaDatabase, '_instance'):
            BayaDatabase._instance = BayaDatabase()
        return BayaDatabase._instance

    def log_trade(self, symbol, side, price, amount):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO trades (symbol, side, entry_price, amount, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol, side, price, amount, 'OPEN', datetime.now()))

    def get_open_trades(self):
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM trades WHERE status = 'OPEN'", conn)

    def get_performance_stats(self):
        df = self.get_trade_history()
        if df.empty:
            return {"win_rate": 0, "total_profit": 0, "trade_count": 0}
        wins = len(df[df['profit'] > 0])
        return {
            "win_rate": (wins / len(df)) * 100,
            "total_profit": df['profit'].sum(),
            "trade_count": len(df)
        }

    def get_trade_history(self):
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM trades ORDER BY timestamp DESC", conn)

def main():
    st.markdown("# 🛡️ Baya Empire - AI Trading Guardian")
    
    menu = st.sidebar.radio("القائمة", ["🏠 الرئيسية", "📊 لوحة التحكم", "💼 الصفقات"])
    db = BayaDatabase.get_instance()

    if menu == "🏠 الرئيسية":
        st.success("مرحباً بك في Baya Empire!")

    elif menu == "📊 لوحة التحكم":
        stats = db.get_performance_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("نسبة الفوز", f"{stats['win_rate']:.1f}%")
        col2.metric("إجمالي الربح", f"${stats['total_profit']:.2f}")
        col3.metric("عدد الصفقات", stats['trade_count'])

    elif menu == "💼 الصفقات":
        with st.form("new_trade"):
            symbol = st.text_input("الرمز", "BTCUSDT")
            side = st.selectbox("الاتجاه", ["BUY", "SELL"])
            price = st.number_input("السعر", value=50000.0)
            amount = st.number_input("الكمية", value=0.01)
            if st.form_submit_button("فتح صفقة"):
                db.log_trade(symbol, side, price, amount)
                st.success("تم فتح الصفقة!")

        open_trades = db.get_open_trades()
        if not open_trades.empty:
            st.dataframe(open_trades)
        else:
            st.info("لا توجد صفقات مفتوحة")

if __name__ == "__main__":
    main()

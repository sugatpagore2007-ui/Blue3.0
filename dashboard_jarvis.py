
import json
import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

DB_FILE = "blue3_memory.db"
MEMORY_FILE = "blue3_memory.json"

st.set_page_config(
    page_title="Blue 3.0 JARVIS UI",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #102030 0%, #05070a 45%, #000000 100%);
    color: #d7f7ff;
}
.big-title {
    text-align: center;
    font-size: 52px;
    font-weight: 800;
    color: #6ee7ff;
    text-shadow: 0 0 20px #00d9ff;
    margin-bottom: 0;
}
.sub-title {
    text-align: center;
    color: #9befff;
    font-size: 18px;
    margin-top: -8px;
    margin-bottom: 30px;
}
.jarvis-card {
    background: rgba(0, 25, 45, 0.75);
    border: 1px solid rgba(0, 217, 255, 0.45);
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 0 18px rgba(0, 217, 255, 0.18);
}
.status-online {
    color: #00ff99;
    font-weight: 700;
    text-shadow: 0 0 10px #00ff99;
}
.console {
    background: rgba(0, 0, 0, 0.65);
    border-left: 4px solid #00d9ff;
    padding: 14px;
    border-radius: 10px;
    font-family: Consolas, monospace;
    color: #bff7ff;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='big-title'>BLUE 3.0</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>JARVIS Style Voice AI Dashboard</p>", unsafe_allow_html=True)

if not Path(DB_FILE).exists():
    st.warning("No database found. Run main.py first and use some commands.")
    st.stop()

conn = sqlite3.connect(DB_FILE)
try:
    df = pd.read_sql_query("SELECT * FROM command_logs ORDER BY timestamp DESC", conn)
except Exception as e:
    st.error(f"Could not read command_logs table: {e}")
    st.stop()
finally:
    conn.close()

if df.empty:
    st.info("No commands logged yet. Start Blue and try: blue open youtube.")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"])

if "category" not in df.columns:
    df["category"] = "unknown"

st.sidebar.title("⚙️ Blue Controls")
st.sidebar.button("🔄 Refresh Dashboard")

intent_options = ["All"] + sorted(df["intent"].dropna().unique().tolist())
selected_intent = st.sidebar.selectbox("Intent", intent_options)

category_options = ["All"] + sorted(df["category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Category", category_options)

filtered = df.copy()
if selected_intent != "All":
    filtered = filtered[filtered["intent"] == selected_intent]
if selected_category != "All":
    filtered = filtered[filtered["category"] == selected_category]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("<div class='jarvis-card'>", unsafe_allow_html=True)
    st.markdown("### System")
    st.markdown("<span class='status-online'>ONLINE</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='jarvis-card'>", unsafe_allow_html=True)
    st.metric("Total Commands", len(df))
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='jarvis-card'>", unsafe_allow_html=True)
    st.metric("Top Intent", df["intent"].value_counts().idxmax())
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='jarvis-card'>", unsafe_allow_html=True)
    st.metric("Top Category", df["category"].value_counts().idxmax())
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("## 🛰️ Live Command Console")
latest = df.iloc[0]

console_text = f"""[{datetime.now().strftime('%H:%M:%S')}] BLUE SYSTEM ONLINE
Last Command: {latest.get('command', '')}
Intent: {latest.get('intent', '')}
Category: {latest.get('category', '')}
Response: {latest.get('response', '')}
"""

st.markdown(f"<div class='console'><pre>{console_text}</pre></div>", unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    st.markdown("## 📊 Most Used Commands")
    st.bar_chart(filtered["command"].value_counts().head(10))

with right:
    st.markdown("## 🧠 Intent Usage")
    st.bar_chart(filtered["intent"].value_counts())

left2, right2 = st.columns(2)

with left2:
    st.markdown("## 🧩 Category Usage")
    st.bar_chart(filtered["category"].value_counts())

with right2:
    st.markdown("## ⏱️ Commands By Hour")
    hourly = filtered.groupby(filtered["timestamp"].dt.hour).size()
    st.bar_chart(hourly)

st.markdown("## 🔮 Next Command Prediction")
if not filtered.empty:
    prediction = filtered["command"].value_counts().idxmax()
    st.success(f"Blue predicts your next likely command may be: {prediction}")

st.markdown("## 📜 Command Logs")
st.dataframe(filtered.head(50), use_container_width=True)

st.markdown("## 🧬 Memory Core")

if Path(MEMORY_FILE).exists():
    try:
        memory = json.loads(Path(MEMORY_FILE).read_text(encoding="utf-8"))
        mem_col1, mem_col2 = st.columns(2)

        with mem_col1:
            st.markdown("### User Profile")
            st.json({
                "user_name": memory.get("user_name", ""),
                "preferences": memory.get("preferences", {}),
                "last_command": memory.get("last_command", "")
            })

        with mem_col2:
            st.markdown("### Saved Facts")
            facts = memory.get("facts", [])
            if facts:
                for fact in facts[-10:]:
                    st.markdown(f"- {fact}")
            else:
                st.info("No saved facts yet.")
    except Exception as e:
        st.error(f"Could not load memory: {e}")
else:
    st.info("No memory file found.")

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#6ee7ff;'>BLUE 3.0 • Voice AI • Data Science • Automation • ML</p>",
    unsafe_allow_html=True
)

import streamlit as st
import requests
import json

# ==========================================
# 1. 核心設定：直接定義
# ==========================================
# 請在這裡填入你的 AIza... 金鑰
API_KEY = "AIzaSyCIS2bXPy30kmPmq60D_BbBGCxQhX770qQ"

st.set_page_config(page_title="AI 稽核專家", layout="wide")

st.title("🛡️ AI 國際條文稽核儀表板")
st.write("目前連線狀態：測試中")

user_input = st.text_area("請輸入稽核紀錄：", height=150)

if st.button("開始分析"):
    if user_input:
        st.write(f"你輸入了：{user_input}")
        st.info("API 功能稍後接通，先確認網頁能開！")

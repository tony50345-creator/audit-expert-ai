import streamlit as st
import requests
import json

# ==========================================
# 1. 核心設定：請在此貼上你的 API Key
# ==========================================
# 只要改這裡就好，其他都不要動
API_KEY = "AIzaSyCIS2bXPy30kmPmq60D_BbBGCxQhX770qQ"

st.set_page_config(page_title="AI 稽核專家", layout="wide")

# ==========================================
# 2. API 連線函式
# ==========================================
def analyze_data(text):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    prompt = f"""
    你是一位專業稽核員。請分析此事項："{text}"
    請回傳純 JSON 格式，包含以下欄位：
    professional_note, category_id, grade, classification, iso_9001, iatf_16949, vda_63
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            raw_text = res.json()['candidates'][0]['content']['parts'][0]['text']
            # 清除可能出現的 Markdown 標籤
            clean_text = raw_text.replace("```json", "").replace("
```", "").strip()
            return json.loads(clean_text)
        else:
            return f"連線失敗: {res.text}"
    except Exception as e:
        return f"發生錯誤: {str(e)}"

# ==========================================
# 3. 網頁介面
# ==========================================
st.title("🛡️ AI 國際條文稽核儀表板")

user_input = st.text_area("請輸入稽核紀錄：", height=150)

if st.button("開始分析"):
    if user_input:
        with st.spinner("分析中..."):
            result = analyze_data(user_input)
            if isinstance(result, dict):
                st.success("分析完成！")
                st.write(result) # 先用最簡單的方式顯示資料
            else:
                st.error(result)

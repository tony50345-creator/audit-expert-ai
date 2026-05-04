import streamlit as st
import requests
import json
import os

# ==========================================
# 1. 核心設定：金鑰管理 (防撞牆加強版)
# ==========================================
def get_api_key():
    # 做法：先嘗試去抓雲端保險箱，失敗了就用下面這串
    try:
        # 這裡會檢查有沒有 secrets 檔案
        if "GEMINI_KEY" in st.secrets:
            return st.secrets["GEMINI_KEY"]
    except Exception:
        # 如果找不到保險箱檔案，會跳到這裡執行
        pass
    
    # --- [本地測試用] 請在下方 @ 雙引號內貼上你的 AIza... 金鑰 ---
    return "AIzaSyCIS2bXPy30kmPmq60D_BbBGCxQhX770qQ"

# 取得最終使用的金鑰並清除空格
API_KEY = get_api_key().strip()

st.set_page_config(page_title="AI 稽核專家 V2", page_icon="🛡️", layout="wide")

# ==========================================
# 2. 專業稽核邏輯定義 (System Prompt)
# ==========================================
SYSTEM_PROMPT = """
你是一位專精於半導體封測與車用電子供應鏈的稽核大師，背景為 ASE 日月光。
請將「稽核紀錄」轉化為專業、簡明、客觀的 7 欄式稽核報告。

### 判定標準：
1. 缺失等級：Major (嚴重)、Minor (輕微)、OFI (建議改善)、Acceptable (符合)。
2. 標準版本：ISO 9001:2015, IATF 16949:2016, VDA 6.3:2023。
"""

# ==========================================
# 3. API 連線功能 (JSON 模式)
# ==========================================
def analyze_audit_finding(finding):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    instruction = f"""
    分析此事項："{finding}"
    請嚴格回傳 JSON 格式 (不可有引言或 Markdown)：
    {{
      "professional_note": "專業術語筆記",
      "category_id": "編號 (如 A0105)",
      "grade": "Major/Minor/OFI/Acceptable",
      "classification": "不符合分類",
      "iso_9001": "ISO 條文",
      "iatf_16949": "IATF 條文",
      "vda_63": "VDA 6.3 條目"
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n" + instruction}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            content = res.json()['candidates'][0]['content']['parts'][0]['text']
            return json.loads(content)
        else:
            error_msg = res.json().get('error', {}).get('message', '未知錯誤')
            return f"❌ API 錯誤: {error_msg} (代碼: {res.status_code})"
    except Exception as e:
        return f"❌ 系統連線異常: {str(e)}"

# ==========================================
# 4. 網頁介面 UI
# ==========================================
st.title("🛡️ AI 國際條文稽核儀表板")
st.caption("日月光部門專用 - 同步對標 IATF 16949 / ISO 9001 / VDA 6.3")

user_input = st.text_area("✍️ 請輸入稽核紀錄事項：", placeholder="例如：設備校正標籤已過期...", height=120)

if st.button("🚀 開始智慧分析"):
    if not user_input:
        st.warning("請先輸入內容")
    else:
        with st.spinner("正在對標資料庫..."):
            result = analyze_audit_finding(user_input)
            
            if isinstance(result, dict):
                st.divider()
                st.subheader("💡 專家分析報告")
                
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.info("**專業稽核筆記**")
                    st.write(result.get('professional_note'))
                with c2:
                    st.info("**Category ID**")
                    st.code(result.get('category_id'))
                with c3:
                    st.info("**缺失等級**")
                    st.write(result.get('grade'))

                st.divider()
                f1, f2, f3, f4 = st.columns(4)
                with f1: st.write("**不符合分類**\n", result.get('classification'))
                with f2: st.caption(f"**ISO 9001**\n{result.get('iso_9001')}")
                with f3: st.caption(f"**IATF 16949**\n{result.get('iatf_16949')}")
                with f4: st.caption(f"**VDA 6.3**\n{result.get('vda_63')}")
            else:
                st.error(result)

st.divider()
st.caption("⚠️ 本工具由 AI 輔助生成，最終判定請以專業稽核員為準。")

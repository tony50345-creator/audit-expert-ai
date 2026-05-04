import streamlit as st
import requests
import json

# ==========================================
# 1. 核心設定：金鑰管理
# ==========================================
# 浩均大大，請在此貼上你的 AIza... 金鑰 @
API_KEY = "AIzaSyCIS2bXPy30kmPmq60D_BbBGCxQhX770qQ"

st.set_page_config(page_title="AI 國際條文稽核儀表板", page_icon="🛡️", layout="wide")

# ==========================================
# 2. 專業稽核邏輯 (日月光封測與車用標準)
# ==========================================
SYSTEM_PROMPT = """
你是一位專精於半導體封測與車用電子供應鏈的稽核大師。
你的任務是將「稽核紀錄」轉化為專業、簡明、客觀的 7 欄式稽核報告。
請務必對應以下最新版本：
- ISO 9001:2015
- IATF 16949:2016
- VDA 6.3:2023
"""

# ==========================================
# 3. API 連線功能 (移除衝突參數)
# ==========================================
def analyze_audit_finding(finding):
    clean_key = API_KEY.strip()
    # 使用最穩定的 v1 穩定版
    url = f"[https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=){clean_key}"
    
    # 在指令中加強要求 JSON
    instruction = f"""
    分析此稽核事項："{finding}"
    請「僅」回傳一個純 JSON 物件，不准有引言、不准有 Markdown 標籤 (如 ```json)。
    格式必須嚴格如下：
    {{
      "professional_note": "專業術語筆記",
      "category_id": "對標編號 (如 A0105)",
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
            "temperature": 0.1 
            # 這裡移除了 responseMimeType，避免 API 不支援導致報錯
        }
    }
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            # 取得原始文字
            raw_text = res.json()['candidates'][0]['content']['parts'][0]['text']
            
            # 【自動清理器】：萬一 AI 還是加了 ```json 標籤，我們會把它清掉
            clean_text = raw_text.replace('
```json', '').replace('```', '').strip()
            
            return json.loads(clean_text)
        else:
            return f"❌ API 報錯 ({res.status_code}): {res.json().get('error', {}).get('message', '未知錯誤')}"
    except Exception as e:
        return f"❌ 系統異常: {str(e)}"

# ==========================================
# 4. 網頁介面 UI
# ==========================================
st.title("🛡️ AI 國際條文稽核儀表板")
st.caption("日月光 Nanzih 廠部門專用 - 同步對標 IATF 16949 / VDA 6.3")

user_input = st.text_area("✍️ 請輸入稽核紀錄事項：", placeholder="例如：設備校正標籤已過期...", height=120)

if st.button("🚀 開始智慧分析"):
    if not user_input or API_KEY == "這裡貼上你的最新API_KEY":
        st.warning("請輸入內容並確保 API Key 已正確填寫。")
    else:
        with st.spinner("正在進行專業稽核判定..."):
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

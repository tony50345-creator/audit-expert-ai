import streamlit as st
import requests
import json

# ==========================================
# 1. 核心設定：讀取金鑰 (支援雲端 Secrets & 本地)
# ==========================================
if "GEMINI_KEY" in st.secrets:
    # 這裡括號裡面要填的是「標籤名稱」，不是金鑰本身
    API_KEY = st.secrets["GEMINI_KEY"] 
else:
    # 本地測試時，直接把金鑰字串賦值給變數
    API_KEY = "AIzaSyCGIzYkQkxQCUMJr2ips3_pFoWMz7Kk61U" # 建議僅供本地測試

st.set_page_config(page_title="AI 稽核專家 V2", page_icon="🛡️", layout="wide")

# ==========================================
# 2. 定義專業 System Prompt (核心邏輯)
# ==========================================
SYSTEM_PROMPT = """
你是一位專精於 ASE 半導體封測與車用電子供應鏈的稽核大師。
你的任務是將「稽核紀錄事項」轉化為專業的 7 欄式稽核報告。

### 判定準則 (必須嚴格遵守)：
1. 缺失等級定義：
   - Acceptable: 通過沒問題。
   - OFI: 觀察項，非缺失但建議改善。
   - Minor: 規範與執行不符，但不直接影響產品品質。
   - Major: 嚴重違反 IATF/ISO 條文、未告知客戶變更、影響產品品質/可靠度、違反客戶特殊要求、或 VDA 6.3 星號提問為 0/4 分。

2. 最新版本鎖定：
   - ISO 9001: 2015
   - IATF 16949: 2016
   - VDA 6.3: 2023 (聚焦 P2~P7)

3. 專業術語：採用簡明扼要、客觀陳述。

### Category Check Item 比對表 (僅列舉核心類別)：
(AI 必須根據用戶輸入，從 Man/Machine/Material/Method/Environment/Other 中找出最符合的 Category ID，如 A0105, A0301 等)
"""

# ==========================================
# 3. 核心功能函數
# ==========================================
def analyze_audit_finding(finding):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    # 強制要求 JSON 格式輸出，確保排版不會亂掉
    instruction = f"""
    請針對以下稽核發現進行分析："{finding}"
    請回傳 JSON 格式，包含以下鍵值：
    - professional_note: 專業稽核筆記
    - category_id: Category Check Item 編號 (如 A01xx)
    - grade: 缺失等級 (Acceptable/OFI/Minor/Major)
    - classification: 不符合分類
    - iso_9001: 對應條文編號與名稱
    - iatf_16949: 對應條文編號與名稱
    - vda_63: 對應 P2~P7 條目與名稱
    """
    
    payload = {
        "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n" + instruction}]}],
        "generationConfig": {
            "temperature": 0, # 鎖定答案一致性
            "response_mime_type": "application/json"
        }
    }
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            return json.loads(res.json()['candidates'][0]['content']['parts'][0]['text'])
        else:
            return f"Error: {res.status_code}"
    except Exception as e:
        return f"連線異常: {str(e)}"

# ==========================================
# 4. 網頁介面佈局
# ==========================================
st.title("🛡️ AI 國際條文稽核儀表板 (部門專用版)")
st.caption("支援 IATF 16949, ISO 9001:2015, VDA 6.3:2023 最新版分析")

# 輸入區
user_input = st.text_area("✍️ 請輸入稽核紀錄事項：", placeholder="例如：員工 K10748 於 2026/03/03 取得綠色產品認證...", height=150)

if st.button("🚀 開始智慧分析"):
    if not user_input:
        st.warning("請先輸入紀錄內容")
    else:
        with st.spinner("正在對標國際條文並進行風險判定..."):
            result = analyze_audit_finding(user_input)
            
            if isinstance(result, dict):
                st.divider()
                st.subheader("💡 專家分析報告")
                
                # 第一行：專業筆記與分類
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.info("**專業稽核筆記**")
                    st.write(result.get('professional_note'))
                with col2:
                    st.info("**Category ID**")
                    st.code(result.get('category_id'))
                with col3:
                    grade = result.get('grade')
                    st.info("**缺失等級**")
                    # 自動變色邏輯
                    if "Major" in grade: st.error(grade)
                    elif "Minor" in grade: st.warning(grade)
                    else: st.success(grade)

                # 第二行：條文對照
                st.divider()
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown("**不符合分類**")
                    st.write(result.get('classification'))
                with c2:
                    st.markdown("**ISO 9001**")
                    st.caption(result.get('iso_9001'))
                with c3:
                    st.markdown("**IATF 16949**")
                    st.caption(result.get('iatf_16949'))
                with c4:
                    st.markdown("**VDA 6.3**")
                    st.caption(result.get('vda_63'))
            else:
                st.error(result)

# 頁尾說明
st.divider()
st.caption("⚠️ 本工具僅供稽核參考，最終判定請依公司內部規範與稽核員專業判斷為準。")

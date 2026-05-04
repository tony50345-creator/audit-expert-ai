import streamlit as st
import requests
import json

# ==========================================
# 1. 核心設定：金鑰管理
# ==========================================
# 優先讀取雲端 Secrets，沒有則讀取 else 區塊
if "GEMINI_KEY" in st.secrets:
    RAW_KEY = st.secrets["GEMINI_KEY"]
else:
    # [請在此貼上您的最新 API Key]
    RAW_KEY = "AIzaSyCIS2bXPy30kmPmq60D_BbBGCxQhX770qQ" 

# 清除可能誤貼的空格，避免 404 錯誤
API_KEY = RAW_KEY.strip()

st.set_page_config(page_title="AI 稽核專家 V2", page_icon="🛡️", layout="wide")

# ==========================================
# 2. 定義專業 System Prompt (核心邏輯庫)
# ==========================================
SYSTEM_PROMPT = """
你是一位專精於半導體封測與車用電子供應鏈的稽核大師，工作背景為 ASE 日月光。
你的任務是將「稽核紀錄事項」轉化為專業的 7 欄式稽核報告。

### 判定準則：
1. 缺失等級：
   - Acceptable: 通過。
   - OFI: 觀察項，建議改善。
   - Minor: 規範與執行不符，不直接影響品質。
   - Major: 嚴重違反條文、未告知客戶變更、影響產品可靠度、或 VDA 6.3 星號提問 0/4 分。
2. 版本鎖定：ISO 9001:2015, IATF 16949:2016, VDA 6.3:2023。
3. 術語要求：必須使用專業、客觀的稽核術語。

### 參考 Category Check Item 分類 (核心類別)：
- Man (A01xx): 訓練、認證、教育訓練。
- Machine (A02xx-A06xx, A26xx): 設備驗收、PM、治具、校正、MSA、車用專機。
- Material (A07xx-A08xx): 防護、儲存、識別、追溯。
- Method (A09xx-A17xx): 管制計劃、SPC、不合格品處理、客訴、FMEA、文控、變更管制。
- Environment (A18xx-A23xx): 環境監控、無塵室、5S、ESD、GP(綠色產品)、安全。
- Other (A24xx-A25xx): 安全產品(Soteria)、ULA專線。
"""

# ==========================================
# 3. 核心功能函式 (這裡就是你找不到的那段)
# ==========================================
def analyze_audit_finding(finding):
    clean_key = API_KEY.strip()
    
    # 使用 v1 穩定版端點
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={clean_key}"
    
    instruction = f"""
    請分析此稽核事項："{finding}"
    請回傳精確的 JSON 格式 (不可有任何 markdown 標籤或引言)：
    {{
      "professional_note": "改寫後的專業稽核筆記",
      "category_id": "最對標的 Category 編號",
      "grade": "Acceptable/OFI/Minor/Major",
      "classification": "不符合分類名稱",
      "iso_9001": "ISO 9001 條號及名稱",
      "iatf_16949": "IATF 16949 條號及名稱",
      "vda_63": "VDA 6.3 條號及名稱"
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n" + instruction}]}],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json"  # 關鍵修正：這裡改為大寫 M 和 T
        }
    }
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        
        if res.status_code == 200:
            # 取得 AI 回傳的純 JSON 字串
            raw_text = res.json()['candidates'][0]['content']['parts'][0]['text']
            return json.loads(raw_text)
        else:
            # 顯示具體的 API 錯誤原因，方便後續稽核
            error_msg = res.json().get('error', {}).get('message', '未知錯誤')
            return f"❌ API 報錯 ({res.status_code}): {error_msg}"
            
    except Exception as e:
        return f"❌ 連線異常: {str(e)}"

# ==========================================
# 4. 網頁介面
# ==========================================
st.title("🛡️ AI 國際條文稽核儀表板 (日月光部門專用)")
st.caption("同步對應 IATF 16949 / ISO 9001 / VDA 6.3 (2026 最新版)")

user_input = st.text_area("✍️ 請輸入稽核紀錄事項：", placeholder="例如：發現設備 A123 上的校正標籤已過期...", height=150)

if st.button("🚀 開始智慧分析"):
    if not user_input:
        st.warning("請先輸入紀錄內容")
    else:
        with st.spinner("正在對標 Category Check Items 並進行條文判定..."):
            result = analyze_audit_finding(user_input)
            
            if isinstance(result, dict):
                st.divider()
                st.subheader("💡 專家分析報告")
                
                # 第一行：核心判定
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.info("**專業稽核筆記**")
                    st.write(result.get('professional_note'))
                with col2:
                    st.info("**Category ID**")
                    st.code(result.get('category_id'))
                with col3:
                    grade = result.get('grade', 'Acceptable')
                    st.info("**缺失等級**")
                    if "Major" in grade: st.error(grade)
                    elif "Minor" in grade: st.warning(grade)
                    elif "OFI" in grade: st.info(grade)
                    else: st.success(grade)

                # 第二行：法規對照
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

st.divider()
st.caption("⚠️ 本工具由 AI 輔助生成，最終稽核判定請以專業稽核員與公司規範為準。")

import streamlit as st
import requests
import json

# ==========================================
# 1. 核心設定：金鑰管理 (防止本地測試報錯)
# ==========================================
try:
    if "GEMINI_KEY" in st.secrets:
        RAW_KEY = st.secrets["GEMINI_KEY"]
    else:
        # [本地測試用] 請在下方雙引號內貼上你的 AIza... 金鑰
        RAW_KEY = "AIzaSyCIS2bXPy30kmPmq60D_BbBGCxQhX770qQ" 
except Exception:
    # 當在私人電腦執行且找不到 secrets 檔案時，會改用這裡
    RAW_KEY = "AIzaSyCIS2bXPy30kmPmq60D_BbBGCxQhX770qQ"

# 清除隱形空格
API_KEY = RAW_KEY.strip()

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
3. 分類參考 (Category Check Items)：
   - Man (A01xx): 訓練與認證。
   - Machine (A02xx-A06xx, A26xx): 設備、PM、校正、車用專機。
   - Material (A07xx-A08xx): 儲存、追溯。
   - Method (A09xx-A17xx): 管制計劃、SPC、變更管制、文控。
   - Environment (A18xx-A23xx): 5S、ESD、GP(綠色產品)、環境監控。
"""

# ==========================================
# 3. API 連線功能 (支援 JSON 模式)
# ==========================================
def analyze_audit_finding(finding):
    # 使用 v1 穩定版網址
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    instruction = f"""
    分析此事項："{finding}"
    請嚴格回傳 JSON 格式 (不可有 Markdown 標籤)：
    {{
      "professional_note": "專業術語改寫後的筆記",
      "category_id": "對標編號 (如 A0105)",
      "grade": "Major/Minor/OFI/Acceptable",
      "classification": "不符合分類名稱",
      "iso_9001": "ISO 9001 條目",
      "iatf_16949": "IATF 16949 條目",
      "vda_63": "VDA 6.3 P2-P7 條目"
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

# 稽核輸入區
user_input = st.text_area("✍️ 請輸入稽核紀錄事項：", placeholder="例如：設備校正標籤過期、員工認證失效...", height=120)

if st.button("🚀 開始智慧分析"):
    if not user_input:
        st.warning("請先輸入紀錄內容")
    else:
        with st.spinner("正在對標資料庫並產生專業報告..."):
            result = analyze_audit_finding(user_input)
            
            if isinstance(result, dict):
                st.divider()
                st.subheader("💡 專家分析報告")
                
                # 上排：核心分析
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.info("**專業稽核筆記**")
                    st.write(result.get('professional_note'))
                with c2:
                    st.info("**Category ID**")
                    st.code(result.get('category_id'))
                with c3:
                    grade = result.get('grade', 'Acceptable')
                    st.info("**缺失等級**")
                    if "Major" in grade: st.error(grade)
                    elif "Minor" in grade: st.warning(grade)
                    else: st.success(grade)

                # 下排：條文對照
                st.divider()
                f1, f2, f3, f4 = st.columns(4)
                with f1:
                    st.markdown("**不符合分類**")
                    st.write(result.get('classification'))
                with f2:
                    st.markdown("**ISO 9001**")
                    st.caption(result.get('iso_9001'))
                with f3:
                    st.markdown("**IATF 16949**")
                    st.caption(result.get('iatf_16949'))
                with f4:
                    st.markdown("**VDA 6.3**")
                    st.caption(result.get('vda_63'))
            else:
                st.error(result)

st.divider()
st.caption("⚠️ 本工具供 ASE 內部稽核參考，最終判定請以專業稽核員為準。")

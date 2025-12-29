import streamlit as st
import time
from PIL import Image
import io
import json
import warnings

# --- 1. 系統設定與優化 ---
# 忽略 Google 套件的棄用警告，讓介面保持乾淨
warnings.filterwarnings("ignore", category=FutureWarning)

# 嘗試匯入 google.generativeai
try:
    import google.generativeai as genai
    HAS_GENAI_LIB = True
except ImportError:
    HAS_GENAI_LIB = False

# ==========================================
# 2. 核心設定與認證邏輯 (自動化配置)
# ==========================================

def setup_page():
    st.set_page_config(
        page_title="麻將神算子 Pro",
        page_icon="🀄",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    # 自訂 CSS 美化
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa; }
        .main-header { font-size: 2.2rem; color: #2c3e50; text-align: center; font-weight: 700; margin-bottom: 0.5rem; }
        .sub-header { font-size: 1rem; color: #7f8c8d; text-align: center; margin-bottom: 1.5rem; }
        .result-card { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-top: 15px; border-left: 6px solid #2ecc71; }
        .strategy-box { background-color: #ffffff; padding: 15px; border-radius: 10px; margin-bottom: 12px; border: 1px solid #e0e0e0; transition: transform 0.2s; }
        .strategy-box:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .high-score { border-left: 6px solid #e74c3c !important; background-color: #fff5f5 !important; }
        </style>
    """, unsafe_allow_html=True)

def get_api_key():
    """
    自動化配置邏輯：
    1. 優先檢查 Streamlit Secrets (雲端部署用)
    2. 如果沒有，才顯示側邊欄輸入框 (本機測試用)
    """
    api_key = None
    
    # 方法 A: 從 Secrets 讀取 (推薦)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        # 在側邊欄顯示狀態，但不顯示 Key 本身
        with st.sidebar:
            st.success("✅ 系統已自動載入 API Key")
    
    # 方法 B: 如果 Secrets 沒設定，開放手動輸入
    else:
        with st.sidebar:
            st.warning("⚠️ 未檢測到自動配置，請手動輸入")
            api_key = st.text_input("Gemini API Key", type="password")
            
    return api_key

# ==========================================
# 3. AI 邏輯 (Gemini 3.0 pro)
# ==========================================

def clean_json_string(json_str):
    """清除 Markdown 標記，確保 JSON 解析成功"""
    cleaned = json_str.strip()
    if cleaned.startswith("```json"): cleaned = cleaned[7:]
    elif cleaned.startswith("```"): cleaned = cleaned[3:]
    if cleaned.endswith("```"): cleaned = cleaned[:-3]
    return cleaned.strip()

def analyze_mahjong(image, api_key):
    if not HAS_GENAI_LIB:
        return {"error": "系統缺少 google-generativeai 套件，請檢查 requirements.txt"}
    
    try:
        genai.configure(api_key=api_key)
        # 直上 2025 年最強的型號！
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        prompt = """
        Role: Grandmaster of Taiwanese 16-tile Mahjong (台灣十六張麻將神算子).
        
        Task: Analyze the image of the Mahjong hand to provide winning strategies.
        
        # CRITICAL RULES (Taiwanese Mahjong):
        1. Standard hand size is 16 tiles (standing) + 1 drawn tile, or 16 tiles total when waiting.
        2. Ignore "Flowers" (Season/Plant tiles) for hand completion, but count them for bonus if visible.
        3. Differentiate visually similar tiles (e.g., One Bamboo 'bird' vs One Circle).
        4. "White Dragon" (白皮) is a plain white tile with a border.
        
        # ANALYSIS STEPS:
        Step 1 [Identification]: Identify all standing tiles and exposed melds (Chi/Pon/Kang). Count the total tiles to determine if it's the player's turn to discard (17 tiles) or if they are waiting (16 tiles).
        Step 2 [Efficiency]: Calculate 'Shanten' (moves to win).
        Step 3 [Strategy]: 
           - If 17 tiles: Suggest the BEST tile to discard that maximizes "Uke-ire" (number of winning tiles) and "Tai" (Score).
           - If 16 tiles: Identify what tiles the player is waiting for (Ting Pai).
        Step 4 [Scoring]: Estimate 'Tai' (Fan) based on standard Taiwan rules (e.g., Ping Hu, All Triplets, Mixed One Suit).
        
        # OUTPUT FORMAT:
        Output STRICTLY in the following JSON structure. Do NOT output markdown code blocks.
        
        {
            "status": "success",
            "detected_tiles": ["一萬", "二萬", ...], 
            "hand_state": "Need to Discard" or "Waiting (Ting Pai)",
            "strategies": [
                {
                    "tile": "Name of the tile to WAIT FOR (e.g. 三條)",
                    "discard_suggestion": "If having 17 tiles, discard this tile first (e.g. 北風). If waiting, leave null.",
                    "tai": 5, 
                    "types": ["碰碰胡", "三暗刻"], 
                    "comment": "Analysis of why this is the best strategy (win rate vs score)."
                }
            ],
            "analysis": "A concise, professional summary in Traditional Chinese (繁體中文). Mention if the hand is bad (相公) or good."
        }
        """
        
        response = model.generate_content(
            [prompt, image],
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(clean_json_string(response.text))
        
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg and "models/" in error_msg:
            return {"error": "❌ 模型版本錯誤：請確認 requirements.txt 內包含 'google-generativeai>=0.8.3'"}
        return {"error": f"AI 連線失敗: {error_msg}"}

# ==========================================
# 4. 主程式介面 (修正縮排版)
# ==========================================

def main():
    setup_page()
    st.markdown("<div class='main-header'>🀄 麻將神算子 Pro</div>", unsafe_allow_html=True)
    # 這裡幫你把文字更新成 3.0 了
    st.markdown("<div class='sub-header'>Powered by Gemini 3.0 Pro • Vibe Coding Edition</div>", unsafe_allow_html=True)

    # 1. 取得 API Key (自動或手動)
    api_key = get_api_key()

    if not api_key:
        st.info("👈 請在側邊欄輸入 API Key，或設定 Secrets 以啟用自動化功能。")
        st.stop() # 停止執行下方程式碼

    # 2. 圖片輸入區
    upload_type = st.radio(" ", ["📸 拍照辨識", "📂 上傳照片"], horizontal=True, label_visibility="collapsed")
    
    img_file = None
    if upload_type == "📸 拍照辨識":
        img_file = st.camera_input("拍攝手牌")
    else:
        img_file = st.file_uploader("上傳照片", type=['jpg', 'png', 'jpeg'])

    # 3. 分析按鈕與邏輯
    if img_file:
        # 顯示預覽圖
        image = Image.open(img_file)
        st.image(image, caption="分析目標", width="stretch") # 順手修了 width 警告
        
        if st.button("🚀 開始神算 (Analyze)", type="primary", use_container_width=True):
            # 使用 status 顯示進度
            with st.status("🤖 AI 大腦運轉中...", expanded=True) as status:
                st.write("🔍 正在識別牌面...")
                time.sleep(0.5)
                st.write("🧮 計算聽牌機率與台數...")
                
                result = analyze_mahjong(image, api_key)
                
                if "error" in result:
                    status.update(label="❌ 分析失敗", state="error", expanded=True)
                    st.error(result["error"])
                else:
                    status.update(label="✅ 分析完成！", state="complete", expanded=False)
                    
                    # 顯示結果
                    st.markdown(f"""
                    <div class='result-card'>
                        <h4>💡 神算點評</h4>
                        <p>{result.get('analysis', '無分析內容')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.subheader("🎯 聽牌策略推薦")
                    strategies = result.get('strategies', [])
                    
                    if not strategies:
                        st.warning("看不出聽牌，可能是相公或還沒聽。")
                    else:
                        # 排序：台數高的在前面
                        strategies.sort(key=lambda x: x.get('tai', 0), reverse=True)
                        
                        for s in strategies:
                            is_best = (s == strategies[0])
                            css = "strategy-box high-score" if is_best else "strategy-box"
                            badge = "🏆 推薦" if is_best else ""
                            types_str = ', '.join(s.get('types', []))

                            st.markdown(f"""
                            <div class='{css}'>
                                <div style="display: flex; justify_content: space-between; align-items: center;">
                                    <div>
                                        <h3 style="margin:0; color: #e74c3c;">🀄 聽 {s.get('tile')}</h3>
                                        <small style="color: #666;">{types_str}</small>
                                        <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #555;">{s.get('comment')}</p>
                                    </div>
                                    <div style="text-align: right;">
                                        <h2 style="margin:0; color: #2980b9;">{s.get('tai')} 台</h2>
                                        <b style="color: #e74c3c;">{badge}</b>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

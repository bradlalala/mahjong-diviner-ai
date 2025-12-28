import streamlit as st
import time
from PIL import Image
import io
import json

import streamlit as st
import google.generativeai as genai

# === 新增這段檢查代碼 ===
st.warning(f"目前使用的套件版本：{genai.__version__}")
# ======================

# 嘗試匯入 google.generativeai，如果沒安裝則提示
try:
    import google.generativeai as genai
    HAS_GENAI_LIB = True
except ImportError:
    HAS_GENAI_LIB = False

# ==========================================
# 1. 頁面設定與全域樣式
# ==========================================

def setup_page():
    st.set_page_config(
        page_title="AI 麻將神算",
        page_icon="🀄",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    st.markdown("""
        <style>
        .stApp {
            background-color: #f5f7f9;
        }
        .main-header {
            font-size: 2.5rem;
            color: #2c3e50;
            text-align: center;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        .result-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-top: 20px;
            border-left: 5px solid #00c853;
        }
        .strategy-box {
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border: 1px solid #bbdefb;
        }
        .high-score {
            border-left: 5px solid #d32f2f !important;
            background-color: #ffebee !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. AI 核心邏輯 (整合 Gemini API)
# ==========================================

def clean_json_string(json_str):
    """
    [修復 Bug] 清除 Gemini 可能回傳的 Markdown 標記 (```json ... ```)
    """
    cleaned = json_str.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def analyze_mahjong_image(image_input, api_key=None):
    """
    核心 AI 分析函式 - 專注於聽牌策略分析
    """
    
    # 1. 檢查函式庫是否安裝
    if not HAS_GENAI_LIB:
        return {"status": "error", "msg": "缺少 google-generativeai 套件，請執行 pip install google-generativeai"}

    # 2. 檢查 API Key
    if not api_key:
        print("⚠️ 未偵測到 API Key，使用模擬資料模式。")
        time.sleep(1.5)
        # 模擬資料：加入策略分析數據
        return {
            "status": "success",
            "detected_tiles": "測試模式: 1萬 2萬 3萬...",
            "strategies": [
                {"tile": "三條", "tai": 5, "types": ["碰碰胡", "三暗刻"], "comment": "拚大牌首選！"},
                {"tile": "六條", "tai": 1, "types": ["平胡"], "comment": "保守聽牌"}
            ],
            "analysis": "模擬建議：若追求高台數請聽三條，若求穩請聽六條。"
        }

    # 3. 圖片轉檔 (Bytes -> PIL)
    try:
        if isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, io.BytesIO):
             image = Image.open(image_input)
        else:
            image = image_input
    except Exception as e:
        return {"status": "error", "msg": f"圖片讀取失敗: {str(e)}"}

    # 4. 設定 Gemini API
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # 策略分析 Prompt
        prompt = """
        Role: You are an advanced Mahjong AI referee.
        Task: Analyze the image of the standing hand (hand tiles).
        1. Identify the tiles.
        2. Determine what tiles the player is waiting for (Ting Pai).
        3. CRITICAL: For EACH waiting tile, calculate the potential Tai (Score/Fan) assuming that specific tile is won. 
           (e.g., If waiting for '3 Bamboo' completes 'All Triplets', that is higher Tai).
        
        Output Requirement: STRICT JSON format.
        JSON Structure:
        {
            "status": "success",
            "detected_tiles": "list of detected tiles",
            "strategies": [
                { "tile": "Tile Name (e.g. 三條)", "tai": 5, "types": ["Hand Type 1", "Hand Type 2"], "comment": "Brief explanation" },
                { "tile": "Tile Name 2", "tai": 1, "types": ["Hand Type 1"], "comment": "Brief explanation" }
            ],
            "analysis": "Overall strategic advice in Traditional Chinese"
        }
        """

        print(f"🚀 發送 API 請求中 (Strategy Analysis)...")
        response = model.generate_content(
            [prompt, image],
            generation_config={"response_mime_type": "application/json"}
        )
        
        json_text = clean_json_string(response.text)
        result_data = json.loads(json_text)
        
        if "status" not in result_data:
            result_data["status"] = "success"
            
        return result_data

    except Exception as e:
        return {"status": "error", "msg": f"AI 連線錯誤: {str(e)}"}

# ==========================================
# 3. 功能模組 (UI)
# ==========================================

def render_image_uploader(label_key):
    """渲染圖片上傳元件"""
    upload_method = st.radio(
        "選擇輸入方式：", 
        ["📸 拍照", "📂 上傳照片"], 
        horizontal=True,
        key=f"method_{label_key}"
    )
    
    image_data = None
    if upload_method == "📸 拍照":
        image_data = st.camera_input("請拍攝手牌", key=f"cam_{label_key}")
    else:
        image_data = st.file_uploader("請上傳手牌照片", type=['jpg', 'png', 'jpeg'], key=f"file_{label_key}")
        
    return image_data

def page_tenpai_helper(api_key):
    st.markdown("### 🔍 聽牌策略分析")
    st.info("AI 將分析手牌，並告訴您聽哪張牌台數最高！")
    
    image_file = render_image_uploader("tenpai")
    
    if image_file:
        image = Image.open(image_file)
        st.image(image, caption='已載入圖片', use_container_width=True)
        
        if st.button("🧙‍♂️ 開始策略分析", type="primary", use_container_width=True):
            with st.spinner("🤖 AI 正在計算最佳策略..."):
                result = analyze_mahjong_image(image_file, api_key=api_key)
                
            if result.get("status") == "success":
                st.markdown(f"""
                <div class="result-card">
                    <h4>🀄 分析結果</h4>
                    <p style="color: #666;">{result.get('analysis', '')}</p>
                    <hr>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("### 🎯 聽牌選擇與預測台數")
                
                strategies = result.get('strategies', [])
                if not strategies:
                    st.warning("AI 認為目前尚未聽牌，或無法判斷。")
                else:
                    # 找出最高台數，用來標記
                    max_tai = 0
                    for s in strategies:
                        if isinstance(s.get('tai'), int) and s['tai'] > max_tai:
                            max_tai = s['tai']

                    for s in strategies:
                        # 判斷是否為最高台數的選擇
                        is_best = (s.get('tai') == max_tai and max_tai > 0)
                        css_class = "strategy-box high-score" if is_best else "strategy-box"
                        best_badge = "🏆 推薦首選" if is_best else ""
                        
                        types_str = ', '.join(s.get('types', []))
                        
                        st.markdown(f"""
                        <div class="{css_class}">
                            <div style="display: flex; justify_content: space-between; align-items: center;">
                                <div>
                                    <h3 style="margin:0; color: #d32f2f;">🀄 聽：{s.get('tile')}</h3>
                                    <p style="margin:5px 0 0 0; color: #555;">預計台型：{types_str}</p>
                                    <small style="color: #777;">{s.get('comment', '')}</small>
                                </div>
                                <div style="text-align: right;">
                                    <h2 style="margin:0; color: #1976d2;">{s.get('tai')} 台</h2>
                                    <strong style="color: #d32f2f;">{best_badge}</strong>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with st.expander("查看原始數據"):
                    st.json(result)
            else:
                st.error(f"分析失敗：{result.get('msg')}")

def main():
    setup_page()
    st.markdown("<div class='main-header'>🀄 AI 麻將神算</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.header("🔑 設定")
        api_key = st.text_input("Gemini API Key", type="password", placeholder="在此貼上 API Key")
        if not api_key:
            st.warning("請輸入 API Key 才能啟用 AI 功能，否則將使用模擬資料。")
        st.markdown("---")
        st.caption("v2.1 Strategy Only")

    # 移除「胡牌算台」分頁，專注於聽牌策略
    tab1, tab2 = st.tabs(["🔍 聽牌策略分析", "ℹ️ 關於"])
    
    with tab1:
        page_tenpai_helper(api_key)
    with tab2:
        st.markdown("### 關於本專題")
        st.info("整合 Gemini 1.5 Flash 模型，專注於聽牌策略與台數預測。")

if __name__ == "__main__":
    main()

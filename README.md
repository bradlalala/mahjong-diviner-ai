# 🀄 麻將神算子 Pro (Mahjong Diviner AI)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mahjong-diviner-ai.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Gemini AI](https://img.shields.io/badge/AI-Gemini%203.0%20Pro-orange)

> **「拍一下，這把聽什麼？」** —— 專為台灣十六張麻將設計的 AI 視覺辨識輔助工具。

## 📖 專案簡介 (Introduction)
本專案採用 **Vibecoding (AI 輔助編碼)** 模式開發，整合 **Google Gemini** 最新的視覺模型與 **Streamlit** 快速部署架構。

為了解決大學生打麻將時常見的「相公」、「不知聽什麼」或「算錯台數」的痛點，我們開發了這款 App。使用者只需開啟相機拍攝手牌，AI 即可在幾秒內分析牌型，算出聽牌張數與預估台數。

### ✨ 核心功能 (Features)
* 📸 **AI 視覺辨識**：支援手機拍照或上傳照片，自動識別 16 張麻將手牌。
* 🧠 **智慧聽牌分析**：精準判斷目前是否聽牌，並列出所有「聽牌選項」。
* 🔢 **台數計算 (Tai/Fan)**：結合台灣麻將規則，預估胡牌後的牌型與台數（如：碰碰胡、三暗刻）。
* 🇹🇼 **在地化優化**：針對台灣麻將規則（花牌不計入聽牌、白皮辨識等）進行 Prompt 優化。

## 🚀 線上體驗 (Demo)
👉 **點擊立即使用：[麻將神算子 Live App](https://mahjong-diviner-gemini.streamlit.app/)**

*(註：若遇多人使用導致 API 忙碌，請稍候重試)*

## 🛠️ 技術堆疊 (Tech Stack)
* **核心語言**：Python 3.11
* **前端框架**：[Streamlit](https://streamlit.io/)
* **AI 大腦**：Google Gemini 3.0 Pro Preview / 2.5 Pro
* **影像處理**：Pillow (PIL)
* **雲端部署**：Streamlit Cloud

## 💻 本機安裝與執行 (Local Installation)

如果你想在自己的電腦上運行此專案，請按照以下步驟操作：

1.  **複製專案 (Clone Repo)**
    ```bash
    git clone [https://github.com/bradlalala/mahjong-diviner-ai.git](https://github.com/bradlalala/mahjong-diviner-ai.git)
    cd mahjong-diviner-ai
    ```

2.  **安裝依賴套件 (Install Dependencies)**
    *注意：必須鎖定 `google-generativeai` 版本以支援最新模型。*
    ```bash
    pip install -r requirements.txt
    ```

3.  **設定 API Key**
    在專案根目錄建立 `.streamlit/secrets.toml` 檔案，並填入你的 Google AI Studio Key：
    ```toml
    GOOGLE_API_KEY = "你的_API_KEY_貼在這裡"
    ```

4.  **啟動 App**
    ```bash
    streamlit run main.py
    ```

## 🧗 開發挑戰與解決方案 (Challenges & Solutions)

本專案在開發過程中經歷了多次技術迭代，我們克服了以下關鍵挑戰：

| 挑戰 (Challenge) | 解決方案 (Solution) |
| :--- | :--- |
| **☁️ 部署環境 404** | Streamlit Cloud 預設套件過舊。我們透過 `requirements.txt` 強制指定 `google-generativeai==0.8.3` 解決相容性問題。 |
| **⚡ 模型版本迭代** | 舊版 1.5 Flash 偶有誤判。透過 `genai.list_models()` 偵測，我們成功搶先部署了最新的 **Gemini 3.0 Pro Preview** 模型。 |
| **🧠 AI 幻覺** | 初期 AI 誤用日本麻將規則。我們導入 **思維鏈 (Chain of Thought)** Prompt，強制 AI 先計算張數（16 vs 17）再進行策略建議。 |

## 👥 製作團隊 (The Team)
**逢甲大學 vibecoding 計概專案小組**

| 職能 Squad | 成員 |
| :--- | :--- |
| **🟢 A 組 (AI & Logic)** | 蔣承諭 (組長)、陳柏宇 |
| **🔵 B 組 (Frontend & Deploy)** | 蘇志翔、黃宣堯 |
| **🟠 C 組 (Data & Demo)** | 呂定瑜、鄧崴澤 |

## 📄 License
MIT License

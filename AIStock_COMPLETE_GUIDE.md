# 🚀 AIStock 完整使用指南

## 📋 系統概述

AIStock 是一個功能強大的股票分析系統，集成了技術分析、基本面分析、AI智能分析和股票分類功能。本指南涵蓋了系統的所有核心功能，包括股票分類、Gemini AI 智能分析等最新特性。

---

# 📂 第一部分：股票分類功能

## 📋 功能概述

AIStock 現在支持簡單的股票分類功能，讓您可以按行業或主題對股票進行分組，並在報告中按分類顯示。

## 🚀 分類語法

### 基本格式
```bash
python main.py [分類名稱] 股票1 股票2 股票3 [另一個分類] 股票4 股票5 --save-daily-report --GEMINI-API 您的API金鑰
```

### 分類標記
- 使用方括號 `[分類名稱]` 來標記分類
- 分類名稱後面的股票都屬於該分類
- 直到遇到下一個分類標記為止

## 📊 使用示例

### 完整示例
```bash
python main.py [ASIC] AVGO MRVL [CSP] AMAN MSFT GOOGL 9988.HK [SEMI] TSM 2330.HK --save-daily-report --GEMINI-API %GEMINI_API%
```

### 分類結果
- **ASIC**: AVGO, MRVL
- **CSP**: AMAN, MSFT, GOOGL, 9988.HK  
- **SEMI**: TSM, 2330.HK

### 更多示例

#### 按行業分類
```bash
python main.py [科技] AAPL MSFT GOOGL [金融] JPM BAC [能源] XOM CVX --save-daily-report
```

#### 按主題分類
```bash
python main.py [AI] NVDA AMD [電動車] TSLA NIO [雲端] AMZN SNOW --save-daily-report
```

#### 按地區分類
```bash
python main.py [美國] AAPL MSFT [台灣] 2330.TW 2317.TW [香港] 0700.HK 9988.HK --save-daily-report
```

## 🎯 功能特色

### 1. 智能分類解析
- 自動識別 `[分類名稱]` 格式
- 支持中文和英文分類名稱
- 避免重複股票代碼

### 2. 分類導航
- 在報告頂部的股票導航中按分類顯示
- 每個分類有清晰的標題
- 股票按分類分組排列

### 3. 視覺化效果
- 分類標題使用特殊樣式
- 保持原有的信號顏色指示
- 響應式設計，支持手機和電腦

## 📈 報告顯示效果

### 股票導航區域
```
📂 ASIC
  AVGO (買入信號)
  MRVL (持有信號)

📂 CSP  
  AMAN (買入信號)
  MSFT (買入信號)
  GOOGL (持有信號)
  9988.HK (賣出信號)

📂 SEMI
  TSM (買入信號)
  2330.HK (持有信號)
```

### 個股分析區域
- 每個股票的詳細分析保持不變
- 包含技術分析、基本面分析和AI分析
- 按原有順序顯示

## 🔧 技術實現

### 1. 分類解析邏輯
```python
# 檢查是否為分類標記 [CATEGORY]
if symbol_input.startswith('[') and symbol_input.endswith(']'):
    current_category = symbol_input[1:-1]  # 移除方括號
    continue

# 添加到分類中
for symbol in symbol_list:
    if symbol not in symbols:  # 避免重複
        symbols.append(symbol)
        if current_category not in categories:
            categories[current_category] = []
        categories[current_category].append(symbol)
```

### 2. 導航生成
- 按分類組織股票列表
- 為每個分類添加標題
- 保持原有的信號顏色和點擊功能

### 3. 數據傳遞
- 分類信息從 main.py 傳遞到 visualizer.py
- 每個股票結果包含分類信息
- 支持向後兼容（無分類時正常顯示）

## 📝 使用技巧

### 1. 分類命名建議
- 使用簡潔明瞭的名稱
- 支持中文和英文
- 建議使用 2-10 個字符

### 2. 股票組織建議
- 按行業分類：`[科技]` `[金融]` `[能源]`
- 按主題分類：`[AI]` `[電動車]` `[雲端]`
- 按地區分類：`[美國]` `[台灣]` `[香港]`
- 按策略分類：`[成長股]` `[價值股]` `[股息股]`

### 3. 命令行技巧
- 使用環境變數存儲API金鑰
- 可以將常用股票組合保存為腳本
- 支持混合使用分類和未分類股票

## ⚠️ 注意事項

### 1. 分類規則
- 分類標記必須使用方括號 `[]`
- 分類名稱不能包含方括號
- 股票代碼會自動轉為大寫

### 2. 重複處理
- 系統會自動避免重複的股票代碼
- 如果同一股票出現在多個分類中，只會顯示一次

### 3. 向後兼容
- 不使用分類標記時，功能完全正常
- 所有現有的命令行參數都保持不變

---

# 🤖 第二部分：Gemini AI 集成功能

## 📋 功能概述

AIStock 現在支持 Gemini AI 智能分析功能，為每日報告增加 AI 建議。當您提供 Gemini API 金鑰時，系統會自動為每支股票生成 AI 分析建議。

## 🚀 新增功能

### 1. AI 智能分析面板
- **AI 情緒分析**: 看漲/看跌/中性
- **AI 投資建議**: 買入/持有/賣出
- **目標價格預測**: AI 預測的目標價格
- **信心等級**: 高/中/低
- **風險等級**: 低/中/高

### 2. 未來成長賽道分析
- **主要成長賽道**: AI 識別的核心成長領域
- **潛在收購目標**: AI 預測的可能收購目標
- **複合成長率預測**: 1年/3年/5年 EPS 和股價 CAGR
- **新賽道營收佔比**: 3年/5年後新業務營收佔比

### 3. AI 統計摘要
- **AI 買入/賣出/持有統計**: 基於 AI 建議的統計
- **看漲/看跌情緒統計**: 基於 AI 情緒分析的統計

## 🔧 使用方法

### 基本語法
```bash
python main.py 股票代碼 --save-daily-report --GEMINI-API 您的API金鑰
```

### 完整示例
```bash
python main.py 2330.TW 2317.TW 2382.TW 3231.TW 2308.TW 2454.TW 3706.TW 3019.TW AAPL AMZN GOOGL META MSFT NVDA TSLA TSM AVGO MRVL UNH MU PANW CRWD TEM VST 0388.HK 0700.HK 9988.HK 2628.HK --save-daily-report --GEMINI-API %GEMINI_API%
```

### 參數說明
- `股票代碼`: 支援多個股票代碼，用空格分隔
- `--save-daily-report`: 生成每日報告（必需）
- `--GEMINI-API`: Gemini API 金鑰（可選，不提供則不啟用 AI 功能）

## 📊 報告內容

### 1. 摘要統計區域
新增 **🤖 Gemini AI 摘要** 面板，顯示：
- AI 買入/賣出/持有建議統計
- 看漲/看跌情緒統計

### 2. 個股分析區域
每支股票新增 **🤖 Gemini AI 智能分析** 面板，包含：

#### 基本分析
- AI 情緒: 看漲/看跌/中性
- AI 建議: 買入/持有/賣出
- 目標價格: AI 預測的目標價
- 信心等級: 高/中/低
- 風險等級: 低/中/高

#### 成長賽道分析
- **主要成長賽道**: 列出前3個主要成長領域
- **潛在收購目標**: 列出前3個可能的收購目標

#### 複合成長率預測
- **EPS CAGR**: 1年/3年/5年每股盈餘複合成長率
- **股價CAGR**: 1年/3年/5年股價複合成長率

#### 新賽道營收佔比
- **3年後**: 新賽道在總營收中的佔比
- **5年後**: 新賽道在總營收中的佔比

## 🎯 AI 分析特色

### 1. 五個核心維度
Gemini AI 專注於五個核心分析維度：
1. **未來潛在的重大收購以及成長賽道**
2. **新賽道的預計複合成長率**
3. **新賽道的營收及獲利佔比**
4. **未來1/3/5年的EPS複合成長率**
5. **未來1/3/5年股價複合成長率**

### 2. 通用AI賽道分析
適用於所有公司的AI發展方向分析，包括：
- **AI基礎設施與技術**: 收購LLM公司、雲擴展、AI電力等
- **AI應用領域**: AI醫療、AI機器人、AI XR眼鏡等
- **AI金融與數字資產**: AI金融、穩定幣、加密貨幣等
- **AI垂直整合**: AI教育、AI娛樂、AI零售等
- **AI效率提升**: AI客服、AI研發、AI營銷等

### 3. 完全中文化
所有 AI 分析結果都以中文表達，便於理解。

## ⚙️ 技術特點

### 1. 智能延遲控制
- 每次 AI 分析之間自動延遲 3 秒
- 避免觸發 API 頻率限制

### 2. 錯誤處理
- 完整的錯誤處理機制
- 即使 AI 分析失敗，不影響其他功能

### 3. 響應式設計
- AI 面板採用漸變背景設計
- 與現有界面完美融合

## 📝 注意事項

### 1. API 金鑰安全
- 不要在代碼中硬編碼 API 金鑰
- 建議使用環境變數 `%GEMINI_API%`
- 定期輪換 API 金鑰

### 2. 使用限制
- 注意 Gemini API 的調用頻率限制
- 大量股票分析時會自動延遲

### 3. 分析結果
- AI 分析結果僅供參考
- 不構成投資建議
- 投資有風險，決策需謹慎

---

# 🤖 第三部分：Gemini AI 股票分析器完整文檔

## 📋 功能概述

Gemini AI 股票分析器是一個基於 Google Gemini API 的智能股票分析工具，提供全面、深度的投資分析功能。該模組專注於五個核心維度，提供更精準、更實用的投資分析結果。

### 🎯 核心特色
- **AI 驅動分析**: 使用 Google Gemini 1.5 Flash 模型進行智能分析
- **五個核心維度**: 專注於投資者最關心的成長驅動力
- **通用AI賽道分析**: 適用於所有公司的AI發展方向分析
- **結構化輸出**: 統一的 JSON 格式便於後續處理
- **完全中文化**: 所有分析結果都以中文表達
- **獨立模組**: 不依賴其他代碼，可單獨使用

## 🚀 五個核心分析維度

### 1. 未來潛在的重大收購以及成長賽道
- **潛在收購目標**: 分析公司可能收購的目標企業和戰略意義
- **主要成長賽道**: 識別公司的核心成長領域和市場規模
- **競爭優勢**: 評估在新賽道中的競爭地位
- **戰略合作**: 分析潛在的合作和聯盟機會

### 2. 新賽道的預計複合成長率
- **三年複合成長率**: 各成長賽道的三年 CAGR 預測
- **五年複合成長率**: 各成長賽道的五年 CAGR 預測
- **市場滲透率**: 分析市場採用速度和滲透潛力
- **商業化時間表**: 評估技術成熟度和商業化進程

### 3. 新賽道的營收及獲利佔比
- **營收佔比預測**: 各賽道在總營收中的佔比變化
- **利潤率貢獻**: 新賽道對整體利潤率的影響
- **營收結構轉型**: 分析營收結構的轉型時間表
- **獲利質量改善**: 評估獲利質量的提升潛力

### 4. 未來1/3/5年的EPS複合成長率
- **一年EPS CAGR**: 基於短期發展的EPS成長預測
- **三年EPS CAGR**: 基於中期發展的EPS成長預測
- **五年EPS CAGR**: 基於長期發展的EPS成長預測
- **情境分析**: 提供樂觀、中性、保守三種情境的預測

### 5. 未來1/3/5年股價複合成長率
- **一年股價CAGR**: 短期股價成長預測
- **三年股價CAGR**: 中期股價成長預測
- **五年股價CAGR**: 長期股價成長預測
- **估值倍數擴張**: 分析估值倍數擴張的可能性

## 🎯 通用AI賽道分析

### 未來五年營收動力分析 - 基於AI改革的二十個核心發展方向：

#### 1. AI基礎設施與技術
- **收購LLM公司**: 評估收購大型語言模型初創公司的戰略價值和整合潛力
- **雲擴展**: AI雲服務的市場擴張和企業採用率提升
- **AI電力**: AI優化的電力管理和智能電網技術
- **推論ASIC**: 專用AI推理晶片的開發和商業化
- **資料中心+推論中心ASIC化**: 數據中心向AI專用架構轉型

#### 2. AI應用領域
- **AI醫療**: 醫療診斷、藥物研發、個性化治療的AI應用
- **AI機器人**: 工業自動化、服務機器人、人形機器人技術
- **AI XR眼鏡**: 增強現實和虛擬現實的AI整合應用
- **ROBOTAXI與機器人**: 自動駕駛計程車和機器人服務
- **產線進一步自動化**: 製造業的AI驅動自動化升級

#### 3. AI金融與數字資產
- **AI金融**: 智能投顧、風險管理、欺詐檢測的AI應用
- **穩定幣**: AI驅動的穩定幣算法和監管技術
- **加密貨幣**: AI在加密貨幣交易和區塊鏈技術中的應用

#### 4. AI垂直整合
- **AI教育**: 個性化學習、智能輔導、教育內容生成
- **AI娛樂**: 內容創作、遊戲AI、娛樂體驗個性化
- **AI零售**: 智能推薦、庫存管理、客戶服務自動化
- **AI物流**: 供應鏈優化、配送路線規劃、倉儲自動化
- **AI農業**: 精準農業、作物監控、農業機器人

#### 5. AI效率提升
- **AI客服**: 智能客服系統和客戶體驗優化
- **AI研發**: 研發流程自動化和創新加速
- **AI營銷**: 精準營銷、內容生成、市場分析
- **AI法務**: 法律文檔分析、合規監控、智能合約

## 📊 精簡版 JSON 結構

```json
{
  "symbol": "股票代碼",
  "analysis_summary": {
    "overall_sentiment": "看漲/看跌/中性",
    "confidence_level": "高/中/低",
    "risk_level": "低/中/高",
    "time_horizon": "短期/中期/長期"
  },
  "future_acquisitions_and_growth_tracks": {
    "potential_major_acquisitions": ["潛在收購目標1", "潛在收購目標2", "潛在收購目標3"],
    "acquisition_strategic_importance": "收購的戰略意義和影響分析",
    "primary_growth_tracks": ["主要成長賽道1", "主要成長賽道2", "主要成長賽道3"],
    "growth_track_market_size": "成長賽道市場規模預估",
    "competitive_advantages": ["競爭優勢1", "競爭優勢2", "競爭優勢3"],
    "strategic_partnerships": ["戰略合作1", "戰略合作2"]
  },
  "growth_track_cagr": {
    "track_1_cagr_3y": "成長賽道1三年複合成長率（百分比）",
    "track_1_cagr_5y": "成長賽道1五年複合成長率（百分比）",
    "track_2_cagr_3y": "成長賽道2三年複合成長率（百分比）",
    "track_2_cagr_5y": "成長賽道2五年複合成長率（百分比）",
    "track_3_cagr_3y": "成長賽道3三年複合成長率（百分比）",
    "track_3_cagr_5y": "成長賽道3五年複合成長率（百分比）",
    "market_penetration_analysis": "市場滲透率分析",
    "commercialization_timeline": "商業化時間表",
    "growth_catalysts": ["成長催化劑1", "成長催化劑2", "成長催化劑3"]
  },
  "revenue_profit_contribution": {
    "track_1_revenue_share_3y": "成長賽道1三年後營收佔比（百分比）",
    "track_1_revenue_share_5y": "成長賽道1五年後營收佔比（百分比）",
    "track_2_revenue_share_3y": "成長賽道2三年後營收佔比（百分比）",
    "track_2_revenue_share_5y": "成長賽道2五年後營收佔比（百分比）",
    "track_3_revenue_share_3y": "成長賽道3三年後營收佔比（百分比）",
    "track_3_revenue_share_5y": "成長賽道3五年後營收佔比（百分比）",
    "profit_contribution_analysis": "新賽道利潤率貢獻分析",
    "revenue_structure_transformation": "營收結構轉型時間表",
    "profit_quality_improvement": "獲利質量改善潛力"
  },
  "eps_cagr_forecast": {
    "eps_cagr_1y": "一年EPS複合成長率（百分比）",
    "eps_cagr_3y": "三年EPS複合成長率（百分比）",
    "eps_cagr_5y": "五年EPS複合成長率（百分比）",
    "eps_growth_drivers": ["EPS成長驅動力1", "EPS成長驅動力2", "EPS成長驅動力3"],
    "profit_margin_expansion": "利潤率擴張預期",
    "capex_rd_impact": "資本支出和研發投入影響",
    "eps_scenarios": {
      "bull_case_eps_cagr": "樂觀情境EPS複合成長率",
      "base_case_eps_cagr": "中性情境EPS複合成長率",
      "bear_case_eps_cagr": "保守情境EPS複合成長率"
    }
  },
  "stock_price_cagr_forecast": {
    "price_cagr_1y": "一年股價複合成長率（百分比）",
    "price_cagr_3y": "三年股價複合成長率（百分比）",
    "price_cagr_5y": "五年股價複合成長率（百分比）",
    "valuation_multiple_expansion": "估值倍數擴張可能性",
    "market_sentiment_impact": "市場情緒和投資者認知變化",
    "risk_adjusted_growth": "風險調整後股價成長預期",
    "price_scenarios": {
      "bull_case_price_cagr": "樂觀情境股價複合成長率",
      "base_case_price_cagr": "中性情境股價複合成長率",
      "bear_case_price_cagr": "保守情境股價複合成長率"
    }
  },
  "investment_recommendation": {
    "action": "買入/持有/賣出",
    "conviction_level": "高/中/低",
    "target_price": "具體價格",
    "time_horizon": "短期/中期/長期"
  }
}
```

## 🔧 安裝和設置

### 1. 安裝依賴
```bash
pip install requests
```

### 2. 獲取 Gemini API 金鑰
1. 訪問 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 創建新的 API 金鑰
3. 複製 API 金鑰

### 3. 基本使用
```python
# 從 src 目錄導入
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from gemini import GeminiStockAnalyzer

# 創建分析器實例
analyzer = GeminiStockAnalyzer("your_api_key_here")

# 分析股票
result = analyzer.analyze_stock(
    symbol="AAPL",
    current_price=150.0,
    company_name="Apple Inc."
)

# 檢查分析結果
if result.get('metadata', {}).get('status') == 'success':
    # 獲取未來收購和成長賽道
    acquisitions = result.get('future_acquisitions_and_growth_tracks', {})
    potential_buys = acquisitions.get('potential_major_acquisitions', [])
    
    # 獲取EPS CAGR預測
    eps_forecast = result.get('eps_cagr_forecast', {})
    eps_3y = eps_forecast.get('eps_cagr_3y', 'N/A')
    
    # 獲取股價CAGR預測
    price_forecast = result.get('stock_price_cagr_forecast', {})
    price_3y = price_forecast.get('price_cagr_3y', 'N/A')
    
    print(f"潛在收購: {potential_buys}")
    print(f"三年EPS CAGR: {eps_3y}")
    print(f"三年股價CAGR: {price_3y}")
```

## 🧪 測試方法

### 1. 整合測試
```bash
# 運行所有測試（包括Gemini測試）
python test_all.py --all

# 只運行Gemini AI分析測試
python test_all.py --gemini-analysis
```

### 2. 測試重點
- 五個核心維度的分析準確性
- AI賽道分析的適用性
- JSON格式輸出的正確性
- 中文表達的準確性

## 📊 公司特定分析重點

### Apple (AAPL)
- **AI收購**: Perplexity AI、Anthropic等AI初創公司
- **服務業務**: Apple Music、iCloud、Apple Pay、App Store
- **AR/VR**: Vision Pro在企業和消費市場的應用
- **健康科技**: Apple Watch和健康相關服務

### Tesla (TSLA)
- **Robotaxi**: 自動駕駛計程車業務的技術進展和商業化
- **人形機器人**: Optimus在製造業和服務業的應用
- **能源業務**: 太陽能和儲能業務的市場擴張
- **自動駕駛**: FSD技術成熟度和Robotaxi時間表

### NVIDIA (NVDA)
- **AI晶片**: 大型語言模型訓練和推理的晶片需求
- **數據中心**: 雲端服務商的AI基礎設施投資
- **汽車晶片**: 自動駕駛和電動車的晶片需求
- **軟體生態**: CUDA生態系統和AI軟體的商業化

### Google (GOOGL)
- **AI競賽地位**: 與OpenAI、Microsoft的競爭態勢
- **Gemini模型發展**: 技術進展和商業化應用
- **雲端業務競爭**: 與AWS、Azure的競爭策略
- **廣告業務轉型**: 隱私保護趨勢下的適應策略

### Microsoft (MSFT)
- **AI整合戰略**: 將AI整合到所有產品線的策略
- **OpenAI合作**: 深度合作關係和投資回報
- **雲端業務領導**: Azure在雲端市場的競爭優勢
- **企業軟體轉型**: Office 365、Teams的AI升級

### Amazon (AMZN)
- **AWS雲端業務**: 在雲端市場的競爭地位
- **電商業務轉型**: 電商市場的競爭策略
- **AI服務發展**: Amazon Bedrock、AI工具發展
- **廣告業務成長**: 廣告業務的成長潛力

## 🔍 精簡版的優勢

### 1. 專注核心
- 移除了冗長的傳統技術和基本面分析
- 專注於投資者最關心的成長驅動力
- 提供更精準的未來發展預測

### 2. 實用性強
- 直接回答投資決策的關鍵問題
- 提供具體的數值預測和時間表
- 包含樂觀、中性、保守三種情境

### 3. 易於理解
- 結構化的五個核心維度
- 清晰的JSON格式輸出
- 中文表達，便於理解

### 4. 前瞻性強
- 重點分析未來潛在收購
- 預測新賽道的發展潛力
- 評估長期成長驅動力

## 📈 與原版對比

| 維度 | 原版 | 精簡版 |
|------|------|--------|
| 分析維度 | 10+ 個複雜維度 | 5 個核心維度 |
| 社群情緒 | 詳細分析 | 簡化處理 |
| 財報分析 | 深度分析 | 聚焦成長 |
| 技術分析 | 詳細指標 | 移除 |
| 成長賽道 | 一般分析 | 重點分析 |
| 收購預測 | 簡單提及 | 詳細分析 |
| CAGR預測 | 基本預測 | 多維度預測 |
| 情境分析 | 單一預測 | 三種情境 |

## 🎯 適用場景

### 1. 成長股投資
- 識別高成長潛力的公司
- 評估新賽道的發展前景
- 預測未來收購機會

### 2. 長期投資
- 分析5年成長潛力
- 評估公司轉型能力
- 預測估值倍數變化

### 3. 戰略投資
- 分析公司戰略方向
- 評估競爭優勢變化
- 預測市場地位演變

### 4. 風險管理
- 提供三種情境預測
- 評估成長風險
- 分析競爭威脅

## 🔧 技術特點

### 1. 智能提示詞
- 針對不同公司的特定分析重點
- 專注於未來發展和成長潛力
- 避免重複性分析內容

### 2. 結構化輸出
- 統一的JSON格式
- 清晰的數據結構
- 便於程序化處理

### 3. 錯誤處理
- 多層JSON修復機制
- 備用分析結構
- 詳細錯誤日誌

### 4. 中文輸出
- 所有分析結果使用中文
- 便於中文投資者理解
- 符合本地化需求

## 📝 注意事項

1. **API限制**: 注意Gemini API的調用頻率限制
2. **數據準確性**: AI分析結果僅供參考，不構成投資建議
3. **市場變化**: 分析基於當前市場情況，需要定期更新
4. **風險提示**: 投資有風險，決策需謹慎

## 🚀 未來改進

1. **更多公司**: 擴展到更多股票的分析重點
2. **實時數據**: 整合實時市場數據
3. **歷史對比**: 添加歷史預測準確性分析
4. **視覺化**: 提供圖表化分析結果
5. **批量分析**: 支持批量股票分析功能

## 📁 項目結構

### 文件位置
```
AIStock/
├── src/
│   └── gemini.py                # Gemini AI 分析器 ⭐
├── test_all.py                  # 整合測試程序（包含Gemini測試）
└── gemini.md                    # 完整文檔（當前文件）
```

### 導入方式
```python
# 推薦方式：從 src 目錄導入
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from gemini import GeminiStockAnalyzer
```

## 🎯 實現成果

### 主要成就
1. **成功集成 Gemini API**: 使用最新的 gemini-1.5-flash 模型
2. **五個核心維度**: 專注於投資者最關心的分析維度
3. **通用AI賽道分析**: 適用於所有公司的AI發展方向
4. **自定義 JSON 格式**: 結構化的分析結果便於後續處理
5. **完整的錯誤處理**: 健壯的異常處理機制
6. **獨立模組設計**: 不依賴其他代碼，可單獨使用

### 技術亮點
1. **現代 API 設計**: RESTful API 調用
2. **智能提示詞**: 精心設計的分析框架
3. **結構化輸出**: 統一的 JSON 格式
4. **日誌記錄**: 完整的操作追蹤
5. **中文輸出**: 完全中文化的分析結果

### 用戶價值
1. **智能分析**: AI 驅動的股票分析
2. **實用建議**: 具體的投資建議和風險管理
3. **易於集成**: 簡單的 API 調用
4. **可擴展性**: 模組化設計便於擴展
5. **本地化**: 中文表達，便於理解

## 🔮 未來擴展

### 計劃功能
- [ ] 實時市場數據整合
- [ ] 歷史分析結果比較
- [ ] 投資組合優化建議
- [ ] 風險管理工具
- [ ] 多語言支持

### 技術改進
- [ ] 更精確的提示詞工程
- [ ] 自適應分析參數
- [ ] 機器學習模型整合
- [ ] 預測準確性評估

## 📞 支持和反饋

如果您在使用過程中遇到問題或有改進建議，請：

1. 檢查錯誤日誌
2. 驗證 API 金鑰有效性
3. 確認網絡連接正常
4. 查看 API 使用限制

## 📄 授權和許可

本模組僅供學習和研究使用，請遵守：
- Google Gemini API 使用條款
- 相關金融法規
- 數據隱私保護規定

---

# 🎯 完整使用示例

## 📋 基本使用流程

### 1. 設置環境
```bash
# 設置環境變數
set GEMINI_API=您的API金鑰
```

### 2. 運行完整分析（包含分類和AI）
```bash
python main.py [ASIC] AVGO MRVL [CSP] AMAN MSFT GOOGL 9988.HK [SEMI] TSM 2330.HK --save-daily-report --GEMINI-API %GEMINI_API%
```

### 3. 查看結果
- 生成的HTML報告會按分類組織股票
- 導航區域顯示分類標題和股票列表
- 每個股票包含完整的技術分析、基本面分析和AI分析

## 🔮 未來發展

### 計劃功能
- [ ] 支持嵌套分類
- [ ] 分類統計摘要
- [ ] 按分類的批量操作
- [ ] 分類模板保存和載入
- [ ] 實時市場數據整合
- [ ] 歷史 AI 分析結果比較
- [ ] 投資組合優化建議
- [ ] 風險管理工具
- [ ] 多語言支持

### 技術改進
- [ ] 更豐富的分類樣式
- [ ] 分類篩選功能
- [ ] 分類比較分析
- [ ] 自定義分類圖標
- [ ] 更精確的提示詞工程
- [ ] 自適應分析參數
- [ ] 機器學習模型整合
- [ ] 預測準確性評估

---

**🎯 AIStock 完整功能已成功實現！**
**📂 股票分類功能讓您的分析更有條理！**
**🤖 Gemini AI 智能分析提供專業建議！**
**📊 結合技術分析、基本面分析和 AI 智能分析！**
**🚀 為您的投資決策提供全方位的專業支持！**

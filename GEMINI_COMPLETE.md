# 🤖 Gemini AI 股票分析器 - 完整文檔

## 📋 功能概述

Gemini AI 股票分析器是一個獨立的模組，使用 Google Gemini API 進行智能股票分析和投資建議。該模組提供結構化的 JSON 格式分析結果，包含基本面分析、技術分析、投資建議等詳細信息。

### 🎯 核心特色
- **AI 驅動分析**: 使用 Google Gemini 1.5 Flash 模型進行智能分析
- **多維度評估**: 基本面、技術面、市場環境全方位分析
- **結構化輸出**: 統一的 JSON 格式便於後續處理
- **實用建議**: 具體的投資建議和風險管理策略
- **獨立模組**: 不依賴其他代碼，可單獨使用

## 🚀 主要功能

### 📊 股票分析
- **基本面分析**: 公司實力、財務健康、增長潛力評估
- **技術分析**: 趨勢方向、支撐阻力位、技術指標信號
- **投資建議**: 買入/持有/賣出建議、目標價格、止損位
- **風險評估**: 風險等級、信心等級、時間週期
- **市場環境**: 行業前景、市場情緒、經濟因素
- **詳細推理**: 看漲/看跌/中性因素分析

### 📰 新聞分析
- **新聞情緒分析**: 正面/負面/中性新聞分類
- **事件影響評估**: 重要事件對股價的影響分析
- **市場反應預測**: 基於新聞的市場反應預測

### 🎯 自定義 JSON 格式
- **結構化數據**: 統一的 JSON 格式便於後續處理
- **詳細分類**: 多維度的分析結果分類
- **元數據**: 包含分析時間、API 來源等元信息

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
# 從 src 目錄導入（推薦方式）
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

# 查看結果
print(result)
```

## 📊 API 響應格式

### 股票分析響應格式
```json
{
    "symbol": "AAPL",
    "analysis_summary": {
        "overall_sentiment": "bullish/bearish/neutral",
        "confidence_level": "high/medium/low",
        "risk_level": "low/medium/high",
        "time_horizon": "short_term/medium_term/long_term"
    },
    "fundamental_analysis": {
        "company_strength": "strong/moderate/weak",
        "financial_health": "excellent/good/fair/poor",
        "growth_potential": "high/medium/low",
        "competitive_position": "strong/moderate/weak",
        "key_strengths": ["創新能力強", "品牌價值高", "現金流充足"],
        "key_risks": ["供應鏈風險", "監管風險", "競爭加劇"]
    },
    "technical_analysis": {
        "trend_direction": "uptrend/downtrend/sideways",
        "support_level": "145.0",
        "resistance_level": "160.0",
        "technical_indicators": {
            "rsi_signal": "oversold/neutral/overbought",
            "macd_signal": "bullish/bearish/neutral",
            "moving_averages": "bullish/bearish/neutral"
        }
    },
    "investment_recommendation": {
        "action": "buy/hold/sell",
        "target_price": "175.0",
        "stop_loss": "140.0",
        "position_size": "small/medium/large",
        "entry_strategy": "立即買入/等待回調/分批建倉",
        "exit_strategy": "長期持有/設定止盈/技術止損"
    },
    "market_context": {
        "sector_outlook": "positive/neutral/negative",
        "market_sentiment": "bullish/bearish/neutral",
        "economic_factors": ["利率環境", "通脹預期"],
        "sector_trends": ["科技股強勢", "消費升級"]
    },
    "detailed_reasoning": {
        "bullish_factors": ["強勁的產品線", "服務收入增長", "回購計劃"],
        "bearish_factors": ["估值偏高", "供應鏈問題"],
        "neutral_factors": ["市場波動", "宏觀不確定性"],
        "key_insights": ["長期投資價值", "創新驅動增長", "財務穩健"]
    },
    "metadata": {
        "symbol": "AAPL",
        "analysis_date": "2024-01-15T10:30:00",
        "api_source": "gemini",
        "status": "success"
    }
}
```

### 新聞分析響應格式
```json
{
    "symbol": "AAPL",
    "news_analysis": {
        "overall_sentiment": "positive/negative/neutral",
        "news_impact": "high/medium/low",
        "key_events": ["新產品發布", "財報超預期"],
        "market_reaction": "股價上漲預期"
    },
    "recent_developments": [
        {
            "event": "iPhone 15 銷量超預期",
            "impact": "positive/negative/neutral",
            "significance": "high/medium/low",
            "description": "新產品銷售表現強勁，超出市場預期"
        }
    ],
    "sentiment_breakdown": {
        "positive_news": ["新產品成功", "服務收入增長"],
        "negative_news": ["供應鏈延遲"],
        "neutral_news": ["市場分析報告"]
    },
    "metadata": {
        "symbol": "AAPL",
        "analysis_date": "2024-01-15T10:30:00",
        "api_source": "gemini",
        "analysis_type": "news",
        "status": "success"
    }
}
```

## 🧪 測試和驗證

### 基本功能測試
```bash
# 直接運行 gemini.py 進行測試
python src/gemini.py
```

### 測試說明
- 運行測試時會提示輸入 Gemini API 金鑰
- 測試會分析多支股票並生成分析結果
- 分析結果會保存為 JSON 格式文件

## 📈 使用範例

### 範例 1: 基本股票分析
```python
from gemini import GeminiStockAnalyzer

# 創建分析器
analyzer = GeminiStockAnalyzer("your_api_key")

# 分析股票
result = analyzer.analyze_stock("AAPL", 150.0, "Apple Inc.")

# 提取關鍵信息
if result.get('metadata', {}).get('status') == 'success':
    analysis = result['analysis_summary']
    recommendation = result['investment_recommendation']
    
    print(f"整體情緒: {analysis['overall_sentiment']}")
    print(f"建議動作: {recommendation['action']}")
    print(f"目標價格: {recommendation['target_price']}")
```

### 範例 2: 新聞分析
```python
# 分析股票相關新聞
news_result = analyzer.get_stock_news_analysis("AAPL")

if news_result.get('metadata', {}).get('status') == 'success':
    news_analysis = news_result['news_analysis']
    print(f"新聞情緒: {news_analysis['overall_sentiment']}")
    print(f"影響程度: {news_analysis['news_impact']}")
```

### 範例 3: 批量分析
```python
stocks = [
    {"symbol": "AAPL", "price": 150.0, "name": "Apple Inc."},
    {"symbol": "GOOGL", "price": 2800.0, "name": "Alphabet Inc."},
    {"symbol": "MSFT", "price": 350.0, "name": "Microsoft Corp."}
]

results = []
for stock in stocks:
    result = analyzer.analyze_stock(
        symbol=stock['symbol'],
        current_price=stock['price'],
        company_name=stock['name']
    )
    results.append(result)
    
    # 避免 API 限制
    time.sleep(3)
```

## ⚙️ 配置選項

### API 配置
```python
analyzer = GeminiStockAnalyzer(api_key)

# 可調整的生成配置
payload = {
    "generationConfig": {
        "temperature": 0.7,      # 創造性 (0.0-1.0)
        "topK": 40,             # 詞彙選擇範圍
        "topP": 0.95,           # 核採樣
        "maxOutputTokens": 2048  # 最大輸出長度
    }
}
```

### 錯誤處理
```python
result = analyzer.analyze_stock("INVALID")

if result.get('metadata', {}).get('status') == 'error':
    error_msg = result['error']['message']
    print(f"分析失敗: {error_msg}")
```

## 🔧 技術實現

### API 端點和模型
```python
# 使用最新的 Gemini 1.5 Flash 模型
base_url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
```

### 錯誤處理機制
```python
def _create_error_response(self, error_message: str) -> Dict[str, Any]:
    return {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "api_source": "gemini",
            "status": "error"
        },
        "error": {
            "message": error_message,
            "type": "api_error"
        }
    }
```

### 配置和優化
- **模型**: gemini-1.5-flash (最新穩定版本)
- **溫度**: 0.7 (平衡創造性和一致性)
- **最大輸出**: 2048 tokens
- **超時**: 30 秒
- **請求間隔**: 3 秒 (避免 API 限制)
- **錯誤重試**: 完整的異常處理
- **日誌記錄**: 詳細的操作日誌

## 📈 特色功能

### 1. 智能提示詞工程
- 結構化的分析框架
- 明確的輸出格式要求
- 中文友好的分析語言

### 2. 多維度分析
- 基本面 + 技術面 + 市場環境
- 定量 + 定性分析結合
- 風險和機會並重

### 3. 實用投資建議
- 具體的買入/持有/賣出建議
- 明確的目標價格和止損位
- 詳細的進場和出場策略

### 4. 風險管理
- 風險等級評估
- 信心等級說明
- 關鍵風險因素識別

## 🔒 安全和最佳實踐

### API 金鑰安全
- 不要在代碼中硬編碼 API 金鑰
- 使用環境變數或配置文件
- 定期輪換 API 金鑰

### 速率限制
- 添加請求間隔避免 API 限制
- 實現重試機制處理臨時錯誤
- 監控 API 使用量

### 錯誤處理
- 實現完整的錯誤處理機制
- 記錄錯誤日誌便於調試
- 提供用戶友好的錯誤信息

## 📊 性能優化

### 請求優化
- 使用連接池減少連接開銷
- 設置適當的超時時間
- 實現請求緩存機制

### 響應處理
- 異步處理大量請求
- 並行處理多個股票分析
- 優化 JSON 解析性能

## 📁 項目結構

### 文件位置
```
AIStock/
├── src/
│   └── gemini.py                # Gemini AI 分析器 ⭐
└── GEMINI_COMPLETE.md           # 完整文檔（當前文件）
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
2. **自定義 JSON 格式**: 結構化的分析結果便於後續處理
3. **完整的錯誤處理**: 健壯的異常處理機制
4. **獨立模組設計**: 不依賴其他代碼，可單獨使用

### 技術亮點
1. **現代 API 設計**: RESTful API 調用
2. **智能提示詞**: 精心設計的分析框架
3. **結構化輸出**: 統一的 JSON 格式
4. **日誌記錄**: 完整的操作追蹤

### 用戶價值
1. **智能分析**: AI 驅動的股票分析
2. **實用建議**: 具體的投資建議和風險管理
3. **易於集成**: 簡單的 API 調用
4. **可擴展性**: 模組化設計便於擴展

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

**🎯 Gemini AI 股票分析器已成功實現！**
**🤖 提供智能、全面、實用的股票分析功能！**
**🚀 為您的投資決策提供 AI 驅動的專業建議！**

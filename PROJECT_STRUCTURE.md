# 📁 AIStock 項目結構

## 🗂️ 目錄結構

```
AIStock/
├── src/                          # 核心源代碼目錄
│   ├── __init__.py              # Python 包初始化文件
│   ├── stock_analyzer.py        # 股票分析器核心模組
│   ├── visualizer.py            # 響應式視覺化報告生成器
│   ├── left_analysis.py         # 左側分析策略模組
│   └── gemini.py                # Gemini AI 股票分析模組 ⭐
├── examples/                     # 示例代碼
│   └── example_usage.py         # 使用示例
├── main.py                      # 主程序入口
├── test_all.py                  # 完整測試腳本
├── requirements.txt             # 項目依賴
├── README.md                    # 項目說明
└── 文檔/
    ├── GEMINI_COMPLETE.md       # Gemini 完整文檔 ⭐
    └── PROJECT_STRUCTURE.md     # 項目結構說明
```

## 🔧 核心模組說明

### 📊 `src/stock_analyzer.py`
- **功能**: 股票數據獲取和技術分析
- **主要類**: `StockAnalyzer`
- **依賴**: yfinance, pandas, numpy, ta

### 📈 `src/visualizer.py`
- **功能**: 響應式 HTML 報告生成
- **主要類**: `StockVisualizer`
- **特色**: 響應式設計，支持 PC/手機/平板
- **依賴**: plotly, datetime

### 💰 `src/left_analysis.py`
- **功能**: 左側分析策略（基本面分析）
- **主要類**: 各種分析函數
- **特色**: 價值投資策略

### 🤖 `src/gemini.py` ⭐
- **功能**: Gemini AI 智能股票分析
- **主要類**: `GeminiStockAnalyzer`
- **特色**: AI 驅動的投資建議
- **依賴**: requests, json, logging

## 🚀 使用方式

### 1. 導入模組
```python
# 從 src 目錄導入
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_analyzer import StockAnalyzer
from visualizer import StockVisualizer
from gemini import GeminiStockAnalyzer
```

### 2. 基本使用流程
```python
# 1. 創建股票分析器
analyzer = StockAnalyzer("AAPL")

# 2. 創建視覺化器
visualizer = StockVisualizer()

# 3. 創建 Gemini AI 分析器
gemini_analyzer = GeminiStockAnalyzer("your_api_key")

# 4. 生成分析報告
result = visualizer.create_batch_html_report([analyzer], "report.html")
```

## 🧪 測試文件

### 基本測試
- `test_all.py`: 完整項目測試腳本

### 運行測試
```bash
# 運行完整測試
python test_all.py
```

## 📊 生成的文件

### 報告文件
- `*.html`: 響應式股票分析報告
- `test_responsive_report.html`: 響應式設計測試報告

### 文檔文件
- `GEMINI_COMPLETE.md`: Gemini 完整文檔 ⭐
- `PROJECT_STRUCTURE.md`: 項目結構說明

## 🔄 開發流程

### 1. 模組開發
- 所有核心模組放在 `src/` 目錄下
- 每個模組都是獨立的，可以單獨測試
- 使用 `__init__.py` 管理包結構

### 2. 測試驗證
- 使用統一的測試腳本 `test_all.py`
- 測試文件放在根目錄，便於運行
- 測試結果保存為適當格式

### 3. 文檔維護
- 每個模組都有詳細的 README 說明
- 包含使用範例和 API 文檔
- 定期更新項目結構說明

## 🎯 項目特色

### 🤖 AI 驅動
- 集成 Gemini AI 進行智能分析
- 提供結構化的投資建議
- 支持多維度分析

### 📱 響應式設計
- 支持 PC、平板、手機三種設備
- 現代化的 UI 設計
- 流暢的用戶體驗

### 🔧 模組化架構
- 清晰的模組分離
- 易於維護和擴展
- 支持獨立開發和測試

### 📊 數據驅動
- 實時股票數據獲取
- 技術指標分析
- 基本面分析

---

**🎯 項目結構清晰，模組化設計，便於長期開發和維護！**

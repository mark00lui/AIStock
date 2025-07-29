# AIStock - 股票訊號分析系統

一個基於 Python 的智能股票分析系統，結合多種技術指標自動生成買賣訊號。

## 功能特色

- 📊 **多指標分析**: 整合移動平均線、MACD、RSI、布林通道、隨機指標等技術指標
- 🎯 **智能訊號**: 基於多指標加權計算，生成買入/賣出/持有訊號
- 📈 **視覺化圖表**: 提供 K線圖、技術指標圖、訊號強度圖等多種視覺化
- 🌍 **全球股票**: 支援美股、台股等全球主要股市
- 🔄 **批量分析**: 可同時分析多支股票
- 📱 **互動介面**: 提供命令列和互動式兩種使用方式

## 技術指標

系統整合以下技術指標：

- **移動平均線 (MA)**: SMA 20日、50日，EMA 12日、26日
- **MACD**: 移動平均收斂發散指標
- **RSI**: 相對強弱指標 (14日)
- **布林通道**: 20日布林通道
- **隨機指標**: %K、%D 線
- **成交量指標**: 成交量移動平均
- **ATR**: 平均真實範圍

## 安裝與設定

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 2. 驗證安裝

```bash
python main.py AAPL --plot
```

## 使用方法

### 命令列模式

```bash
# 基本分析
python main.py AAPL

# 指定期間並顯示圖表
python main.py AAPL --period 6mo --plot

# 儲存圖表
python main.py AAPL --save analysis_result.html

# 台股分析
python main.py 2330.TW --period 1y
```

### 互動模式

```bash
python main.py
```

然後按照提示選擇操作：
1. 分析單一股票
2. 批量分析股票
3. 查看歷史分析結果
4. 退出

### 程式碼使用

```python
from src.stock_analyzer import StockAnalyzer
from src.visualizer import StockVisualizer

# 創建分析器
analyzer = StockAnalyzer("AAPL", period="1y")

# 執行分析
analyzer.run_analysis()

# 獲取當前訊號
signal = analyzer.get_current_signal()
print(f"建議: {signal['signal']}")
print(f"強度: {signal['strength']}")

# 視覺化
visualizer = StockVisualizer(analyzer)
visualizer.plot_candlestick_with_signals()
```

## 專案結構

```
AIStock-1/
├── README.md                 # 專案說明
├── requirements.txt          # Python 依賴套件
├── main.py                  # 主程式
├── src/                     # 核心模組
│   ├── __init__.py
│   ├── stock_analyzer.py    # 股票分析器
│   └── visualizer.py        # 視覺化模組
└── examples/                # 使用範例
    └── example_usage.py     # 範例程式碼
```

## 訊號說明

### 訊號類型
- **買入 (1)**: 綜合指標顯示強烈買入訊號
- **賣出 (-1)**: 綜合指標顯示強烈賣出訊號  
- **持有 (0)**: 指標不明確，建議觀望

### 訊號強度
- **-100 到 -30**: 強烈賣出訊號
- **-30 到 30**: 中性區域，建議持有
- **30 到 100**: 強烈買入訊號

### 指標權重
- MACD: 25%
- 移動平均線: 20%
- RSI: 20%
- 隨機指標: 20%
- 布林通道: 15%

## 支援的股票代碼格式

- **美股**: AAPL, GOOGL, MSFT, TSLA
- **台股**: 2330.TW, 2317.TW, 2454.TW
- **港股**: 0700.HK, 0941.HK
- **其他**: 請參考 Yahoo Finance 代碼格式

## 範例輸出

```
=== 分析結果 ===
股票代碼: AAPL
當前價格: $175.43
建議動作: 買入
訊號強度: 45

最近30天摘要:
  買入訊號: 8 次
  賣出訊號: 3 次
  持有天數: 19 天
  平均強度: 12.5
```

## 注意事項

⚠️ **風險提醒**:
- 本系統僅供學習和研究使用
- 股票投資有風險，請謹慎決策
- 技術分析不能保證獲利，請結合基本面分析
- 建議在實際投資前進行充分的回測和驗證

## 開發計畫

- [ ] 添加更多技術指標 (KDJ、CCI、威廉指標等)
- [ ] 實現回測功能
- [ ] 添加機器學習預測模型
- [ ] 開發 Web 介面
- [ ] 支援即時資料更新
- [ ] 添加風險管理功能

## 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個專案！

## 授權

MIT License

## 聯絡資訊

如有問題或建議，請透過 GitHub Issues 聯絡我們。
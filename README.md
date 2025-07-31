# AIStock - 股票訊號分析系統

一個基於 Python 的智能股票分析系統，結合多種技術指標自動生成買賣訊號。

## 功能特色

- 📊 **多指標分析**: 整合移動平均線、MACD、RSI、布林通道、隨機指標等技術指標
- 🎯 **智能訊號**: 基於多指標加權計算，生成買入/賣出/持有訊號
- 📈 **視覺化圖表**: 提供 K線圖、技術指標圖、訊號強度圖等多種視覺化
- 🌍 **全球股票**: 支援美股、台股、加密貨幣等全球主要資產
- 🔄 **批量分析**: 主程式支援多股票批量分析，一次輸入多支股票代碼
- 📱 **互動介面**: 提供命令列、互動式和批量分析三種使用方式
- 📋 **結果排序**: 按訊號強度排序，快速識別最佳投資機會
- 💾 **CSV 匯出**: 支援將分析結果匯出為 CSV 檔案
- 🎯 **靈活輸入**: 支援空格分隔、逗號分隔等多種股票代碼輸入方式
- 🏷️ **股票原始名稱**: 動態獲取並顯示股票的原始名稱（如 AAPL → Apple Inc.，2330.TW → 台積電）

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
# 方法一：直接安裝（推薦）
pip install numpy pandas yfinance matplotlib seaborn ta scikit-learn plotly dash dash-bootstrap-components requests python-dotenv schedule

# 方法二：使用 requirements.txt
pip install -r requirements.txt
```

### 2. 驗證安裝

```bash
# 運行測試腳本
python test_installation.py

# 測試單一股票分析
python main.py AAPL

# 測試批量分析
python main.py AAPL MSFT GOOGL

# 測試圖表功能
python main.py AAPL --plot

# 測試股票原始名稱功能
python test_stock_names.py

# 測試每日報告功能
python test_daily_report.py

# 運行完整演示
python demo_stock_names.py
```

## 使用方法

### 命令列模式

#### 單一股票分析
```bash
# 基本分析
python main.py AAPL

# 指定期間並顯示圖表
python main.py AAPL --period 6mo --plot

# 儲存圖表
python main.py AAPL --save analysis_result.html

# 生成每日報告
python main.py AAPL --save-daily-report

# 台股分析
python main.py 2330.TW --period 1y
```

#### 多股票批量分析
```bash
# 空格分隔多個股票代碼
python main.py AAPL MSFT GOOGL TSLA

# 逗號分隔多個股票代碼
python main.py "AAPL,MSFT,GOOGL,TSLA"

# 混合使用
python main.py "AAPL,MSFT" GOOGL TSLA

# 指定期間批量分析
python main.py AAPL MSFT GOOGL --period 6mo

# 批量分析並顯示圖表（僅第一支股票）
python main.py AAPL MSFT GOOGL --plot

# 批量分析並生成每日報告
python main.py "AAPL,MSFT,GOOGL" --save-daily-report
```

### 股票原始名稱功能

系統會自動獲取並顯示股票的原始名稱，支援多個地區的股票：

#### 支援的股票類型
- **美國股票**: AAPL → Apple Inc., MSFT → Microsoft Corporation
- **台灣股票**: 2330.TW → 台積電, 2317.TW → 鴻海
- **香港股票**: 0700.HK → 騰訊控股, 0941.HK → 中國移動
- **其他地區**: 自動識別並顯示原始名稱

#### 顯示位置
- **命令列輸出**: 分析結果中顯示股票代碼和原始名稱
- **HTML 報告**: 報告標題和摘要卡片中包含股票原始名稱
- **批量分析表格**: 表格中新增股票名稱欄位

#### 範例輸出
```
=== 分析結果 ===
股票代碼: AAPL
股票名稱: Apple Inc.
當前價格: $209.05
建議動作: 持有
訊號強度: -5.0
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

### 批量分析模式

#### 主程式批量分析
使用 `main.py` 可以一次分析多支股票：

```bash
# 空格分隔
python main.py AAPL MSFT GOOGL TSLA

# 逗號分隔
python main.py "AAPL,MSFT,GOOGL,TSLA"

# 混合使用
python main.py "AAPL,MSFT" GOOGL TSLA
```

#### 專用批量分析工具
使用專門的批量分析工具，提供更多功能：

```bash
python batch_analysis.py
```

#### 批量分析功能特色

- **主程式支援**: `main.py` 支援多股票批量分析
- **靈活輸入**: 支援空格分隔、逗號分隔等多種輸入方式
- **快速分析**: 預設股票組合（科技股、金融股、加密貨幣、台股）
- **互動輸入**: 自訂股票代碼列表
- **結果排序**: 按訊號強度排序顯示結果
- **統計摘要**: 提供買入/賣出/持有統計
- **CSV 匯出**: 可將結果儲存為 CSV 檔案

#### 使用範例

**1. 主程式批量分析**
```bash
# 快速分析多支股票
python main.py AAPL MSFT GOOGL TSLA

# 指定期間批量分析
python main.py "AAPL,MSFT,GOOGL" --period 6mo
```

**2. 專用批量分析工具**
```bash
python batch_analysis.py
# 選擇 1-4 的預設組合，或選擇 5 自訂股票代碼
```

**3. 自訂股票代碼**
```bash
python batch_analysis.py
# 選擇模式 1 (互動式輸入)
# 輸入股票代碼: AAPL,MSFT,GOOGL,TSLA,UNH
```

**3. 支援的股票類型**
- **美股**: AAPL, MSFT, GOOGL, TSLA, NVDA, META
- **金融股**: JPM, BAC, WFC, GS, MS, UNH, JNJ
- **加密貨幣**: BTC-USD, ETH-USD, BNB-USD, SOL-USD, ADA-USD
- **台股**: 2330.TW, 2317.TW, 2454.TW, 3008.TW, 2412.TW

#### 批量分析輸出範例

**主程式批量分析輸出**
```
=== AIStock 股票訊號分析系統 ===
分析股票: AAPL, MSFT, GOOGL, TSLA
資料期間: 1y
----------------------------------------
正在批量分析 4 支股票...

[1/4] 分析 AAPL...
  ✅ AAPL: $211.27 | 持有 | 強度: -5.0

[2/4] 分析 MSFT...
  ✅ MSFT: $512.57 | 持有 | 強度: -5.0

[3/4] 分析 GOOGL...
  ✅ GOOGL: $195.75 | 賣出 | 強度: -45.0

[4/4] 分析 TSLA...
  ✅ TSLA: $321.20 | 持有 | 強度: 5.0

============================================================
=== 分析結果摘要 ===
============================================================
股票代碼     價格           建議     強度       日期
------------------------------------------------------------
TSLA     $321.20      持有     5.0      2025-07-29
AAPL     $211.27      持有     -5.0     2025-07-29
MSFT     $512.57      持有     -5.0     2025-07-29
GOOGL    $195.75      賣出     -45.0    2025-07-29

📊 統計摘要:
成功分析: 4/4 支股票
買入建議: 0 支
賣出建議: 1 支
持有建議: 3 支

強度統計:
平均強度: -12.5
最高強度: 5.0
最低強度: -45.0
```

**專用批量分析工具輸出**
```
=== 批量股票分析 ===
分析期間: 1y
股票數量: 7
============================================================

[1/7] 分析 AAPL...
  ✅ AAPL: $212.25 | 持有 | 強度: -5.0

[2/7] 分析 MSFT...
  ✅ MSFT: $514.46 | 賣出 | 強度: -25.0

...

============================================================
=== 分析結果摘要 ===
============================================================
股票代碼     價格           建議     強度       日期
------------------------------------------------------------
TSLA     $319.95      持有     5.0      2025-07-29
AMZN     $231.12      持有     -5.0     2025-07-29
AAPL     $212.25      持有     -5.0     2025-07-29
MSFT     $514.46      賣出     -25.0    2025-07-29
GOOGL    $194.07      賣出     -45.0    2025-07-29

📊 統計摘要:
成功分析: 7/7 支股票
買入建議: 0 支
賣出建議: 3 支
持有建議: 4 支

強度統計:
平均強度: -17.9
最高強度: 5.0
最低強度: -45.0
```

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

# 生成 HTML 報告
visualizer = StockVisualizer(analyzer)
visualizer.create_comprehensive_html_report("my_report.html")
```

### HTML 報告功能

系統現在支援生成專業的 HTML 報告，包含以下特色：

#### 單一股票報告
```bash
# 生成單一股票 HTML 報告
python main.py AAPL --save my_report.html

# 或使用 --plot 參數
python main.py AAPL --plot
```

#### 批量股票報告
```bash
# 生成批量股票 HTML 報告
python main.py AAPL MSFT GOOGL TSLA --save batch_report.html

# 或使用逗號分隔
python main.py "AAPL,MSFT,GOOGL" --save batch_report.html
```

#### 每日報告模式
```bash
# 生成每日報告（檔名格式：YYYY-MM-DD_report.html）
python main.py AAPL --save-daily-report

# 批量分析每日報告
python main.py "AAPL,MSFT,GOOGL" --save-daily-report
```

**每日報告特色**
- **📅 自動日期命名**: 使用當前日期自動生成檔名（YYYY-MM-DD_report.html）
- **🔄 每日更新**: 適合每日定時生成報告的需求
- **📊 完整分析**: 包含單一股票或批量分析的完整報告
- **💾 易於管理**: 按日期組織報告文件，便於歸檔和查找

#### HTML 報告特色
- **🎯 單一文件**: 所有內容都在一個 HTML 文件中
- **📊 互動圖表**: 使用 Plotly 創建互動式圖表
- **📱 響應式設計**: 支援手機、平板、電腦
- **🎨 專業樣式**: 現代化的 CSS 設計
- **📈 完整分析**: 包含所有技術指標和訊號
- **📋 詳細數據**: 價格、訊號、強度等完整信息
- **⚠️ 風險提醒**: 包含投資風險警告
- **💾 易於分享**: 單一文件，方便傳送給客戶

#### 報告內容
1. **摘要卡片**: 當前價格、建議動作、訊號強度、分析期間
2. **技術指標詳情**: 各項技術指標的具體數值
3. **統計摘要**: 最近30天的買入/賣出/持有統計
4. **綜合圖表**: 包含 K線圖、成交量、MACD、RSI、隨機指標、訊號強度
5. **風險提醒**: 投資風險警告聲明

## 專案結構

```
AIStock/
├── README.md                 # 專案說明
├── requirements.txt          # Python 依賴套件
├── main.py                  # 主程式（支援單一/批量分析）
├── batch_analysis.py        # 專用批量分析工具
├── src/                     # 核心模組
│   ├── __init__.py
│   ├── stock_analyzer.py    # 股票分析器
│   └── visualizer.py        # 視覺化模組（含 HTML 報告功能）
├── examples/                # 使用範例
│   └── example_usage.py     # 範例程式碼
├── test_*.py               # 測試腳本
├── test_html_report.py      # HTML 報告功能測試
├── test_stock_names.py      # 股票原始名稱功能測試
├── test_daily_report.py     # 每日報告功能測試
├── demo_html_report.py      # HTML 報告功能演示
└── *.html                  # 生成的 HTML 報告文件
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

- **美股**: AAPL, GOOGL, MSFT, TSLA, NVDA, META
- **台股**: 2330.TW, 2317.TW, 2454.TW, 3008.TW, 2412.TW
- **港股**: 0700.HK, 0941.HK
- **加密貨幣**: BTC-USD, ETH-USD, BNB-USD, SOL-USD, ADA-USD
- **其他**: 請參考 Yahoo Finance 代碼格式

## 範例輸出

### 單一股票分析
```
=== 分析結果 ===
股票代碼: AAPL
股票名稱: Apple Inc.
當前價格: $175.43
建議動作: 買入
訊號強度: 45
```

### 批量分析結果
```
=== 分析結果摘要 ===
============================================================
股票代碼     股票名稱                 價格           建議     強度       日期
----------------------------------------------------------------------
TSLA     Tesla, Inc.           $319.95      持有     5.0      2025-07-29
AMZN     Amazon.com, Inc.      $231.12      持有     -5.0     2025-07-29
AAPL     Apple Inc.            $212.25      持有     -5.0     2025-07-29
MSFT     Microsoft Corporation $514.46      賣出     -25.0    2025-07-29
GOOGL    Alphabet Inc.         $194.07      賣出     -45.0    2025-07-29

📊 統計摘要:
成功分析: 7/7 支股票
買入建議: 0 支
賣出建議: 3 支
持有建議: 4 支

強度統計:
平均強度: -17.9
最高強度: 5.0
最低強度: -45.0
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
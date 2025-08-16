# AIStock - 股票訊號分析系統

一個基於 Python 的智能股票分析系統，結合多種技術指標自動生成買賣訊號，並整合分析師預估和基本面分析功能。

## 功能特色

- 📊 **多指標分析**: 整合移動平均線、MACD、RSI、布林通道、隨機指標等技術指標
- 🎯 **智能訊號**: 基於多指標加權計算，生成買入/賣出/持有訊號
- 📈 **決策導向圖表**: 提供清晰的投資決策分析圖表，重點展示為什麼會得出買入/賣出/保持建議
- 🌍 **全球股票**: 支援美股、台股、加密貨幣等全球主要資產
- 🔄 **批量分析**: 主程式支援多股票批量分析，一次輸入多支股票代碼
- 📱 **互動介面**: 提供命令列、互動式和批量分析三種使用方式
- 📋 **結果排序**: 按訊號強度排序，快速識別最佳投資機會
- 💾 **CSV 匯出**: 支援將分析結果匯出為 CSV 檔案
- 🎯 **靈活輸入**: 支援空格分隔、逗號分隔等多種股票代碼輸入方式
- 🏷️ **股票原始名稱**: 動態獲取並顯示股票的原始名稱（如 AAPL → Apple Inc.，2330.TW → 台積電）
- 🔍 **左側分析**: 整合分析師預估和基本面分析，提供未來1-3年股價預測
- 📊 **視覺化整合**: 圖像化顯示當前股價在未來預估範圍內的位置，判斷估值狀態
- 🎨 **批次圖表**: 批次分析報告包含每個股票的獨立技術分析圖表和價格比較圖表

## 技術指標

系統整合以下技術指標：

- **移動平均線 (MA)**: SMA 20日、50日，EMA 12日、26日
- **MACD**: 移動平均收斂發散指標
- **RSI**: 相對強弱指標 (14日)
- **布林通道**: 20日布林通道
- **隨機指標**: %K、%D 線
- **成交量指標**: 成交量移動平均
- **ATR**: 平均真實範圍

## 左側分析功能

### 多數據源整合
- **Yahoo Finance**: 真實的分析師目標價和建議 (12個月預估)
- **Alpha Vantage**: 專業的金融數據 API (需要 API key)
- **Finviz**: 分析師預估數據 (模擬)
- **TradingView**: 技術分析師預估 (模擬)
- **富途牛牛**: 亞洲市場分析師預估 (模擬)

### 多時間範圍分析
- **1年後預估**: 基於分析師12個月目標價
- **2年後預估**: 基於1年預估的成長率推算
- **3年後預估**: 基於1年預估的複利成長推算

### 智能分析
- **聚合統計**: 計算各時間範圍的平均、中位數、最高、最低預估價
- **信賴區間**: 68% 和 95% 信賴區間計算
- **共識分析**: 分析師意見一致性評估
- **風險評估**: 基於變異係數的風險等級分類
- **預期報酬率**: 各時間範圍的預期投資報酬率

### 共識評分系統
- **共識分數 (0-100)**: 綜合分析師一致性的量化指標
- **一致性等級**: Very High/High/Medium/Low/Very Low
- **建議分布**: 買入/持有/賣出建議的比例分析

## 視覺化整合功能

### 股價範圍可視化
- **直觀顯示**: 以條形圖顯示未來1年、2年、3年的股價預估範圍
- **位置判斷**: 清楚標示當前股價在預估範圍內的位置
- **估值狀態**: 自動判斷股票是否被低估、合理估值或高估
- **顏色編碼**: 
  - 🟢 綠色：當前股價低於預估範圍（可能低估）
  - 🔴 紅色：當前股價在預估範圍內（合理估值）
  - 🟠 橙色：當前股價高於預估範圍（可能高估）

### 綜合分析報告
- **雙重分析**: 技術分析 + 左側分析整合
- **完整圖表**: 包含8個子圖表的綜合分析
- **詳細數據**: 各時間範圍的預估價格和報酬率
- **估值判斷**: 自動判斷估值狀態並提供建議

### 批量分析報告
- **多股票分析**: 同時分析多支股票
- **獨立圖表**: 每個股票都有獨立的技術分析圖表和價格比較圖表
- **並列顯示**: 技術分析和左側分析並列
- **排序功能**: 按訊號強度排序
- **摘要統計**: 技術分析和左側分析的統計摘要

### 技術分析圖表特色
- **股價走勢**: 顯示過去1年的股價走勢
- **布林通道**: 20日布林通道上下軌
- **移動平均**: 120日移動平均線
- **RSI指標**: 14日相對強弱指標
- **MACD指標**: MACD線、信號線和柱狀圖
- **互動功能**: 可縮放、平移、懸停查看詳細數據

### 價格比較圖表特色
- **當前價格**: 顯示當前股價
- **目標價格**: 顯示1年目標價
- **視覺比較**: 直觀比較當前價格與目標價格
- **顏色區分**: 不同顏色區分當前價格和目標價格

## 安裝與設定

### 1. 安裝依賴套件

```bash
# 方法一：直接安裝（推薦）
pip install numpy pandas yfinance matplotlib seaborn ta scikit-learn plotly dash dash-bootstrap-components requests python-dotenv schedule

# 方法二：使用 requirements.txt
pip install -r requirements.txt
```

### 2. 設定 API Keys (可選)
為了獲得更好的數據，建議設定 Alpha Vantage API key：

```bash
# 設定環境變數
export ALPHA_VANTAGE_KEY="your_api_key_here"

# 或在 Windows PowerShell 中
$env:ALPHA_VANTAGE_KEY="your_api_key_here"
```

### 3. 獲取 Alpha Vantage API Key
1. 前往 [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. 註冊免費帳戶
3. 獲取 API key

### 4. 驗證安裝

```bash
# 運行整合測試程序
python test_all.py

# 測試單一股票分析
python main.py AAPL

# 測試批量分析
python main.py AAPL MSFT GOOGL

# 測試圖表功能
python main.py AAPL --plot

# 運行完整演示（包含所有功能說明）
python test_all.py --all
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
# 批量分析功能已整合到主程式中
python main.py AAPL MSFT GOOGL TSLA
```

#### 批量分析功能特色

- **主程式支援**: `main.py` 支援多股票批量分析
- **靈活輸入**: 支援空格分隔、逗號分隔等多種輸入方式
- **快速分析**: 預設股票組合（科技股、金融股、加密貨幣、台股）
- **互動輸入**: 自訂股票代碼列表
- **結果排序**: 按訊號強度排序顯示結果
- **統計摘要**: 提供買入/賣出/持有統計
- **CSV 匯出**: 可將結果儲存為 CSV 檔案
- **獨立圖表**: 每個股票都有獨立的技術分析圖表和價格比較圖表

#### 使用範例

**1. 主程式批量分析**
```bash
# 快速分析多支股票
python main.py AAPL MSFT GOOGL TSLA

# 指定期間批量分析
python main.py "AAPL,MSFT,GOOGL" --period 6mo
```

**2. 批量分析功能**
```bash
python main.py AAPL MSFT GOOGL TSLA
# 或使用逗號分隔: python main.py "AAPL,MSFT,GOOGL,TSLA"
```

**3. 自訂股票代碼**
```bash
python main.py AAPL MSFT GOOGL TSLA UNH
# 或使用互動模式: python main.py
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

#### 基本技術分析
```python
from src.stock_analyzer import StockAnalyzer
from src.visualizer import StockVisualizer

# 創建分析器
analyzer = StockAnalyzer("AAPL", period="1y")

# 執行分析
if analyzer.run_analysis():
    # 獲取當前訊號
    current_signal = analyzer.get_current_signal()
    print(f"建議: {current_signal['signal']}")
    print(f"強度: {current_signal['strength']}")
    
    # 創建視覺化器
    visualizer = StockVisualizer(analyzer)
    
    # 生成決策導向圖表（新功能）
    decision_report = visualizer.create_decision_chart()
    print(f"決策分析報告: {decision_report}")
    
    # 生成傳統綜合圖表
    comprehensive_report = visualizer.create_comprehensive_html_report()
    print(f"綜合分析報告: {comprehensive_report}")
```

#### 左側分析使用
```python
from src.left_analysis import analyze_stock, analyze_multiple_stocks

# 分析單一股票
result = analyze_stock("AAPL")
if result and 'timeframes' in result:
    one_year = result['timeframes']['1_year']
    two_year = result['timeframes']['2_year']
    three_year = result['timeframes']['3_year']
    
    print(f"1年後預估: ${one_year['target_mean']:.2f}")
    print(f"2年後預估: ${two_year['target_mean']:.2f}")
    print(f"3年後預估: ${three_year['target_mean']:.2f}")

# 分析多個股票
symbols = ["AAPL", "TSLA", "MSFT", "2330.TW"]
results = analyze_multiple_stocks(symbols)
for stock_result in results['results']:
    print(f"{stock_result['symbol']}: {stock_result['timeframes']['1_year']['target_mean']:.2f}")
```

#### 視覺化整合使用
```python
from src.stock_analyzer import StockAnalyzer
from src.visualizer import StockVisualizer

# 創建分析器
analyzer = StockAnalyzer('AAPL', period='1y')
analyzer.run_analysis()

# 創建視覺化器
visualizer = StockVisualizer(analyzer)

# 生成股價範圍圖表
fig = visualizer.create_price_range_visualization()
fig.savefig('price_range.png')

# 生成股價範圍 HTML 報告
visualizer.create_price_range_html('price_range.html')

# 生成綜合分析報告
report_path = visualizer.create_comprehensive_html_report('comprehensive_analysis.html')
```

#### 批量分析
```python
# 批量分析
symbols = ['AAPL', 'MSFT', 'TSLA']
analyzers = []

for symbol in symbols:
    analyzer = StockAnalyzer(symbol, period='6mo')
    if analyzer.run_analysis():
        analyzers.append(analyzer)

# 生成批量報告
visualizer = StockVisualizer()
report_path = visualizer.create_batch_html_report(analyzers, 'batch_analysis.html')
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

#### 決策導向圖表（新功能）
- **🎯 決策邏輯**: 清楚展示為什麼會得出買入/賣出/保持的建議
- **📊 分層展示**: 股價趨勢、技術指標、訊號強度、綜合建議
- **📈 重點突出**: 重點展示決策邏輯而非混亂的原始數據
- **💡 決策說明**: 提供詳細的決策邏輯說明
- **🎨 清晰設計**: 減少視覺混亂，提高可讀性

#### HTML 報告特色
- **🎯 單一文件**: 所有內容都在一個 HTML 文件中
- **📊 互動圖表**: 使用 Plotly 創建互動式圖表
- **📱 響應式設計**: 支援手機、平板、電腦
- **🎨 專業樣式**: 現代化的 CSS 設計
- **📈 完整分析**: 包含所有技術指標和訊號
- **📋 詳細數據**: 價格、訊號、強度等完整信息
- **⚠️ 風險提醒**: 包含投資風險警告
- **💾 易於分享**: 單一文件，方便傳送給客戶
- **🎨 獨立圖表**: 每個股票都有獨立的技術分析圖表和價格比較圖表

#### 報告內容
1. **摘要卡片**: 當前價格、建議動作、訊號強度、分析期間
2. **技術指標詳情**: 各項技術指標的具體數值
3. **統計摘要**: 最近30天的買入/賣出/持有統計
4. **綜合圖表**: 包含 K線圖、成交量、MACD、RSI、隨機指標、訊號強度
5. **左側分析摘要**: 基本面數據、各時間範圍預估、估值狀態
6. **股價範圍可視化**: 當前股價在未來預估範圍內的位置
7. **風險提醒**: 投資風險警告聲明
8. **個股分析**: 每個股票的詳細分析，包含獨立的技術分析圖表和價格比較圖表

## 專案結構

```
AIStock/
├── README.md                 # 專案說明
├── requirements.txt          # Python 依賴套件
├── main.py                  # 主程式（支援單一/批量分析）

├── src/                     # 核心模組
│   ├── __init__.py
│   ├── stock_analyzer.py    # 股票分析器
│   ├── left_analysis.py     # 左側分析模組（分析師預估和基本面分析）
│   └── visualizer.py        # 視覺化模組（含 HTML 報告功能）
├── examples/                # 使用範例
│   └── example_usage.py     # 範例程式碼
├── test_all.py              # 整合測試程序（包含所有功能演示）
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

## 左側分析指標解釋

### 共識分數計算
- **目標價一致性 (40%)**: 基於變異係數評估
- **建議一致性 (60%)**: 基於買入/持有/賣出建議分布

### 風險等級分類
- **低風險**: 變異係數 < 0.1 (分析師預估一致性高)
- **中風險**: 變異係數 0.1-0.2 (分析師預估一致性中等)
- **高風險**: 變異係數 > 0.2 (分析師預估分歧較大)

### 信賴區間
- **68% 信賴區間**: 平均價 ± 1個標準差
- **95% 信賴區間**: 平均價 ± 2個標準差

### 時間範圍推算邏輯
- **1年後**: 基於分析師12個月目標價
- **2年後**: 1年預估 × (1 + 年化成長率)
  - 平均預估: 8% 年化成長率
  - 高預估: 10% 年化成長率
  - 低預估: 6% 年化成長率
- **3年後**: 1年預估 × (1 + 年化成長率)²

## 支援的股票代碼格式

- **美股**: AAPL, GOOGL, MSFT, TSLA, NVDA, META
- **台股**: 2330.TW, 2317.TW, 2454.TW, 3008.TW, 2412.TW
- **港股**: 0700.HK, 0941.HK
- **加密貨幣**: BTC-USD, ETH-USD, BNB-USD, SOL-USD, ADA-USD
- **其他**: 請參考 Yahoo Finance 代碼格式

## 測試功能

### 運行測試
```bash
# 測試所有功能
python test_all.py --all

# 測試特定功能
python test_all.py --left-analysis
python test_all.py --visualization
python test_all.py --integration
```

### 測試內容
1. **左側分析功能**: 測試數據獲取和計算
2. **視覺化整合**: 測試圖表生成和報告創建
3. **批量分析**: 測試多股票分析功能
4. **整合測試**: 測試技術分析和左側分析的結合

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

### 左側分析輸出
```
=== 分析師預估聚合分析: AAPL ===
當前股價: $232.78

Yahoo Finance:
  建議: buy
  更新時間: 2025-08-15
  1年後:
    平均目標價: $234.28
    最高目標價: $300.00
    最低目標價: $175.00
    分析師數量: 36
  2年後:
    平均目標價: $253.02
    最高目標價: $330.00
    最低目標價: $185.50
    分析師數量: 36
  3年後:
    平均目標價: $273.26
    最高目標價: $363.00
    最低目標價: $196.63
    分析師數量: 36

============================================================
1年後股價預估聚合分析 (2026-08-15)
============================================================
數據來源數量: 4
平均預估價: $190.94
中位數預估價: $178.50
最高預估價: $234.28
最低預估價: $172.50
標準差: $25.16
預期報酬率: -17.97%

信賴區間:
68% 信賴區間: $165.78 - $216.10
95% 信賴區間: $140.62 - $241.26

共識分析:
共識分數: 90/100
一致性等級: Very High
買入建議比例: 100.0%
持有建議比例: 0.0%
賣出建議比例: 0.0%

風險評估:
變異係數: 0.132
風險等級: 中 (分析師預估一致性中等)
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

### 股價範圍圖表
```
AAPL 股價範圍分析
├── 1年後預估範圍: $150.00 - $200.00
│   ├── 平均預估價: $175.00
│   ├── 當前股價: $160.00 (在範圍內)
│   └── 預期報酬率: +9.38%
├── 2年後預估範圍: $162.00 - $220.00
│   ├── 平均預估價: $189.00
│   └── 預期報酬率: +18.13%
└── 3年後預估範圍: $175.00 - $242.00
    ├── 平均預估價: $204.00
    └── 預期報酬率: +27.50%
```

### HTML 報告結構
```
綜合分析報告
├── 技術分析摘要
│   ├── 建議操作: 買入
│   ├── 當前價格: $160.00
│   └── 訊號強度: 45.2
├── 左側分析摘要
│   ├── 當前股價: $160.00
│   ├── Forward EPS: $6.50
│   └── Forward P/E: 24.6
├── 綜合圖表
│   ├── 股價與交易訊號
│   ├── 技術指標分析
│   └── 股價範圍可視化
└── 詳細分析
    ├── 1年後預估分析
    ├── 2年後預估分析
    └── 3年後預估分析
```

### 批次分析報告結構
```
批次分析報告
├── 摘要統計
│   ├── 技術分析摘要
│   │   ├── 買入信號: 2
│   │   ├── 賣出信號: 1
│   │   ├── 持有信號: 1
│   │   └── 總股票數: 4
│   └── 左側分析摘要
│       ├── 低估股票: 2
│       ├── 高估股票: 2
│       ├── 總股票數: 4
│       └── 分析完成: 4
└── 個股分析
    ├── AAPL
    │   ├── 左側分析策略
    │   │   ├── 當前價格: $211.27
    │   │   ├── 1年目標價: $234.28
    │   │   ├── 2年目標價: $253.02
    │   │   ├── 3年目標價: $273.26
    │   │   ├── 預估EPS: $6.50
    │   │   └── 估值狀態: 低估
    │   ├── 右側技術分析
    │   │   ├── 主要信號: 持有
    │   │   ├── 信號強度: -5.0
    │   │   ├── RSI: 45.2
    │   │   └── MACD: -2.1
    │   ├── 價格比較圖表
    │   └── 技術分析圖表
    ├── MSFT
    │   ├── 左側分析策略
    │   ├── 右側技術分析
    │   ├── 價格比較圖表
    │   └── 技術分析圖表
    └── ...
```

## 數據來源說明

### 技術分析數據
1. **價格數據**: 歷史股價和成交量
2. **技術指標**: MACD、RSI、布林通道、隨機指標
3. **移動平均**: 20日和50日移動平均線
4. **訊號生成**: 綜合多個指標的買賣訊號

### 左側分析數據
1. **Yahoo Finance**: 分析師預估和基本面數據
2. **歷史本益比**: 基於10年歷史數據計算
3. **EPS 預估**: 基於歷史本益比和未來 EPS 預估
4. **模擬數據**: 補充其他來源的預估

### 真實數據源
- **Yahoo Finance**: 免費，提供12個月分析師預估
- **Alpha Vantage**: 付費 API，提供更詳細的分析師數據

### 模擬數據源
- **Finviz**: 模擬數據，實際使用時可替換為真實 API
- **TradingView**: 模擬數據，可整合 TradingView API
- **富途牛牛**: 模擬數據，可整合富途牛牛 API

## 注意事項

⚠️ **風險提醒**:
- 本系統僅供學習和研究使用
- 股票投資有風險，請謹慎決策
- 技術分析不能保證獲利，請結合基本面分析
- 建議在實際投資前進行充分的回測和驗證
- 分析師預估僅供參考，實際投資需考慮市場風險
- 數據時效性: 分析師預估可能不是最新的，請注意更新時間
- API 限制: Alpha Vantage 免費版有 API 調用次數限制
- 模擬數據: 部分數據源使用模擬數據，實際使用時建議替換為真實 API
- 時間推算: 2年和3年預估基於成長率推算，實際情況可能不同

## 開發計畫

- [ ] 添加更多技術指標 (KDJ、CCI、威廉指標等)
- [ ] 實現回測功能
- [ ] 添加機器學習預測模型
- [ ] 開發 Web 介面
- [ ] 支援即時資料更新
- [ ] 添加風險管理功能
- [ ] 整合更多真實數據源 (TipRanks, Zacks, 等)
- [ ] 加入歷史預估準確性分析
- [ ] 提供更多圖表視覺化功能
- [ ] 支援更多市場 (港股、A股等)
- [ ] 獲取真實的2年、3年分析師預估數據
- [ ] 提供 REST API 接口

## 未來改進

1. **更多數據源**: 整合更多分析師預估來源
2. **機器學習**: 使用 ML 模型改進預估準確性
3. **實時更新**: 支援實時數據更新
4. **更多圖表**: 添加更多視覺化圖表類型
5. **API 接口**: 提供 REST API 接口

## 技術架構

```
AIStock 系統架構
├── src/
│   ├── stock_analyzer.py    # 技術分析模組
│   ├── left_analysis.py     # 左側分析模組
│   └── visualizer.py        # 視覺化模組
├── test_all.py              # 綜合測試
└── requirements.txt         # 依賴包
```

## 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個專案！

## 授權

MIT License

## 聯絡資訊

如有問題或建議，請透過 GitHub Issues 聯絡我們。
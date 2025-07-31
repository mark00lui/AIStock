# AIStock 安裝指南

## 系統需求

- Python 3.8 或更高版本
- Windows 10/11, macOS, 或 Linux
- 網路連線（用於獲取股票資料）

## 安裝步驟

### 1. 克隆專案

```bash
git clone https://github.com/your-username/AIStock.git
cd AIStock
```

### 2. 安裝依賴套件

#### 方法一：直接安裝（推薦）

```bash
pip install numpy pandas yfinance matplotlib seaborn ta scikit-learn plotly dash dash-bootstrap-components requests python-dotenv schedule
```

#### 方法二：使用 requirements.txt

```bash
pip install -r requirements.txt
```

### 3. 驗證安裝

運行測試腳本確認所有功能正常：

```bash
python test_installation.py
```

如果看到 "🎉 所有測試通過！AIStock 安裝成功！" 訊息，表示安裝成功。

## 常見問題解決

### 問題 1：編譯錯誤

如果在 Windows 上遇到編譯錯誤，請嘗試：

```bash
# 安裝預編譯的 wheel 包
pip install --only-binary=all numpy pandas

# 或者使用 conda（如果已安裝）
conda install numpy pandas
```

### 問題 2：yfinance 安裝失敗

```bash
# 更新 pip
python -m pip install --upgrade pip

# 重新安裝 yfinance
pip install yfinance --upgrade
```

### 問題 3：matplotlib 顯示問題

```bash
# 安裝後端
pip install tkinter

# 或在程式碼中設置
import matplotlib
matplotlib.use('Agg')  # 非互動式後端
```

## 快速測試

安裝完成後，可以運行以下命令測試：

```bash
# 單一股票分析
python main.py AAPL

# 批量分析
python main.py AAPL MSFT GOOGL

# 互動模式
python main.py

# 顯示圖表
python main.py AAPL --plot
```

## 使用範例

### 基本使用

```bash
# 分析蘋果股票
python main.py AAPL

# 分析多支股票
python main.py AAPL MSFT GOOGL TSLA

# 指定分析期間
python main.py AAPL --period 6mo

# 顯示圖表
python main.py AAPL --plot

# 儲存圖表
python main.py AAPL --save my_analysis.html
```

### 支援的股票代碼

- **美股**: AAPL, MSFT, GOOGL, TSLA, NVDA, META
- **台股**: 2330.TW, 2317.TW, 2454.TW
- **加密貨幣**: BTC-USD, ETH-USD, BNB-USD
- **其他**: 請參考 Yahoo Finance 代碼格式

## 故障排除

### 檢查 Python 版本

```bash
python --version
```

確保版本為 3.8 或更高。

### 檢查已安裝的套件

```bash
pip list
```

### 重新安裝

如果遇到問題，可以嘗試重新安裝：

```bash
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## 支援

如果遇到安裝問題，請：

1. 檢查 Python 版本是否符合要求
2. 確保網路連線正常
3. 嘗試使用不同的安裝方法
4. 查看錯誤訊息並搜尋解決方案
5. 在 GitHub Issues 中報告問題

## 更新

定期更新以獲得最新功能：

```bash
git pull origin main
pip install -r requirements.txt --upgrade
``` 
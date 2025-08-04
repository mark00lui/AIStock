#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIStock 整合測試程序
包含所有功能的測試：安裝檢查、系統功能、HTML報告、加密貨幣、股票分析等
以及完整的使用方法演示和算法說明
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加 src 目錄到路徑
sys.path.append('src')

def test_imports():
    """測試所有依賴包的導入"""
    print("=== 測試依賴包導入 ===")
    
    dependencies = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('yfinance', 'yf'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'sns'),
        ('ta', 'ta'),
        ('sklearn', 'sklearn'),
        ('plotly', 'plotly'),
        ('dash', 'dash')
    ]
    
    failed_imports = []
    
    for package, alias in dependencies:
        try:
            __import__(package)
            print(f"✅ {package} 導入成功")
        except ImportError as e:
            print(f"❌ {package} 導入失敗: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n⚠️ 缺少依賴包: {', '.join(failed_imports)}")
        print("請執行: pip install -r requirements.txt")
        return False
    
    return True

def test_stock_analyzer():
    """測試股票分析器"""
    print("\n=== 測試股票分析器 ===")
    
    try:
        from stock_analyzer import StockAnalyzer
        print("✅ StockAnalyzer 導入成功")
    except ImportError as e:
        print(f"❌ StockAnalyzer 導入失敗: {e}")
        return False
    
    try:
        analyzer = StockAnalyzer('AAPL')
        print("✅ StockAnalyzer 創建成功")
    except Exception as e:
        print(f"❌ StockAnalyzer 創建失敗: {e}")
        return False
    
    try:
        result = analyzer.run_analysis()
        if result:
            print("✅ 股票分析執行成功")
            current_signal = analyzer.get_current_signal()
            print(f"   當前價格: ${current_signal['price']}")
            print(f"   建議動作: {current_signal['signal']}")
            print(f"   訊號強度: {current_signal['strength']}")
        else:
            print("❌ 股票分析執行失敗")
            return False
    except Exception as e:
        print(f"❌ 股票分析執行錯誤: {e}")
        return False
    
    return True

def test_visualizer():
    """測試視覺化模組"""
    print("\n=== 測試視覺化模組 ===")
    
    try:
        from visualizer import StockVisualizer
        print("✅ StockVisualizer 導入成功")
    except ImportError as e:
        print(f"❌ StockVisualizer 導入失敗: {e}")
        return False
    
    try:
        from stock_analyzer import StockAnalyzer
        analyzer = StockAnalyzer('AAPL')
        analyzer.run_analysis()
        visualizer = StockVisualizer(analyzer)
        print("✅ StockVisualizer 創建成功")
    except Exception as e:
        print(f"❌ StockVisualizer 創建失敗: {e}")
        return False
    
    return True

def test_data_fetch():
    """測試資料獲取"""
    print("\n=== 測試資料獲取 ===")
    
    try:
        from stock_analyzer import StockAnalyzer
        analyzer = StockAnalyzer("AAPL", period="1mo")
        if analyzer.fetch_data():
            print("✅ 資料獲取成功")
            print(f"   資料筆數: {len(analyzer.data)}")
            return True
        else:
            print("❌ 資料獲取失敗")
            return False
    except Exception as e:
        print(f"❌ 資料獲取錯誤: {e}")
        return False

def test_technical_indicators():
    """測試技術指標計算"""
    print("\n=== 測試技術指標計算 ===")
    
    try:
        from stock_analyzer import StockAnalyzer
        analyzer = StockAnalyzer("AAPL", period="6mo")
        analyzer.fetch_data()
        analyzer.calculate_technical_indicators()
        
        # 檢查是否有計算技術指標
        required_columns = ['SMA_20', 'SMA_50', 'MACD', 'RSI', 'BB_Upper', 'BB_Lower']
        missing_columns = [col for col in required_columns if col not in analyzer.data.columns]
        
        if not missing_columns:
            print("✅ 技術指標計算成功")
            return True
        else:
            print(f"❌ 缺少技術指標: {missing_columns}")
            return False
    except Exception as e:
        print(f"❌ 技術指標計算錯誤: {e}")
        return False

def test_signal_generation():
    """測試訊號生成"""
    print("\n=== 測試訊號生成 ===")
    
    try:
        from stock_analyzer import StockAnalyzer
        analyzer = StockAnalyzer("AAPL", period="6mo")
        analyzer.fetch_data()
        analyzer.calculate_technical_indicators()
        analyzer.generate_signals()
        
        if analyzer.signals is not None:
            print("✅ 訊號生成成功")
            current_signal = analyzer.get_current_signal()
            print(f"   當前訊號: {current_signal['signal']}")
            print(f"   訊號強度: {current_signal['strength']}")
            return True
        else:
            print("❌ 訊號生成失敗")
            return False
    except Exception as e:
        print(f"❌ 訊號生成錯誤: {e}")
        return False

def test_taiwan_stock():
    """測試台股功能"""
    print("\n=== 測試台股功能 ===")
    
    try:
        from stock_analyzer import StockAnalyzer
        analyzer = StockAnalyzer("2330.TW", period="1mo")
        if analyzer.fetch_data():
            print("✅ 台股資料獲取成功")
            return True
        else:
            print("❌ 台股資料獲取失敗")
            return False
    except Exception as e:
        print(f"❌ 台股功能錯誤: {e}")
        return False

def test_crypto():
    """測試加密貨幣功能"""
    print("\n=== 測試加密貨幣功能 ===")
    
    try:
        from stock_analyzer import StockAnalyzer
        analyzer = StockAnalyzer("BTC-USD", period="1mo")
        if analyzer.fetch_data():
            print("✅ 加密貨幣資料獲取成功")
            return True
        else:
            print("❌ 加密貨幣資料獲取失敗")
            return False
    except Exception as e:
        print(f"❌ 加密貨幣功能錯誤: {e}")
        return False

def test_stock_names():
    """測試股票原始名稱獲取"""
    print("\n=== 測試股票原始名稱 ===")
    
    test_stocks = [
        'AAPL',      # Apple Inc.
        'MSFT',      # Microsoft Corporation
        '2330.TW',   # 台積電
        'GOOGL',     # Alphabet Inc.
        'TSLA'       # Tesla, Inc.
    ]
    
    success_count = 0
    
    for symbol in test_stocks:
        try:
            from stock_analyzer import StockAnalyzer
            analyzer = StockAnalyzer(symbol)
            if analyzer.fetch_data():
                print(f"✅ {symbol} → {analyzer.long_name}")
                success_count += 1
            else:
                print(f"❌ 無法獲取 {symbol} 的資料")
        except Exception as e:
            print(f"❌ {symbol} 錯誤: {e}")
    
    return success_count >= 3  # 至少3個成功

def create_mock_data(symbol, days=250):
    """創建模擬股票數據"""
    # 創建日期範圍
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 創建模擬價格數據
    np.random.seed(42)  # 確保可重複性
    
    # 基礎價格
    base_price = 100.0
    prices = [base_price]
    
    # 生成價格序列
    for i in range(1, len(dates)):
        # 隨機價格變動
        change = np.random.normal(0, 0.02)  # 2% 標準差
        new_price = prices[-1] * (1 + change)
        prices.append(max(new_price, 1))  # 確保價格為正
    
    # 創建 OHLC 數據
    data = []
    for i, price in enumerate(prices):
        # 生成開盤、最高、最低、收盤價
        open_price = price * (1 + np.random.normal(0, 0.005))
        high_price = max(open_price, price) * (1 + abs(np.random.normal(0, 0.01)))
        low_price = min(open_price, price) * (1 - abs(np.random.normal(0, 0.01)))
        close_price = price
        
        # 生成成交量
        volume = np.random.randint(1000000, 10000000)
        
        data.append({
            'Open': open_price,
            'High': high_price,
            'Low': low_price,
            'Close': close_price,
            'Volume': volume
        })
    
    # 創建 DataFrame
    df = pd.DataFrame(data, index=dates)
    return df

def test_html_report():
    """測試 HTML 報告功能"""
    print("\n=== 測試 HTML 報告功能 ===")
    
    try:
        from stock_analyzer import StockAnalyzer
        from visualizer import StockVisualizer
        
        # 創建模擬數據
        mock_data = create_mock_data('AAPL')
        
        # 創建分析器並手動設置數據
        analyzer = StockAnalyzer('AAPL', '1y')
        analyzer.data = mock_data
        
        # 計算技術指標
        analyzer.calculate_technical_indicators()
        
        # 生成訊號
        analyzer.generate_signals()
        
        # 創建視覺化器
        visualizer = StockVisualizer(analyzer)
        
        # 生成 HTML 報告
        report_path = visualizer.create_comprehensive_html_report('test_report.html')
        
        print(f"✅ HTML 報告已生成: {report_path}")
        return True
        
    except Exception as e:
        print(f"❌ HTML 報告測試錯誤: {e}")
        return False

def test_batch_analysis():
    """測試批量分析功能"""
    print("\n=== 測試批量分析功能 ===")
    
    try:
        from stock_analyzer import StockAnalyzer
        from visualizer import StockVisualizer
        
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        analyzers = []
        
        for symbol in symbols:
            # 創建模擬數據
            mock_data = create_mock_data(symbol)
            
            # 創建分析器並手動設置數據
            analyzer = StockAnalyzer(symbol, '1y')
            analyzer.data = mock_data
            
            # 計算技術指標
            analyzer.calculate_technical_indicators()
            
            # 生成訊號
            analyzer.generate_signals()
            
            analyzers.append(analyzer)
            print(f"  ✅ {symbol} 分析完成")
        
        # 創建視覺化器
        visualizer = StockVisualizer(analyzers[0])
        
        # 生成批量 HTML 報告
        report_path = visualizer.create_batch_html_report(analyzers, 'test_batch_report.html')
        
        print(f"✅ 批量分析報告已生成: {report_path}")
        return True
        
    except Exception as e:
        print(f"❌ 批量分析測試錯誤: {e}")
        return False

def test_main_program():
    """測試主程式"""
    print("\n=== 測試主程式 ===")
    
    try:
        import main
        print("✅ 主程式導入成功")
        return True
    except ImportError as e:
        print(f"❌ 主程式導入失敗: {e}")
        return False

def demonstrate_batch_analysis():
    """演示批量分析功能"""
    print("\n" + "=" * 60)
    print("=== 批量分析功能演示 ===")
    print("=" * 60)
    
    print("\n📊 批量分析功能特色:")
    print("✅ 主程式支援: python main.py AAPL MSFT GOOGL")
    print("✅ 靈活輸入: 支援空格分隔、逗號分隔")
    print("✅ 快速分析: 預設股票組合（科技股、金融股、加密貨幣、台股）")
    print("✅ 互動輸入: 自訂股票代碼列表")
    print("✅ 結果排序: 按訊號強度排序顯示結果")
    print("✅ 統計摘要: 提供買入/賣出/持有統計")
    print("✅ CSV 匯出: 可將結果儲存為 CSV 檔案")
    
    print("\n🎯 使用範例:")
    print("1. 主程式批量分析:")
    print("   python main.py AAPL MSFT GOOGL TSLA")
    print("   python main.py 'AAPL,MSFT,GOOGL' --period 6mo")
    print()
    print("2. 專用批量分析工具:")
    print("   python batch_analysis.py")
    print("   選擇 1-4 的預設組合，或選擇 5 自訂股票代碼")
    print()
    print("3. 支援的股票類型:")
    print("   • 美股: AAPL, MSFT, GOOGL, TSLA, NVDA, META")
    print("   • 金融股: JPM, BAC, WFC, GS, MS, UNH, JNJ")
    print("   • 加密貨幣: BTC-USD, ETH-USD, BNB-USD, SOL-USD, ADA-USD")
    print("   • 台股: 2330.TW, 2317.TW, 2454.TW, 3008.TW, 2412.TW")

def demonstrate_html_reports():
    """演示 HTML 報告功能"""
    print("\n" + "=" * 60)
    print("=== HTML 報告功能演示 ===")
    print("=" * 60)
    
    print("\n📄 單一股票 HTML 報告:")
    print("使用命令: python main.py AAPL --save my_report.html")
    print("這將生成一個包含以下內容的單一 HTML 文件:")
    print("✅ 股票價格和交易訊號")
    print("✅ 技術指標圖表 (MACD, RSI, 隨機指標等)")
    print("✅ 訊號強度分析")
    print("✅ 詳細的技術指標數據")
    print("✅ 風險提醒聲明")
    print("✅ 專業的 CSS 樣式設計")
    print("✅ 響應式佈局，支援手機和電腦")
    print("✅ 所有內容都在單一 HTML 文件中，無需額外圖片")
    
    print("\n📄 批量股票 HTML 報告:")
    print("使用命令: python main.py AAPL MSFT GOOGL TSLA --save batch_report.html")
    print("這將生成一個包含以下內容的單一 HTML 文件:")
    print("✅ 多支股票的綜合分析")
    print("✅ 批量統計摘要")
    print("✅ 每支股票的詳細結果表格")
    print("✅ 所有股票的訊號強度對比圖")
    print("✅ 買入/賣出/持有統計")
    print("✅ 平均強度和強度範圍分析")
    print("✅ 專業的表格和圖表展示")
    
    print("\n🎨 HTML 報告功能特色:")
    print("🎯 單一文件: 所有內容都在一個 HTML 文件中")
    print("📊 互動圖表: 使用 Plotly 創建互動式圖表")
    print("📱 響應式設計: 支援手機、平板、電腦")
    print("🎨 專業樣式: 現代化的 CSS 設計")
    print("📈 完整分析: 包含所有技術指標和訊號")
    print("📋 詳細數據: 價格、訊號、強度等完整信息")
    print("⚠️ 風險提醒: 包含投資風險警告")
    print("💾 易於分享: 單一文件，方便傳送給客戶")

def explain_signal_algorithm():
    """詳細解釋訊號強度演算法"""
    print("\n" + "=" * 60)
    print("=== 訊號強度演算法詳細說明 ===")
    print("=" * 60)
    
    print("\n📊 演算法概述")
    print("訊號強度是一個綜合評分系統，範圍從 -100 到 +100")
    print("正值表示買入傾向，負值表示賣出傾向，0表示中性")
    
    print("\n🔧 演算法步驟")
    print("1. 計算5個技術指標的個別訊號")
    print("2. 根據權重加總各指標訊號")
    print("3. 根據總強度決定最終買賣建議")
    
    print("\n📈 技術指標及其權重")
    print("-" * 40)
    print("1. 移動平均線 (MA)     - 權重: 20")
    print("2. MACD               - 權重: 25")
    print("3. RSI                - 權重: 20")
    print("4. 布林通道 (BB)       - 權重: 15")
    print("5. 隨機指標 (Stoch)    - 權重: 20")
    print("總權重: 100")
    
    print("\n🎯 各指標訊號規則")
    print("-" * 40)
    print("每個指標的訊號值: -1 (賣出), 0 (中性), 1 (買入)")
    
    print("\n1. 移動平均線 (MA) - 權重 20")
    print("   • SMA_20 > SMA_50 → 買入訊號 (+1)")
    print("   • SMA_20 < SMA_50 → 賣出訊號 (-1)")
    print("   • 貢獻強度: ±20")
    
    print("\n2. MACD - 權重 25")
    print("   • MACD > MACD_Signal → 買入訊號 (+1)")
    print("   • MACD < MACD_Signal → 賣出訊號 (-1)")
    print("   • 貢獻強度: ±25")
    
    print("\n3. RSI - 權重 20")
    print("   • RSI < 30 → 超賣，買入訊號 (+1)")
    print("   • RSI > 70 → 超買，賣出訊號 (-1)")
    print("   • 30 ≤ RSI ≤ 70 → 中性 (0)")
    print("   • 貢獻強度: ±20")
    
    print("\n4. 布林通道 (BB) - 權重 15")
    print("   • 價格 < BB_Lower → 買入訊號 (+1)")
    print("   • 價格 > BB_Upper → 賣出訊號 (-1)")
    print("   • BB_Lower ≤ 價格 ≤ BB_Upper → 中性 (0)")
    print("   • 貢獻強度: ±15")
    
    print("\n5. 隨機指標 (Stoch) - 權重 20")
    print("   • Stoch_K < 20 且 Stoch_D < 20 → 買入訊號 (+1)")
    print("   • Stoch_K > 80 且 Stoch_D > 80 → 賣出訊號 (-1)")
    print("   • 其他情況 → 中性 (0)")
    print("   • 貢獻強度: ±20")
    
    print("\n🧮 強度計算公式")
    print("-" * 40)
    print("總強度 = MA_Signal × 20 + MACD_Signal × 25 + RSI_Signal × 20 + BB_Signal × 15 + Stoch_Signal × 20")
    
    print("\n📊 最終訊號判斷")
    print("-" * 40)
    print("• 強度 ≥ +20 → 買入訊號")
    print("• 強度 ≤ -20 → 賣出訊號")
    print("• -20 < 強度 < +20 → 持有訊號")
    
    print("\n💡 演算法特點")
    print("-" * 40)
    print("✅ 綜合多個技術指標，避免單一指標的誤判")
    print("✅ 權重分配反映各指標的重要性")
    print("✅ MACD權重最高(25)，因為趨勢指標較可靠")
    print("✅ 布林通道權重最低(15)，因為波動較大")
    print("✅ 閾值±20提供適當的緩衝區間")

def demonstrate_usage_examples():
    """演示使用方法"""
    print("\n" + "=" * 60)
    print("=== 完整使用方法演示 ===")
    print("=" * 60)
    
    print("\n🚀 快速開始:")
    print("1. 單一股票分析:")
    print("   python main.py AAPL")
    print("   python main.py AAPL --plot")
    print("   python main.py AAPL --save my_report.html")
    print()
    print("2. 批量股票分析:")
    print("   python main.py AAPL MSFT GOOGL TSLA")
    print("   python main.py 'AAPL,MSFT,GOOGL' --save batch.html")
    print()
    print("3. 指定分析期間:")
    print("   python main.py AAPL --period 6mo")
    print("   python main.py AAPL --period 1y --plot")
    print()
    print("4. 互動模式:")
    print("   python main.py")
    print("   然後選擇分析選項")
    print()
    print("5. 台股和加密貨幣:")
    print("   python main.py 2330.TW --period 1y")
    print("   python main.py BTC-USD --period 6mo")
    print()
    print("6. 每日報告模式:")
    print("   python main.py AAPL --save-daily-report")
    print("   python main.py 'AAPL,MSFT,GOOGL' --save-daily-report")
    
    print("\n📋 支援的股票代碼格式:")
    print("• 美股: AAPL, GOOGL, MSFT, TSLA, NVDA, META")
    print("• 台股: 2330.TW, 2317.TW, 2454.TW, 3008.TW, 2412.TW")
    print("• 港股: 0700.HK, 0941.HK")
    print("• 加密貨幣: BTC-USD, ETH-USD, BNB-USD, SOL-USD, ADA-USD")
    print("• 其他: 請參考 Yahoo Finance 代碼格式")
    
    print("\n📊 訊號說明:")
    print("• 買入 (1): 綜合指標顯示強烈買入訊號")
    print("• 賣出 (-1): 綜合指標顯示強烈賣出訊號")
    print("• 持有 (0): 指標不明確，建議觀望")
    print()
    print("📈 訊號強度:")
    print("• -100 到 -30: 強烈賣出訊號")
    print("• -30 到 30: 中性區域，建議持有")
    print("• 30 到 100: 強烈買入訊號")

def main():
    """執行所有測試和演示"""
    print("=== AIStock 整合測試程序 ===")
    print("包含功能測試、使用方法演示和算法說明")
    print("開始執行所有測試...\n")
    
    tests = [
        ("依賴包導入", test_imports),
        ("股票分析器", test_stock_analyzer),
        ("視覺化模組", test_visualizer),
        ("資料獲取", test_data_fetch),
        ("技術指標計算", test_technical_indicators),
        ("訊號生成", test_signal_generation),
        ("台股功能", test_taiwan_stock),
        ("加密貨幣功能", test_crypto),
        ("股票名稱獲取", test_stock_names),
        ("HTML 報告", test_html_report),
        ("批量分析", test_batch_analysis),
        ("主程式", test_main_program)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
    
    print(f"\n=== 測試結果 ===")
    print(f"通過: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有測試通過！系統運行正常。")
        
        # 執行功能演示
        demonstrate_batch_analysis()
        demonstrate_html_reports()
        explain_signal_algorithm()
        demonstrate_usage_examples()
        
        print("\n" + "=" * 60)
        print("🎉 測試和演示完成！")
        print("=" * 60)
        print("\n您可以開始使用系統了：")
        print("1. 執行 python main.py 進入互動模式")
        print("2. 執行 python main.py AAPL --plot 分析蘋果股票")
        print("3. 執行 python examples/example_usage.py 查看使用範例")
        print("4. 執行 python main.py AAPL MSFT GOOGL 進行批量分析")
        print("5. 執行 python main.py AAPL --save report.html 生成HTML報告")
    else:
        print("⚠️ 部分測試失敗，請檢查安裝和設定。")
        print("建議執行: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
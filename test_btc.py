#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 BTC 在 Yahoo Finance 上的可用性
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_analyzer import StockAnalyzer
import yfinance as yf
import pandas as pd

def test_btc_availability():
    """測試 BTC 的可用性"""
    print("=== 測試 BTC 在 Yahoo Finance 上的可用性 ===")
    
    # 測試不同的 BTC 代碼
    btc_symbols = [
        "BTC-USD",      # 比特幣美元對
        "BTCUSD=X",     # 比特幣美元匯率
        "BTC",          # 簡稱
        "BTC-USD.P",    # 預託證券
    ]
    
    for symbol in btc_symbols:
        print(f"\n📊 測試 {symbol}...")
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 獲取基本資訊
            print(f"  名稱: {info.get('longName', 'N/A')}")
            print(f"  簡稱: {info.get('shortName', 'N/A')}")
            print(f"  類型: {info.get('quoteType', 'N/A')}")
            print(f"  市場: {info.get('market', 'N/A')}")
            
            # 獲取歷史資料
            hist = ticker.history(period="1mo")
            if not hist.empty:
                print(f"  資料筆數: {len(hist)}")
                print(f"  最新價格: ${hist['Close'].iloc[-1]:.2f}")
                print(f"  最高價: ${hist['High'].max():.2f}")
                print(f"  最低價: ${hist['Low'].min():.2f}")
                print(f"  成交量: {hist['Volume'].iloc[-1]:,.0f}")
                print("  ✅ 可用")
            else:
                print("  ❌ 無資料")
                
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")

def test_btc_analysis():
    """使用我們的系統分析 BTC"""
    print("\n=== 使用 AIStock 系統分析 BTC ===")
    
    # 測試 BTC-USD
    symbol = "BTC-USD"
    period = "6mo"
    
    print(f"股票代碼: {symbol}")
    print(f"分析期間: {period}")
    print("-" * 50)
    
    # 創建分析器
    analyzer = StockAnalyzer(symbol, period)
    
    # 執行完整分析
    if analyzer.run_analysis():
        print("✅ 分析成功！")
        
        # 獲取當前訊號
        current_signal = analyzer.get_current_signal()
        print(f"\n📊 當前訊號詳情:")
        print(f"日期: {current_signal['date']}")
        print(f"價格: ${current_signal['price']:,.2f}")
        print(f"建議: {current_signal['signal']}")
        print(f"強度: {current_signal['strength']}")
        
        # 獲取訊號摘要
        summary = analyzer.get_signal_summary(30)
        print(f"\n📈 最近30天摘要:")
        print(f"買入訊號: {summary['buy_signals']} 次")
        print(f"賣出訊號: {summary['sell_signals']} 次")
        print(f"持有天數: {summary['hold_days']} 天")
        print(f"平均強度: {summary['avg_strength']}")
        
        # 檢查訊號分布
        signal_counts = analyzer.signals['Signal'].value_counts()
        print(f"\n📊 整體訊號分布:")
        print(f"買入訊號: {signal_counts.get(1, 0)} 次")
        print(f"賣出訊號: {signal_counts.get(-1, 0)} 次")
        print(f"持有天數: {signal_counts.get(0, 0)} 天")
        
        return True
    else:
        print("❌ 分析失敗")
        return False

def test_crypto_symbols():
    """測試其他加密貨幣"""
    print("\n=== 測試其他加密貨幣 ===")
    
    crypto_symbols = [
        "ETH-USD",      # 以太坊
        "BNB-USD",      # 幣安幣
        "ADA-USD",      # 卡達諾
        "SOL-USD",      # 索拉納
        "DOT-USD",      # 波卡
        "DOGE-USD",     # 狗狗幣
    ]
    
    for symbol in crypto_symbols:
        print(f"\n📈 測試 {symbol}...")
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                print(f"  當前價格: ${price:.4f}")
                print("  ✅ 可用")
            else:
                print("  ❌ 無資料")
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")

def test_btc_with_visualization():
    """測試 BTC 分析並生成圖表"""
    print("\n=== 測試 BTC 視覺化分析 ===")
    
    symbol = "BTC-USD"
    period = "3mo"
    
    print(f"分析 {symbol} ({period})...")
    
    analyzer = StockAnalyzer(symbol, period)
    
    if analyzer.run_analysis():
        print("✅ 分析成功！正在生成圖表...")
        
        # 導入視覺化模組
        from visualizer import StockVisualizer
        visualizer = StockVisualizer(analyzer)
        
        # 生成圖表
        visualizer.plot_candlestick_with_signals("btc_analysis.html")
        print("✅ K線圖已生成: btc_analysis.html")
        
        # 生成技術指標圖
        visualizer.plot_technical_indicators()
        print("✅ 技術指標圖已生成")
        
        # 生成訊號強度圖
        visualizer.plot_signal_strength()
        print("✅ 訊號強度圖已生成")
        
        # 創建儀表板
        visualizer.create_dashboard()
        print("✅ 儀表板已生成")
        
        return True
    else:
        print("❌ 分析失敗")
        return False

if __name__ == "__main__":
    # 測試 BTC 可用性
    test_btc_availability()
    
    # 測試 BTC 分析
    test_btc_analysis()
    
    # 測試其他加密貨幣
    test_crypto_symbols()
    
    # 詢問是否要生成圖表
    print(f"\n是否要生成 BTC 的視覺化圖表? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice in ['y', 'yes', '是']:
        test_btc_with_visualization()
    
    print("\n🎉 BTC 測試完成！") 
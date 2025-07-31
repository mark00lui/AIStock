#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIStock 使用範例
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from stock_analyzer import StockAnalyzer
from visualizer import StockVisualizer

def example_single_stock():
    """單一股票分析範例"""
    print("=== 單一股票分析範例 ===")
    
    # 分析蘋果股票
    symbol = "AAPL"
    analyzer = StockAnalyzer(symbol, period='6mo')
    
    # 執行完整分析
    if analyzer.run_analysis():
        # 獲取當前訊號
        current_signal = analyzer.get_current_signal()
        print(f"\n當前訊號詳情:")
        print(f"日期: {current_signal['date']}")
        print(f"價格: ${current_signal['price']}")
        print(f"建議: {current_signal['signal']}")
        print(f"強度: {current_signal['strength']}")
        
        # 獲取訊號摘要
        summary = analyzer.get_signal_summary(30)
        print(f"\n最近30天摘要:")
        print(f"買入訊號: {summary['buy_signals']} 次")
        print(f"賣出訊號: {summary['sell_signals']} 次")
        print(f"持有天數: {summary['hold_days']} 天")

def example_taiwan_stock():
    """台股分析範例"""
    print("\n=== 台股分析範例 ===")
    
    # 分析台積電
    symbol = "2330.TW"
    analyzer = StockAnalyzer(symbol, period='1y')
    
    if analyzer.run_analysis():
        current_signal = analyzer.get_current_signal()
        print(f"台積電 ({symbol}) 分析結果:")
        print(f"當前價格: NT${current_signal['price']}")
        print(f"建議動作: {current_signal['signal']}")
        print(f"訊號強度: {current_signal['strength']}")

def example_visualization():
    """視覺化範例"""
    print("\n=== 視覺化範例 ===")
    
    # 分析特斯拉股票
    symbol = "TSLA"
    analyzer = StockAnalyzer(symbol, period='3mo')
    
    if analyzer.run_analysis():
        # 創建視覺化器
        visualizer = StockVisualizer(analyzer)
        
        # 繪製各種圖表
        print("正在生成圖表...")
        
        # 儲存K線圖
        visualizer.plot_candlestick_with_signals("tsla_analysis.html")
        
        # 顯示技術指標圖
        visualizer.plot_technical_indicators()
        
        # 顯示訊號強度圖
        visualizer.plot_signal_strength()
        
        # 創建儀表板
        visualizer.create_dashboard()

def example_batch_analysis():
    """批量分析範例"""
    print("\n=== 批量分析範例 ===")
    
    # 分析多支股票
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    results = []
    
    for symbol in symbols:
        print(f"分析 {symbol}...")
        analyzer = StockAnalyzer(symbol, period='1mo')
        
        if analyzer.run_analysis():
            current_signal = analyzer.get_current_signal()
            results.append({
                'symbol': symbol,
                'price': current_signal['price'],
                'signal': current_signal['signal'],
                'strength': current_signal['strength']
            })
    
    # 顯示結果
    print("\n批量分析結果:")
    print(f"{'股票代碼':<8} {'價格':<10} {'訊號':<8} {'強度':<8}")
    print("-" * 40)
    for result in results:
        print(f"{result['symbol']:<8} ${result['price']:<9} {result['signal']:<8} {result['strength']:<8}")

def example_custom_analysis():
    """自訂分析範例"""
    print("\n=== 自訂分析範例 ===")
    
    # 分析 NVIDIA
    symbol = "NVDA"
    analyzer = StockAnalyzer(symbol, period='2y')
    
    # 只獲取資料，不執行完整分析
    if analyzer.fetch_data():
        print(f"成功獲取 {symbol} 的資料")
        
        # 計算技術指標
        analyzer.calculate_technical_indicators()
        print("技術指標計算完成")
        
        # 生成訊號
        analyzer.generate_signals()
        print("訊號生成完成")
        
        # 獲取特定資訊
        latest_data = analyzer.data.iloc[-1]
        print(f"\n最新資料:")
        print(f"收盤價: ${latest_data['Close']:.2f}")
        print(f"RSI: {latest_data['RSI']:.2f}")
        print(f"MACD: {latest_data['MACD']:.4f}")
        print(f"布林通道位置: {((latest_data['Close'] - latest_data['BB_Lower']) / (latest_data['BB_Upper'] - latest_data['BB_Lower']) * 100):.1f}%")

if __name__ == "__main__":
    print("AIStock 使用範例")
    print("=" * 50)
    
    # 執行各種範例
    example_single_stock()
    example_taiwan_stock()
    example_custom_analysis()
    example_batch_analysis()
    
    # 視覺化範例 (會開啟瀏覽器)
    print("\n是否要執行視覺化範例? (會開啟瀏覽器顯示圖表)")
    choice = input("請輸入 y/n: ").strip().lower()
    if choice in ['y', 'yes', '是']:
        example_visualization()
    
    print("\n範例執行完成！") 
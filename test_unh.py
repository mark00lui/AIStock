#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNH 股票測試腳本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_analyzer import StockAnalyzer
from visualizer import StockVisualizer

def test_unh_stock():
    """測試 UNH 股票分析"""
    print("=== UNH (UnitedHealth Group) 股票分析 ===")
    
    # 分析 UNH 股票
    symbol = "UNH"
    period = "1y"  # 可以改為 6mo, 2y, 5y 等
    
    print(f"股票代碼: {symbol}")
    print(f"分析期間: {period}")
    print("-" * 50)
    
    # 創建分析器
    analyzer = StockAnalyzer(symbol, period)
    
    # 執行分析
    if analyzer.run_analysis():
        print("✅ 分析成功！")
        
        # 獲取當前訊號
        current_signal = analyzer.get_current_signal()
        print(f"\n📊 當前訊號詳情:")
        print(f"日期: {current_signal['date']}")
        print(f"價格: ${current_signal['price']:.2f}")
        print(f"建議: {current_signal['signal']}")
        print(f"強度: {current_signal['strength']}")
        
        # 獲取訊號摘要
        summary = analyzer.get_signal_summary(30)
        print(f"\n📈 最近30天摘要:")
        print(f"買入訊號: {summary['buy_signals']} 次")
        print(f"賣出訊號: {summary['sell_signals']} 次")
        print(f"持有天數: {summary['hold_days']} 天")
        
        # 顯示技術指標
        latest_data = analyzer.data.iloc[-1]
        print(f"\n🔧 技術指標:")
        print(f"RSI: {latest_data['RSI']:.2f}")
        print(f"MACD: {latest_data['MACD']:.4f}")
        print(f"布林通道位置: {((latest_data['Close'] - latest_data['BB_Lower']) / (latest_data['BB_Upper'] - latest_data['BB_Lower']) * 100):.1f}%")
        
        # 詢問是否要顯示圖表
        print(f"\n是否要顯示圖表? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice in ['y', 'yes', '是']:
            print("正在生成圖表...")
            visualizer = StockVisualizer(analyzer)
            
            # 繪製K線圖與訊號
            visualizer.plot_candlestick_with_signals("unh_analysis.html")
            
            # 繪製技術指標
            visualizer.plot_technical_indicators()
            
            # 繪製訊號強度
            visualizer.plot_signal_strength()
            
            # 創建儀表板
            visualizer.create_dashboard()
            
            print("✅ 圖表已生成！請查看瀏覽器中的圖表。")
        
        return True
    else:
        print("❌ 分析失敗，請檢查股票代碼是否正確")
        return False

def test_unh_different_periods():
    """測試不同期間的 UNH 分析"""
    print("\n=== 測試不同期間的 UNH 分析 ===")
    
    periods = ["3mo", "6mo", "1y", "2y"]
    symbol = "UNH"
    
    for period in periods:
        print(f"\n📅 分析期間: {period}")
        analyzer = StockAnalyzer(symbol, period)
        
        if analyzer.run_analysis():
            current_signal = analyzer.get_current_signal()
            print(f"價格: ${current_signal['price']:.2f} | 訊號: {current_signal['signal']} | 強度: {current_signal['strength']}")
        else:
            print("分析失敗")

if __name__ == "__main__":
    # 執行主要測試
    test_unh_stock()
    
    # 詢問是否要測試不同期間
    print(f"\n是否要測試不同期間的分析? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice in ['y', 'yes', '是']:
        test_unh_different_periods()
    
    print("\n🎉 UNH 股票測試完成！") 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復後的訊號生成
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_analyzer import StockAnalyzer

def test_fixed_signals():
    """測試修復後的訊號生成"""
    print("=== 測試修復後的訊號生成 ===")
    
    # 分析 UNH 股票
    symbol = "UNH"
    period = "1y"
    
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
        print(f"價格: ${current_signal['price']}")
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
        
        # 顯示最近10天的訊號
        print(f"\n📅 最近10天訊號:")
        recent_signals = analyzer.signals.tail(10)
        for i, row in recent_signals.iterrows():
            signal_map = {1: "買入", -1: "賣出", 0: "持有"}
            print(f"{i.strftime('%Y-%m-%d')}: {signal_map[row['Signal']]} (強度: {row['Strength']:.1f})")
        
        return True
    else:
        print("❌ 分析失敗")
        return False

def test_multiple_stocks():
    """測試多支股票的訊號生成"""
    print("\n=== 測試多支股票的訊號生成 ===")
    
    symbols = ["UNH", "AAPL", "MSFT", "GOOGL", "TSLA"]
    
    for symbol in symbols:
        print(f"\n📈 分析 {symbol}...")
        analyzer = StockAnalyzer(symbol, "6mo")
        
        if analyzer.run_analysis():
            current_signal = analyzer.get_current_signal()
            signal_counts = analyzer.signals['Signal'].value_counts()
            
            print(f"  當前價格: ${current_signal['price']}")
            print(f"  建議: {current_signal['signal']}")
            print(f"  強度: {current_signal['strength']}")
            print(f"  訊號分布: 買入={signal_counts.get(1, 0)}, 賣出={signal_counts.get(-1, 0)}, 持有={signal_counts.get(0, 0)}")
        else:
            print(f"  ❌ 分析失敗")

if __name__ == "__main__":
    test_fixed_signals()
    test_multiple_stocks()
    print("\n🎉 修復測試完成！") 
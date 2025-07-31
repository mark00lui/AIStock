#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試每日報告功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime
from stock_analyzer import StockAnalyzer
from visualizer import StockVisualizer

def test_daily_report():
    """測試每日報告功能"""
    
    print("=== 每日報告功能測試 ===")
    
    # 測試單一股票每日報告
    print("\n1. 測試單一股票每日報告...")
    try:
        analyzer = StockAnalyzer("AAPL")
        if analyzer.run_analysis():
            visualizer = StockVisualizer(analyzer)
            daily_report_path = f"{datetime.now().strftime('%Y-%m-%d')}_report.html"
            result_path = visualizer.create_comprehensive_html_report(daily_report_path)
            print(f"✅ 單一股票每日報告已生成: {result_path}")
        else:
            print("❌ 單一股票分析失敗")
    except Exception as e:
        print(f"❌ 單一股票測試錯誤: {e}")
    
    # 測試批量分析每日報告
    print("\n2. 測試批量分析每日報告...")
    try:
        analyzers = []
        symbols = ["AAPL", "MSFT"]
        
        for symbol in symbols:
            analyzer = StockAnalyzer(symbol)
            if analyzer.run_analysis():
                analyzers.append(analyzer)
                print(f"  ✅ {symbol} 分析完成")
            else:
                print(f"  ❌ {symbol} 分析失敗")
        
        if analyzers:
            visualizer = StockVisualizer(analyzers[0])
            daily_report_path = f"{datetime.now().strftime('%Y-%m-%d')}_batch_report.html"
            result_path = visualizer.create_batch_html_report(analyzers, daily_report_path)
            print(f"✅ 批量分析每日報告已生成: {result_path}")
        else:
            print("❌ 沒有成功的分析結果")
    except Exception as e:
        print(f"❌ 批量分析測試錯誤: {e}")
    
    print("\n=== 測試完成 ===")
    print("請檢查生成的 HTML 報告文件")

if __name__ == "__main__":
    test_daily_report() 
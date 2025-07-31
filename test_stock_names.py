#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試股票原始名稱功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_analyzer import StockAnalyzer

def test_stock_names():
    """測試股票原始名稱獲取"""
    
    test_stocks = [
        'AAPL',      # Apple Inc.
        'MSFT',      # Microsoft Corporation
        '2330.TW',   # 台積電
        'GOOGL',     # Alphabet Inc.
        'TSLA'       # Tesla, Inc.
    ]
    
    print("=== 股票原始名稱測試 ===")
    
    for symbol in test_stocks:
        print(f"\n測試: {symbol}")
        try:
            analyzer = StockAnalyzer(symbol)
            if analyzer.fetch_data():
                print(f"✅ {symbol} → {analyzer.long_name}")
            else:
                print(f"❌ 無法獲取 {symbol} 的資料")
        except Exception as e:
            print(f"❌ 錯誤: {e}")
    
    print("\n測試完成")

if __name__ == "__main__":
    test_stock_names() 
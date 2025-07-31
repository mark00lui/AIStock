#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 HTML 報告功能
使用模擬數據來驗證報告生成
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加 src 目錄到路徑
sys.path.append('src')

from stock_analyzer import StockAnalyzer
from visualizer import StockVisualizer

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

def test_single_stock_report():
    """測試單一股票 HTML 報告"""
    print("=== 測試單一股票 HTML 報告 ===")
    
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
    report_path = visualizer.create_comprehensive_html_report('test_single_report.html')
    
    print(f"✅ 單一股票報告已生成: {report_path}")
    return report_path

def test_batch_stock_report():
    """測試批量股票 HTML 報告"""
    print("\n=== 測試批量股票 HTML 報告 ===")
    
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
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
        print(f"✅ {symbol} 分析完成")
    
    # 創建視覺化器
    visualizer = StockVisualizer(analyzers[0])
    
    # 生成批量 HTML 報告
    report_path = visualizer.create_batch_html_report(analyzers, 'test_batch_report.html')
    
    print(f"✅ 批量股票報告已生成: {report_path}")
    return report_path

def main():
    """主測試函數"""
    print("AIStock HTML 報告功能測試")
    print("=" * 50)
    
    try:
        # 測試單一股票報告
        single_report = test_single_stock_report()
        
        # 測試批量股票報告
        batch_report = test_batch_stock_report()
        
        print("\n" + "=" * 50)
        print("🎉 所有測試通過！HTML 報告功能正常！")
        print("=" * 50)
        print(f"\n生成的報告文件:")
        print(f"1. 單一股票報告: {single_report}")
        print(f"2. 批量股票報告: {batch_report}")
        print(f"\n請在瀏覽器中打開這些 HTML 文件查看結果")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
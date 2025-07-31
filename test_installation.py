#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIStock 安裝測試腳本
"""

import sys
import os

def test_imports():
    """測試所有依賴包的導入"""
    print("=== 測試依賴包導入 ===")
    
    try:
        import pandas as pd
        print("✅ pandas 導入成功")
    except ImportError as e:
        print(f"❌ pandas 導入失敗: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy 導入成功")
    except ImportError as e:
        print(f"❌ numpy 導入失敗: {e}")
        return False
    
    try:
        import yfinance as yf
        print("✅ yfinance 導入成功")
    except ImportError as e:
        print(f"❌ yfinance 導入失敗: {e}")
        return False
    
    try:
        import matplotlib
        print("✅ matplotlib 導入成功")
    except ImportError as e:
        print(f"❌ matplotlib 導入失敗: {e}")
        return False
    
    try:
        import seaborn as sns
        print("✅ seaborn 導入成功")
    except ImportError as e:
        print(f"❌ seaborn 導入失敗: {e}")
        return False
    
    try:
        import ta
        print("✅ ta 導入成功")
    except ImportError as e:
        print(f"❌ ta 導入失敗: {e}")
        return False
    
    try:
        import sklearn
        print("✅ scikit-learn 導入成功")
    except ImportError as e:
        print(f"❌ scikit-learn 導入失敗: {e}")
        return False
    
    try:
        import plotly
        print("✅ plotly 導入成功")
    except ImportError as e:
        print(f"❌ plotly 導入失敗: {e}")
        return False
    
    try:
        import dash
        print("✅ dash 導入成功")
    except ImportError as e:
        print(f"❌ dash 導入失敗: {e}")
        return False
    
    return True

def test_stock_analyzer():
    """測試股票分析器"""
    print("\n=== 測試股票分析器 ===")
    
    try:
        sys.path.append('src')
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
        sys.path.append('src')
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

def test_main_program():
    """測試主程式"""
    print("\n=== 測試主程式 ===")
    
    try:
        import main
        print("✅ 主程式導入成功")
    except ImportError as e:
        print(f"❌ 主程式導入失敗: {e}")
        return False
    
    return True

def main():
    """主測試函數"""
    print("AIStock 安裝測試")
    print("=" * 50)
    
    # 測試依賴包
    if not test_imports():
        print("\n❌ 依賴包測試失敗")
        return False
    
    # 測試股票分析器
    if not test_stock_analyzer():
        print("\n❌ 股票分析器測試失敗")
        return False
    
    # 測試視覺化模組
    if not test_visualizer():
        print("\n❌ 視覺化模組測試失敗")
        return False
    
    # 測試主程式
    if not test_main_program():
        print("\n❌ 主程式測試失敗")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有測試通過！AIStock 安裝成功！")
    print("=" * 50)
    print("\n使用方式:")
    print("1. 單一股票分析: python main.py AAPL")
    print("2. 批量分析: python main.py AAPL MSFT GOOGL")
    print("3. 互動模式: python main.py")
    print("4. 顯示圖表: python main.py AAPL --plot")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
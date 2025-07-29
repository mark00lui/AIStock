#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIStock 系統測試腳本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """測試模組導入"""
    print("測試模組導入...")
    try:
        from stock_analyzer import StockAnalyzer
        from visualizer import StockVisualizer
        print("✅ 模組導入成功")
        return True
    except ImportError as e:
        print(f"❌ 模組導入失敗: {e}")
        return False

def test_data_fetch():
    """測試資料獲取"""
    print("\n測試資料獲取...")
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
    print("\n測試技術指標計算...")
    try:
        from stock_analyzer import StockAnalyzer
        analyzer = StockAnalyzer("AAPL", period="1mo")
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
    print("\n測試訊號生成...")
    try:
        from stock_analyzer import StockAnalyzer
        analyzer = StockAnalyzer("AAPL", period="1mo")
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

def test_visualization():
    """測試視覺化功能"""
    print("\n測試視覺化功能...")
    try:
        from stock_analyzer import StockAnalyzer
        from visualizer import StockVisualizer
        
        analyzer = StockAnalyzer("AAPL", period="1mo")
        analyzer.run_analysis()
        
        visualizer = StockVisualizer(analyzer)
        print("✅ 視覺化器創建成功")
        return True
    except Exception as e:
        print(f"❌ 視覺化功能錯誤: {e}")
        return False

def test_taiwan_stock():
    """測試台股功能"""
    print("\n測試台股功能...")
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

def main():
    """執行所有測試"""
    print("=== AIStock 系統測試 ===")
    print("開始執行系統測試...\n")
    
    tests = [
        ("模組導入", test_imports),
        ("資料獲取", test_data_fetch),
        ("技術指標計算", test_technical_indicators),
        ("訊號生成", test_signal_generation),
        ("視覺化功能", test_visualization),
        ("台股功能", test_taiwan_stock)
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
        print("\n您可以開始使用系統了：")
        print("1. 執行 python main.py 進入互動模式")
        print("2. 執行 python main.py AAPL --plot 分析蘋果股票")
        print("3. 執行 python examples/example_usage.py 查看使用範例")
    else:
        print("⚠️ 部分測試失敗，請檢查安裝和設定。")
        print("建議執行: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIStock - 整合測試程序
展示所有功能的完整演示
"""

import sys
import os
import argparse
from datetime import datetime

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_analyzer import StockAnalyzer
from visualizer import StockVisualizer
from left_analysis import analyze_stock, analyze_multiple_stocks

def print_header(title):
    """打印標題"""
    print("\n" + "=" * 60)
    print(f"=== {title} ===")
    print("=" * 60)

def print_section(title):
    """打印章節標題"""
    print(f"\n--- {title} ---")

def test_single_stock_analysis():
    """測試單一股票分析"""
    print_header("單一股票分析測試")
    
    # 測試股票
    symbol = "AAPL"
    print(f"分析股票: {symbol}")
    
    try:
        # 創建分析器
        analyzer = StockAnalyzer(symbol, period='1y')
        
        # 執行分析
        if analyzer.run_analysis():
            print(f"✅ 分析成功")
            
            # 獲取當前訊號
            current_signal = analyzer.get_current_signal()
            summary = analyzer.get_signal_summary()
            
            print(f"股票名稱: {analyzer.long_name}")
            print(f"當前價格: ${current_signal['price']:.2f}")
            print(f"建議動作: {current_signal['signal']}")
            print(f"訊號強度: {current_signal['strength']}")
            print(f"分析日期: {current_signal['date']}")
            
            # 顯示技術指標摘要
            print_section("技術指標摘要")
            print(f"RSI: {summary.get('rsi', 'N/A')}")
            print(f"MACD: {summary.get('macd', 'N/A')}")
            print(f"SMA_20: {summary.get('sma_20', 'N/A')}")
            print(f"SMA_50: {summary.get('sma_50', 'N/A')}")
            
            return analyzer
        else:
            print("❌ 分析失敗")
            return None
            
    except Exception as e:
        print(f"❌ 分析時發生錯誤: {e}")
        return None

def test_left_analysis():
    """測試左側分析"""
    print_header("左側分析測試")
    
    symbol = "AAPL"
    print(f"分析股票: {symbol}")
    
    try:
        # 執行左側分析
        result = analyze_stock(symbol)
        
        if result and 'timeframes' in result:
            print("✅ 左側分析成功")
            
            # 顯示各時間範圍的預估
            for timeframe_key, timeframe_data in result['timeframes'].items():
                print_section(f"{timeframe_data['timeframe']}預估")
                print(f"平均目標價: ${timeframe_data.get('target_mean', 0):.2f}")
                print(f"最高目標價: ${timeframe_data.get('target_high', 0):.2f}")
                print(f"最低目標價: ${timeframe_data.get('target_low', 0):.2f}")
                print(f"預估EPS: ${timeframe_data.get('future_eps', 0):.2f}")
            
            # 顯示基本面數據
            if 'fundamentals' in result:
                fundamentals = result['fundamentals']
                print_section("基本面數據")
                print(f"Forward EPS: ${fundamentals.get('forward_eps', 0):.2f}")
                print(f"Forward P/E: {fundamentals.get('forward_pe', 0):.2f}")
                print(f"Current P/E: {fundamentals.get('current_pe', 0):.2f}")
            
            return result
        else:
            print("❌ 左側分析失敗")
            return None
            
    except Exception as e:
        print(f"❌ 左側分析時發生錯誤: {e}")
        return None

def test_visualization():
    """測試視覺化功能"""
    print_header("視覺化功能測試")
    
    symbol = "AAPL"
    print(f"分析股票: {symbol}")
    
    try:
        # 創建分析器
        analyzer = StockAnalyzer(symbol, period='1y')
        analyzer.run_analysis()
        
        # 創建視覺化器
        visualizer = StockVisualizer()
        
        # 生成單一股票報告
        print_section("生成單一股票報告")
        single_report = visualizer.create_single_stock_report(analyzer, 'test_single_stock.html')
        if single_report:
            print(f"✅ 單一股票報告已生成: {single_report}")
        else:
            print("❌ 單一股票報告生成失敗")
        
        return visualizer
        
    except Exception as e:
        print(f"❌ 視覺化測試時發生錯誤: {e}")
        return None

def test_batch_analysis():
    """測試批量分析"""
    print_header("批量分析測試")
    
    # 測試股票列表
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    print(f"分析股票: {', '.join(symbols)}")
    
    try:
        analyzers = []
        
        # 分析每個股票
        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] 分析 {symbol}...")
            
            analyzer = StockAnalyzer(symbol, period='1y')
            if analyzer.run_analysis():
                current_signal = analyzer.get_current_signal()
                analyzers.append(analyzer)
                print(f"  ✅ {symbol}: ${current_signal['price']:.2f} | {current_signal['signal']} | 強度: {current_signal['strength']}")
            else:
                print(f"  ❌ {symbol}: 分析失敗")
        
        if analyzers:
            print_section("生成批量報告")
            visualizer = StockVisualizer()
            batch_report = visualizer.create_batch_html_report(analyzers, 'test_batch_analysis.html')
            
            if batch_report:
                print(f"✅ 批量報告已生成: {batch_report}")
                
                # 檢查文件大小
                file_size = os.path.getsize(batch_report)
                print(f"📁 報告文件大小: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                
                # 檢查文件內容
                with open(batch_report, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"📄 文件內容長度: {len(content):,} 字符")
                
                # 檢查關鍵元素
                checks = [
                    ('AAPL', 'AAPL'),
                    ('MSFT', 'MSFT'), 
                    ('GOOGL', 'GOOGL'),
                    ('生成日期', '生成日期'),
                    ('技術分析摘要', '技術分析摘要'),
                    ('左側分析摘要', '左側分析摘要'),
                    ('價格比較圖表', '價格比較圖表'),
                    ('技術分析圖表', '技術分析圖表'),
                    ('price-chart-AAPL', 'AAPL 價格圖表'),
                    ('technical-chart-AAPL', 'AAPL 技術圖表'),
                    ('price-chart-MSFT', 'MSFT 價格圖表'),
                    ('technical-chart-MSFT', 'MSFT 技術圖表'),
                    ('price-chart-GOOGL', 'GOOGL 價格圖表'),
                    ('technical-chart-GOOGL', 'GOOGL 技術圖表'),
                    ('Plotly.newPlot', 'Plotly 圖表代碼')
                ]
                
                for check, description in checks:
                    if check in content:
                        print(f"  ✅ {description}")
                    else:
                        print(f"  ❌ {description}")
                
            else:
                print("❌ 批量報告生成失敗")
        else:
            print("❌ 沒有成功分析任何股票")
            
        return analyzers
        
    except Exception as e:
        print(f"❌ 批量分析時發生錯誤: {e}")
        return None

def test_left_analysis_batch():
    """測試批量左側分析"""
    print_header("批量左側分析測試")
    
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    print(f"分析股票: {', '.join(symbols)}")
    
    try:
        # 執行批量左側分析
        results = analyze_multiple_stocks(symbols)
        
        if results and 'results' in results:
            print("✅ 批量左側分析成功")
            
            for stock_result in results['results']:
                symbol = stock_result['symbol']
                timeframes = stock_result.get('timeframes', {})
                
                print_section(f"{symbol} 分析結果")
                
                if '1_year' in timeframes:
                    year1 = timeframes['1_year']
                    print(f"1年目標價: ${year1.get('target_mean', 0):.2f}")
                    print(f"預估EPS: ${year1.get('future_eps', 0):.2f}")
                
                if '2_year' in timeframes:
                    year2 = timeframes['2_year']
                    print(f"2年目標價: ${year2.get('target_mean', 0):.2f}")
                
                if '3_year' in timeframes:
                    year3 = timeframes['3_year']
                    print(f"3年目標價: ${year3.get('target_mean', 0):.2f}")
            
            return results
        else:
            print("❌ 批量左側分析失敗")
            return None
            
    except Exception as e:
        print(f"❌ 批量左側分析時發生錯誤: {e}")
        return None

def test_main_program():
    """測試主程式功能"""
    print_header("主程式功能測試")
    
    print("測試主程式的各種功能...")
    
    # 模擬主程式的功能
    symbols = ['AAPL', 'MSFT']
    
    try:
        analyzers = []
        results = []
        
        for symbol in symbols:
            analyzer = StockAnalyzer(symbol, period='1y')
            if analyzer.run_analysis():
                current_signal = analyzer.get_current_signal()
                analyzers.append(analyzer)
                results.append({
                    'symbol': symbol,
                    'price': current_signal['price'],
                    'signal': current_signal['signal'],
                    'strength': current_signal['strength'],
                    'date': current_signal['date']
                })
        
        if results:
            print("✅ 主程式分析成功")
            
            # 顯示結果摘要
            print_section("分析結果摘要")
            print(f"{'股票代碼':<8} {'價格':<12} {'建議':<6} {'強度':<8} {'日期':<12}")
            print("-" * 50)
            
            for result in results:
                print(f"{result['symbol']:<8} ${result['price']:<11.2f} {result['signal']:<6} {result['strength']:<8.1f} {result['date']:<12}")
            
            # 統計摘要
            successful_count = len(results)
            signal_counts = {}
            for result in results:
                signal = result['signal']
                signal_counts[signal] = signal_counts.get(signal, 0) + 1
            
            print_section("統計摘要")
            print(f"成功分析: {successful_count}/{len(symbols)} 支股票")
            for signal, count in signal_counts.items():
                print(f"{signal}建議: {count} 支")
            
            if successful_count > 0:
                strengths = [r['strength'] for r in results]
                print(f"平均強度: {sum(strengths)/len(strengths):.1f}")
                print(f"最高強度: {max(strengths):.1f}")
                print(f"最低強度: {min(strengths):.1f}")
            
            return analyzers
        else:
            print("❌ 主程式分析失敗")
            return None
            
    except Exception as e:
        print(f"❌ 主程式測試時發生錯誤: {e}")
        return None

def test_html_report_features():
    """測試 HTML 報告功能"""
    print_header("HTML 報告功能測試")
    
    try:
        # 創建測試分析器
        analyzer = StockAnalyzer("AAPL", period='1y')
        analyzer.run_analysis()
        
        # 創建視覺化器
        visualizer = StockVisualizer()
        
        # 測試不同的報告生成方式
        reports = []
        
        # 1. 單一股票報告
        print_section("單一股票報告")
        single_report = visualizer.create_single_stock_report(analyzer, 'test_single_report.html')
        if single_report:
            reports.append(('單一股票報告', single_report))
            print(f"✅ 已生成: {single_report}")
        
        # 2. 批量報告（單一股票）
        print_section("批量報告（單一股票）")
        batch_report = visualizer.create_batch_html_report([analyzer], 'test_batch_single.html')
        if batch_report:
            reports.append(('批量報告（單一股票）', batch_report))
            print(f"✅ 已生成: {batch_report}")
        
        # 3. 多股票批量報告
        print_section("多股票批量報告")
        analyzers = []
        for symbol in ['AAPL', 'MSFT']:
            analyzer = StockAnalyzer(symbol, period='1y')
            if analyzer.run_analysis():
                analyzers.append(analyzer)
        
        if len(analyzers) > 1:
            multi_batch_report = visualizer.create_batch_html_report(analyzers, 'test_multi_batch.html')
            if multi_batch_report:
                reports.append(('多股票批量報告', multi_batch_report))
                print(f"✅ 已生成: {multi_batch_report}")
        
        # 顯示報告摘要
        if reports:
            print_section("生成的報告摘要")
            for report_name, report_path in reports:
                if os.path.exists(report_path):
                    file_size = os.path.getsize(report_path)
                    print(f"📄 {report_name}: {report_path} ({file_size:,} bytes)")
                else:
                    print(f"❌ {report_name}: {report_path} (文件不存在)")
        
        return reports
        
    except Exception as e:
        print(f"❌ HTML 報告測試時發生錯誤: {e}")
        return None

def run_all_tests():
    """運行所有測試"""
    print_header("AIStock 完整功能測試")
    print(f"測試開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    # 1. 單一股票分析測試
    try:
        analyzer = test_single_stock_analysis()
        test_results['single_stock'] = analyzer is not None
    except Exception as e:
        print(f"❌ 單一股票分析測試失敗: {e}")
        test_results['single_stock'] = False
    
    # 2. 左側分析測試
    try:
        left_result = test_left_analysis()
        test_results['left_analysis'] = left_result is not None
    except Exception as e:
        print(f"❌ 左側分析測試失敗: {e}")
        test_results['left_analysis'] = False
    
    # 3. 視覺化功能測試
    try:
        visualizer = test_visualization()
        test_results['visualization'] = visualizer is not None
    except Exception as e:
        print(f"❌ 視覺化功能測試失敗: {e}")
        test_results['visualization'] = False
    
    # 4. 批量分析測試
    try:
        analyzers = test_batch_analysis()
        test_results['batch_analysis'] = analyzers is not None
    except Exception as e:
        print(f"❌ 批量分析測試失敗: {e}")
        test_results['batch_analysis'] = False
    
    # 5. 批量左側分析測試
    try:
        batch_left_result = test_left_analysis_batch()
        test_results['batch_left_analysis'] = batch_left_result is not None
    except Exception as e:
        print(f"❌ 批量左側分析測試失敗: {e}")
        test_results['batch_left_analysis'] = False
    
    # 6. 主程式功能測試
    try:
        main_analyzers = test_main_program()
        test_results['main_program'] = main_analyzers is not None
    except Exception as e:
        print(f"❌ 主程式功能測試失敗: {e}")
        test_results['main_program'] = False
    
    # 7. HTML 報告功能測試
    try:
        reports = test_html_report_features()
        test_results['html_reports'] = reports is not None
    except Exception as e:
        print(f"❌ HTML 報告功能測試失敗: {e}")
        test_results['html_reports'] = False
    
    # 顯示測試結果摘要
    print_header("測試結果摘要")
    
    test_names = {
        'single_stock': '單一股票分析',
        'left_analysis': '左側分析',
        'visualization': '視覺化功能',
        'batch_analysis': '批量分析',
        'batch_left_analysis': '批量左側分析',
        'main_program': '主程式功能',
        'html_reports': 'HTML 報告功能'
    }
    
    passed = 0
    total = len(test_results)
    
    for test_key, passed_test in test_results.items():
        test_name = test_names.get(test_key, test_key)
        status = "✅ 通過" if passed_test else "❌ 失敗"
        print(f"{test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\n總體結果: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有測試都通過了！系統運行正常。")
    else:
        print("⚠️ 部分測試失敗，請檢查相關功能。")
    
    print(f"\n測試結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return test_results

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='AIStock 整合測試程序')
    parser.add_argument('--all', action='store_true', help='運行所有測試')
    parser.add_argument('--single-stock', action='store_true', help='測試單一股票分析')
    parser.add_argument('--left-analysis', action='store_true', help='測試左側分析')
    parser.add_argument('--visualization', action='store_true', help='測試視覺化功能')
    parser.add_argument('--batch-analysis', action='store_true', help='測試批量分析')
    parser.add_argument('--batch-left-analysis', action='store_true', help='測試批量左側分析')
    parser.add_argument('--main-program', action='store_true', help='測試主程式功能')
    parser.add_argument('--html-reports', action='store_true', help='測試 HTML 報告功能')
    
    args = parser.parse_args()
    
    if args.all or not any(vars(args).values()):
        # 運行所有測試
        run_all_tests()
    else:
        # 運行指定的測試
        if args.single_stock:
            test_single_stock_analysis()
        if args.left_analysis:
            test_left_analysis()
        if args.visualization:
            test_visualization()
        if args.batch_analysis:
            test_batch_analysis()
        if args.batch_left_analysis:
            test_left_analysis_batch()
        if args.main_program:
            test_main_program()
        if args.html_reports:
            test_html_report_features()

if __name__ == "__main__":
    main() 
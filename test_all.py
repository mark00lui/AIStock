#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIStock 完整功能測試程式
整合所有模組的測試和演示功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import argparse
from datetime import datetime
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 導入所有模組
from stock_analyzer import StockAnalyzer
from visualizer import StockVisualizer
from left_analysis import LeftAnalysis, analyze_stock, analyze_multiple_stocks

def test_left_analysis():
    """測試左側分析功能"""
    print("\n" + "=" * 60)
    print("=== 左側分析功能測試 ===")
    print("=" * 60)
    
    # 創建分析器
    analyzer = LeftAnalysis()
    
    # 測試股票
    test_symbols = ['AAPL', 'MSFT', 'TSLA']
    
    print("\n🔍 測試單一股票分析:")
    for symbol in test_symbols:
        print(f"\n--- 分析 {symbol} ---")
        result = analyzer.analyze_stock_price(symbol)
        
        if 'error' in result:
            print(f"❌ {result['error']}")
            continue
        
        print(f"✅ 分析成功")
        print(f"   股票名稱: {result['stock_name']}")
        print(f"   當前股價: ${result['current_price']:.2f}")
        print(f"   Forward EPS: ${result['forward_eps']:.2f}" if result['forward_eps'] else "   Forward EPS: N/A")
        print(f"   Forward P/E: {result['forward_pe']:.2f}" if result['forward_pe'] else "   Forward P/E: N/A")
        print(f"   數據來源: {', '.join(result['sources_used'])}")
        
        # 顯示各時間範圍的預估
        for timeframe in ['1_year', '2_year', '3_year']:
            if timeframe in result['timeframes']:
                tf_data = result['timeframes'][timeframe]
                print(f"\n   {tf_data['timeframe']} ({tf_data['target_date']}):")
                print(f"     平均預估價: ${tf_data['target_mean']:.2f}")
                print(f"     最高預估價: ${tf_data['target_high']:.2f}" if tf_data['target_high'] else "     最高預估價: N/A")
                print(f"     最低預估價: ${tf_data['target_low']:.2f}" if tf_data['target_low'] else "     最低預估價: N/A")
                print(f"     預期報酬率: {tf_data['potential_return']:.2f}%" if tf_data['potential_return'] else "     預期報酬率: N/A")
                if tf_data.get('future_eps'):
                    print(f"     預估 EPS: ${tf_data['future_eps']:.2f}")
        
        # 顯示歷史本益比數據（如果可用）
        if 'historical_pe' in result:
            pe_data = result['historical_pe']
            print(f"\n   歷史本益比分析:")
            print(f"     數據期間: {pe_data['period']}")
            print(f"     數據點數: {pe_data['data_points']}")
            print(f"     平均本益比: {pe_data['mean_pe']:.2f}")
            print(f"     最高本益比: {pe_data['max_pe']:.2f}")
            print(f"     最低本益比: {pe_data['min_pe']:.2f}")
    
    print(f"\n🔍 測試批量分析:")
    batch_result = analyze_multiple_stocks(test_symbols)
    print(f"✅ 批量分析完成")
    print(f"   分析股票數: {batch_result['total_stocks']}")
    print(f"   分析日期: {batch_result['analysis_date']}")
    
    # 顯示批量分析摘要
    successful_analyses = [r for r in batch_result['results'] if 'error' not in r]
    print(f"   成功分析: {len(successful_analyses)}/{batch_result['total_stocks']}")
    
    if successful_analyses:
        print(f"\n   批量分析摘要:")
        for result in successful_analyses:
            symbol = result['symbol']
            current_price = result['current_price']
            if '1_year' in result['timeframes']:
                target_mean = result['timeframes']['1_year']['target_mean']
                potential_return = result['timeframes']['1_year']['potential_return']
                print(f"     {symbol}: 當前${current_price:.2f} → 1年後${target_mean:.2f} ({potential_return:+.2f}%)")
    
    print(f"\n🔍 測試便捷函數:")
    single_result = analyze_stock('AAPL')
    if 'error' not in single_result:
        print(f"✅ 便捷函數測試成功")
        print(f"   返回數據包含 {len(single_result)} 個主要欄位")
        print(f"   時間範圍: {list(single_result['timeframes'].keys())}")
    else:
        print(f"❌ 便捷函數測試失敗: {single_result['error']}")
    
    print(f"\n📊 JSON 格式輸出示例:")
    if 'error' not in single_result:
        # 顯示 JSON 格式的結構
        json_structure = {
            'symbol': single_result['symbol'],
            'stock_name': single_result['stock_name'],
            'current_price': single_result['current_price'],
            'timeframes': {
                '1_year': {
                    'target_mean': single_result['timeframes']['1_year']['target_mean'],
                    'target_high': single_result['timeframes']['1_year']['target_high'],
                    'target_low': single_result['timeframes']['1_year']['target_low'],
                    'potential_return': single_result['timeframes']['1_year']['potential_return']
                }
            }
        }
        print(f"   主要結構: {list(json_structure.keys())}")
        print(f"   時間範圍結構: {list(json_structure['timeframes']['1_year'].keys())}")
    
    print(f"\n✅ 左側分析功能測試完成")

def demonstrate_left_analysis_usage():
    """演示左側分析使用方法"""
    print("\n" + "=" * 60)
    print("=== 左側分析使用方法演示 ===")
    print("=" * 60)
    
    print("\n🚀 快速開始:")
    print("1. 單一股票分析:")
    print("   from src.left_analysis import analyze_stock")
    print("   result = analyze_stock('AAPL')")
    print("   print(result['timeframes']['1_year']['target_mean'])")
    print()
    print("2. 批量股票分析:")
    print("   from src.left_analysis import analyze_multiple_stocks")
    print("   result = analyze_multiple_stocks(['AAPL', 'MSFT', 'TSLA'])")
    print("   for stock_result in result['results']:")
    print("       print(f\"{stock_result['symbol']}: {stock_result['timeframes']['1_year']['target_mean']}\")")
    print()
    print("3. 使用分析器類:")
    print("   from src.left_analysis import LeftAnalysis")
    print("   analyzer = LeftAnalysis()")
    print("   result = analyzer.analyze_stock_price('AAPL')")
    print()
    print("4. 獲取歷史本益比:")
    print("   historical_pe = analyzer.calculate_historical_pe_ratios('AAPL')")
    print("   print(f\"平均本益比: {historical_pe['mean_pe']}\")")
    
    print("\n📋 返回數據結構:")
    print("• symbol: 股票代碼")
    print("• stock_name: 股票名稱")
    print("• current_price: 當前股價")
    print("• forward_eps: Forward EPS")
    print("• forward_pe: Forward P/E")
    print("• timeframes: 各時間範圍預估")
    print("  - 1_year: 1年後預估")
    print("  - 2_year: 2年後預估")
    print("  - 3_year: 3年後預估")
    print("• historical_pe: 歷史本益比數據（如果可用）")
    
    print("\n📊 時間範圍數據結構:")
    print("• target_mean: 平均預估價")
    print("• target_high: 最高預估價")
    print("• target_low: 最低預估價")
    print("• potential_return: 預期報酬率")
    print("• future_eps: 預估 EPS")
    print("• confidence_interval: 信賴區間")
    
    print("\n🎯 支援的股票代碼:")
    print("• 美股: AAPL, MSFT, TSLA, GOOGL, AMZN, META")
    print("• 台股: 2330.TW, 2317.TW, 2454.TW")
    print("• 港股: 0700.HK, 0941.HK")
    print("• 其他: 請參考 Yahoo Finance 代碼格式")

def test_left_analysis_integration():
    """測試左側分析與現有系統的整合"""
    print("\n" + "=" * 60)
    print("=== 左側分析整合測試 ===")
    print("=" * 60)
    
    # 測試股票
    symbol = 'AAPL'
    
    print(f"\n🔍 測試 {symbol} 的完整分析流程:")
    
    # 1. 技術分析
    print(f"\n1. 技術分析:")
    analyzer = StockAnalyzer(symbol, period='1y')
    if analyzer.fetch_data():
        analyzer.calculate_technical_indicators()
        analyzer.generate_signals()
        latest_signal = analyzer.get_latest_signal()
        print(f"   ✅ 技術分析完成")
        print(f"   建議: {latest_signal['action']}")
        print(f"   強度: {latest_signal['strength']}")
    else:
        print(f"   ❌ 技術分析失敗")
    
    # 2. 左側分析
    print(f"\n2. 左側分析:")
    left_result = analyze_stock(symbol)
    if 'error' not in left_result:
        print(f"   ✅ 左側分析完成")
        print(f"   當前股價: ${left_result['current_price']:.2f}")
        if '1_year' in left_result['timeframes']:
            target_mean = left_result['timeframes']['1_year']['target_mean']
            potential_return = left_result['timeframes']['1_year']['potential_return']
            print(f"   1年後預估: ${target_mean:.2f} ({potential_return:+.2f}%)")
    else:
        print(f"   ❌ 左側分析失敗: {left_result['error']}")
    
    # 3. 綜合建議
    print(f"\n3. 綜合建議:")
    if 'error' not in left_result and analyzer.data is not None:
        current_price = left_result['current_price']
        if '1_year' in left_result['timeframes']:
            target_mean = left_result['timeframes']['1_year']['target_mean']
            potential_return = left_result['timeframes']['1_year']['potential_return']
            
            # 綜合技術和基本面分析
            tech_signal = latest_signal['action'] if 'latest_signal' in locals() else 'Hold'
            tech_strength = latest_signal['strength'] if 'latest_signal' in locals() else 0
            
            print(f"   技術面: {tech_signal} (強度: {tech_strength})")
            print(f"   基本面: 預期報酬率 {potential_return:+.2f}%")
            
            # 綜合建議邏輯
            if tech_signal == 'Buy' and potential_return > 10:
                print(f"   🟢 強烈買入: 技術面和基本面都看好")
            elif tech_signal == 'Buy' or potential_return > 5:
                print(f"   🟡 買入: 技術面或基本面看好")
            elif tech_signal == 'Sell' and potential_return < -10:
                print(f"   🔴 強烈賣出: 技術面和基本面都看空")
            elif tech_signal == 'Sell' or potential_return < -5:
                print(f"   🟠 賣出: 技術面或基本面看空")
            else:
                print(f"   ⚪ 持有: 等待更好的機會")
    
    print(f"\n✅ 整合測試完成")

def test_visualizer_integration():
    """測試視覺化整合功能"""
    print("\n" + "=" * 60)
    print("=== 視覺化整合測試 ===")
    print("=" * 60)
    
    # 測試股票
    symbol = 'AAPL'
    
    print(f"\n🔍 測試 {symbol} 的視覺化整合:")
    
    # 1. 技術分析
    print(f"\n1. 技術分析:")
    analyzer = StockAnalyzer(symbol, period='1y')
    if analyzer.run_analysis():
        print(f"   ✅ 技術分析完成")
        current_signal = analyzer.get_current_signal()
        print(f"   建議: {current_signal['signal']}")
        print(f"   強度: {current_signal['strength']}")
    else:
        print(f"   ❌ 技術分析失敗")
        return False
    
    # 2. 視覺化整合
    print(f"\n2. 視覺化整合:")
    visualizer = StockVisualizer(analyzer)
    
    # 測試左側分析數據獲取
    print(f"   測試左側分析數據獲取...")
    left_data = visualizer.get_left_analysis_data()
    if left_data and 'error' not in left_data:
        print(f"   ✅ 左側分析數據獲取成功")
        print(f"   股票名稱: {left_data['stock_name']}")
        print(f"   當前股價: ${left_data['current_price']:.2f}")
        print(f"   數據來源: {', '.join(left_data.get('sources_used', []))}")
    else:
        print(f"   ❌ 左側分析數據獲取失敗")
    
    # 測試股價範圍可視化
    print(f"   測試股價範圍可視化...")
    fig = visualizer.create_price_range_visualization()
    if fig:
        print(f"   ✅ 股價範圍圖表生成成功")
        fig.savefig(f'{symbol}_price_range_test.png', dpi=300, bbox_inches='tight')
        print(f"   圖表已保存: {symbol}_price_range_test.png")
    else:
        print(f"   ❌ 股價範圍圖表生成失敗")
    
    # 測試股價範圍 HTML 報告
    print(f"   測試股價範圍 HTML 報告...")
    html_content = visualizer.create_price_range_html(f'{symbol}_price_range_test.html')
    if html_content:
        print(f"   ✅ 股價範圍 HTML 報告生成成功")
    else:
        print(f"   ❌ 股價範圍 HTML 報告生成失敗")
    
    # 測試綜合 HTML 報告
    print(f"   測試綜合 HTML 報告...")
    report_path = visualizer.create_comprehensive_html_report(f'{symbol}_comprehensive_test.html')
    if report_path:
        print(f"   ✅ 綜合 HTML 報告生成成功")
    else:
        print(f"   ❌ 綜合 HTML 報告生成失敗")
    
    print(f"\n✅ 視覺化整合測試完成")
    return True

def test_batch_visualization():
    """測試批量視覺化功能"""
    print("\n" + "=" * 60)
    print("=== 批量視覺化測試 ===")
    print("=" * 60)
    
    # 測試股票列表
    symbols = ['AAPL', 'MSFT', 'TSLA']
    analyzers = []
    
    print(f"\n🔍 測試批量分析: {', '.join(symbols)}")
    
    # 創建分析器列表
    for symbol in symbols:
        analyzer = StockAnalyzer(symbol, period='6mo')
        if analyzer.run_analysis():
            analyzers.append(analyzer)
            print(f"   ✅ {symbol} 分析完成")
        else:
            print(f"   ❌ {symbol} 分析失敗")
    
    if analyzers:
        print(f"\n成功分析 {len(analyzers)} 支股票")
        
        # 創建視覺化器
        visualizer = StockVisualizer(analyzers[0])
        
        # 測試批量 HTML 報告
        print(f"\n📄 測試批量 HTML 報告...")
        report_path = visualizer.create_batch_html_report(analyzers, 'batch_comprehensive_test.html')
        if report_path:
            print(f"✅ 批量 HTML 報告生成成功")
            print(f"   報告路徑: {report_path}")
        else:
            print(f"❌ 批量 HTML 報告生成失敗")
        
        return True
    else:
        print("❌ 沒有成功分析任何股票")
        return False

def demonstrate_visualization_features():
    """演示視覺化功能特色"""
    print("\n" + "=" * 60)
    print("=== 視覺化功能特色演示 ===")
    print("=" * 60)
    
    print("\n🎨 新增的視覺化功能:")
    print("1. 股價範圍可視化:")
    print("   • 顯示當前股價在未來三年預估範圍內的位置")
    print("   • 直觀判斷股票是否被低估或高估")
    print("   • 支援 1年、2年、3年的預估範圍")
    print("   • 顏色編碼：綠色(低估)、紅色(合理)、橙色(高估)")
    print()
    print("2. 綜合分析報告:")
    print("   • 技術分析 + 左側分析整合")
    print("   • 包含股價範圍圖表")
    print("   • 各時間範圍的詳細預估")
    print("   • 估值狀態判斷")
    print()
    print("3. 批量分析報告:")
    print("   • 多股票綜合分析")
    print("   • 可折疊式設計")
    print("   • 技術分析和左側分析並列顯示")
    print("   • 按訊號強度排序")
    print()
    print("4. 使用方法:")
    print("   from src.stock_analyzer import StockAnalyzer")
    print("   from src.visualizer import StockVisualizer")
    print("   analyzer = StockAnalyzer('AAPL')")
    print("   analyzer.run_analysis()")
    print("   visualizer = StockVisualizer(analyzer)")
    print("   visualizer.create_price_range_visualization()")
    print("   visualizer.create_comprehensive_html_report()")
    print()
    print("5. 支援的圖表類型:")
    print("   • 股價範圍條形圖")
    print("   • 技術指標綜合圖表")
    print("   • 互動式 HTML 報告")
    print("   • 批量分析摘要")
    
    print(f"\n✅ 視覺化功能特色演示完成")

def main():
    """主測試函數"""
    parser = argparse.ArgumentParser(description='AIStock 完整功能測試')
    parser.add_argument('--left-analysis', action='store_true', help='測試左側分析功能')
    parser.add_argument('--integration', action='store_true', help='測試整合功能')
    parser.add_argument('--visualization', action='store_true', help='測試視覺化功能')
    parser.add_argument('--demo', action='store_true', help='演示使用方法')
    parser.add_argument('--all', action='store_true', help='執行所有測試')
    
    args = parser.parse_args()
    
    print("=== AIStock 完整功能測試系統 ===")
    print("整合技術分析、左側分析和視覺化功能")
    
    if args.left_analysis or args.all:
        test_left_analysis()
    
    if args.integration or args.all:
        test_left_analysis_integration()
    
    if args.visualization or args.all:
        test_visualizer_integration()
        test_batch_visualization()
        demonstrate_visualization_features()
    
    if args.demo or args.all:
        demonstrate_left_analysis_usage()
    
    if not any([args.left_analysis, args.integration, args.visualization, args.demo, args.all]):
        # 預設執行所有測試
        test_left_analysis()
        test_left_analysis_integration()
        test_visualizer_integration()
        test_batch_visualization()
        demonstrate_left_analysis_usage()
        demonstrate_visualization_features()
    
    print(f"\n{'='*60}")
    print("=== 測試完成 ===")
    print("=" * 60)
    print("✅ 所有功能測試完成")
    print("📊 左側分析功能已整合到系統中")
    print("🎨 視覺化功能已整合股價範圍分析")
    print("🎯 可以使用 analyze_stock() 和 analyze_multiple_stocks() 函數")
    print("📈 支援 JSON 格式輸出，方便圖表使用")
    print("📄 生成的 HTML 報告包含技術分析和左側分析")

if __name__ == "__main__":
    main() 
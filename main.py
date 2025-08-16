#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIStock - 股票訊號分析系統
主程式檔案
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import argparse
from datetime import datetime
from stock_analyzer import StockAnalyzer
from visualizer import StockVisualizer
from left_analysis import analyze_stock

def main():
    parser = argparse.ArgumentParser(description='AIStock 股票訊號分析系統')
    parser.add_argument('symbols', nargs='+', help='股票代碼 (例如: AAPL MSFT GOOGL 或 AAPL,MSFT,GOOGL)')
    parser.add_argument('--period', default='1y', 
                       help='資料期間 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)')
    parser.add_argument('--plot', action='store_true', help='顯示圖表')
    parser.add_argument('--save', help='儲存圖表到指定路徑')
    parser.add_argument('--save-daily-report', action='store_true', help='儲存每日報告，檔名格式為 YYYY-MM-DD_report.html')
    
    args = parser.parse_args()
    
    # 處理股票代碼輸入
    symbols = []
    for symbol_input in args.symbols:
        # 支援逗號分隔的多個股票代碼
        if ',' in symbol_input:
            symbols.extend([s.strip().upper() for s in symbol_input.split(',')])
        else:
            symbols.append(symbol_input.upper())
    
    # 移除重複的股票代碼
    symbols = list(dict.fromkeys(symbols))
    
    # 驗證股票代碼
    valid_symbols = []
    invalid_symbols = []
    
    print("=== 股票代碼驗證 ===")
    for symbol in symbols:
        is_valid, error_msg = StockAnalyzer.validate_symbol(symbol)
        if is_valid:
            symbol_info = StockAnalyzer.get_symbol_info(symbol)
            print(f"✅ {symbol:<10} - {symbol_info['exchange']:<15} - {symbol_info['market']}")
            valid_symbols.append(symbol)
        else:
            print(f"❌ {symbol:<10} - {error_msg}")
            invalid_symbols.append(symbol)
    
    if invalid_symbols:
        print(f"\n警告: 發現 {len(invalid_symbols)} 個無效的股票代碼，將被忽略")
        print(f"無效股票代碼: {', '.join(invalid_symbols)}")
    
    if not valid_symbols:
        print("錯誤: 沒有有效的股票代碼可供分析")
        return
    
    print(f"\n=== AIStock 股票訊號分析系統 ===")
    print(f"分析股票: {', '.join(valid_symbols)}")
    print(f"資料期間: {args.period}")
    print("-" * 40)
    
    # 執行批量分析（無論單一或多支股票都使用批量模式）
    print(f"正在批量分析 {len(valid_symbols)} 支股票...")
    
    results = []
    analyzers = []  # 儲存分析器實例用於生成 HTML 報告
    
    for i, symbol in enumerate(valid_symbols, 1):
        print(f"\n[{i}/{len(valid_symbols)}] 分析 {symbol}...")
        
        try:
            analyzer = StockAnalyzer(symbol, args.period)
            
            if analyzer.run_analysis():
                current_signal = analyzer.get_current_signal()
                results.append({
                    'symbol': symbol,
                    'price': current_signal['price'],
                    'signal': current_signal['signal'],
                    'strength': current_signal['strength'],
                    'date': current_signal['date']
                })
                analyzers.append(analyzer)  # 添加到分析器列表
                print(f"  ✅ {symbol} ({analyzer.long_name}): ${current_signal['price']:.2f} | {current_signal['signal']} | 強度: {current_signal['strength']}")
            else:
                print(f"  ❌ {symbol}: 分析失敗")
                results.append({
                    'symbol': symbol,
                    'price': 0,
                    'signal': '分析失敗',
                    'strength': 0,
                    'date': 'N/A'
                })
                
        except Exception as e:
            print(f"  ❌ {symbol}: 錯誤 - {e}")
            results.append({
                'symbol': symbol,
                'price': 0,
                'signal': f'錯誤: {e}',
                'strength': 0,
                'date': 'N/A'
            })
    
    # 顯示結果摘要
    print("\n" + "=" * 60)
    print("=== 分析結果摘要 ===")
    print("=" * 60)
    
    # 按強度排序
    successful_results = [r for r in results if r['signal'] in ['買入', '賣出', '持有']]
    if successful_results:
        successful_results.sort(key=lambda x: x['strength'], reverse=True)
    
    # 顯示表格
    print(f"{'股票代碼':<8} {'股票名稱':<20} {'價格':<12} {'建議':<6} {'強度':<8} {'日期':<12}")
    print("-" * 70)
    
    for result in results:
        # 獲取對應分析器的股票名稱
        analyzer = next((a for a in analyzers if a.symbol == result['symbol']), None)
        stock_name = analyzer.long_name if analyzer else result['symbol']
        
        if result['signal'] in ['買入', '賣出', '持有']:
            print(f"{result['symbol']:<8} {stock_name:<20} ${result['price']:<11.2f} {result['signal']:<6} {result['strength']:<8.1f} {result['date']:<12}")
        else:
            print(f"{result['symbol']:<8} {stock_name:<20} {'N/A':<12} {result['signal']:<6} {'N/A':<8} {result['date']:<12}")
    
    # 統計摘要
    successful_count = len([r for r in results if r['signal'] in ['買入', '賣出', '持有']])
    if successful_count > 0:
        signal_counts = {}
        for result in results:
            if result['signal'] in ['買入', '賣出', '持有']:
                signal_counts[result['signal']] = signal_counts.get(result['signal'], 0) + 1
        
        print(f"\n📊 統計摘要:")
        print(f"成功分析: {successful_count}/{len(valid_symbols)} 支股票")
        print(f"買入建議: {signal_counts.get('買入', 0)} 支")
        print(f"賣出建議: {signal_counts.get('賣出', 0)} 支")
        print(f"持有建議: {signal_counts.get('持有', 0)} 支")
        
        if successful_count > 0:
            strengths = [r['strength'] for r in results if r['signal'] in ['買入', '賣出', '持有']]
            print(f"\n強度統計:")
            print(f"平均強度: {sum(strengths)/len(strengths):.1f}")
            print(f"最高強度: {max(strengths):.1f}")
            print(f"最低強度: {min(strengths):.1f}")
    
    # 生成 HTML 報告
    if analyzers and (args.plot or args.save or args.save_daily_report):
        print("\n正在生成批量分析 HTML 報告...")
        # 創建一個通用的視覺化器，不綁定特定分析器
        visualizer = StockVisualizer()  # 不綁定特定分析器
        
        if args.save_daily_report:
            # 生成每日報告檔名格式：YYYY-MM-DD_report.html
            daily_report_path = f"{datetime.now().strftime('%Y-%m-%d')}_report.html"
            result = visualizer.create_batch_html_report(analyzers, daily_report_path)
            if result:
                print(f"✅ 每日報告已保存: {daily_report_path}")
            else:
                print("❌ 每日報告生成失敗")
        elif args.save:
            save_path = args.save
            if not save_path.endswith('.html'):
                save_path += '.html'
            result = visualizer.create_batch_html_report(analyzers, save_path)
            if result:
                print(f"✅ 報告已保存: {save_path}")
            else:
                print("❌ 報告生成失敗")
        else:
            # 默認保存為當前日期報告
            default_path = f"{datetime.now().strftime('%Y-%m-%d')}_default_report.html"
            result = visualizer.create_batch_html_report(analyzers, default_path)
            if result:
                print(f"✅ 默認報告已保存: {default_path}")
            else:
                print("❌ 默認報告生成失敗")

if __name__ == "__main__":
    main() 
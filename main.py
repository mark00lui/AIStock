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
from gemini import GeminiStockAnalyzer

def main():
    parser = argparse.ArgumentParser(description='AIStock 股票訊號分析系統')
    parser.add_argument('symbols', nargs='+', help='股票代碼 (例如: AAPL MSFT GOOGL 或 AAPL,MSFT,GOOGL)')
    parser.add_argument('--period', default='1y', 
                       help='資料期間 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)')
    parser.add_argument('--plot', action='store_true', help='顯示圖表')
    parser.add_argument('--save', help='儲存圖表到指定路徑')
    parser.add_argument('--save-daily-report', action='store_true', help='儲存每日報告，檔名格式為 YYYY-MM-DD_report.html')
    parser.add_argument('--GEMINI-API', help='Gemini API 金鑰，啟用AI建議功能')
    
    args = parser.parse_args()
    
    # 處理股票代碼輸入和分類
    symbols = []
    categories = {}
    current_category = "未分類"
    
    for symbol_input in args.symbols:
        # 檢查是否為分類標記 [CATEGORY]
        if symbol_input.startswith('[') and symbol_input.endswith(']'):
            current_category = symbol_input[1:-1]  # 移除方括號
            continue
        
        # 支援逗號分隔的多個股票代碼
        if ',' in symbol_input:
            symbol_list = [s.strip().upper() for s in symbol_input.split(',')]
        else:
            symbol_list = [symbol_input.upper()]
        
        # 添加到分類中
        for symbol in symbol_list:
            if symbol not in symbols:  # 避免重複
                symbols.append(symbol)
                if current_category not in categories:
                    categories[current_category] = []
                categories[current_category].append(symbol)
    
    # 顯示分類結果
    print("=== 股票分類結果 ===")
    for category, category_symbols in categories.items():
        print(f"📂 {category}: {', '.join(category_symbols)}")
    print()
    
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
    
    # 執行批量分析
    print(f"正在批量分析 {len(valid_symbols)} 支股票...")
    
    # 初始化Gemini分析器（如果提供API金鑰）
    gemini_analyzer = None
    gemini_results = {}
    if args.GEMINI_API:
        try:
            print("🤖 初始化Gemini AI分析器...")
            gemini_analyzer = GeminiStockAnalyzer(args.GEMINI_API)
            print("✅ Gemini AI分析器初始化成功")
        except Exception as e:
            print(f"❌ Gemini AI分析器初始化失敗: {e}")
            gemini_analyzer = None
    
    results = []
    analyzers = []  # 儲存分析器實例用於生成 HTML 報告
    
    # 批量處理股票分析
    def process_stock_batch(symbol_batch, batch_num, total_batches):
        """處理一批股票"""
        batch_results = []
        batch_analyzers = []
        
        print(f"\n📦 處理批次 {batch_num}/{total_batches} ({len(symbol_batch)} 支股票)...")
        
        # 先進行技術分析
        for symbol in symbol_batch:
            try:
                analyzer = StockAnalyzer(symbol, args.period)
                if analyzer.run_analysis():
                    current_signal = analyzer.get_current_signal()
                    batch_results.append({
                        'symbol': symbol,
                        'price': current_signal['price'],
                        'signal': current_signal['signal'],
                        'strength': current_signal['strength'],
                        'date': current_signal['date']
                    })
                    batch_analyzers.append(analyzer)
                    print(f"  ✅ {symbol} ({analyzer.long_name}): ${current_signal['price']:.2f} | {current_signal['signal']} | 強度: {current_signal['strength']}")
                else:
                    print(f"  ❌ {symbol}: 技術分析失敗")
                    batch_results.append({
                        'symbol': symbol,
                        'price': 0,
                        'signal': '分析失敗',
                        'strength': 0,
                        'date': 'N/A'
                    })
            except Exception as e:
                print(f"  ❌ {symbol}: 錯誤 - {e}")
                batch_results.append({
                    'symbol': symbol,
                    'price': 0,
                    'signal': f'錯誤: {e}',
                    'strength': 0,
                    'date': 'N/A'
                })
        
        # 批量進行Gemini AI分析
        if gemini_analyzer and batch_analyzers:
            try:
                print(f"    🤖 正在進行批量Gemini AI分析...")
                
                # 準備批量分析數據
                batch_symbols = [r['symbol'] for r in batch_results if r['signal'] in ['買入', '賣出', '持有']]
                current_prices = {r['symbol']: r['price'] for r in batch_results if r['signal'] in ['買入', '賣出', '持有']}
                company_names = {a.symbol: a.long_name for a in batch_analyzers}
                
                if batch_symbols:
                    gemini_batch_results = gemini_analyzer.analyze_stock_batch(
                        symbols=batch_symbols,
                        current_prices=current_prices,
                        company_names=company_names
                    )
                    
                    # 處理批量結果
                    for symbol, gemini_result in gemini_batch_results.items():
                        if gemini_result.get('metadata', {}).get('status') == 'success':
                            gemini_results[symbol] = gemini_result
                            sentiment = gemini_result.get('sentiment', 'N/A')
                            print(f"    🤖 {symbol} AI建議: {sentiment}")
                        else:
                            print(f"    ❌ {symbol} Gemini AI分析失敗")
                    
                    # 添加延遲避免API限制 (2分鐘)
                    import time
                    if batch_num < total_batches:  # 不是最後一批才需要等待
                        print(f"    ⏳ 等待 3.5 分鐘避免 API 速率限制...")
                        time.sleep(210)  # 3.5分鐘 = 210秒
                    
            except Exception as e:
                print(f"    ❌ 批量Gemini AI分析異常: {e}")
        
        return batch_results, batch_analyzers
    
    # 根據分類進行批量處理
    if categories and len(categories) > 1:
        # 有分類的情況：按分類進行批量處理
        print("📂 按分類進行批量處理...")
        for category, category_symbols in categories.items():
            print(f"\n📂 處理分類: {category}")
            batch_results, batch_analyzers = process_stock_batch(
                category_symbols, 
                list(categories.keys()).index(category) + 1, 
                len(categories)
            )
            results.extend(batch_results)
            analyzers.extend(batch_analyzers)
    else:
        # 沒有分類的情況：按預設批次大小進行批量處理
        batch_size = 10  # 預設每批10支股票
        total_batches = (len(valid_symbols) + batch_size - 1) // batch_size
        
        print(f"📦 按預設批次大小 ({batch_size}) 進行批量處理...")
        for i in range(0, len(valid_symbols), batch_size):
            batch_symbols = valid_symbols[i:i + batch_size]
            batch_num = i // batch_size + 1
            batch_results, batch_analyzers = process_stock_batch(batch_symbols, batch_num, total_batches)
            results.extend(batch_results)
            analyzers.extend(batch_analyzers)
    
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
            result = visualizer.create_batch_html_report(analyzers, daily_report_path, gemini_results, categories)
            if result:
                print(f"✅ 每日報告已保存: {daily_report_path}")
            else:
                print("❌ 每日報告生成失敗")
        elif args.save:
            save_path = args.save
            if not save_path.endswith('.html'):
                save_path += '.html'
            result = visualizer.create_batch_html_report(analyzers, save_path, gemini_results, categories)
            if result:
                print(f"✅ 報告已保存: {save_path}")
            else:
                print("❌ 報告生成失敗")
        else:
            # 默認保存為當前日期報告
            default_path = f"{datetime.now().strftime('%Y-%m-%d')}_default_report.html"
            result = visualizer.create_batch_html_report(analyzers, default_path, gemini_results, categories)
            if result:
                print(f"✅ 默認報告已保存: {default_path}")
            else:
                print("❌ 默認報告生成失敗")

if __name__ == "__main__":
    main() 
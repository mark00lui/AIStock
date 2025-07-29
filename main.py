#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIStock - 股票訊號分析系統
主程式檔案
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_analyzer import StockAnalyzer
from visualizer import StockVisualizer
import argparse

def main():
    parser = argparse.ArgumentParser(description='AIStock 股票訊號分析系統')
    parser.add_argument('symbol', help='股票代碼 (例如: AAPL, 2330.TW)')
    parser.add_argument('--period', default='1y', 
                       help='資料期間 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)')
    parser.add_argument('--plot', action='store_true', help='顯示圖表')
    parser.add_argument('--save', help='儲存圖表到指定路徑')
    
    args = parser.parse_args()
    
    print("=== AIStock 股票訊號分析系統 ===")
    print(f"分析股票: {args.symbol}")
    print(f"資料期間: {args.period}")
    print("-" * 40)
    
    # 創建分析器
    analyzer = StockAnalyzer(args.symbol, args.period)
    
    # 執行分析
    if not analyzer.run_analysis():
        print("分析失敗，請檢查股票代碼是否正確")
        return
    
    # 如果需要繪圖
    if args.plot or args.save:
        print("\n正在生成圖表...")
        visualizer = StockVisualizer(analyzer)
        
        # 繪製K線圖與訊號
        if args.save:
            save_path = args.save
            if not save_path.endswith('.html'):
                save_path += '.html'
            visualizer.plot_candlestick_with_signals(save_path)
        else:
            visualizer.plot_candlestick_with_signals()
        
        # 繪製技術指標
        visualizer.plot_technical_indicators()
        
        # 繪製訊號強度
        visualizer.plot_signal_strength()
        
        # 創建儀表板
        visualizer.create_dashboard()

def interactive_mode():
    """互動模式"""
    print("=== AIStock 股票訊號分析系統 (互動模式) ===")
    
    while True:
        print("\n請選擇操作:")
        print("1. 分析單一股票")
        print("2. 批量分析股票")
        print("3. 查看歷史分析結果")
        print("4. 退出")
        
        choice = input("\n請輸入選項 (1-4): ").strip()
        
        if choice == '1':
            symbol = input("請輸入股票代碼: ").strip().upper()
            period = input("請輸入資料期間 (預設: 1y): ").strip() or '1y'
            
            print(f"\n正在分析 {symbol}...")
            analyzer = StockAnalyzer(symbol, period)
            
            if analyzer.run_analysis():
                plot_choice = input("\n是否顯示圖表? (y/n): ").strip().lower()
                if plot_choice in ['y', 'yes', '是']:
                    visualizer = StockVisualizer(analyzer)
                    visualizer.plot_candlestick_with_signals()
                    visualizer.plot_technical_indicators()
                    visualizer.plot_signal_strength()
                    visualizer.create_dashboard()
        
        elif choice == '2':
            symbols_input = input("請輸入股票代碼 (用逗號分隔): ").strip()
            symbols = [s.strip().upper() for s in symbols_input.split(',')]
            period = input("請輸入資料期間 (預設: 1y): ").strip() or '1y'
            
            print(f"\n正在批量分析 {len(symbols)} 支股票...")
            
            results = []
            for symbol in symbols:
                print(f"\n分析 {symbol}...")
                analyzer = StockAnalyzer(symbol, period)
                if analyzer.run_analysis():
                    current_signal = analyzer.get_current_signal()
                    results.append({
                        'symbol': symbol,
                        'price': current_signal['price'],
                        'signal': current_signal['signal'],
                        'strength': current_signal['strength']
                    })
            
            # 顯示結果摘要
            print("\n=== 批量分析結果 ===")
            print(f"{'股票代碼':<10} {'價格':<10} {'訊號':<8} {'強度':<8}")
            print("-" * 40)
            for result in results:
                print(f"{result['symbol']:<10} ${result['price']:<9} {result['signal']:<8} {result['strength']:<8}")
        
        elif choice == '3':
            print("歷史分析結果功能尚未實現")
        
        elif choice == '4':
            print("感謝使用 AIStock 系統！")
            break
        
        else:
            print("無效選項，請重新選擇")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        interactive_mode() 
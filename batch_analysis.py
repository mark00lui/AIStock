#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量股票分析工具
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_analyzer import StockAnalyzer
import pandas as pd
from datetime import datetime

def batch_analyze_stocks(symbols, period='1y'):
    """
    批量分析多支股票
    
    Args:
        symbols (list): 股票代碼列表
        period (str): 分析期間
    """
    print("=== 批量股票分析 ===")
    print(f"分析期間: {period}")
    print(f"股票數量: {len(symbols)}")
    print("=" * 60)
    
    results = []
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] 分析 {symbol}...")
        
        try:
            analyzer = StockAnalyzer(symbol, period)
            
            if analyzer.run_analysis():
                current_signal = analyzer.get_current_signal()
                
                result = {
                    'symbol': symbol,
                    'price': current_signal['price'],
                    'signal': current_signal['signal'],
                    'strength': current_signal['strength'],
                    'date': current_signal['date']
                }
                results.append(result)
                
                print(f"  ✅ {symbol}: ${result['price']:.2f} | {result['signal']} | 強度: {result['strength']}")
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
    
    # 創建結果表格
    df_results = pd.DataFrame(results)
    
    # 按強度排序
    df_results = df_results.sort_values('strength', ascending=False)
    
    # 顯示表格
    print(f"{'股票代碼':<8} {'價格':<12} {'建議':<6} {'強度':<8} {'日期':<12}")
    print("-" * 60)
    
    for _, row in df_results.iterrows():
        if row['signal'] in ['買入', '賣出', '持有']:
            print(f"{row['symbol']:<8} ${row['price']:<11.2f} {row['signal']:<6} {row['strength']:<8.1f} {row['date']:<12}")
        else:
            print(f"{row['symbol']:<8} {'N/A':<12} {row['signal']:<6} {'N/A':<8} {row['date']:<12}")
    
    # 統計摘要
    successful_results = df_results[df_results['signal'].isin(['買入', '賣出', '持有'])]
    
    if len(successful_results) > 0:
        print(f"\n📊 統計摘要:")
        print(f"成功分析: {len(successful_results)}/{len(symbols)} 支股票")
        
        signal_counts = successful_results['signal'].value_counts()
        print(f"買入建議: {signal_counts.get('買入', 0)} 支")
        print(f"賣出建議: {signal_counts.get('賣出', 0)} 支")
        print(f"持有建議: {signal_counts.get('持有', 0)} 支")
        
        print(f"\n強度統計:")
        print(f"平均強度: {successful_results['strength'].mean():.1f}")
        print(f"最高強度: {successful_results['strength'].max():.1f}")
        print(f"最低強度: {successful_results['strength'].min():.1f}")
    
    return df_results

def interactive_batch_analysis():
    """互動式批量分析"""
    print("=== 互動式批量股票分析 ===")
    print("請輸入您關心的股票代碼，用逗號分隔")
    print("例如: AAPL,MSFT,GOOGL,TSLA,UNH")
    print("或輸入 'exit' 退出")
    
    while True:
        print("\n" + "-" * 50)
        symbols_input = input("請輸入股票代碼: ").strip()
        
        if symbols_input.lower() in ['exit', 'quit', '退出']:
            print("感謝使用！")
            break
        
        if not symbols_input:
            print("請輸入有效的股票代碼")
            continue
        
        # 解析股票代碼
        symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
        
        if not symbols:
            print("請輸入有效的股票代碼")
            continue
        
        print(f"\n準備分析 {len(symbols)} 支股票: {', '.join(symbols)}")
        
        # 選擇分析期間
        print("\n請選擇分析期間:")
        print("1. 1個月 (1mo)")
        print("2. 3個月 (3mo)")
        print("3. 6個月 (6mo)")
        print("4. 1年 (1y) - 預設")
        print("5. 2年 (2y)")
        
        period_choice = input("請選擇 (1-5，預設4): ").strip()
        
        period_map = {
            '1': '1mo',
            '2': '3mo', 
            '3': '6mo',
            '4': '1y',
            '5': '2y'
        }
        
        period = period_map.get(period_choice, '1y')
        
        # 執行批量分析
        results = batch_analyze_stocks(symbols, period)
        
        # 詢問是否要儲存結果
        save_choice = input(f"\n是否要儲存結果到 CSV 檔案? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes', '是']:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_analysis_{timestamp}.csv"
            results.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ 結果已儲存至: {filename}")

def quick_analysis():
    """快速分析常用股票組合"""
    print("=== 快速分析常用股票組合 ===")
    
    # 預設股票組合
    stock_groups = {
        "科技股": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"],
        "金融股": ["JPM", "BAC", "WFC", "GS", "MS", "UNH", "JNJ"],
        "加密貨幣": ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "ADA-USD"],
        "台股": ["2330.TW", "2317.TW", "2454.TW", "3008.TW", "2412.TW"],
        "自訂": []
    }
    
    print("請選擇股票組合:")
    for i, (name, symbols) in enumerate(stock_groups.items(), 1):
        if name != "自訂":
            print(f"{i}. {name} ({', '.join(symbols)})")
        else:
            print(f"{i}. {name}")
    
    choice = input("請選擇 (1-5): ").strip()
    
    if choice == '5':  # 自訂
        symbols_input = input("請輸入股票代碼 (用逗號分隔): ").strip()
        symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
    elif choice in ['1', '2', '3', '4']:
        group_names = list(stock_groups.keys())
        selected_group = group_names[int(choice) - 1]
        symbols = stock_groups[selected_group]
    else:
        print("無效選擇，使用預設科技股組合")
        symbols = stock_groups["科技股"]
    
    print(f"\n分析組合: {', '.join(symbols)}")
    
    # 執行分析
    results = batch_analyze_stocks(symbols, '1y')
    
    return results

if __name__ == "__main__":
    print("批量股票分析工具")
    print("=" * 50)
    
    print("請選擇模式:")
    print("1. 互動式輸入")
    print("2. 快速分析 (預設股票組合)")
    
    mode = input("請選擇 (1-2，預設2): ").strip()
    
    if mode == '1':
        interactive_batch_analysis()
    else:
        quick_analysis()
    
    print("\n🎉 分析完成！") 
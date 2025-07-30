#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試訊號生成問題
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_analyzer import StockAnalyzer
import pandas as pd

def debug_signal_generation():
    """調試訊號生成過程"""
    print("=== 調試訊號生成問題 ===")
    
    # 分析 UNH 股票
    symbol = "UNH"
    period = "1y"
    
    print(f"股票代碼: {symbol}")
    print(f"分析期間: {period}")
    print("-" * 50)
    
    # 創建分析器
    analyzer = StockAnalyzer(symbol, period)
    
    # 獲取資料
    if not analyzer.fetch_data():
        print("❌ 獲取資料失敗")
        return
    
    # 計算技術指標
    analyzer.calculate_technical_indicators()
    
    # 手動調試訊號生成
    df = analyzer.data.copy()
    signals = pd.DataFrame(index=df.index)
    signals['Price'] = df['Close']
    signals['Signal'] = 0
    signals['Strength'] = 0
    
    print("\n=== 技術指標檢查 ===")
    latest = df.iloc[-1]
    print(f"最新收盤價: ${latest['Close']:.2f}")
    print(f"SMA_20: ${latest['SMA_20']:.2f}")
    print(f"SMA_50: ${latest['SMA_50']:.2f}")
    print(f"MACD: {latest['MACD']:.4f}")
    print(f"MACD_Signal: {latest['MACD_Signal']:.4f}")
    print(f"RSI: {latest['RSI']:.2f}")
    print(f"BB_Upper: ${latest['BB_Upper']:.2f}")
    print(f"BB_Lower: ${latest['BB_Lower']:.2f}")
    print(f"Stoch_K: {latest['Stoch_K']:.2f}")
    print(f"Stoch_D: {latest['Stoch_D']:.2f}")
    
    # 1. 移動平均線交叉訊號
    signals['MA_Signal'] = 0
    signals.loc[df['SMA_20'] > df['SMA_50'], 'MA_Signal'] = 1
    signals.loc[df['SMA_20'] < df['SMA_50'], 'MA_Signal'] = -1
    
    # 2. MACD 訊號
    signals['MACD_Signal'] = 0
    signals.loc[df['MACD'] > df['MACD_Signal'], 'MACD_Signal'] = 1
    signals.loc[df['MACD'] < df['MACD_Signal'], 'MACD_Signal'] = -1
    
    # 3. RSI 訊號
    signals['RSI_Signal'] = 0
    signals.loc[df['RSI'] < 30, 'RSI_Signal'] = 1  # 超賣
    signals.loc[df['RSI'] > 70, 'RSI_Signal'] = -1  # 超買
    
    # 4. 布林通道訊號
    signals['BB_Signal'] = 0
    signals.loc[df['Close'] < df['BB_Lower'], 'BB_Signal'] = 1  # 價格觸及下軌
    signals.loc[df['Close'] > df['BB_Upper'], 'BB_Signal'] = -1  # 價格觸及上軌
    
    # 5. 隨機指標訊號
    signals['Stoch_Signal'] = 0
    signals.loc[(df['Stoch_K'] < 20) & (df['Stoch_D'] < 20), 'Stoch_Signal'] = 1
    signals.loc[(df['Stoch_K'] > 80) & (df['Stoch_D'] > 80), 'Stoch_Signal'] = -1
    
    print("\n=== 各指標訊號檢查 ===")
    latest_signals = signals.iloc[-1]
    print(f"MA_Signal: {latest_signals['MA_Signal']}")
    print(f"MACD_Signal: {latest_signals['MACD_Signal']}")
    print(f"RSI_Signal: {latest_signals['RSI_Signal']}")
    print(f"BB_Signal: {latest_signals['BB_Signal']}")
    print(f"Stoch_Signal: {latest_signals['Stoch_Signal']}")
    
    # 檢查最近10天的訊號分布
    print("\n=== 最近10天各指標訊號分布 ===")
    recent_signals = signals.tail(10)
    for col in ['MA_Signal', 'MACD_Signal', 'RSI_Signal', 'BB_Signal', 'Stoch_Signal']:
        values = recent_signals[col].value_counts()
        print(f"{col}: {dict(values)}")
    
    # 綜合訊號強度計算
    print("\n=== 訊號強度計算過程 ===")
    for i in range(len(signals)):
        strength = 0
        strength += signals.iloc[i]['MA_Signal'] * 20
        strength += signals.iloc[i]['MACD_Signal'] * 25
        strength += signals.iloc[i]['RSI_Signal'] * 20
        strength += signals.iloc[i]['BB_Signal'] * 15
        strength += signals.iloc[i]['Stoch_Signal'] * 20
        
        signals.iloc[i, signals.columns.get_loc('Strength')] = strength
        
        # 根據強度決定最終訊號
        if strength >= 30:
            signals.iloc[i, signals.columns.get_loc('Signal')] = 1
        elif strength <= -30:
            signals.iloc[i, signals.columns.get_loc('Signal')] = -1
    
    print("\n=== 最終訊號檢查 ===")
    latest_final = signals.iloc[-1]
    print(f"最終強度: {latest_final['Strength']}")
    print(f"最終訊號: {latest_final['Signal']}")
    
    # 檢查最近10天的強度和訊號
    print("\n=== 最近10天強度和訊號 ===")
    recent_final = signals.tail(10)
    for i, row in recent_final.iterrows():
        print(f"{i.strftime('%Y-%m-%d')}: 強度={row['Strength']:.1f}, 訊號={row['Signal']}")
    
    # 統計所有訊號
    print("\n=== 整體訊號統計 ===")
    signal_counts = signals['Signal'].value_counts()
    print(f"訊號分布: {dict(signal_counts)}")
    
    strength_stats = signals['Strength'].describe()
    print(f"強度統計:\n{strength_stats}")
    
    # 檢查是否有極端值
    print(f"\n強度 >= 30 的天數: {len(signals[signals['Strength'] >= 30])}")
    print(f"強度 <= -30 的天數: {len(signals[signals['Strength'] <= -30])}")
    print(f"強度在 -30 到 30 之間的天數: {len(signals[(signals['Strength'] > -30) & (signals['Strength'] < 30)])}")

def test_different_thresholds():
    """測試不同的閾值設定"""
    print("\n=== 測試不同閾值 ===")
    
    symbol = "UNH"
    period = "1y"
    analyzer = StockAnalyzer(symbol, period)
    
    if not analyzer.fetch_data():
        return
    
    analyzer.calculate_technical_indicators()
    
    df = analyzer.data.copy()
    signals = pd.DataFrame(index=df.index)
    signals['Price'] = df['Close']
    signals['Signal'] = 0
    signals['Strength'] = 0
    
    # 計算各指標訊號
    signals['MA_Signal'] = 0
    signals.loc[df['SMA_20'] > df['SMA_50'], 'MA_Signal'] = 1
    signals.loc[df['SMA_20'] < df['SMA_50'], 'MA_Signal'] = -1
    
    signals['MACD_Signal'] = 0
    signals.loc[df['MACD'] > df['MACD_Signal'], 'MACD_Signal'] = 1
    signals.loc[df['MACD'] < df['MACD_Signal'], 'MACD_Signal'] = -1
    
    signals['RSI_Signal'] = 0
    signals.loc[df['RSI'] < 30, 'RSI_Signal'] = 1
    signals.loc[df['RSI'] > 70, 'RSI_Signal'] = -1
    
    signals['BB_Signal'] = 0
    signals.loc[df['Close'] < df['BB_Lower'], 'BB_Signal'] = 1
    signals.loc[df['Close'] > df['BB_Upper'], 'BB_Signal'] = -1
    
    signals['Stoch_Signal'] = 0
    signals.loc[(df['Stoch_K'] < 20) & (df['Stoch_D'] < 20), 'Stoch_Signal'] = 1
    signals.loc[(df['Stoch_K'] > 80) & (df['Stoch_D'] > 80), 'Stoch_Signal'] = -1
    
    # 計算強度
    for i in range(len(signals)):
        strength = 0
        strength += signals.iloc[i]['MA_Signal'] * 20
        strength += signals.iloc[i]['MACD_Signal'] * 25
        strength += signals.iloc[i]['RSI_Signal'] * 20
        strength += signals.iloc[i]['BB_Signal'] * 15
        strength += signals.iloc[i]['Stoch_Signal'] * 20
        signals.iloc[i, signals.columns.get_loc('Strength')] = strength
    
    # 測試不同閾值
    thresholds = [10, 20, 30, 40, 50]
    for threshold in thresholds:
        test_signals = signals.copy()
        test_signals['Signal'] = 0
        test_signals.loc[test_signals['Strength'] >= threshold, 'Signal'] = 1
        test_signals.loc[test_signals['Strength'] <= -threshold, 'Signal'] = -1
        
        signal_counts = test_signals['Signal'].value_counts()
        print(f"閾值 {threshold}: 買入={signal_counts.get(1, 0)}, 賣出={signal_counts.get(-1, 0)}, 持有={signal_counts.get(0, 0)}")

if __name__ == "__main__":
    debug_signal_generation()
    test_different_thresholds() 
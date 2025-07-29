#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
訊號強度演算法詳細說明
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_analyzer import StockAnalyzer
import pandas as pd

def explain_signal_algorithm():
    """詳細解釋訊號強度演算法"""
    print("=== 訊號強度演算法詳細說明 ===")
    print("=" * 60)
    
    print("\n📊 演算法概述")
    print("訊號強度是一個綜合評分系統，範圍從 -100 到 +100")
    print("正值表示買入傾向，負值表示賣出傾向，0表示中性")
    
    print("\n🔧 演算法步驟")
    print("1. 計算5個技術指標的個別訊號")
    print("2. 根據權重加總各指標訊號")
    print("3. 根據總強度決定最終買賣建議")
    
    print("\n📈 技術指標及其權重")
    print("-" * 40)
    print("1. 移動平均線 (MA)     - 權重: 20")
    print("2. MACD               - 權重: 25")
    print("3. RSI                - 權重: 20")
    print("4. 布林通道 (BB)       - 權重: 15")
    print("5. 隨機指標 (Stoch)    - 權重: 20")
    print("總權重: 100")
    
    print("\n🎯 各指標訊號規則")
    print("-" * 40)
    print("每個指標的訊號值: -1 (賣出), 0 (中性), 1 (買入)")
    
    print("\n1. 移動平均線 (MA) - 權重 20")
    print("   • SMA_20 > SMA_50 → 買入訊號 (+1)")
    print("   • SMA_20 < SMA_50 → 賣出訊號 (-1)")
    print("   • 貢獻強度: ±20")
    
    print("\n2. MACD - 權重 25")
    print("   • MACD > MACD_Signal → 買入訊號 (+1)")
    print("   • MACD < MACD_Signal → 賣出訊號 (-1)")
    print("   • 貢獻強度: ±25")
    
    print("\n3. RSI - 權重 20")
    print("   • RSI < 30 → 超賣，買入訊號 (+1)")
    print("   • RSI > 70 → 超買，賣出訊號 (-1)")
    print("   • 30 ≤ RSI ≤ 70 → 中性 (0)")
    print("   • 貢獻強度: ±20")
    
    print("\n4. 布林通道 (BB) - 權重 15")
    print("   • 價格 < BB_Lower → 買入訊號 (+1)")
    print("   • 價格 > BB_Upper → 賣出訊號 (-1)")
    print("   • BB_Lower ≤ 價格 ≤ BB_Upper → 中性 (0)")
    print("   • 貢獻強度: ±15")
    
    print("\n5. 隨機指標 (Stoch) - 權重 20")
    print("   • Stoch_K < 20 且 Stoch_D < 20 → 買入訊號 (+1)")
    print("   • Stoch_K > 80 且 Stoch_D > 80 → 賣出訊號 (-1)")
    print("   • 其他情況 → 中性 (0)")
    print("   • 貢獻強度: ±20")
    
    print("\n🧮 強度計算公式")
    print("-" * 40)
    print("總強度 = MA_Signal × 20 + MACD_Signal × 25 + RSI_Signal × 20 + BB_Signal × 15 + Stoch_Signal × 20")
    
    print("\n📊 最終訊號判斷")
    print("-" * 40)
    print("• 強度 ≥ +20 → 買入訊號")
    print("• 強度 ≤ -20 → 賣出訊號")
    print("• -20 < 強度 < +20 → 持有訊號")
    
    print("\n💡 演算法特點")
    print("-" * 40)
    print("✅ 綜合多個技術指標，避免單一指標的誤判")
    print("✅ 權重分配反映各指標的重要性")
    print("✅ MACD權重最高(25)，因為趨勢指標較可靠")
    print("✅ 布林通道權重最低(15)，因為波動較大")
    print("✅ 閾值±20提供適當的緩衝區間")

def demonstrate_algorithm():
    """實際演示演算法運作"""
    print("\n" + "=" * 60)
    print("=== 實際演算法演示 ===")
    print("=" * 60)
    
    # 分析 UNH 股票
    symbol = "UNH"
    period = "1mo"
    
    print(f"\n📈 分析股票: {symbol}")
    print(f"📅 期間: {period}")
    
    analyzer = StockAnalyzer(symbol, period)
    
    if analyzer.run_analysis():
        # 獲取最新資料
        latest_data = analyzer.data.iloc[-1]
        latest_signals = analyzer.signals.iloc[-1]
        
        print(f"\n📊 最新技術指標值 ({latest_data.name.strftime('%Y-%m-%d')})")
        print("-" * 50)
        print(f"收盤價: ${latest_data['Close']:.2f}")
        print(f"SMA_20: ${latest_data['SMA_20']:.2f}")
        print(f"SMA_50: ${latest_data['SMA_50']:.2f}")
        print(f"MACD: {latest_data['MACD']:.4f}")
        print(f"MACD_Signal: {latest_data['MACD_Signal']:.4f}")
        print(f"RSI: {latest_data['RSI']:.2f}")
        print(f"BB_Upper: ${latest_data['BB_Upper']:.2f}")
        print(f"BB_Lower: ${latest_data['BB_Lower']:.2f}")
        print(f"Stoch_K: {latest_data['Stoch_K']:.2f}")
        print(f"Stoch_D: {latest_data['Stoch_D']:.2f}")
        
        print(f"\n🎯 各指標訊號計算")
        print("-" * 50)
        
        # 1. MA 訊號
        ma_signal = 1 if latest_data['SMA_20'] > latest_data['SMA_50'] else -1
        ma_contribution = ma_signal * 20
        print(f"1. MA訊號: {ma_signal} (SMA_20 {'>' if ma_signal == 1 else '<'} SMA_50)")
        print(f"   貢獻強度: {ma_contribution}")
        
        # 2. MACD 訊號
        macd_signal = 1 if latest_data['MACD'] > latest_data['MACD_Signal'] else -1
        macd_contribution = macd_signal * 25
        print(f"2. MACD訊號: {macd_signal} (MACD {'>' if macd_signal == 1 else '<'} MACD_Signal)")
        print(f"   貢獻強度: {macd_contribution}")
        
        # 3. RSI 訊號
        if latest_data['RSI'] < 30:
            rsi_signal = 1
        elif latest_data['RSI'] > 70:
            rsi_signal = -1
        else:
            rsi_signal = 0
        rsi_contribution = rsi_signal * 20
        print(f"3. RSI訊號: {rsi_signal} (RSI = {latest_data['RSI']:.2f})")
        print(f"   貢獻強度: {rsi_contribution}")
        
        # 4. BB 訊號
        if latest_data['Close'] < latest_data['BB_Lower']:
            bb_signal = 1
        elif latest_data['Close'] > latest_data['BB_Upper']:
            bb_signal = -1
        else:
            bb_signal = 0
        bb_contribution = bb_signal * 15
        print(f"4. BB訊號: {bb_signal} (價格 = ${latest_data['Close']:.2f})")
        print(f"   貢獻強度: {bb_contribution}")
        
        # 5. Stoch 訊號
        if latest_data['Stoch_K'] < 20 and latest_data['Stoch_D'] < 20:
            stoch_signal = 1
        elif latest_data['Stoch_K'] > 80 and latest_data['Stoch_D'] > 80:
            stoch_signal = -1
        else:
            stoch_signal = 0
        stoch_contribution = stoch_signal * 20
        print(f"5. Stoch訊號: {stoch_signal} (K={latest_data['Stoch_K']:.2f}, D={latest_data['Stoch_D']:.2f})")
        print(f"   貢獻強度: {stoch_contribution}")
        
        # 總強度計算
        total_strength = ma_contribution + macd_contribution + rsi_contribution + bb_contribution + stoch_contribution
        
        print(f"\n🧮 總強度計算")
        print("-" * 50)
        print(f"總強度 = {ma_contribution} + {macd_contribution} + {rsi_contribution} + {bb_contribution} + {stoch_contribution}")
        print(f"總強度 = {total_strength}")
        
        # 最終訊號判斷
        if total_strength >= 20:
            final_signal = "買入"
        elif total_strength <= -20:
            final_signal = "賣出"
        else:
            final_signal = "持有"
        
        print(f"\n📊 最終結果")
        print("-" * 50)
        print(f"總強度: {total_strength}")
        print(f"建議動作: {final_signal}")
        print(f"系統計算結果: {analyzer.get_current_signal()['signal']} (強度: {analyzer.get_current_signal()['strength']})")
        
        # 驗證計算
        if abs(total_strength - analyzer.get_current_signal()['strength']) < 0.1:
            print("✅ 計算驗證成功！")
        else:
            print("❌ 計算驗證失敗！")

def show_strength_distribution():
    """顯示強度分布統計"""
    print("\n" + "=" * 60)
    print("=== 強度分布統計 ===")
    print("=" * 60)
    
    symbol = "UNH"
    period = "1y"
    
    analyzer = StockAnalyzer(symbol, period)
    analyzer.run_analysis()
    
    signals = analyzer.signals
    
    print(f"\n📊 {symbol} 強度分布統計")
    print("-" * 40)
    
    # 強度統計
    strength_stats = signals['Strength'].describe()
    print(f"平均強度: {strength_stats['mean']:.2f}")
    print(f"標準差: {strength_stats['std']:.2f}")
    print(f"最小值: {strength_stats['min']:.2f}")
    print(f"最大值: {strength_stats['max']:.2f}")
    
    # 強度區間分布
    print(f"\n📈 強度區間分布")
    print("-" * 40)
    
    intervals = [
        (-100, -50, "極強賣出"),
        (-50, -20, "強賣出"),
        (-20, 0, "弱賣出"),
        (0, 20, "中性"),
        (20, 50, "弱買入"),
        (50, 100, "強買入")
    ]
    
    for min_val, max_val, label in intervals:
        if min_val == -100:
            count = len(signals[(signals['Strength'] >= min_val) & (signals['Strength'] <= max_val)])
        elif max_val == 100:
            count = len(signals[(signals['Strength'] >= min_val) & (signals['Strength'] <= max_val)])
        else:
            count = len(signals[(signals['Strength'] >= min_val) & (signals['Strength'] < max_val)])
        
        percentage = (count / len(signals)) * 100
        print(f"{label:8}: {count:3d} 天 ({percentage:5.1f}%)")

if __name__ == "__main__":
    explain_signal_algorithm()
    demonstrate_algorithm()
    show_strength_distribution()
    
    print("\n" + "=" * 60)
    print("🎉 訊號強度演算法說明完成！")
    print("=" * 60) 
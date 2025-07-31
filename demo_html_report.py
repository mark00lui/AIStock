#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIStock HTML 報告功能演示
"""

import sys
import os

# 添加 src 目錄到路徑
sys.path.append('src')

def demo_single_stock_report():
    """演示單一股票 HTML 報告"""
    print("=== 單一股票 HTML 報告演示 ===")
    print("使用命令: python main.py AAPL --save my_report.html")
    print("這將生成一個包含以下內容的單一 HTML 文件:")
    print("✅ 股票價格和交易訊號")
    print("✅ 技術指標圖表 (MACD, RSI, 隨機指標等)")
    print("✅ 訊號強度分析")
    print("✅ 詳細的技術指標數據")
    print("✅ 風險提醒聲明")
    print("✅ 專業的 CSS 樣式設計")
    print("✅ 響應式佈局，支援手機和電腦")
    print("✅ 所有內容都在單一 HTML 文件中，無需額外圖片")

def demo_batch_stock_report():
    """演示批量股票 HTML 報告"""
    print("\n=== 批量股票 HTML 報告演示 ===")
    print("使用命令: python main.py AAPL MSFT GOOGL TSLA --save batch_report.html")
    print("這將生成一個包含以下內容的單一 HTML 文件:")
    print("✅ 多支股票的綜合分析")
    print("✅ 批量統計摘要")
    print("✅ 每支股票的詳細結果表格")
    print("✅ 所有股票的訊號強度對比圖")
    print("✅ 買入/賣出/持有統計")
    print("✅ 平均強度和強度範圍分析")
    print("✅ 專業的表格和圖表展示")

def demo_features():
    """演示功能特色"""
    print("\n=== HTML 報告功能特色 ===")
    print("🎯 單一文件: 所有內容都在一個 HTML 文件中")
    print("📊 互動圖表: 使用 Plotly 創建互動式圖表")
    print("📱 響應式設計: 支援手機、平板、電腦")
    print("🎨 專業樣式: 現代化的 CSS 設計")
    print("📈 完整分析: 包含所有技術指標和訊號")
    print("📋 詳細數據: 價格、訊號、強度等完整信息")
    print("⚠️ 風險提醒: 包含投資風險警告")
    print("💾 易於分享: 單一文件，方便傳送給客戶")

def demo_usage():
    """演示使用方法"""
    print("\n=== 使用方法 ===")
    print("1. 單一股票分析:")
    print("   python main.py AAPL --save report.html")
    print("   python main.py AAPL --plot")
    print()
    print("2. 批量股票分析:")
    print("   python main.py AAPL MSFT GOOGL --save batch.html")
    print("   python main.py 'AAPL,MSFT,GOOGL' --plot")
    print()
    print("3. 指定分析期間:")
    print("   python main.py AAPL --period 6mo --save report.html")
    print()
    print("4. 互動模式:")
    print("   python main.py")
    print("   然後選擇分析選項")

def main():
    """主演示函數"""
    print("AIStock HTML 報告功能演示")
    print("=" * 50)
    
    demo_single_stock_report()
    demo_batch_stock_report()
    demo_features()
    demo_usage()
    
    print("\n" + "=" * 50)
    print("🎉 HTML 報告功能已成功實現！")
    print("=" * 50)
    print("\n主要改進:")
    print("✅ 所有圖表整合到單一 HTML 文件")
    print("✅ 不使用圖片，完全基於 Plotly 互動圖表")
    print("✅ 專業的 CSS 樣式和響應式設計")
    print("✅ 包含完整的分析數據和風險提醒")
    print("✅ 支援單一股票和批量分析")
    print("✅ 方便傳送給客戶的單一文件格式")
    
    print("\n測試文件:")
    print("📄 test_single_report.html - 單一股票報告示例")
    print("📄 test_batch_report.html - 批量股票報告示例")
    print("\n請在瀏覽器中打開這些文件查看效果")

if __name__ == "__main__":
    main() 
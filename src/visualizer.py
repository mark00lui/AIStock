#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import ta
import base64
from io import BytesIO

class StockVisualizer:
    def __init__(self, analyzer=None):
        self.analyzer = analyzer
    
    def create_single_stock_report(self, analyzer, output_file):
        """
        創建單一股票分析報告 - 用於測試和調試
        """
        print(f"創建單一股票報告: {analyzer.symbol}")
        
        try:
            # 獲取左側分析數據
            from left_analysis import analyze_stock
            left_data = analyze_stock(analyzer.symbol)
            
            result = {
                'symbol': analyzer.symbol,
                'analyzer': analyzer,
                'signal': analyzer.get_current_signal(),
                'summary': analyzer.get_signal_summary(),
                'left_data': left_data
            }
            
            # 創建HTML內容
            html_content = self._generate_single_stock_html(result)
            
            # 寫入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"單一股票報告已保存到: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"創建單一股票報告時發生錯誤: {e}")
            return None
    
    def create_batch_html_report(self, analyzers, output_file, gemini_results=None, categories=None):
        """
        創建批次分析HTML報告 - 復用單一股票功能
        """
        print(f"開始創建批次報告，包含 {len(analyzers)} 個股票...")
        
        # 準備數據
        all_results = []
        for analyzer in analyzers:
            try:
                # 獲取左側分析數據
                from left_analysis import analyze_stock
                left_data = analyze_stock(analyzer.symbol)
                
                # 獲取Gemini AI分析結果
                gemini_data = gemini_results.get(analyzer.symbol) if gemini_results else None
                
                # 獲取分類信息
                category = "未分類"
                if categories:
                    for cat, symbols in categories.items():
                        if analyzer.symbol in symbols:
                            category = cat
                            break
                
                result = {
                    'symbol': analyzer.symbol,
                    'analyzer': analyzer,
                    'signal': analyzer.get_current_signal(),
                    'summary': analyzer.get_signal_summary(),
                    'left_data': left_data,
                    'gemini_data': gemini_data,
                    'category': category
                }
                all_results.append(result)
                print(f"已處理 {analyzer.symbol} (分類: {category})")
            except Exception as e:
                print(f"處理 {analyzer.symbol} 時發生錯誤: {e}")
                continue
        
        # 創建HTML內容
        html_content = self._generate_batch_html(all_results, categories)
        
        # 寫入文件
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"批次報告已保存到: {output_file}")
            return output_file
        except Exception as e:
            print(f"保存報告時發生錯誤: {e}")
            return None
    
    def _generate_single_stock_html(self, result):
        """
        生成單一股票HTML內容 - 簡化版本用於測試
        """
        symbol = result['symbol']
        analyzer = result['analyzer']
        signal_data = result['signal']
        summary = result['summary']
        left_data = result['left_data']
        
        # 獲取股票名稱信息
        stock_name = analyzer.long_name if analyzer.long_name and analyzer.long_name != symbol else symbol
        stock_display_name = f"{symbol} - {stock_name}"
        
        # 獲取數據
        year1_data = left_data.get('timeframes', {}).get('1_year', {}) if left_data else {}
        year2_data = left_data.get('timeframes', {}).get('2_year', {}) if left_data else {}
        year3_data = left_data.get('timeframes', {}).get('3_year', {}) if left_data else {}
        current_price = analyzer.data['Close'].iloc[-1] if analyzer.data is not None else 0
        target_price_1y = year1_data.get('target_mean', 0)
        target_price_2y = year2_data.get('target_mean', 0)
        target_price_3y = year3_data.get('target_mean', 0)
        eps = year1_data.get('future_eps', 0) if year1_data.get('future_eps') is not None else 0
        
        # 獲取增強的分析數據
        recommended_action_1y = year1_data.get('recommended_action', 'Hold')
        confidence_1y = year1_data.get('confidence', 'Medium')
        buy_zone_1y = year1_data.get('buy_zone', 'N/A')
        hold_zone_1y = year1_data.get('hold_zone', 'N/A')
        sell_zone_1y = year1_data.get('sell_zone', 'N/A')
        potential_return_1y = year1_data.get('potential_return', 0)
        
        # 獲取信號
        signal_str = signal_data.get('signal', '持有') if isinstance(signal_data, dict) else str(signal_data)
        signal_class = 'buy' if '買入' in signal_str else 'sell' if '賣出' in signal_str else 'hold'
        
        # 創建增強圖表
        price_chart = self._create_enhanced_price_chart(symbol, current_price, year1_data, stock_display_name)
        technical_chart = self._create_technical_chart(analyzer)
        
        current_date = datetime.now().strftime('%Y年%m月%d日')
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} 股票分析報告</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: clamp(1.8em, 4vw, 2.5em);
            font-weight: 300;
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: clamp(0.9em, 2vw, 1.1em);
        }}
        
        .report-date {{
            margin-top: 15px !important;
            font-size: 0.9em !important;
            opacity: 0.8 !important;
        }}
        
        .analysis-section {{
            padding: 20px;
        }}
        
        .analysis-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .analysis-panel {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
        }}
        
        .analysis-panel h3 {{
            margin: 0 0 20px 0;
            color: #333;
            font-size: 1.3em;
        }}
        
        .info-grid {{
            display: grid;
            gap: 10px;
        }}
        
        .info-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .info-item:last-child {{
            border-bottom: none;
        }}
        
        .label {{
            font-weight: 500;
            color: #666;
        }}
        
        .value {{
            font-weight: bold;
            color: #333;
        }}
        
        .signal-badge {{
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            color: white;
        }}
        
        .signal-buy {{
            background: #4CAF50;
        }}
        
        .signal-sell {{
            background: #f44336;
        }}
        
        .signal-hold {{
            background: #ff9800;
        }}
        
        .chart-container {{
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .chart-container h3 {{
            margin: 0 0 15px 0;
            color: #333;
            font-size: 1.2em;
        }}
        
        /* 響應式設計 */
        @media (min-width: 768px) {{
            .header {{
                padding: 40px 30px;
            }}
            
            .analysis-section {{
                padding: 30px;
            }}
            
            .analysis-grid {{
                grid-template-columns: 1fr 1fr;
                gap: 30px;
            }}
        }}
        
        /* 動畫效果 */
        .analysis-panel {{
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .analysis-panel:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .chart-container {{
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .chart-container:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        /* 響應式設計 */
        @media (max-width: 768px) {{
            .container {{
                margin: 0;
                box-shadow: none;
            }}
            
            .stock-nav {{
                width: 85vw;
                max-width: 320px;
            }}
            
            .header {{
                padding: 20px 15px;
            }}
            
            .summary-section {{
                padding: 15px;
            }}
            
            .summary-grid {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
            
            .stocks-section {{
                padding: 15px;
            }}
            
            .stock-card {{
                margin-bottom: 20px;
            }}
            
            .analysis-grid {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
            
            .chart-container {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {stock_display_name} 股票分析報告</h1>
            <p>技術分析 + 基本面分析綜合評估</p>
            <p class="report-date">生成日期: {current_date}</p>
        </div>
        
        <div class="analysis-section">
            <div class="analysis-grid">
                <div class="analysis-panel">
                    <h3>💰 左側分析策略</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">當前價格:</span>
                            <span class="value">${current_price:.2f}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">1年目標價:</span>
                            <span class="value">${target_price_1y:.2f}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">2年目標價:</span>
                            <span class="value">${target_price_2y:.2f}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">3年目標價:</span>
                            <span class="value">${target_price_3y:.2f}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">預估EPS:</span>
                            <span class="value">${eps:.2f}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">建議動作:</span>
                            <span class="value" style="color: {'#4CAF50' if 'Buy' in recommended_action_1y else '#F44336' if 'Sell' in recommended_action_1y else '#FF9800'};">{recommended_action_1y}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">信心等級:</span>
                            <span class="value">{confidence_1y}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">潛在報酬:</span>
                            <span class="value" style="color: {'#4CAF50' if potential_return_1y > 0 else '#F44336'};">{potential_return_1y:.1f}%</span>
                        </div>
                    </div>
                    
                    <!-- 價格區間信息 -->
                    <div style="margin-top: 15px; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #2196F3;">
                        <h4 style="margin: 0 0 15px 0; color: #333; font-size: 1.1em;">📊 1年價格區間分析</h4>
                        <div style="font-size: 0.9em; line-height: 1.5;">
                            <div style="margin-bottom: 8px;">
                                <span style="color: #4CAF50; font-weight: bold;">🟢 買入區間:</span> {buy_zone_1y}
                            </div>
                            <div style="margin-bottom: 8px;">
                                <span style="color: #2196F3; font-weight: bold;">🔵 持有區間:</span> {hold_zone_1y}
                            </div>
                            <div style="margin-bottom: 8px;">
                                <span style="color: #F44336; font-weight: bold;">🔴 賣出區間:</span> {sell_zone_1y}
                            </div>
                            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #ddd;">
                                <span style="color: #666; font-weight: bold;">當前位置:</span> 
                                <span style="color: {'#4CAF50' if current_price < year1_data.get('target_low', current_price) else '#F44336' if current_price > year1_data.get('target_high', current_price) else '#FF9800'}; font-weight: bold; font-size: 1.1em;">
                                    {'買入區間' if current_price < year1_data.get('target_low', current_price) else '賣出區間' if current_price > year1_data.get('target_high', current_price) else '持有區間'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="analysis-panel">
                    <h3>📈 右側技術分析</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">主要信號:</span>
                            <span class="value">{signal_str.upper()}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">信號強度:</span>
                            <span class="value">{signal_data.get('strength', 'N/A') if isinstance(signal_data, dict) else 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">RSI:</span>
                            <span class="value">{summary.get('rsi', 'N/A')}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">MACD:</span>
                            <span class="value">{summary.get('macd', 'N/A')}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>💰 價格區間分析圖表</h3>
                <div id="price-chart" style="height: 400px;"></div>
            </div>
            
            <div class="chart-container">
                <h3>📈 技術分析圖表</h3>
                <div id="technical-chart" style="height: 600px;"></div>
            </div>
        </div>
    </div>
    
    <script>
        // 價格比較圖表
        {price_chart}
        
        // 技術分析圖表
        {technical_chart}
    </script>
</body>
</html>
        """
        
        return html_content
    
    def _generate_batch_html(self, all_results, categories=None):
        """
        生成批次分析HTML內容 - 響應式設計版本
        """
        current_date = datetime.now().strftime('%Y年%m月%d日')
        
        # 生成股票導航列表
        stock_navigation = self._generate_stock_navigation(all_results, categories)
        
        # 生成摘要統計
        summary_stats = self._generate_summary_stats(all_results)
        
        # 生成股票內容
        stock_content = self._generate_stock_sections(all_results)
        
        # 響應式批次HTML模板
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票分析報告</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-left: 0;
            transition: margin-left 0.3s ease;
        }}
        
        .container.with-nav {{
            margin-left: 280px;
        }}
        
        /* 手機版容器不受導航影響 */
        @media (max-width: 768px) {{
            .container {{
                margin-left: 0 !important;
                transition: none;
            }}
        }}
        
        /* 響應式導航 */
        .nav-toggle {{
            display: block;
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 15px;
            font-size: 1.2em;
            cursor: pointer;
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 1001;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }}
        
        .nav-toggle:hover {{
            background: #5a6fd8;
            transform: scale(1.05);
        }}
        
        .stock-nav {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            position: fixed;
            left: 0;
            top: 0;
            width: 280px;
            height: 100vh;
            z-index: 1000;
            box-shadow: 2px 0 10px rgba(0,0,0,0.2);
            overflow-y: auto;
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }}
        
        .stock-nav.active {{
            transform: translateX(0);
        }}
        
        /* 手機版浮出式導航 */
        @media (max-width: 768px) {{
            .stock-nav {{
                width: 85vw;
                max-width: 320px;
                box-shadow: 0 0 20px rgba(0,0,0,0.3);
                border-radius: 0 10px 10px 0;
            }}
            
            /* 手機版導航背景遮罩 */
            .nav-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(0,0,0,0.5);
                z-index: 999;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
            }}
            
            .nav-overlay.active {{
                opacity: 1;
                visibility: visible;
            }}
        }}
        
        .stock-nav h3 {{
            margin: 0 0 15px 0;
            font-size: 1.2em;
            text-align: center;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }}
        
        .stock-list {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        
        .stock-link {{
            display: flex;
            align-items: center;
            padding: 6px 10px;
            background: rgba(255,255,255,0.1);
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.85em;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }}
        
        .stock-link:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateX(5px);
        }}
        
        .stock-link .symbol {{
            font-weight: bold;
            margin-right: 8px;
        }}
        
        .stock-link .name {{
            opacity: 0.8;
            font-size: 0.8em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: clamp(1.8em, 4vw, 2.5em);
            font-weight: 300;
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: clamp(0.9em, 2vw, 1.1em);
        }}
        
        .report-date {{
            margin-top: 15px !important;
            font-size: 0.9em !important;
            opacity: 0.8 !important;
        }}
        
        .summary-section {{
            padding: 20px;
            border-bottom: 1px solid #eee;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .summary-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .summary-card h3 {{
            margin: 0 0 20px 0;
            color: #333;
            font-size: 1.3em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 15px;
        }}
        
        .stat-item {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}
        
        .signal-list {{
            margin-top: 15px;
            padding: 12px;
            background: rgba(0,0,0,0.8);
            border-radius: 8px;
            font-size: 0.9em;
            line-height: 1.5;
            border: 2px solid rgba(255,255,255,0.3);
            box-shadow: 0 3px 10px rgba(0,0,0,0.4);
            color: #fff;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }}
        
        .signal-list strong {{
            color: #ffd700;
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
            font-size: 1.1em;
        }}
        
        /* 不同類型信號的特殊顏色 */
        .signal-list:has(strong:contains("買入")) {{
            border-left: 4px solid #4CAF50;
            background: linear-gradient(135deg, rgba(76,175,80,0.2) 0%, rgba(0,0,0,0.8) 100%);
        }}
        
        .signal-list:has(strong:contains("賣出")) {{
            border-left: 4px solid #f44336;
            background: linear-gradient(135deg, rgba(244,67,54,0.2) 0%, rgba(0,0,0,0.8) 100%);
        }}
        
        .signal-list:has(strong:contains("AI")) {{
            border-left: 4px solid #667eea;
            background: linear-gradient(135deg, rgba(102,126,234,0.2) 0%, rgba(0,0,0,0.8) 100%);
        }}
        
        /* AI摘要卡片的信號列表特殊樣式 */
        .summary-card[style*="gradient"] .signal-list {{
            background: rgba(0,0,0,0.7);
            border: 2px solid rgba(255,255,255,0.4);
            box-shadow: 0 4px 15px rgba(0,0,0,0.6);
        }}
        
        .summary-card[style*="gradient"] .signal-list strong {{
            color: #ffd700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }}
        
        .signal-list br {{
            margin-bottom: 2px;
        }}
        
        /* 信號列表光澤效果 */
        .signal-list::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent 0%, rgba(255,255,255,0.05) 50%, transparent 100%);
            pointer-events: none;
            border-radius: 8px;
        }}
        
        /* 懸停效果 */
        .signal-list:hover {{
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            border-color: rgba(255,255,255,0.5);
        }}
        
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        
        .stocks-section {{
            padding: 20px;
        }}
        
        .stocks-section h2 {{
            margin: 0 0 30px 0;
            color: #333;
            font-size: clamp(1.5em, 3vw, 2em);
            text-align: center;
        }}
        
        .stock-card {{
            background: white;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            overflow: hidden;
            scroll-margin-top: 100px;
        }}
        
        .stock-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .stock-header h3 {{
            margin: 0;
            font-size: clamp(1.2em, 2.5vw, 1.5em);
            text-align: center;
        }}
        
        .signal-badge {{
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            text-align: center;
            align-self: center;
        }}
        
        .signal-buy {{
            background: #4CAF50;
        }}
        
        .signal-sell {{
            background: #f44336;
        }}
        
        .signal-hold {{
            background: #ff9800;
        }}
        
        .analysis-layout {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            padding: 20px;
        }}
        
        .analysis-panel {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
        }}
        
        .analysis-panel h4 {{
            margin: 0 0 20px 0;
            color: #333;
            font-size: 1.2em;
        }}
        
        .info-grid {{
            display: grid;
            gap: 10px;
        }}
        
        .info-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .info-item:last-child {{
            border-bottom: none;
        }}
        
        .label {{
            font-weight: 500;
            color: #666;
        }}
        
        .value {{
            font-weight: bold;
            color: #333;
        }}
        
        .chart-container {{
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .chart-container h5 {{
            margin: 0 0 15px 0;
            color: #333;
            font-size: 1.1em;
        }}
        
        /* 響應式設計 */
        @media (min-width: 768px) {{
            .stock-nav {{
                padding: 20px 30px;
            }}
            
            .stock-list {{
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                max-height: 150px;
            }}
            
            .header {{
                padding: 40px 30px;
            }}
            
            .summary-section {{
                padding: 30px;
            }}
            
            .stocks-section {{
                padding: 30px;
            }}
            
            .analysis-layout {{
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                padding: 30px;
            }}
            
            .stock-header {{
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
                padding: 25px 30px;
            }}
            
            .stock-header h3 {{
                text-align: left;
            }}
            
            .signal-badge {{
                align-self: auto;
            }}
        }}
        
        @media (min-width: 1024px) {{
            .stock-list {{
                grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            }}
            
            .summary-grid {{
                grid-template-columns: 1fr 1fr;
            }}
        }}
        
        /* 滾動條樣式 */
        .stock-list::-webkit-scrollbar {{
            width: 6px;
        }}
        
        .stock-list::-webkit-scrollbar-track {{
            background: #34495e;
            border-radius: 3px;
        }}
        
        .stock-list::-webkit-scrollbar-thumb {{
            background: #667eea;
            border-radius: 3px;
        }}
        
        .stock-list::-webkit-scrollbar-thumb:hover {{
            background: #5a6fd8;
        }}
        
        /* 動畫效果 */
        .stock-card {{
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stock-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        /* 回到頂部按鈕 */
        .back-to-top {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.2em;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            z-index: 1000;
        }}
        
        .back-to-top:hover {{
            background: #5a6fd8;
            transform: translateY(-2px);
        }}
        
        /* 載入動畫 */
        .loading {{
            text-align: center;
            padding: 40px;
            color: #666;
        }}
        
        .spinner {{
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <button class="nav-toggle" onclick="toggleNav()">📋</button>
    
    <!-- 手機版導航背景遮罩 -->
    <div class="nav-overlay" id="navOverlay" onclick="toggleNav()"></div>
    
    <div class="stock-nav" id="stockNav">
        <h3>📊 股票導航</h3>
        <div class="stock-list">
            {stock_navigation}
        </div>
    </div>
    
    <div class="container">
        
        <div class="header">
            <h1>📊 股票分析報告</h1>
            <p>技術分析 + 基本面分析綜合評估</p>
            <p class="report-date">生成日期: {current_date}</p>
        </div>
        
        <div class="summary-section">
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>📈 技術分析摘要</h3>
                    <div class="stats-grid">
                        {summary_stats['technical']}
                    </div>
                </div>
                <div class="summary-card">
                    <h3>💰 左側分析摘要</h3>
                    <div class="stats-grid">
                        {summary_stats['left']}
                    </div>
                </div>
                <div class="summary-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <h3>🤖 Gemini AI 摘要</h3>
                    <div class="stats-grid">
                        {summary_stats['ai']}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="stocks-section">
            <h2>📋 個股分析</h2>
            {stock_content}
        </div>
    </div>
    
    <button class="back-to-top" onclick="scrollToTop()" title="回到頂部">↑</button>
    
    <script>
        // 導航切換功能
        function toggleNav() {{
            const nav = document.getElementById('stockNav');
            const container = document.querySelector('.container');
            const overlay = document.getElementById('navOverlay');
            
            nav.classList.toggle('active');
            
            // 手機版顯示背景遮罩
            if (window.innerWidth <= 768 && overlay) {{
                overlay.classList.toggle('active');
            }}
            
            // 只在桌面版調整容器邊距
            if (window.innerWidth > 768) {{
                container.classList.toggle('with-nav');
            }}
        }}
        
        // 平滑滾動到指定股票
        function scrollToStock(symbol) {{
            const element = document.getElementById('stock-' + symbol);
            if (element) {{
                element.scrollIntoView({{ 
                    behavior: 'smooth',
                    block: 'start'
                }});
                
                // 手機版點擊後自動收起導航
                if (window.innerWidth <= 768) {{
                    setTimeout(() => {{
                        const nav = document.getElementById('stockNav');
                        const overlay = document.getElementById('navOverlay');
                        nav.classList.remove('active');
                        if (overlay) {{
                            overlay.classList.remove('active');
                        }}
                    }}, 300); // 等待滾動動畫開始後收起
                }}
            }}
        }}
        
        // 回到頂部
        function scrollToTop() {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }}
        
        // 響應式導航顯示控制
        function handleResize() {{
            const nav = document.getElementById('stockNav');
            const toggle = document.querySelector('.nav-toggle');
            const container = document.querySelector('.container');
            const overlay = document.getElementById('navOverlay');
            
            if (window.innerWidth <= 768) {{
                nav.classList.remove('active');
                container.classList.remove('with-nav');
                if (overlay) {{
                    overlay.classList.remove('active');
                }}
                toggle.style.display = 'block';
            }} else {{
                nav.classList.add('active');
                container.classList.add('with-nav');
                if (overlay) {{
                    overlay.classList.remove('active');
                }}
                toggle.style.display = 'block';
            }}
        }}
        
        // 頁面載入完成後初始化
        window.addEventListener('load', function() {{
            handleResize();
            
            // 添加滾動監聽，顯示/隱藏回到頂部按鈕
            window.addEventListener('scroll', function() {{
                const backToTop = document.querySelector('.back-to-top');
                if (window.pageYOffset > 300) {{
                    backToTop.style.display = 'block';
                }} else {{
                    backToTop.style.display = 'none';
                }}
            }});
        }});
        
        // 視窗大小改變時重新調整
        window.addEventListener('resize', handleResize);
        
        // 初始化回到頂部按鈕為隱藏
        document.querySelector('.back-to-top').style.display = 'none';
    </script>
</body>
</html>
        """
        
        return html_content
    
    def _generate_stock_navigation(self, all_results, categories=None):
        """
        生成股票導航列表 - 支持分類
        """
        navigation_html = ""
        
        if categories:
            # 按分類組織股票
            for category, category_symbols in categories.items():
                # 添加分類標題
                navigation_html += f"""
                <div style="grid-column: 1 / -1; margin: 10px 0 5px 0; padding: 5px 10px; background: rgba(255,255,255,0.1); border-radius: 5px; font-weight: bold; font-size: 0.9em; color: #fff;">
                    📂 {category}
                </div>
                """
                
                # 添加該分類下的股票
                for symbol in category_symbols:
                    # 找到對應的結果
                    result = next((r for r in all_results if r['symbol'] == symbol), None)
                    if result:
                        analyzer = result['analyzer']
                        signal_data = result['signal']
                        
                        # 獲取股票名稱信息
                        stock_name = analyzer.long_name if analyzer.long_name and analyzer.long_name != symbol else symbol
                        display_name = f"{symbol}<br><small>{stock_name[:15]}{'...' if len(stock_name) > 15 else ''}</small>"
                        
                        # 獲取信號顏色
                        signal_str = signal_data.get('signal', '持有') if isinstance(signal_data, dict) else str(signal_data)
                        signal_color = '#4CAF50' if '買入' in signal_str else '#f44336' if '賣出' in signal_str else '#ff9800'
                        
                        navigation_html += f"""
                        <a href="#stock-{symbol}" class="stock-link" onclick="scrollToStock('{symbol}')" 
                           style="border-left: 3px solid {signal_color};">
                            <span class="symbol">{symbol}</span>
                            <span class="name">{stock_name[:12]}{'...' if len(stock_name) > 12 else ''}</span>
                        </a>
                        """
        else:
            # 原有的不分類導航
            for result in all_results:
                symbol = result['symbol']
                analyzer = result['analyzer']
                signal_data = result['signal']
                
                # 獲取股票名稱信息
                stock_name = analyzer.long_name if analyzer.long_name and analyzer.long_name != symbol else symbol
                display_name = f"{symbol}<br><small>{stock_name[:15]}{'...' if len(stock_name) > 15 else ''}</small>"
                
                # 獲取信號顏色
                signal_str = signal_data.get('signal', '持有') if isinstance(signal_data, dict) else str(signal_data)
                signal_color = '#4CAF50' if '買入' in signal_str else '#f44336' if '賣出' in signal_str else '#ff9800'
                
                navigation_html += f"""
                <a href="#stock-{symbol}" class="stock-link" onclick="scrollToStock('{symbol}')" 
                   style="border-left: 3px solid {signal_color};">
                    <span class="symbol">{symbol}</span>
                    <span class="name">{stock_name[:12]}{'...' if len(stock_name) > 12 else ''}</span>
                </a>
                """
        
        return navigation_html
    
    def _create_enhanced_price_chart(self, symbol, current_price, timeframe_data, stock_display_name=None):
        """
        創建增強的價格區間圖表 - 顯示買賣區間和當前位置
        """
        # 確保價格不為0或負數
        current_price = max(current_price, 0.01)
        
        # 將股票代碼中的點號替換為下劃線，使其成為有效的JavaScript變量名
        safe_symbol = symbol.replace('.', '_')
        
        # 使用提供的顯示名稱或默認使用股票代碼
        chart_title = stock_display_name if stock_display_name else symbol
        
        # 獲取價格區間數據
        target_low = timeframe_data.get('target_low', current_price * 0.8)
        target_mean = timeframe_data.get('target_mean', current_price * 1.1)
        target_high = timeframe_data.get('target_high', current_price * 1.2)
        
        # 確保價格合理性
        target_low = max(target_low, current_price * 0.5)
        target_high = max(target_high, current_price * 1.5)
        
        # 計算當前價格在區間中的位置
        price_range = target_high - target_low
        if price_range > 0:
            current_position = (current_price - target_low) / price_range
            current_position = max(0, min(1, current_position))  # 限制在0-1之間
        else:
            current_position = 0.5
        
        # 確定顏色
        if current_price < target_low:
            current_color = '#4CAF50'  # 綠色 - 買入區間
        elif current_price < target_mean:
            current_color = '#FF9800'  # 橙色 - 持有/買入區間
        elif current_price < target_high:
            current_color = '#FFC107'  # 黃色 - 持有區間
        else:
            current_color = '#F44336'  # 紅色 - 賣出區間
        
        chart_js = f"""
        const priceData_{safe_symbol} = [
            // 價格區間背景
            {{
                x: ['價格區間'],
                y: [{target_high}],
                type: 'bar',
                name: '上限',
                marker: {{
                    color: '#F44336',
                    opacity: 0.3
                }},
                showlegend: false
            }},
            {{
                x: ['價格區間'],
                y: [{target_mean}],
                type: 'bar',
                name: '目標均值',
                marker: {{
                    color: '#2196F3',
                    opacity: 0.5
                }},
                showlegend: false
            }},
            {{
                x: ['價格區間'],
                y: [{target_low}],
                type: 'bar',
                name: '下限',
                marker: {{
                    color: '#4CAF50',
                    opacity: 0.3
                }},
                showlegend: false
            }},
            // 當前價格
            {{
                x: ['當前價格'],
                y: [{current_price}],
                type: 'bar',
                name: '當前價格',
                marker: {{
                    color: '{current_color}',
                    line: {{
                        color: '#333',
                        width: 2
                    }}
                }},
                text: ['${current_price:.2f}'],
                textposition: 'auto',
                textfont: {{
                    size: 14,
                    color: 'white',
                    weight: 'bold'
                }},
                showlegend: false
            }}
        ];
        
        const priceLayout_{safe_symbol} = {{
            title: '{chart_title} 價格區間分析',
            yaxis: {{
                title: '價格 ($)',
                range: [{target_low * 0.9}, {target_high * 1.1}]
            }},
            margin: {{
                l: 60,
                r: 40,
                t: 80,
                b: 80
            }},
            annotations: [
                {{
                    x: 0.5,
                    y: {target_high},
                    xref: 'paper',
                    yref: 'y',
                    text: '賣出區間',
                    showarrow: false,
                    font: {{
                        color: '#F44336',
                        size: 12
                    }}
                }},
                {{
                    x: 0.5,
                    y: {target_mean},
                    xref: 'paper',
                    yref: 'y',
                    text: '持有區間',
                    showarrow: false,
                    font: {{
                        color: '#2196F3',
                        size: 12
                    }}
                }},
                {{
                    x: 0.5,
                    y: {target_low},
                    xref: 'paper',
                    yref: 'y',
                    text: '買入區間',
                    showarrow: false,
                    font: {{
                        color: '#4CAF50',
                        size: 12
                    }}
                }}
            ],
            showlegend: false
        }};
        
        Plotly.newPlot('price-chart-{symbol}', priceData_{safe_symbol}, priceLayout_{safe_symbol});
        """
        return chart_js
    
    def _create_price_comparison_chart(self, symbol, current_price, target_price, stock_display_name=None):
        """
        創建價格比較圖表 - 可重用函數（保持向後兼容）
        """
        # 確保價格不為0或負數
        current_price = max(current_price, 0.01)
        target_price = max(target_price, 0.01)
        
        # 將股票代碼中的點號替換為下劃線，使其成為有效的JavaScript變量名
        safe_symbol = symbol.replace('.', '_')
        
        # 使用提供的顯示名稱或默認使用股票代碼
        chart_title = stock_display_name if stock_display_name else symbol
        
        chart_js = f"""
        const priceData_{safe_symbol} = [
            {{
                x: ['當前價格', '1年目標價'],
                y: [{current_price}, {target_price}],
                type: 'bar',
                marker: {{
                    color: ['#667eea', '#4CAF50']
                }},
                text: ['${current_price:.2f}', '${target_price:.2f}'],
                textposition: 'auto',
                textfont: {{
                    size: 14,
                    color: 'white'
                }}
            }}
        ];
        
        const priceLayout_{safe_symbol} = {{
            title: '{chart_title} 價格比較',
            yaxis: {{
                title: '價格 ($)'
            }},
            margin: {{
                l: 60,
                r: 40,
                t: 60,
                b: 60
            }},
            showlegend: false
        }};
        
        Plotly.newPlot('price-chart-{symbol}', priceData_{safe_symbol}, priceLayout_{safe_symbol});
        """
        return chart_js
    
    def _create_technical_chart(self, analyzer):
        """
        創建技術分析圖表 - 可重用函數
        """
        try:
            if analyzer.data is None or len(analyzer.data) < 50:
                return f"document.getElementById('technical-chart-{analyzer.symbol}').innerHTML = '<p style=\"text-align: center; color: #666;\">數據不足，無法生成技術圖表</p>';"
            
            # 取最近252個交易日
            df = analyzer.data.tail(252).copy()
            
            # 計算技術指標
            df['SMA_120'] = df['Close'].rolling(window=120).mean()
            df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
            
            # 計算MACD
            macd = ta.trend.MACD(df['Close'])
            df['MACD'] = macd.macd()
            df['MACD_Signal'] = macd.macd_signal()
            df['MACD_Histogram'] = macd.macd_diff()
            
            # 計算布林通道
            bb = ta.volatility.BollingerBands(df['Close'])
            df['BB_Upper'] = bb.bollinger_hband()
            df['BB_Lower'] = bb.bollinger_lband()
            
            # 移除NaN值
            df = df.dropna()
            
            if len(df) < 50:
                return f"document.getElementById('technical-chart-{analyzer.symbol}').innerHTML = '<p style=\"text-align: center; color: #666;\">有效數據不足，無法生成技術圖表</p>';"
            
            # 準備圖表數據
            dates = df.index.strftime('%Y-%m-%d').tolist()
            close_prices = df['Close'].tolist()
            sma_120 = df['SMA_120'].tolist()
            bb_upper = df['BB_Upper'].tolist()
            bb_lower = df['BB_Lower'].tolist()
            rsi = df['RSI'].tolist()
            macd = df['MACD'].tolist()
            macd_signal = df['MACD_Signal'].tolist()
            macd_histogram = df['MACD_Histogram'].tolist()
            
            # 將股票代碼中的點號替換為下劃線，使其成為有效的JavaScript變量名
            safe_symbol = analyzer.symbol.replace('.', '_')
            
            chart_js = f"""
            const technicalData_{safe_symbol} = [
                // 股價圖表
                {{
                    x: {dates},
                    y: {close_prices},
                    type: 'scatter',
                    mode: 'lines',
                    name: '股價',
                    line: {{ color: '#333', width: 2 }},
                    yaxis: 'y'
                }},
                {{
                    x: {dates},
                    y: {sma_120},
                    type: 'scatter',
                    mode: 'lines',
                    name: '120MA',
                    line: {{ color: 'orange', width: 2 }},
                    yaxis: 'y'
                }},
                {{
                    x: {dates},
                    y: {bb_upper},
                    type: 'scatter',
                    mode: 'lines',
                    name: '布林上軌',
                    line: {{ color: 'gray', dash: 'dash', width: 1 }},
                    yaxis: 'y'
                }},
                {{
                    x: {dates},
                    y: {bb_lower},
                    type: 'scatter',
                    mode: 'lines',
                    name: '布林下軌',
                    line: {{ color: 'gray', dash: 'dash', width: 1 }},
                    fill: 'tonexty',
                    fillcolor: 'rgba(128,128,128,0.1)',
                    yaxis: 'y'
                }},
                // RSI
                {{
                    x: {dates},
                    y: {rsi},
                    type: 'scatter',
                    mode: 'lines',
                    name: 'RSI',
                    line: {{ color: 'purple', width: 1.5 }},
                    yaxis: 'y2'
                }},
                // MACD
                {{
                    x: {dates},
                    y: {macd},
                    type: 'scatter',
                    mode: 'lines',
                    name: 'MACD',
                    line: {{ color: 'blue', width: 1.5 }},
                    yaxis: 'y3'
                }},
                {{
                    x: {dates},
                    y: {macd_signal},
                    type: 'scatter',
                    mode: 'lines',
                    name: 'MACD Signal',
                    line: {{ color: 'red', width: 1.5 }},
                    yaxis: 'y3'
                }},
                {{
                    x: {dates},
                    y: {macd_histogram},
                    type: 'bar',
                    name: 'MACD Histogram',
                    marker: {{
                        color: {macd_histogram}.map(val => val >= 0 ? 'green' : 'red'),
                        opacity: 0.7
                    }},
                    yaxis: 'y3'
                }}
            ];
            
                         const technicalLayout_{safe_symbol} = {{
                 title: '{analyzer.symbol} - {analyzer.long_name if analyzer.long_name and analyzer.long_name != analyzer.symbol else analyzer.symbol} 技術分析',
                height: 600,
                grid: {{
                    rows: 3,
                    columns: 1,
                    pattern: 'independent'
                }},
                yaxis: {{ title: '股價 ($)', domain: [0.67, 1] }},
                yaxis2: {{ 
                    title: 'RSI', 
                    domain: [0.33, 0.66],
                    range: [0, 100]
                }},
                yaxis3: {{ 
                    title: 'MACD', 
                    domain: [0, 0.32]
                }},
                showlegend: false
            }};
            
            Plotly.newPlot('technical-chart-{analyzer.symbol}', technicalData_{safe_symbol}, technicalLayout_{safe_symbol});
            """
            
            return chart_js
            
        except Exception as e:
            return f"document.getElementById('technical-chart-{analyzer.symbol}').innerHTML = '<p style=\"text-align: center; color: #666;\">技術圖表生成失敗: {str(e)}</p>';"
    
    def _generate_summary_stats(self, all_results):
        """
        生成摘要統計 - 包含信號強度排序
        """
        # 技術分析統計和排序
        buy_count = 0
        sell_count = 0
        hold_count = 0
        technical_signals = []
        
        for result in all_results:
            symbol = result['symbol']
            signal_data = result['signal']
            if isinstance(signal_data, dict):
                signal_str = signal_data.get('signal', '持有')
                signal_strength = signal_data.get('strength', '中')
            else:
                signal_str = str(signal_data)
                signal_strength = '中'
            
            # 統計數量
            if '買入' in signal_str:
                buy_count += 1
            elif '賣出' in signal_str:
                sell_count += 1
            else:
                hold_count += 1
            
            # 收集信號數據用於排序
            technical_signals.append({
                'symbol': symbol,
                'signal': signal_str,
                'strength': signal_strength,
                'current_price': result['analyzer'].data['Close'].iloc[-1] if result['analyzer'].data is not None else 0
            })
        
        # 按信號強度排序技術分析信號
        buy_signals = [s for s in technical_signals if '買入' in s['signal']]
        sell_signals = [s for s in technical_signals if '賣出' in s['signal']]
        
        # 按強度排序（強 > 中 > 弱）
        strength_order = {'強': 3, '中': 2, '弱': 1}
        buy_signals.sort(key=lambda x: strength_order.get(x['strength'], 1), reverse=True)
        sell_signals.sort(key=lambda x: strength_order.get(x['strength'], 1), reverse=True)
        
        # 左側分析統計和排序
        total_stocks = len(all_results)
        undervalued_count = 0
        overvalued_count = 0
        left_signals = []
        
        for result in all_results:
            symbol = result['symbol']
            left_data = result['left_data']
            if left_data and 'timeframes' in left_data:
                year1_data = left_data['timeframes'].get('1_year', {})
                if year1_data:
                    current_price = result['analyzer'].data['Close'].iloc[-1]
                    target_price = year1_data.get('target_mean', current_price)
                    potential_return = year1_data.get('potential_return', 0)
                    confidence = year1_data.get('confidence', 'Medium')
                    
                    if current_price < target_price:
                        undervalued_count += 1
                        signal_type = '買入'
                    else:
                        overvalued_count += 1
                        signal_type = '賣出'
                    
                    # 收集左側分析數據用於排序
                    left_signals.append({
                        'symbol': symbol,
                        'signal': signal_type,
                        'potential_return': potential_return,
                        'confidence': confidence,
                        'current_price': current_price,
                        'target_price': target_price
                    })
        
        # 按潛在報酬排序左側分析信號
        left_buy_signals = [s for s in left_signals if s['signal'] == '買入']
        left_sell_signals = [s for s in left_signals if s['signal'] == '賣出']
        
        # 按潛在報酬排序（買入信號按報酬從高到低，賣出信號按報酬從低到高）
        left_buy_signals.sort(key=lambda x: x['potential_return'], reverse=True)
        left_sell_signals.sort(key=lambda x: x['potential_return'])  # 賣出信號按報酬從低到高排序
        
        # Gemini AI統計和排序
        ai_buy_count = 0
        ai_sell_count = 0
        ai_hold_count = 0
        ai_bullish_count = 0
        ai_bearish_count = 0
        ai_neutral_count = 0
        ai_signals = []
        
        for result in all_results:
            symbol = result['symbol']
            gemini_data = result.get('gemini_data')
            if gemini_data:
                analysis_summary = gemini_data.get('analysis_summary', {})
                investment_rec = gemini_data.get('investment_recommendation', {})
                
                # 統計AI建議
                ai_action = investment_rec.get('action', '')
                ai_conviction = investment_rec.get('conviction_level', '中')
                ai_target_price = investment_rec.get('target_price', 'N/A')
                
                if '買入' in ai_action:
                    ai_buy_count += 1
                    signal_type = 'AI買入'
                elif '賣出' in ai_action:
                    ai_sell_count += 1
                    signal_type = 'AI賣出'
                else:
                    ai_hold_count += 1
                    signal_type = 'AI持有'
                
                # 統計AI情緒
                ai_sentiment = analysis_summary.get('overall_sentiment', '')
                if '看漲' in ai_sentiment:
                    ai_bullish_count += 1
                elif '看跌' in ai_sentiment:
                    ai_bearish_count += 1
                else:
                    ai_neutral_count += 1
                
                # 收集AI信號數據用於排序
                ai_signals.append({
                    'symbol': symbol,
                    'signal': signal_type,
                    'conviction': ai_conviction,
                    'sentiment': ai_sentiment,
                    'target_price': ai_target_price,
                    'current_price': result['analyzer'].data['Close'].iloc[-1] if result['analyzer'].data is not None else 0
                })
        
        # 按信心等級排序AI信號
        ai_buy_signals = [s for s in ai_signals if '買入' in s['signal']]
        ai_sell_signals = [s for s in ai_signals if '賣出' in s['signal']]
        
        # 按信心等級排序（高 > 中 > 低）
        conviction_order = {'高': 3, '中': 2, '低': 1}
        ai_buy_signals.sort(key=lambda x: conviction_order.get(x['conviction'], 1), reverse=True)
        ai_sell_signals.sort(key=lambda x: conviction_order.get(x['conviction'], 1), reverse=True)
        
        # 生成技術分析排序列表
        technical_buy_list = ""
        technical_sell_list = ""
        
        if buy_signals:
            technical_buy_list = "<div class='signal-list'><strong>🔥 強烈買入信號:</strong><br>"
            for i, signal in enumerate(buy_signals[:5], 1):  # 顯示前5個
                technical_buy_list += f"{i}. {signal['symbol']} ({signal['strength']})<br>"
            technical_buy_list += "</div>"
        
        if sell_signals:
            technical_sell_list = "<div class='signal-list'><strong>⚠️ 強烈賣出信號:</strong><br>"
            for i, signal in enumerate(sell_signals[:5], 1):  # 顯示前5個
                technical_sell_list += f"{i}. {signal['symbol']} ({signal['strength']})<br>"
            technical_sell_list += "</div>"
        
        technical_stats = f"""
            <div class="stat-item">
                <div class="stat-value">{buy_count}</div>
                <div class="stat-label">買入信號</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{sell_count}</div>
                <div class="stat-label">賣出信號</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{hold_count}</div>
                <div class="stat-label">持有信號</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{total_stocks}</div>
                <div class="stat-label">總股票數</div>
            </div>
            {technical_buy_list}
            {technical_sell_list}
        """
        
        # 生成左側分析排序列表
        left_buy_list = ""
        left_sell_list = ""
        
        if left_buy_signals:
            left_buy_list = "<div class='signal-list'><strong>💰 高報酬買入機會:</strong><br>"
            for i, signal in enumerate(left_buy_signals[:5], 1):  # 顯示前5個
                left_buy_list += f"{i}. {signal['symbol']} (+{signal['potential_return']:.1f}%)<br>"
            left_buy_list += "</div>"
        
        if left_sell_signals:
            left_sell_list = "<div class='signal-list'><strong>📉 高風險賣出警告:</strong><br>"
            for i, signal in enumerate(left_sell_signals[:5], 1):  # 顯示前5個
                left_sell_list += f"{i}. {signal['symbol']} ({signal['potential_return']:.1f}%)<br>"
            left_sell_list += "</div>"
        
        left_stats = f"""
            <div class="stat-item">
                <div class="stat-value">{undervalued_count}</div>
                <div class="stat-label">低估股票</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{overvalued_count}</div>
                <div class="stat-label">高估股票</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{total_stocks}</div>
                <div class="stat-label">總股票數</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{total_stocks}</div>
                <div class="stat-label">分析完成</div>
            </div>
            {left_buy_list}
            {left_sell_list}
        """
        
        # 生成AI排序列表
        ai_buy_list = ""
        ai_sell_list = ""
        
        if ai_buy_signals:
            ai_buy_list = "<div class='signal-list'><strong>🤖 AI高信心買入:</strong><br>"
            for i, signal in enumerate(ai_buy_signals[:5], 1):  # 顯示前5個
                ai_buy_list += f"{i}. {signal['symbol']} ({signal['conviction']})<br>"
            ai_buy_list += "</div>"
        
        if ai_sell_signals:
            ai_sell_list = "<div class='signal-list'><strong>🤖 AI高信心賣出:</strong><br>"
            for i, signal in enumerate(ai_sell_signals[:5], 1):  # 顯示前5個
                ai_sell_list += f"{i}. {signal['symbol']} ({signal['conviction']})<br>"
            ai_sell_list += "</div>"
        
        # 生成AI統計HTML
        ai_stats = ""
        if ai_buy_count + ai_sell_count + ai_hold_count > 0:
            ai_stats = f"""
                <div class="stat-item">
                    <div class="stat-value">{ai_buy_count}</div>
                    <div class="stat-label">AI買入</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{ai_sell_count}</div>
                    <div class="stat-label">AI賣出</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{ai_hold_count}</div>
                    <div class="stat-label">AI持有</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{ai_bullish_count}</div>
                    <div class="stat-label">看漲情緒</div>
                </div>
                {ai_buy_list}
                {ai_sell_list}
            """
        else:
            ai_stats = """
                <div class="stat-item">
                    <div class="stat-value">-</div>
                    <div class="stat-label">AI分析</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">-</div>
                    <div class="stat-label">未啟用</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">-</div>
                    <div class="stat-label">請提供</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">-</div>
                    <div class="stat-label">API金鑰</div>
                </div>
            """
        
        return {
            'technical': technical_stats,
            'left': left_stats,
            'ai': ai_stats
        }
    
    def _generate_stock_sections(self, all_results):
        """
        生成股票分析區塊 - 批次模式（包含圖表）
        """
        content = ""
        
        for result in all_results:
            symbol = result['symbol']
            analyzer = result['analyzer']
            signal_data = result['signal']
            summary = result['summary']
            left_data = result['left_data']
            
            # 獲取股票名稱信息
            stock_name = analyzer.long_name if analyzer.long_name and analyzer.long_name != symbol else symbol
            stock_display_name = f"{symbol} - {stock_name}"
            
            # 獲取左側分析數據
            year1_data = left_data.get('timeframes', {}).get('1_year', {}) if left_data else {}
            year2_data = left_data.get('timeframes', {}).get('2_year', {}) if left_data else {}
            year3_data = left_data.get('timeframes', {}).get('3_year', {}) if left_data else {}
            
            # 獲取Gemini AI分析數據
            gemini_data = result.get('gemini_data')
            
            # 格式化數據
            current_price = analyzer.data['Close'].iloc[-1] if analyzer.data is not None else 0
            target_price_1y = year1_data.get('target_mean', 0)
            target_price_2y = year2_data.get('target_mean', 0)
            target_price_3y = year3_data.get('target_mean', 0)
            eps = year1_data.get('future_eps', 0) if year1_data.get('future_eps') is not None else 0
            
            # 獲取增強的分析數據
            recommended_action_1y = year1_data.get('recommended_action', 'Hold')
            confidence_1y = year1_data.get('confidence', 'Medium')
            buy_zone_1y = year1_data.get('buy_zone', 'N/A')
            hold_zone_1y = year1_data.get('hold_zone', 'N/A')
            sell_zone_1y = year1_data.get('sell_zone', 'N/A')
            potential_return_1y = year1_data.get('potential_return', 0)
            
            # 獲取信號字符串
            signal_str = signal_data.get('signal', '持有') if isinstance(signal_data, dict) else str(signal_data)
            signal_class = 'buy' if '買入' in signal_str else 'sell' if '賣出' in signal_str else 'hold'
            
            # 計算估值狀態（基於1年目標價）
            valuation_status = "低估" if current_price < target_price_1y else "高估" if current_price > target_price_1y else "合理"
            valuation_color = "#4CAF50" if valuation_status == "低估" else "#f44336" if valuation_status == "高估" else "#ff9800"
            
            # 創建增強圖表
            price_chart = self._create_enhanced_price_chart(symbol, current_price, year1_data, stock_display_name)
            technical_chart = self._create_technical_chart(analyzer)
            
            stock_html = f"""
            <div class="stock-card" id="stock-{symbol}">
                <div class="stock-header">
                    <h3>{stock_display_name}</h3>
                    <span class="signal-badge signal-{signal_class}">{signal_str.upper()}</span>
                </div>
                
                <div class="analysis-layout">
                    <div class="analysis-panel">
                        <h4>💰 左側分析策略</h4>
                        <div class="info-grid">
                            <div class="info-item">
                                <span class="label">當前價格:</span>
                                <span class="value">${current_price:.2f}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">1年目標價:</span>
                                <span class="value">${target_price_1y:.2f}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">2年目標價:</span>
                                <span class="value">${target_price_2y:.2f}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">3年目標價:</span>
                                <span class="value">${target_price_3y:.2f}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">預估EPS:</span>
                                <span class="value">${eps:.2f}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">建議動作:</span>
                                <span class="value" style="color: {'#4CAF50' if 'Buy' in recommended_action_1y else '#F44336' if 'Sell' in recommended_action_1y else '#FF9800'};">{recommended_action_1y}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">信心等級:</span>
                                <span class="value">{confidence_1y}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">潛在報酬:</span>
                                <span class="value" style="color: {'#4CAF50' if potential_return_1y > 0 else '#F44336'};">{potential_return_1y:.1f}%</span>
                            </div>
                        </div>
                        
                        <!-- 價格區間信息 -->
                        <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #2196F3;">
                            <h5 style="margin: 0 0 10px 0; color: #333; font-size: 0.9em;">📊 1年價格區間分析</h5>
                            <div style="font-size: 0.85em; line-height: 1.4;">
                                <div style="margin-bottom: 5px;">
                                    <span style="color: #4CAF50; font-weight: bold;">🟢 買入區間:</span> {buy_zone_1y}
                                </div>
                                <div style="margin-bottom: 5px;">
                                    <span style="color: #2196F3; font-weight: bold;">🔵 持有區間:</span> {hold_zone_1y}
                                </div>
                                <div style="margin-bottom: 5px;">
                                    <span style="color: #F44336; font-weight: bold;">🔴 賣出區間:</span> {sell_zone_1y}
                                </div>
                                <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #ddd;">
                                    <span style="color: #666; font-weight: bold;">當前位置:</span> 
                                    <span style="color: {'#4CAF50' if current_price < year1_data.get('target_low', current_price) else '#F44336' if current_price > year1_data.get('target_high', current_price) else '#FF9800'}; font-weight: bold;">
                                        {'買入區間' if current_price < year1_data.get('target_low', current_price) else '賣出區間' if current_price > year1_data.get('target_high', current_price) else '持有區間'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="analysis-panel">
                        <h4>📈 右側技術分析</h4>
                        <div class="info-grid">
                            <div class="info-item">
                                <span class="label">主要信號:</span>
                                <span class="value">{signal_str.upper()}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">信號強度:</span>
                                <span class="value">{signal_data.get('strength', 'N/A') if isinstance(signal_data, dict) else 'N/A'}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">年化波動率:</span>
                                <span class="value" style="color: {self._get_volatility_color(summary.get('volatility', 'N/A'))};">
                                    {summary.get('volatility', 'N/A')}%
                                </span>
                            </div>
                            <div class="info-item">
                                <span class="label">Beta值:</span>
                                <span class="value" style="color: {self._get_beta_color(summary.get('beta', 'N/A'))};">
                                    {summary.get('beta', 'N/A')}
                                </span>
                            </div>
                            <div class="info-item">
                                <span class="label">風險等級:</span>
                                <span class="value" style="color: {self._get_risk_level_color(summary.get('risk_level', 'N/A'))};">
                                    {summary.get('risk_level', 'N/A')}
                                </span>
                            </div>
                            <div class="info-item">
                                <span class="label">Beta風險:</span>
                                <span class="value" style="color: {self._get_beta_risk_color(summary.get('beta_risk', 'N/A'))};">
                                    {summary.get('beta_risk', 'N/A')}
                                </span>
                            </div>
                            <div class="info-item">
                                <span class="label">夏普比率:</span>
                                <span class="value" style="color: {self._get_sharpe_color(summary.get('sharpe_ratio', 'N/A'))};">
                                    {summary.get('sharpe_ratio', 'N/A')}
                                </span>
                            </div>
                            <div class="info-item">
                                <span class="label">年化報酬率:</span>
                                <span class="value" style="color: {self._get_return_color(summary.get('annual_return', 'N/A'))};">
                                    {summary.get('annual_return', 'N/A')}%
                                </span>
                            </div>
                            <div class="info-item">
                                <span class="label">市場相關性:</span>
                                <span class="value">{summary.get('correlation', 'N/A')}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">對應指數:</span>
                                <span class="value">{summary.get('market_symbol', 'N/A')}</span>
                            </div>
                        </div>
                        
                        <!-- 風險提醒區塊 -->
                        <div style="margin-top: 15px; padding: 12px; background: #fff3cd; border-radius: 5px; border-left: 4px solid #ffc107;">
                            <h5 style="margin: 0 0 10px 0; color: #856404; font-size: 0.9em;">⚠️ 風險提醒</h5>
                            <div style="font-size: 0.85em; line-height: 1.4; color: #856404;">
                                {self._generate_risk_warning(summary)}
                            </div>
                        </div>
                        
                        <div class="info-grid" style="margin-top: 15px;">
                            <div class="info-item">
                                <span class="label">RSI:</span>
                                <span class="value">{summary.get('rsi', 'N/A')}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">MACD:</span>
                                <span class="value">{summary.get('macd', 'N/A')}</span>
                            </div>
                        </div>
                    </div>
                    
                    {self._generate_gemini_ai_panel(symbol, gemini_data) if gemini_data else ''}
                </div>
                
                <!-- 圖表區域 -->
                <div class="chart-container">
                    <h5>💰 價格區間分析圖表</h5>
                    <div id="price-chart-{symbol}" style="height: 400px;"></div>
                </div>
                
                <div class="chart-container">
                    <h5>📈 技術分析圖表</h5>
                    <div id="technical-chart-{symbol}" style="height: 600px;"></div>
                </div>
                
                <script>
                    // {symbol} 價格比較圖表
                    {price_chart}
                    
                    // {symbol} 技術分析圖表
                    {technical_chart}
                </script>
            </div>
            """
            
            content += stock_html
        
        return content
    
    def _get_volatility_color(self, volatility):
        """獲取波動率顏色"""
        try:
            vol = float(volatility)
            if vol >= 60:
                return '#f44336'  # 紅色
            elif vol >= 40:
                return '#ff9800'  # 橙色
            elif vol >= 15:
                return '#4CAF50'  # 綠色
            else:
                return '#2196F3'  # 藍色
        except (ValueError, TypeError):
            return '#666666'  # 灰色 (N/A)
    
    def _get_beta_color(self, beta):
        """獲取Beta值顏色"""
        try:
            beta_val = float(beta)
            if beta_val >= 1.5:
                return '#f44336'  # 紅色
            elif beta_val >= 1.0:
                return '#ff9800'  # 橙色
            elif beta_val >= 0.5:
                return '#4CAF50'  # 綠色
            else:
                return '#2196F3'  # 藍色
        except (ValueError, TypeError):
            return '#666666'  # 灰色 (N/A)
    
    def _get_risk_level_color(self, risk_level):
        """獲取風險等級顏色"""
        if isinstance(risk_level, str):
            if '極高' in risk_level:
                return '#f44336'  # 紅色
            elif '高' in risk_level:
                return '#ff9800'  # 橙色
            elif '低' in risk_level:
                return '#4CAF50'  # 綠色
            elif '極低' in risk_level:
                return '#2196F3'  # 藍色
        return '#666666'  # 灰色 (N/A)
    
    def _get_beta_risk_color(self, beta_risk):
        """獲取Beta風險顏色"""
        if isinstance(beta_risk, str):
            if '高Beta' in beta_risk:
                return '#f44336'  # 紅色
            elif '中等Beta' in beta_risk:
                return '#ff9800'  # 橙色
            elif '低Beta' in beta_risk:
                return '#4CAF50'  # 綠色
            elif '極低Beta' in beta_risk:
                return '#2196F3'  # 藍色
        return '#666666'  # 灰色 (N/A)
    
    def _get_sharpe_color(self, sharpe):
        """獲取夏普比率顏色"""
        try:
            sharpe_val = float(sharpe)
            if sharpe_val > 1.0:
                return '#4CAF50'  # 綠色
            elif sharpe_val > 0.5:
                return '#ff9800'  # 橙色
            else:
                return '#f44336'  # 紅色
        except (ValueError, TypeError):
            return '#666666'  # 灰色 (N/A)
    
    def _get_return_color(self, annual_return):
        """獲取年化報酬率顏色"""
        try:
            return_val = float(annual_return)
            if return_val > 0:
                return '#4CAF50'  # 綠色
            else:
                return '#f44336'  # 紅色
        except (ValueError, TypeError):
            return '#666666'  # 灰色 (N/A)
    
    def _generate_risk_warning(self, summary):
        """
        生成風險提醒信息
        """
        volatility = summary.get('volatility', 'N/A')
        beta = summary.get('beta', 'N/A')
        risk_level = summary.get('risk_level', '')
        beta_risk = summary.get('beta_risk', '')
        
        warnings = []
        
        # 顯示具體數值
        warnings.append(f"📊 <strong>具體數值</strong>: 波動率 {volatility}% | Beta值 {beta}")
        
        # 波動率警告
        try:
            vol = float(volatility)
            if vol >= 60:
                warnings.append("🔴 <strong>極高波動率</strong>: 股價波動劇烈，適合短線操作或風險承受能力強的投資者")
            elif vol >= 40:
                warnings.append("🟡 <strong>高波動率</strong>: 股價波動較大，建議分批建倉並設置止損")
            elif vol >= 25:
                warnings.append("🟢 <strong>中等波動率</strong>: 股價波動適中，適合一般投資者")
            else:
                warnings.append("🔵 <strong>低波動率</strong>: 股價相對穩定，適合保守型投資者")
        except (ValueError, TypeError):
            warnings.append("⚠️ <strong>波動率數據不足</strong>: 無法計算波動率，請檢查數據")
        
        # Beta警告
        try:
            beta_val = float(beta)
            if beta_val >= 1.5:
                warnings.append("🔴 <strong>高Beta股票</strong>: 市場敏感度高，牛市表現優於大盤，熊市跌幅更大")
            elif beta_val >= 1.0:
                warnings.append("🟡 <strong>中等Beta股票</strong>: 波動性略高於市場，需注意市場環境")
            elif beta_val >= 0.5:
                warnings.append("🟢 <strong>低Beta股票</strong>: 相對穩定，適合防禦性投資")
            else:
                warnings.append("🔵 <strong>極低Beta股票</strong>: 防禦性強，市場下跌時相對抗跌")
        except (ValueError, TypeError):
            warnings.append("⚠️ <strong>Beta數據不足</strong>: 無法計算Beta值，請檢查數據")
        
        # 綜合建議
        try:
            vol = float(volatility)
            beta_val = float(beta)
            if vol >= 50 and beta_val >= 1.2:
                warnings.append("⚠️ <strong>高風險組合</strong>: 高波動率+高Beta，建議謹慎操作，嚴格控制倉位")
            elif vol <= 20 and beta_val <= 0.8:
                warnings.append("✅ <strong>低風險組合</strong>: 低波動率+低Beta，適合保守型投資者")
        except (ValueError, TypeError):
            pass  # 如果無法轉換為數字，跳過綜合建議
        
        return "<br>".join(warnings)
    
    def _generate_gemini_ai_panel(self, symbol, gemini_data):
        """
        生成Gemini AI建議面板（精簡版）
        """
        if not gemini_data:
            return ""
        
        # 提取精簡的Gemini分析數據
        price_forecast = gemini_data.get('price_forecast', {})
        recent_news = gemini_data.get('recent_news', 'N/A')
        ai_judgment = gemini_data.get('ai_judgment', 'N/A')
        sentiment = gemini_data.get('sentiment', 'N/A')
        
        # 格式化數據
        price_1y = price_forecast.get('price_1y', 'N/A')
        price_3y = price_forecast.get('price_3y', 'N/A')
        price_5y = price_forecast.get('price_5y', 'N/A')
        
        # 設置顏色
        sentiment_color = '#4CAF50' if '看漲' in sentiment else '#F44336' if '看跌' in sentiment else '#FF9800'
        
        return f"""
                    <div class="analysis-panel" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <h4>🤖 Gemini AI 智能分析</h4>
                        <div class="info-grid">
                            <div class="info-item">
                                <span class="label">AI情緒:</span>
                                <span class="value" style="color: {sentiment_color};">{sentiment}</span>
                            </div>
                        </div>
                        
                        <!-- 股價預測 -->
                        <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                            <h5 style="margin: 0 0 10px 0; font-size: 0.9em;">📈 未來股價預測</h5>
                            <div style="font-size: 0.85em; line-height: 1.4;">
                                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                                    <div>
                                        <span style="font-weight: bold;">1年後:</span>
                                        <div style="margin-top: 3px;">{price_1y}</div>
                                    </div>
                                    <div>
                                        <span style="font-weight: bold;">3年後:</span>
                                        <div style="margin-top: 3px;">{price_3y}</div>
                                    </div>
                                    <div>
                                        <span style="font-weight: bold;">5年後:</span>
                                        <div style="margin-top: 3px;">{price_5y}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 重大新聞 -->
                        <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                            <h5 style="margin: 0 0 10px 0; font-size: 0.9em;">📰 近期重大新聞</h5>
                            <div style="font-size: 0.85em; line-height: 1.4;">
                                <div style="margin-bottom: 8px;">
                                    <span style="font-weight: bold;">新聞:</span>
                                    <div style="margin-top: 3px;">{recent_news}</div>
                                </div>
                                <div>
                                    <span style="font-weight: bold;">AI判斷:</span>
                                    <div style="margin-top: 3px;">{ai_judgment}</div>
                                </div>
                            </div>
                        </div>
                    </div>
        """ 
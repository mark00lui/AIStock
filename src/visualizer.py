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
    
    def create_batch_html_report(self, analyzers, output_file):
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
                
                result = {
                    'symbol': analyzer.symbol,
                    'analyzer': analyzer,
                    'signal': analyzer.get_current_signal(),
                    'summary': analyzer.get_signal_summary(),
                    'left_data': left_data
                }
                all_results.append(result)
                print(f"已處理 {analyzer.symbol}")
            except Exception as e:
                print(f"處理 {analyzer.symbol} 時發生錯誤: {e}")
                continue
        
        # 創建HTML內容
        html_content = self._generate_batch_html(all_results)
        
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
    
    def _generate_batch_html(self, all_results):
        """
        生成批次分析HTML內容 - 響應式設計版本
        """
        current_date = datetime.now().strftime('%Y年%m月%d日')
        
        # 生成股票導航列表
        stock_navigation = self._generate_stock_navigation(all_results)
        
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
        }}
        
        /* 響應式導航 */
        .nav-toggle {{
            display: none;
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 15px;
            font-size: 1.2em;
            cursor: pointer;
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 1000;
            border-radius: 5px;
        }}
        
        .stock-nav {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            position: sticky;
            top: 0;
            z-index: 999;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .stock-nav h3 {{
            margin: 0 0 15px 0;
            font-size: 1.3em;
            text-align: center;
        }}
        
        .stock-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 8px;
            max-height: 200px;
            overflow-y: auto;
        }}
        
        .stock-link {{
            display: block;
            padding: 8px 12px;
            background: #34495e;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            text-align: center;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }}
        
        .stock-link:hover {{
            background: #667eea;
            transform: translateY(-2px);
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
    
    <div class="container">
        <div class="stock-nav" id="stockNav">
            <h3>📊 股票導航</h3>
            <div class="stock-list">
                {stock_navigation}
            </div>
        </div>
        
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
            nav.style.display = nav.style.display === 'none' ? 'block' : 'none';
        }}
        
        // 平滑滾動到指定股票
        function scrollToStock(symbol) {{
            const element = document.getElementById('stock-' + symbol);
            if (element) {{
                element.scrollIntoView({{ 
                    behavior: 'smooth',
                    block: 'start'
                }});
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
            
            if (window.innerWidth <= 768) {{
                nav.style.display = 'none';
                toggle.style.display = 'block';
            }} else {{
                nav.style.display = 'block';
                toggle.style.display = 'none';
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
    
    def _generate_stock_navigation(self, all_results):
        """
        生成股票導航列表
        """
        navigation_html = ""
        
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
               style="border-left: 4px solid {signal_color};">
                {display_name}
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
        生成摘要統計
        """
        # 技術分析統計
        buy_count = 0
        sell_count = 0
        hold_count = 0
        
        for result in all_results:
            signal_data = result['signal']
            if isinstance(signal_data, dict):
                signal_str = signal_data.get('signal', '持有')
            else:
                signal_str = str(signal_data)
            
            if '買入' in signal_str:
                buy_count += 1
            elif '賣出' in signal_str:
                sell_count += 1
            else:
                hold_count += 1
        
        # 左側分析統計
        total_stocks = len(all_results)
        undervalued_count = 0
        overvalued_count = 0
        
        for result in all_results:
            left_data = result['left_data']
            if left_data and 'timeframes' in left_data:
                year1_data = left_data['timeframes'].get('1_year', {})
                if year1_data:
                    current_price = result['analyzer'].data['Close'].iloc[-1]
                    target_price = year1_data.get('target_mean', current_price)
                    if current_price < target_price:
                        undervalued_count += 1
                    else:
                        overvalued_count += 1
        
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
        """
        
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
        """
        
        return {
            'technical': technical_stats,
            'left': left_stats
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
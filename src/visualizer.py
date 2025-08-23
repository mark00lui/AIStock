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
    
    def _get_base_css(self):
        """統一的基礎CSS樣式"""
        return """
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: margin-left 0.3s ease;
        }
        
        .container.with-nav {
            margin-left: 280px;
            margin-right: 0;
            max-width: calc(100vw - 280px);
        }
        
        /* 手機版容器不受導航影響 */
        @media (max-width: 768px) {
            .container {
                margin-left: 0 !important;
                margin-right: 0 !important;
                max-width: 100vw !important;
                transition: none;
            }
        }
        """
    
    def _get_navigation_css(self):
        """導航相關的CSS樣式"""
        return """
        /* 響應式導航 */
        .nav-toggle {
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
        }
        
        .nav-toggle:hover {
            background: #5a6fd8;
            transform: scale(1.05);
        }
        
        .stock-nav {
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
        }
        
        .stock-nav.active {
            transform: translateX(0);
        }
        
        /* 手機版浮出式導航 */
        @media (max-width: 768px) {
            .stock-nav {
                width: 85vw;
                max-width: 320px;
                box-shadow: 0 0 20px rgba(0,0,0,0.3);
                border-radius: 0 10px 10px 0;
            }
            
            /* 手機版導航背景遮罩 */
            .nav-overlay {
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
            }
            
            .nav-overlay.active {
                opacity: 1;
                visibility: visible;
            }
        }
        
        .stock-link {
            display: block;
            color: white;
            text-decoration: none;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 5px;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
        }
        
        .stock-link:hover {
            background: rgba(255,255,255,0.1);
            transform: translateX(5px);
        }
        
        .stock-link .symbol {
            font-weight: bold;
            display: block;
        }
        
        .stock-link .name {
            font-size: 0.9em;
            opacity: 0.8;
        }
        """
    
    def _get_component_css(self):
        """組件相關的CSS樣式"""
        return """
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        
        .header h1 {
            margin: 0;
            font-size: clamp(1.8em, 4vw, 2.5em);
            font-weight: 300;
        }
        
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: clamp(0.9em, 2vw, 1.1em);
        }
        
        .report-date {
            margin-top: 15px !important;
            font-size: 0.9em !important;
            opacity: 0.8 !important;
        }
        
        .stock-card {
            background: white;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            overflow: hidden;
            scroll-margin-top: 100px;
            width: 100%;
            max-width: 100%;
        }
        
        .stock-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .stock-header h3 {
            margin: 0;
            font-size: clamp(1.2em, 2.5vw, 1.5em);
            text-align: center;
        }
        
        .signal-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            text-align: center;
            align-self: center;
        }
        
        .signal-buy { background: #4CAF50; }
        .signal-sell { background: #f44336; }
        .signal-hold { background: #ff9800; }
        
        .analysis-layout {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            padding: 20px;
            width: 100%;
            max-width: 100%;
        }
        
        .analysis-panel {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            width: 100%;
            max-width: 100%;
        }
        
        .analysis-panel h4 {
            margin: 0 0 20px 0;
            color: #333;
            font-size: 1.2em;
        }
        
        .info-grid {
            display: grid;
            gap: 10px;
            width: 100%;
            max-width: 100%;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        
        .info-item:last-child {
            border-bottom: none;
        }
        
        .label {
            font-weight: 500;
            color: #666;
        }
        
        .value {
            font-weight: bold;
            color: #333;
        }
        
        .chart-container {
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 100%;
        }
        
        .chart-container h5 {
            margin: 0 0 15px 0;
            color: #333;
            font-size: 1.1em;
        }
        
        /* 響應式設計 */
        @media (min-width: 768px) {
            .analysis-layout {
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                padding: 30px;
            }
        }
        
        @media (min-width: 1200px) {
            .analysis-layout {
                grid-template-columns: 1fr 1fr 1fr;
                gap: 25px;
                padding: 30px;
            }
            
            .stock-header {
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
                padding: 25px 30px;
            }
            
            .stock-header h3 {
                text-align: left;
            }
            
            .signal-badge {
                align-self: auto;
            }
        }
        
        /* 回到頂部按鈕 */
        .back-to-top {
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
        }
        
        .back-to-top:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        """
    
    def _get_summary_css(self):
        """摘要相關的CSS樣式"""
        return """
        .summary-section {
            padding: 20px;
            border-bottom: 1px solid #eee;
            width: 100%;
            max-width: 100%;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
            width: 100%;
            max-width: 100%;
        }
        
        .summary-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 100%;
        }
        
        .summary-card h3 {
            margin: 0 0 20px 0;
            color: #333;
            font-size: 1.3em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 15px;
            width: 100%;
            max-width: 100%;
        }
        
        .stat-item {
            background: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            width: 100%;
            max-width: 100%;
        }
        
        .signal-list {
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
        }
        
        .signal-list strong {
            color: #ffd700;
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
            font-size: 1.1em;
        }
        
        @media (min-width: 768px) {
            .summary-section {
                padding: 30px;
            }
        }
        
        @media (min-width: 1024px) {
            .summary-grid {
                grid-template-columns: 1fr 1fr;
            }
        }
        """
    
    def _get_javascript(self):
        """統一的JavaScript功能"""
        return """
        // 導航切換功能
        function toggleNav() {
            const nav = document.getElementById('stockNav');
            const container = document.querySelector('.container');
            const overlay = document.getElementById('navOverlay');
            
            if (nav && container) {
                nav.classList.toggle('active');
                container.classList.toggle('with-nav');
                
                if (overlay) {
                    overlay.classList.toggle('active');
                }
            }
        }
        
        // 平滑滾動到指定股票
        function scrollToStock(symbol) {
            const element = document.getElementById('stock-' + symbol);
            if (element) {
                element.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // 手機版點擊後收起導航
                if (window.innerWidth <= 768) {
                    toggleNav();
                }
            }
        }
        
        // 回到頂部
        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
        
        // 響應式導航顯示控制
        function handleResize() {
            const nav = document.getElementById('stockNav');
            const container = document.querySelector('.container');
            const overlay = document.getElementById('navOverlay');
            
            if (window.innerWidth > 768) {
                // 桌面版：移除手機版樣式
                if (nav) nav.classList.remove('active');
                if (container) container.classList.remove('with-nav');
                if (overlay) overlay.classList.remove('active');
            }
        }
        
        // 頁面載入完成後初始化
        window.addEventListener('load', function() {
            // 初始化導航狀態
            handleResize();
            
            // 顯示回到頂部按鈕
            const backToTop = document.querySelector('.back-to-top');
            if (backToTop) {
                backToTop.style.display = 'none';
                
                window.addEventListener('scroll', function() {
                    if (window.pageYOffset > 300) {
                        backToTop.style.display = 'block';
                    } else {
                        backToTop.style.display = 'none';
                    }
                });
            }
        });
        
        // 監聽窗口大小變化
        window.addEventListener('resize', handleResize);
        """
    
    def _create_navigation_html(self, results, categories=None):
        """創建導航HTML"""
        nav_items = []
        
        if categories:
            # 按分類顯示
            for category, symbols in categories.items():
                nav_items.append(f'<div style="margin: 15px 0 5px 0; font-size: 0.9em; opacity: 0.7; font-weight: bold;">{category}</div>')
                for result in results:
                    if result['symbol'] in symbols:
                        symbol = result['symbol']
                        stock_name = getattr(result['analyzer'], 'long_name', symbol)
                        display_name = stock_name[:12] + ('...' if len(stock_name) > 12 else '')
                        
                        # 使用修正後的信號判斷邏輯
                        signal_str = str(result.get('signal', '')).upper()
                        if isinstance(result.get('signal'), dict):
                            signal_str = str(result.get('signal', {}).get('signal', '')).upper()
                        
                        if 'SELL' in signal_str:
                            signal_color = '#f44336'
                        elif 'BUY' in signal_str:
                            signal_color = '#4CAF50'
                        else:
                            signal_color = '#ff9800'
                        
                        nav_items.append(f'''
                        <a href="#stock-{symbol}" class="stock-link" onclick="scrollToStock('{symbol}')" 
                           style="border-left: 3px solid {signal_color};">
                            <span class="symbol">{symbol}</span>
                            <span class="name">{display_name}</span>
                        </a>
                        ''')
        else:
            # 無分類顯示
            for result in results:
                symbol = result['symbol']
                stock_name = getattr(result['analyzer'], 'long_name', symbol)
                display_name = stock_name[:12] + ('...' if len(stock_name) > 12 else '')
                
                # 使用修正後的信號判斷邏輯
                signal_str = str(result.get('signal', '')).upper()
                if isinstance(result.get('signal'), dict):
                    signal_str = str(result.get('signal', {}).get('signal', '')).upper()
                
                if 'SELL' in signal_str:
                    signal_color = '#f44336'
                elif 'BUY' in signal_str:
                    signal_color = '#4CAF50'
                else:
                    signal_color = '#ff9800'
                
                nav_items.append(f'''
                <a href="#stock-{symbol}" class="stock-link" onclick="scrollToStock('{symbol}')" 
                   style="border-left: 3px solid {signal_color};">
                    <span class="symbol">{symbol}</span>
                    <span class="name">{display_name}</span>
                </a>
                ''')
        
        return f'''
        <div id="stockNav" class="stock-nav">
            <div style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.2);">
                <h3 style="margin: 0; font-size: 1.2em;">📋 股票導航</h3>
                <p style="margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.8;">點擊快速跳轉</p>
            </div>
            <div style="display: grid; gap: 5px;">
                {''.join(nav_items)}
            </div>
        </div>
        '''
    
    def _create_header_html(self, title, subtitle=None, date=None):
         """創建標題HTML"""
         current_date = date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
         sub_text = subtitle or "左側分析 + 右側分析綜合評估"
         
         return f'''
         <div class="header">
             <h1>{title}</h1>
             <p>{sub_text}</p>
             <p class="report-date">生成日期: {current_date}</p>
         </div>
         '''
    
    def _create_stock_card_html(self, result):
        """創建單一股票卡片HTML"""
        symbol = result['symbol']
        analyzer = result['analyzer']
        signal_data = result.get('signal', {})
        summary = result.get('summary', {})
        left_data = result.get('left_data', {})
        gemini_data = result.get('gemini_data', {})
        
        # 獲取股票顯示名稱
        stock_name = getattr(analyzer, 'long_name', symbol)
        stock_display_name = f"{stock_name} ({symbol})"
        
        # 獲取信號信息
        signal_str = str(signal_data.get('signal', 'HOLD')).upper() if isinstance(signal_data, dict) else str(signal_data).upper()
        signal_class = signal_str.lower()
        
        # 獲取當前價格
        try:
            current_price = analyzer.data['Close'].iloc[-1] if hasattr(analyzer, 'data') and not analyzer.data.empty else 0.0
        except:
            current_price = 0.0
        
        # 獲取左側分析數據
        timeframes_data = left_data.get('timeframes', {}) if left_data else {}
        year1_data = timeframes_data.get('1_year', {}) if timeframes_data else {}
        year2_data = timeframes_data.get('2_year', {}) if timeframes_data else {}
        year3_data = timeframes_data.get('3_year', {}) if timeframes_data else {}
        
        # 獲取目標價格（使用 target_mean 作為主要目標價）
        target_price_1y = year1_data.get('target_mean', current_price) if year1_data.get('target_mean') is not None else current_price
        target_price_2y = year2_data.get('target_mean', current_price) if year2_data.get('target_mean') is not None else current_price
        target_price_3y = year3_data.get('target_mean', current_price) if year3_data.get('target_mean') is not None else current_price
        
        # 獲取EPS（使用 future_eps）
        eps = year1_data.get('future_eps', 0.0) if year1_data.get('future_eps') is not None else 0.0
        
        # 獲取建議動作和信心等級
        recommended_action_1y = year1_data.get('recommended_action', 'Hold')
        confidence_1y = year1_data.get('confidence', 'Medium')
        potential_return_1y = year1_data.get('potential_return', 0.0) if year1_data.get('potential_return') is not None else 0.0
        
        # 獲取價格區間
        buy_zone_1y = year1_data.get('buy_zone', 'N/A') if year1_data.get('buy_zone') is not None else 'N/A'
        hold_zone_1y = year1_data.get('hold_zone', 'N/A') if year1_data.get('hold_zone') is not None else 'N/A'
        sell_zone_1y = year1_data.get('sell_zone', 'N/A') if year1_data.get('sell_zone') is not None else 'N/A'
        
        # 創建左側分析面板
        left_panel = f'''
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
                </div>
            </div>
        </div>
        '''
        
        # 創建右側信號分析面板
        tech_panel = self._create_right_analysis_panel(analyzer, signal_data, signal_str)
        
        # 創建 Gemini AI 分析面板
        gemini_panel = self._create_gemini_analysis_panel(gemini_data)
         
        # 創建技術分析圖表
        technical_chart = self._create_technical_chart(analyzer)
        
        return f'''
         <div class="stock-card" id="stock-{symbol}">
             <div class="stock-header">
                 <h3>{stock_display_name}</h3>
                 <span class="signal-badge signal-{signal_class}">{signal_str}</span>
             </div>
             
             <div class="analysis-layout">
                 {left_panel}
                 {tech_panel}
                 {gemini_panel}
             </div>
             
             <div class="chart-container">
                 <h5>📈 技術分析圖表</h5>
                 <div id="technical-chart-{symbol}" style="height: 600px;"></div>
             </div>
         </div>
         
         <script>
             // 技術分析圖表
             {technical_chart}
         </script>
         '''
    
    def create_single_stock_report(self, analyzer, output_file):
        """創建單一股票分析報告"""
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
    
    def _generate_single_stock_html(self, result):
        """生成單一股票HTML報告"""
        symbol = result['symbol']
        analyzer = result['analyzer']
        stock_name = getattr(analyzer, 'long_name', symbol)
        stock_display_name = f"{stock_name} ({symbol})"
        
        # 組合所有CSS
        all_css = self._get_base_css() + self._get_navigation_css() + self._get_component_css() + self._get_summary_css()
        
        # 創建導航（單一股票）
        navigation = f'''
        <div id="stockNav" class="stock-nav">
            <div style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.2);">
                <h3 style="margin: 0; font-size: 1.2em;">📋 股票導航</h3>
                <p style="margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.8;">點擊快速跳轉</p>
            </div>
            <div style="display: grid; gap: 5px;">
                <a href="#stock-{symbol}" class="stock-link" onclick="scrollToStock('{symbol}')" 
                   style="border-left: 3px solid #4CAF50;">
                    <span class="symbol">{symbol}</span>
                    <span class="name">{stock_name[:12]}{'...' if len(stock_name) > 12 else ''}</span>
                </a>
            </div>
        </div>
        '''
        
        # 創建標題
        header = self._create_header_html(f"📊 {stock_display_name} 股票分析報告")
        
        # 創建股票卡片
        stock_card = self._create_stock_card_html(result)
        
        # 創建JavaScript
        javascript = self._get_javascript()
        
        return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_display_name} 股票分析報告</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        {all_css}
    </style>
</head>
<body>
    <!-- 導航切換按鈕 -->
    <button class="nav-toggle" onclick="toggleNav()" title="切換導航">☰</button>
    
    {navigation}
    
    <!-- 手機版導航背景遮罩 -->
    <div id="navOverlay" class="nav-overlay"></div>
    
    <div class="container">
        {header}
        {stock_card}
    </div>
    
    <button class="back-to-top" onclick="scrollToTop()" title="回到頂部">↑</button>
    
    <script>
        {javascript}
    </script>
</body>
</html>'''
    
    def create_batch_html_report(self, analyzers, output_file, gemini_results=None, categories=None):
        """創建批次分析HTML報告"""
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
            print(f"保存批次報告時發生錯誤: {e}")
            return None
    
    def _generate_batch_html(self, results, categories=None):
        """生成批次HTML報告"""
        if not results:
            return "<html><body><h1>沒有可用的股票數據</h1></body></html>"
        
        # 組合所有CSS
        all_css = self._get_base_css() + self._get_navigation_css() + self._get_component_css() + self._get_summary_css()
        
        # 創建導航
        navigation = self._create_navigation_html(results, categories)
        
        # 創建標題
        header = self._create_header_html("📊 股票分析報告", f"共 {len(results)} 檔股票")
        
        # 創建摘要區段
        summary_section = self._create_summary_section(results)
        
        # 創建所有股票卡片
        stock_cards = []
        for result in results:
            stock_card = self._create_stock_card_html(result)
            stock_cards.append(stock_card)
        
        # 創建JavaScript
        javascript = self._get_javascript()
        
        return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票分析報告</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        {all_css}
    </style>
</head>
<body>
    <!-- 導航切換按鈕 -->
    <button class="nav-toggle" onclick="toggleNav()" title="切換導航">📋</button>
    
    {navigation}
    
    <!-- 手機版導航背景遮罩 -->
    <div id="navOverlay" class="nav-overlay" onclick="toggleNav()"></div>
    
    <div class="container">
        {header}
        {summary_section}
        
        <div class="stocks-section">
            {''.join(stock_cards)}
        </div>
    </div>
    
    <button class="back-to-top" onclick="scrollToTop()" title="回到頂部">↑</button>
    
    <script>
        {javascript}
    </script>
</body>
</html>'''
    
    def _create_summary_section(self, results):
        """創建摘要區段"""
        if not results:
            return ""
        
        # 統計信號 - 修正邏輯，每個股票只能歸類為一種信號
        buy_signals = []
        sell_signals = []
        hold_signals = []
        
        for r in results:
            # 正確處理信號數據結構
            signal_data = r.get('signal', {})
            if isinstance(signal_data, dict):
                signal_str = signal_data.get('signal', '')
            else:
                signal_str = str(signal_data)
            
            # 優先級：賣出 > 買入 > 持有
            if '賣出' in signal_str:
                sell_signals.append(r)
            elif '買入' in signal_str:
                buy_signals.append(r)
            else:
                hold_signals.append(r)
        
        # 統計右側分析指標
        right_analysis_stats = self._calculate_right_analysis_stats(results)
        
        # 創建買入信號列表
        buy_signals_list = ""
        if buy_signals:
            buy_items = []
            for signal in buy_signals:
                symbol = signal['symbol']
                stock_name = getattr(signal['analyzer'], 'long_name', symbol)
                buy_items.append(f'<li><a href="#stock-{symbol}" style="color: #4CAF50; text-decoration: none;">{symbol} ({stock_name[:15]}{"..." if len(stock_name) > 15 else ""})</a></li>')
            buy_signals_list = f'''
            <div style="margin-top: 15px; padding: 10px; background: rgba(76, 175, 80, 0.1); border-radius: 5px; border-left: 4px solid #4CAF50;">
                <h5 style="margin: 0 0 10px 0; color: #4CAF50; font-size: 0.9em;">🟢 買入信號股票列表</h5>
                <ul style="margin: 0; padding-left: 20px; font-size: 0.85em;">
                    {''.join(buy_items)}
                </ul>
            </div>
            '''
        
        # 創建賣出信號列表
        sell_signals_list = ""
        if sell_signals:
            sell_items = []
            for signal in sell_signals:
                symbol = signal['symbol']
                stock_name = getattr(signal['analyzer'], 'long_name', symbol)
                sell_items.append(f'<li><a href="#stock-{symbol}" style="color: #f44336; text-decoration: none;">{symbol} ({stock_name[:15]}{"..." if len(stock_name) > 15 else ""})</a></li>')
            sell_signals_list = f'''
            <div style="margin-top: 15px; padding: 10px; background: rgba(244, 67, 54, 0.1); border-radius: 5px; border-left: 4px solid #f44336;">
                <h5 style="margin: 0 0 10px 0; color: #f44336; font-size: 0.9em;">🔴 賣出信號股票列表</h5>
                <ul style="margin: 0; padding-left: 20px; font-size: 0.85em;">
                    {''.join(sell_items)}
                </ul>
            </div>
            '''
        
        # 創建右側分析摘要
        tech_summary = f'''
         <div class="summary-card">
             <h3>📈 右側分析摘要</h3>
             <div class="stats-grid">
                 <div class="stat-item">
                     <div style="font-size: 2em; color: #4CAF50; font-weight: bold;">{len(buy_signals)}</div>
                     <div>買入信號</div>
                 </div>
                 <div class="stat-item">
                     <div style="font-size: 2em; color: #ff9800; font-weight: bold;">{len(hold_signals)}</div>
                     <div>持有信號</div>
                 </div>
                 <div class="stat-item">
                     <div style="font-size: 2em; color: #f44336; font-weight: bold;">{len(sell_signals)}</div>
                     <div>賣出信號</div>
                 </div>
                 <div class="stat-item">
                     <div style="font-size: 2em; color: #2196F3; font-weight: bold;">{right_analysis_stats['bullish_count']}</div>
                     <div>看多指標</div>
                 </div>
                 <div class="stat-item">
                     <div style="font-size: 2em; color: #f44336; font-weight: bold;">{right_analysis_stats['bearish_count']}</div>
                     <div>看空指標</div>
                 </div>
                 <div class="stat-item">
                     <div style="font-size: 2em; color: #FF9800; font-weight: bold;">{right_analysis_stats['pressure_risk_count']}</div>
                     <div>賣壓風險</div>
                 </div>
             </div>
             {buy_signals_list}
             {sell_signals_list}
         </div>
         '''
        
        # 統計左側分析區間
        buy_zone_stocks = []
        hold_zone_stocks = []
        sell_zone_stocks = []
        
        for result in results:
            try:
                # 獲取當前價格和目標價格
                analyzer = result['analyzer']
                current_price = analyzer.data['Close'].iloc[-1] if hasattr(analyzer, 'data') and not analyzer.data.empty else 0
                
                left_data = result.get('left_data', {})
                timeframes = left_data.get('timeframes', {})
                year1_data = timeframes.get('1_year', {})
                
                # 獲取價格區間
                buy_zone = year1_data.get('buy_zone', '')
                hold_zone = year1_data.get('hold_zone', '')
                sell_zone = year1_data.get('sell_zone', '')
                
                # 判斷當前價格在哪個區間
                if buy_zone and buy_zone != 'N/A':
                    try:
                        # 解析買入區間 (例如: "$150-180")
                        buy_range = buy_zone.replace('$', '').split('-')
                        if len(buy_range) == 2:
                            buy_low = float(buy_range[0])
                            buy_high = float(buy_range[1])
                            if buy_low <= current_price <= buy_high:
                                buy_zone_stocks.append(result)
                    except:
                        pass
                
                if sell_zone and sell_zone != 'N/A':
                    try:
                        # 解析賣出區間 (例如: "$200-250")
                        sell_range = sell_zone.replace('$', '').split('-')
                        if len(sell_range) == 2:
                            sell_low = float(sell_range[0])
                            sell_high = float(sell_range[1])
                            if sell_low <= current_price <= sell_high:
                                sell_zone_stocks.append(result)
                    except:
                        pass
                
                # 如果不在買入或賣出區間，則在持有區間
                if result not in buy_zone_stocks and result not in sell_zone_stocks:
                    hold_zone_stocks.append(result)
                    
            except Exception as e:
                print(f"分析 {result['symbol']} 價格區間時發生錯誤: {e}")
                continue
        
        # 創建買入區間股票列表
        buy_zone_list = ""
        if buy_zone_stocks:
            buy_zone_items = []
            for stock in buy_zone_stocks:
                symbol = stock['symbol']
                stock_name = getattr(stock['analyzer'], 'long_name', symbol)
                buy_zone_items.append(f'<li><a href="#stock-{symbol}" style="color: #4CAF50; text-decoration: none;">{symbol} ({stock_name[:15]}{"..." if len(stock_name) > 15 else ""})</a></li>')
            buy_zone_list = f'''
            <div style="margin-top: 15px; padding: 10px; background: rgba(76, 175, 80, 0.1); border-radius: 5px; border-left: 4px solid #4CAF50;">
                <h5 style="margin: 0 0 10px 0; color: #4CAF50; font-size: 0.9em;">🟢 買入區間股票列表</h5>
                <ul style="margin: 0; padding-left: 20px; font-size: 0.85em;">
                    {''.join(buy_zone_items)}
                </ul>
            </div>
            '''
        
        # 創建賣出區間股票列表
        sell_zone_list = ""
        if sell_zone_stocks:
            sell_zone_items = []
            for stock in sell_zone_stocks:
                symbol = stock['symbol']
                stock_name = getattr(stock['analyzer'], 'long_name', symbol)
                sell_zone_items.append(f'<li><a href="#stock-{symbol}" style="color: #f44336; text-decoration: none;">{symbol} ({stock_name[:15]}{"..." if len(stock_name) > 15 else ""})</a></li>')
            sell_zone_list = f'''
            <div style="margin-top: 15px; padding: 10px; background: rgba(244, 67, 54, 0.1); border-radius: 5px; border-left: 4px solid #f44336;">
                <h5 style="margin: 0 0 10px 0; color: #f44336; font-size: 0.9em;">🔴 賣出區間股票列表</h5>
                <ul style="margin: 0; padding-left: 20px; font-size: 0.85em;">
                    {''.join(sell_zone_items)}
                </ul>
            </div>
            '''
        
        # 創建左側分析摘要
        left_summary = f'''
        <div class="summary-card">
            <h3>💰 左側分析摘要</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div style="font-size: 2em; color: #2196F3; font-weight: bold;">{len(results)}</div>
                    <div>分析股票</div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 2em; color: #4CAF50; font-weight: bold;">{len(buy_zone_stocks)}</div>
                    <div>買入區間</div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 2em; color: #ff9800; font-weight: bold;">{len(hold_zone_stocks)}</div>
                    <div>持有區間</div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 2em; color: #f44336; font-weight: bold;">{len(sell_zone_stocks)}</div>
                    <div>賣出區間</div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 2em; color: #4CAF50; font-weight: bold;">{len([r for r in results if r.get('left_data', {}).get('timeframes', {}).get('1_year', {}).get('potential_return', 0) is not None and r.get('left_data', {}).get('timeframes', {}).get('1_year', {}).get('potential_return', 0) > 0])}</div>
                    <div>正報酬</div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 2em; color: #f44336; font-weight: bold;">{len([r for r in results if r.get('left_data', {}).get('timeframes', {}).get('1_year', {}).get('potential_return', 0) is not None and r.get('left_data', {}).get('timeframes', {}).get('1_year', {}).get('potential_return', 0) < 0])}</div>
                    <div>負報酬</div>
                </div>
            </div>
            {buy_zone_list}
            {sell_zone_list}
        </div>
        '''
        
        return f'''
        <div class="summary-section">
            <div class="summary-grid">
                {tech_summary}
                {left_summary}
            </div>
        </div>
        '''
    
    def _create_enhanced_price_chart(self, symbol, current_price, year1_data, stock_display_name):
        """創建增強的價格比較圖"""
        try:
            safe_symbol = symbol.replace('.', '_').replace('-', '_')
            target_price = year1_data.get('target_mean', current_price) if year1_data and year1_data.get('target_mean') is not None else current_price
            
            chart_js = f'''
            var priceData_{safe_symbol} = [
                {{
                    x: ['當前價格', '1年目標價'],
                    y: [{current_price:.2f}, {target_price:.2f}],
                    type: 'bar',
                    marker: {{
                        color: ['{self._get_price_color(current_price, target_price)}', '#2196F3']
                    }},
                    text: ['${current_price:.2f}', '${target_price:.2f}'],
                    textposition: 'auto'
                }}
            ];
            
            var priceLayout_{safe_symbol} = {{
                title: '{stock_display_name} 價格比較',
                xaxis: {{ title: '項目' }},
                yaxis: {{ title: '價格 (USD)' }},
                showlegend: false,
                height: 350
            }};
            
            Plotly.newPlot('price-chart-{symbol}', priceData_{safe_symbol}, priceLayout_{safe_symbol});
            '''
            
            return chart_js
        except Exception as e:
            print(f"創建價格圖表時發生錯誤: {e}")
            return f"console.log('價格圖表生成失敗: {e}');"
    
    def _create_technical_chart(self, analyzer):
        """創建技術分析圖表"""
        try:
            if not hasattr(analyzer, 'data') or analyzer.data.empty:
                return "console.log('技術圖表生成失敗: 無數據');"
            
            symbol = analyzer.symbol
            safe_symbol = symbol.replace('.', '_').replace('-', '_')
            data = analyzer.data.tail(100)  # 取最近100天數據
            
            if len(data) < 20:
                return "console.log('技術圖表生成失敗: 數據不足');"
            
            # 準備數據
            dates = [d.strftime('%Y-%m-%d') for d in data.index]
            closes = data['Close'].tolist()
            volumes = data['Volume'].tolist() if 'Volume' in data.columns else [0] * len(dates)
            
            # 計算移動平均線
            ma5 = data['Close'].rolling(window=5, min_periods=1).mean().tolist()
            ma20 = data['Close'].rolling(window=20, min_periods=1).mean().tolist()
            
            chart_js = f'''
            var technicalData_{safe_symbol} = [
                {{
                    x: {dates},
                    y: {closes},
                    type: 'scatter',
                    mode: 'lines',
                    name: '收盤價',
                    line: {{ color: '#1f77b4' }}
                }},
                {{
                    x: {dates},
                    y: {ma5},
                    type: 'scatter',
                    mode: 'lines',
                    name: 'MA5',
                    line: {{ color: '#ff7f0e' }}
                }},
                {{
                    x: {dates},
                    y: {ma20},
                    type: 'scatter',
                    mode: 'lines',
                    name: 'MA20',
                    line: {{ color: '#2ca02c' }}
                }},
                {{
                    x: {dates},
                    y: {volumes},
                    type: 'bar',
                    name: '成交量',
                    yaxis: 'y2',
                    marker: {{ color: 'rgba(158,202,225,0.6)' }}
                }}
            ];
            
            var technicalLayout_{safe_symbol} = {{
                title: '{symbol} 技術分析圖表',
                xaxis: {{ title: '日期' }},
                yaxis: {{ title: '價格 (USD)', side: 'left' }},
                yaxis2: {{
                    title: '成交量',
                    side: 'right',
                    overlaying: 'y'
                }},
                height: 550,
                showlegend: true
            }};
            
            Plotly.newPlot('technical-chart-{symbol}', technicalData_{safe_symbol}, technicalLayout_{safe_symbol});
            '''
            
            return chart_js
        except Exception as e:
            print(f"創建技術圖表時發生錯誤: {e}")
            return f"console.log('技術圖表生成失敗: {e}');"
    
    def _get_price_color(self, current_price, target_price):
        """根據價格差異獲取顏色"""
        if target_price > current_price:
            return '#4CAF50'  # 綠色（上漲）
        elif target_price < current_price:
            return '#f44336'  # 紅色（下跌）
        else:
            return '#ff9800'  # 橙色（持平）
    
    def _get_rsi_signal(self, rsi_value):
        """獲取RSI信號"""
        try:
            rsi = float(rsi_value)
            if rsi > 70:
                return "超買"
            elif rsi < 30:
                return "超賣"
            else:
                return "正常"
        except:
            return "N/A"
    
    def _get_rsi_signal_color(self, rsi_value):
        """獲取RSI信號顏色"""
        try:
            rsi = float(rsi_value)
            if rsi > 70:
                return "#f44336"  # 紅色
            elif rsi < 30:
                return "#4CAF50"  # 綠色
            else:
                return "#2196F3"  # 藍色
        except:
            return "#666"
    
    def _get_macd_signal(self, macd_value, macd_signal_value):
        """獲取MACD信號"""
        try:
            macd = float(macd_value)
            macd_signal = float(macd_signal_value)
            if macd > macd_signal:
                return "看多"
            else:
                return "看空"
        except:
            return "N/A"
    
    def _get_macd_signal_color(self, macd_value, macd_signal_value):
         """獲取MACD信號顏色"""
         try:
             macd = float(macd_value)
             macd_signal = float(macd_signal_value)
             if macd > macd_signal:
                 return "#4CAF50"  # 綠色
             else:
                 return "#f44336"  # 紅色
         except:
             return "#666"
     
    def _create_right_analysis_panel(self, analyzer, signal_data, signal_str):
         """創建右側信號分析面板"""
         try:
             # 獲取技術指標數據 - 使用足夠的數據來計算6個月平均成本
             data = analyzer.data.tail(120)  # 取最近120天數據以支持6個月計算
             
             # 計算布林通道
             bb_period = 20
             bb_std = 2
             bb_middle = data['Close'].rolling(window=bb_period).mean()
             bb_std_dev = data['Close'].rolling(window=bb_period).std()
             bb_upper = bb_middle + (bb_std_dev * bb_std)
             bb_lower = bb_middle - (bb_std_dev * bb_std)
             
             current_price = data['Close'].iloc[-1]
             current_bb_upper = bb_upper.iloc[-1]
             current_bb_lower = bb_lower.iloc[-1]
             current_bb_middle = bb_middle.iloc[-1]
             
             # 布林通道評分
             bb_position = (current_price - current_bb_lower) / (current_bb_upper - current_bb_lower) if current_bb_upper != current_bb_lower else 0.5
             if bb_position > 0.8:
                 bb_score = "超買"
                 bb_color = "#f44336"
             elif bb_position < 0.2:
                 bb_score = "超賣"
                 bb_color = "#4CAF50"
             else:
                 bb_score = "正常"
                 bb_color = "#2196F3"
             
             # 計算RSI
             rsi_period = 14
             delta = data['Close'].diff()
             gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
             loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
             rs = gain / loss
             rsi = 100 - (100 / (1 + rs))
             current_rsi = rsi.iloc[-1]
             
             # RSI評分
             if current_rsi > 70:
                 rsi_score = "超買"
                 rsi_color = "#f44336"
             elif current_rsi < 30:
                 rsi_score = "超賣"
                 rsi_color = "#4CAF50"
             else:
                 rsi_score = "正常"
                 rsi_color = "#2196F3"
             
             # 計算MACD
             exp1 = data['Close'].ewm(span=12).mean()
             exp2 = data['Close'].ewm(span=26).mean()
             macd_line = exp1 - exp2
             macd_signal = macd_line.ewm(span=9).mean()
             current_macd = macd_line.iloc[-1]
             current_macd_signal = macd_signal.iloc[-1]
             
             # MACD評分
             if current_macd > current_macd_signal:
                 macd_score = "看多"
                 macd_color = "#4CAF50"
             else:
                 macd_score = "看空"
                 macd_color = "#f44336"
             
             # 價量分析
             volume_analysis = self._analyze_volume_price(data)
             
             return f'''
             <div class="analysis-panel">
                 <h4>📈 右側信號分析</h4>
                 <div class="info-grid">
                     <div class="info-item">
                         <span class="label">主要信號:</span>
                         <span class="value">{signal_str}</span>
                     </div>
                     <div class="info-item">
                         <span class="label">信號強度:</span>
                         <span class="value">{signal_data.get('strength', 'N/A') if isinstance(signal_data, dict) else 'N/A'}</span>
                     </div>
                     <div class="info-item">
                         <span class="label">布林通道:</span>
                         <span class="value" style="color: {bb_color};">{bb_score}</span>
                     </div>
                     <div class="info-item">
                         <span class="label">RSI (14):</span>
                         <span class="value" style="color: {rsi_color};">{current_rsi:.1f} ({rsi_score})</span>
                     </div>
                     <div class="info-item">
                         <span class="label">MACD:</span>
                         <span class="value" style="color: {macd_color};">{macd_score}</span>
                     </div>
                 </div>
                 
                                   <!-- 價量分析 -->
                  <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #FF9800;">
                      <h5 style="margin: 0 0 10px 0; color: #333; font-size: 0.9em;">📊 價量分析</h5>
                      <div style="font-size: 0.85em; line-height: 1.4;">
                          <div style="margin-bottom: 5px;">
                              <span style="color: #333; font-weight: bold;">當前價格:</span> ${current_price:.2f}
                          </div>
                          <div style="margin-bottom: 5px;">
                              <span style="color: #333; font-weight: bold;">3個月平均成本:</span> ${volume_analysis['avg_cost_3m']:.2f}
                          </div>
                          <div style="margin-bottom: 5px;">
                              <span style="color: {volume_analysis['cost_3m_color']}; font-weight: bold;">3個月偏離:</span> {volume_analysis['cost_deviation_3m']:.1f}%
                          </div>
                          <div style="margin-bottom: 5px;">
                              <span style="color: #333; font-weight: bold;">6個月平均成本:</span> ${volume_analysis['avg_cost_6m']:.2f}
                          </div>
                          <div style="margin-bottom: 5px;">
                              <span style="color: {volume_analysis['cost_6m_color']}; font-weight: bold;">6個月偏離:</span> {volume_analysis['cost_deviation_6m']:.1f}%
                          </div>
                          <div style="margin-bottom: 5px;">
                              <span style="color: {volume_analysis['pressure_color']}; font-weight: bold;">市場壓力:</span> {volume_analysis['pressure_type']}
                          </div>
                          <div style="margin-bottom: 5px;">
                              <span style="color: #333; font-weight: bold;">成交量趨勢:</span> {volume_analysis['volume_trend']}
                          </div>
                      </div>
                  </div>
             </div>
             '''
         except Exception as e:
             print(f"創建右側分析面板時發生錯誤: {e}")
             return f'''
             <div class="analysis-panel">
                 <h4>📈 右側信號分析</h4>
                 <div class="info-grid">
                     <div class="info-item">
                         <span class="label">主要信號:</span>
                         <span class="value">{signal_str}</span>
                     </div>
                     <div class="info-item">
                         <span class="label">信號強度:</span>
                         <span class="value">{signal_data.get('strength', 'N/A') if isinstance(signal_data, dict) else 'N/A'}</span>
                     </div>
                     <div class="info-item">
                         <span class="label">分析狀態:</span>
                         <span class="value" style="color: #f44336;">數據不足</span>
                     </div>
                 </div>
             </div>
             '''
    
    def _create_gemini_analysis_panel(self, gemini_data):
        """創建 Gemini AI 分析面板"""
        try:
            if not gemini_data or gemini_data.get('metadata', {}).get('status') != 'success':
                return '''
                <div class="analysis-panel">
                    <h4>🤖 Gemini AI 分析</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">分析狀態:</span>
                            <span class="value" style="color: #666;">暫無數據</span>
                        </div>
                    </div>
                </div>
                '''
            
            # 獲取股價預測數據
            price_forecast = gemini_data.get('price_forecast', {})
            price_1y = price_forecast.get('price_1y', 'N/A')
            price_3y = price_forecast.get('price_3y', 'N/A')
            price_5y = price_forecast.get('price_5y', 'N/A')
            
            # 獲取風險指標
            risk_metrics = gemini_data.get('risk_metrics', {})
            beta = risk_metrics.get('beta', 'N/A')
            volatility = risk_metrics.get('volatility', 'N/A')
            sharpe_ratio = risk_metrics.get('sharpe_ratio', 'N/A')
            risk_level = risk_metrics.get('risk_level', 'N/A')
            
            # 獲取新聞和判斷
            recent_news = gemini_data.get('recent_news', 'N/A')
            ai_judgment = gemini_data.get('ai_judgment', 'N/A')
            sentiment = gemini_data.get('sentiment', 'N/A')
            
            # 設定情緒顏色
            sentiment_color = "#4CAF50" if sentiment == "看漲" else "#f44336" if sentiment == "看跌" else "#666"
            
            # 設定風險等級顏色
            risk_color = "#f44336" if risk_level in ["極高", "高"] else "#ff9800" if risk_level == "中" else "#4CAF50"
            
            return f'''
            <div class="analysis-panel">
                <h4>🤖 Gemini AI 分析</h4>
                
                <!-- 股價預測 -->
                <div style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #2196F3;">
                    <h5 style="margin: 0 0 10px 0; color: #333; font-size: 0.9em;">📈 股價預測</h5>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">1年目標:</span>
                            <span class="value">{price_1y}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">3年目標:</span>
                            <span class="value">{price_3y}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">5年目標:</span>
                            <span class="value">{price_5y}</span>
                        </div>
                    </div>
                </div>
                
                <!-- 風險指標 -->
                <div style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #FF9800;">
                    <h5 style="margin: 0 0 10px 0; color: #333; font-size: 0.9em;">⚡ 風險指標</h5>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">Beta值:</span>
                            <span class="value">{beta if isinstance(beta, (int, float)) else beta}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">波動率:</span>
                            <span class="value">{volatility if isinstance(volatility, (int, float)) else volatility}{'%' if isinstance(volatility, (int, float)) else ''}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">夏普比率:</span>
                            <span class="value">{sharpe_ratio if isinstance(sharpe_ratio, (int, float)) else sharpe_ratio}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">風險等級:</span>
                            <span class="value" style="color: {risk_color};">{risk_level}</span>
                        </div>
                    </div>
                </div>
                
                <!-- 重要新聞與AI判斷 -->
                <div style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #4CAF50;">
                    <h5 style="margin: 0 0 10px 0; color: #333; font-size: 0.9em;">📰 市場動態</h5>
                    <div class="info-grid">
                        <div class="info-item" style="grid-column: span 2;">
                            <span class="label">重要新聞:</span>
                            <span class="value" style="font-size: 0.85em; line-height: 1.4;">{recent_news}</span>
                        </div>
                        <div class="info-item" style="grid-column: span 2;">
                            <span class="label">AI判斷:</span>
                            <span class="value" style="font-size: 0.85em; line-height: 1.4;">{ai_judgment}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">投資情緒:</span>
                            <span class="value" style="color: {sentiment_color}; font-weight: bold;">{sentiment}</span>
                        </div>
                    </div>
                </div>
            </div>
            '''
            
        except Exception as e:
            print(f"創建 Gemini 分析面板時發生錯誤: {e}")
            return '''
            <div class="analysis-panel">
                <h4>🤖 Gemini AI 分析</h4>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="label">分析狀態:</span>
                        <span class="value" style="color: #f44336;">分析失敗</span>
                    </div>
                </div>
            </div>
            '''
     
    def _calculate_right_analysis_stats(self, results):
        """計算右側分析統計數據"""
        bullish_count = 0
        bearish_count = 0
        pressure_risk_count = 0
        
        for result in results:
            try:
                analyzer = result['analyzer']
                if not hasattr(analyzer, 'data') or analyzer.data.empty:
                    continue
                
                data = analyzer.data.tail(120)  # 取最近120天數據以支持6個月計算
                
                # 計算技術指標
                # 布林通道
                bb_period = 20
                bb_std = 2
                bb_middle = data['Close'].rolling(window=bb_period).mean()
                bb_std_dev = data['Close'].rolling(window=bb_period).std()
                bb_upper = bb_middle + (bb_std_dev * bb_std)
                bb_lower = bb_middle - (bb_std_dev * bb_std)
                
                current_price = data['Close'].iloc[-1]
                current_bb_upper = bb_upper.iloc[-1]
                current_bb_lower = bb_lower.iloc[-1]
                
                # 布林通道評分
                bb_position = (current_price - current_bb_lower) / (current_bb_upper - current_bb_lower) if current_bb_upper != current_bb_lower else 0.5
                
                # RSI
                rsi_period = 14
                delta = data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]
                
                # MACD
                exp1 = data['Close'].ewm(span=12).mean()
                exp2 = data['Close'].ewm(span=26).mean()
                macd_line = exp1 - exp2
                macd_signal = macd_line.ewm(span=9).mean()
                current_macd = macd_line.iloc[-1]
                current_macd_signal = macd_signal.iloc[-1]
                
                # 價量分析
                volume_analysis = self._analyze_volume_price(data)
                
                # 統計看多指標
                bullish_indicators = 0
                if bb_position < 0.2:  # 布林通道超賣
                    bullish_indicators += 1
                if current_rsi < 30:  # RSI超賣
                    bullish_indicators += 1
                if current_macd > current_macd_signal:  # MACD看多
                    bullish_indicators += 1
                
                # 統計看空指標
                bearish_indicators = 0
                if bb_position > 0.8:  # 布林通道超買
                    bearish_indicators += 1
                if current_rsi > 70:  # RSI超買
                    bearish_indicators += 1
                if current_macd < current_macd_signal:  # MACD看空
                    bearish_indicators += 1
                
                # 判斷整體趨勢
                if bullish_indicators > bearish_indicators:
                    bullish_count += 1
                elif bearish_indicators > bullish_indicators:
                    bearish_count += 1
                
                # 統計賣壓風險
                if volume_analysis['pressure_type'] in ['強烈賣壓風險', '中等賣壓風險']:
                    pressure_risk_count += 1
                    
            except Exception as e:
                print(f"計算右側分析統計時發生錯誤: {e}")
                continue
        
        return {
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'pressure_risk_count': pressure_risk_count
        }
    
    def _analyze_volume_price(self, data):
        """分析價量關係"""
        try:
            # 計算成交量加權平均價格 (VWAP)
            data['VWAP'] = (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()
            
            # 計算不同時間範圍的平均成本
            current_price = data['Close'].iloc[-1]
            
            # 3個月平均成本 (約60個交易日) - 使用成交量加權平均價格
            data_3m = data.tail(min(60, len(data)))
            avg_cost_3m = (data_3m['Close'] * data_3m['Volume']).sum() / data_3m['Volume'].sum() if data_3m['Volume'].sum() > 0 else data_3m['Close'].mean()
            
            # 6個月平均成本 (約120個交易日) - 使用成交量加權平均價格
            data_6m = data.tail(min(120, len(data)))
            avg_cost_6m = (data_6m['Close'] * data_6m['Volume']).sum() / data_6m['Volume'].sum() if data_6m['Volume'].sum() > 0 else data_6m['Close'].mean()
            
            # 計算3個月成本偏離度
            cost_deviation_3m = ((current_price - avg_cost_3m) / avg_cost_3m) * 100
            
            # 計算6個月成本偏離度
            cost_deviation_6m = ((current_price - avg_cost_6m) / avg_cost_6m) * 100
            
            # 使用3個月和6個月偏離度綜合判斷市場壓力
            # 如果任一期間偏離度超過閾值，就顯示相應的壓力類型
            if cost_deviation_3m > 30 or cost_deviation_6m > 30:
                pressure_type = "強烈賣壓風險"
                pressure_color = "#f44336"
            elif cost_deviation_3m > 15 or cost_deviation_6m > 15:
                pressure_type = "中等賣壓風險"
                pressure_color = "#ff9800"
            elif cost_deviation_3m < -30 or cost_deviation_6m < -30:
                pressure_type = "強烈支撐"
                pressure_color = "#4CAF50"
            elif cost_deviation_3m < -15 or cost_deviation_6m < -15:
                pressure_type = "中等支撐"
                pressure_color = "#2196F3"
            else:
                pressure_type = "整盤整理"
                pressure_color = "#666"
            
            # 分析成交量趨勢
            recent_volume = data['Volume'].tail(5).mean()
            historical_volume = data['Volume'].tail(20).mean()
            volume_ratio = recent_volume / historical_volume if historical_volume > 0 else 1
            
            if volume_ratio > 1.5:
                volume_trend = "放量"
            elif volume_ratio < 0.7:
                volume_trend = "縮量"
            else:
                volume_trend = "正常"
            
            return {
                'avg_cost_3m': avg_cost_3m,
                'avg_cost_6m': avg_cost_6m,
                'cost_deviation_3m': cost_deviation_3m,
                'cost_deviation_6m': cost_deviation_6m,
                'pressure_type': pressure_type,
                'pressure_color': pressure_color,
                'volume_trend': volume_trend,
                'cost_3m_color': "#f44336" if cost_deviation_3m > 15 else "#4CAF50" if cost_deviation_3m < -15 else "#666",
                'cost_6m_color': "#f44336" if cost_deviation_6m > 15 else "#4CAF50" if cost_deviation_6m < -15 else "#666"
            }
            
        except Exception as e:
            print(f"價量分析時發生錯誤: {e}")
            return {
                'avg_cost_3m': current_price,
                'avg_cost_6m': current_price,
                'cost_deviation_3m': 0,
                'cost_deviation_6m': 0,
                'pressure_type': "分析失敗",
                'pressure_color': "#666",
                'volume_trend': "N/A",
                'cost_3m_color': "#666",
                'cost_6m_color': "#666"
            }

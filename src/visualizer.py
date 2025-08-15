import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime
import sys
import os

# 添加左側分析模組
try:
    from .left_analysis import analyze_stock, analyze_multiple_stocks
except ImportError:
    # 如果相對導入失敗，嘗試絕對導入
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from src.left_analysis import analyze_stock, analyze_multiple_stocks

class StockVisualizer:
    def __init__(self, analyzer):
        """
        初始化視覺化器
        
        Args:
            analyzer: StockAnalyzer 實例
        """
        self.analyzer = analyzer
        self.data = analyzer.data
        self.signals = analyzer.signals
        self.left_analysis_data = None  # 左側分析數據
        
    def get_left_analysis_data(self):
        """獲取左側分析數據"""
        if self.left_analysis_data is None:
            try:
                self.left_analysis_data = analyze_stock(self.analyzer.symbol)
            except Exception as e:
                print(f"左側分析數據獲取失敗: {e}")
                self.left_analysis_data = None
        return self.left_analysis_data
    
    def create_batch_html_report(self, analyzers, save_path=None):
        """
        為多支股票創建綜合 HTML 報告，包含技術分析和左側分析
        所有內容都在單一 HTML 文件中，使用可折疊式設計
        
        Args:
            analyzers: StockAnalyzer 實例列表
            save_path: 保存路徑
        """
        if not analyzers:
            print("沒有分析器數據")
            return
        
        # 獲取所有股票的當前訊號和左側分析數據
        all_results = []
        for analyzer in analyzers:
            if analyzer.data is not None and analyzer.signals is not None:
                current_signal = analyzer.get_current_signal()
                summary = analyzer.get_signal_summary()
                
                # 獲取左側分析數據
                try:
                    left_data = analyze_stock(analyzer.symbol)
                except:
                    left_data = None
                
                all_results.append({
                    'symbol': analyzer.symbol,
                    'signal': current_signal,
                    'summary': summary,
                    'analyzer': analyzer,
                    'left_data': left_data
                })
        
        if not all_results:
            print("沒有有效的分析結果")
            return
        
        # 統計摘要
        buy_count = len([r for r in all_results if r['signal']['signal'] == '買入'])
        sell_count = len([r for r in all_results if r['signal']['signal'] == '賣出'])
        hold_count = len([r for r in all_results if r['signal']['signal'] == '持有'])
        
        avg_strength = sum([r['signal']['strength'] for r in all_results]) / len(all_results)
        max_strength = max([r['signal']['strength'] for r in all_results])
        min_strength = min([r['signal']['strength'] for r in all_results])
        
        # 左側分析統計
        left_analysis_count = len([r for r in all_results if r['left_data'] and 'error' not in r['left_data']])
        
        # 將數值轉換為字符串的映射
        signal_map = {1: "買入", -1: "賣出", 0: "持有"}
        
        # 創建圖表
        technical_chart = self.create_batch_technical_summary_chart(analyzers)
        left_analysis_chart = self.create_batch_left_analysis_summary_chart(analyzers)
        
        # 準備圖表數據
        technical_chart_json = technical_chart.to_json() if technical_chart else 'null'
        left_analysis_chart_json = left_analysis_chart.to_json() if left_analysis_chart else 'null'
        
        # 創建 HTML 內容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>批量股票綜合分析報告</title>
    <style>
        body {{
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #007bff;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 2.5em;
        }}
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            font-size: 1.2em;
        }}
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stock-results {{
            margin: 30px 0;
        }}
        .stock-card {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            margin: 20px 0;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stock-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .stock-header:hover {{
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }}
        .stock-content {{
            padding: 20px;
            display: none;
        }}
        .stock-content.active {{
            display: block;
        }}
        .analysis-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}
        .technical-section, .left-section {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }}
        .technical-section h4, .left-section h4 {{
            color: #007bff;
            margin-top: 0;
        }}
        .signal-info {{
            background: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .valuation-status {{
            padding: 8px;
            border-radius: 5px;
            margin: 8px 0;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .undervalued {{
            background-color: #d4edda;
            color: #155724;
        }}
        .overvalued {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .fair-value {{
            background-color: #d1ecf1;
            color: #0c5460;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
        .toggle-btn {{
            background: none;
            border: none;
            color: white;
            font-size: 1.2em;
            cursor: pointer;
        }}
        .charts-section {{
            margin: 30px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .chart-container h3 {{
            color: #007bff;
            margin-top: 0;
            margin-bottom: 15px;
            text-align: center;
        }}
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script>
        function toggleStock(symbol) {{
            const content = document.getElementById('content-' + symbol);
            const btn = document.getElementById('btn-' + symbol);
            if (content.classList.contains('active')) {{
                content.classList.remove('active');
                btn.textContent = '▼';
            }} else {{
                content.classList.add('active');
                btn.textContent = '▲';
            }}
        }}
        
        // 技術分析圖表數據
        const technicalChartData = {technical_chart_json};
        
        // 左側分析圖表數據
        const leftAnalysisChartData = {left_analysis_chart_json};
        
        // 繪製圖表
        if (technicalChartData) {{
            Plotly.newPlot('technical-chart', technicalChartData.data, technicalChartData.layout);
        }}
        
        if (leftAnalysisChartData) {{
            Plotly.newPlot('left-analysis-chart', leftAnalysisChartData.data, leftAnalysisChartData.layout);
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>批量股票綜合分析報告</h1>
            <p>技術分析 + 左側分析 | 分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary-stats">
            <div class="stat-card">
                <h3>分析股票數</h3>
                <div class="value">{len(all_results)}</div>
            </div>
            <div class="stat-card">
                <h3>買入建議</h3>
                <div class="value">{buy_count}</div>
            </div>
            <div class="stat-card">
                <h3>賣出建議</h3>
                <div class="value">{sell_count}</div>
            </div>
            <div class="stat-card">
                <h3>持有建議</h3>
                <div class="value">{hold_count}</div>
            </div>
            <div class="stat-card">
                <h3>平均強度</h3>
                <div class="value">{avg_strength:.1f}</div>
            </div>
            <div class="stat-card">
                <h3>左側分析</h3>
                <div class="value">{left_analysis_count}</div>
            </div>
        </div>
        
        <!-- 圖表分析區域 -->
        <div class="charts-section">
            <h2>📈 圖形化分析摘要</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>🔍 技術分析摘要</h3>
                    <div id="technical-chart"></div>
                </div>
                <div class="chart-container">
                    <h3>📊 左側分析摘要</h3>
                    <div id="left-analysis-chart"></div>
                </div>
            </div>
        </div>
        
        <div class="stock-results">
            <h2>📊 各股票詳細分析</h2>
        """
        
        # 按訊號強度排序
        all_results.sort(key=lambda x: x['signal']['strength'], reverse=True)
        
        for result in all_results:
            symbol = result['symbol']
            signal = result['signal']
            left_data = result['left_data']
            
            html_content += f"""
            <div class="stock-card">
                <div class="stock-header" onclick="toggleStock('{symbol}')">
                    <h3>{symbol} - {signal['signal']} (強度: {signal['strength']:.1f})</h3>
                    <button class="toggle-btn" id="btn-{symbol}">▼</button>
                </div>
                <div class="stock-content" id="content-{symbol}">
                    <div class="analysis-grid">
                        <div class="technical-section">
                            <h4>📈 技術分析</h4>
                            <div class="signal-info">
                                <p><strong>建議操作:</strong> {signal['signal']}</p>
                                <p><strong>當前價格:</strong> ${signal['price']:.2f}</p>
                                <p><strong>訊號強度:</strong> {signal['strength']:.1f}</p>
                                <p><strong>分析期間:</strong> {len(result['analyzer'].data)} 個交易日</p>
                            </div>
                        </div>
                        
                        <div class="left-section">
                            <h4>📊 左側分析</h4>
            """
            
            if left_data and 'error' not in left_data:
                current_price = left_data['current_price']
                html_content += f"""
                            <div class="signal-info">
                                <p><strong>當前股價:</strong> ${current_price:.2f}</p>
                                <p><strong>Forward EPS:</strong> ${left_data.get('forward_eps', 0):.2f}</p>
                                <p><strong>Forward P/E:</strong> {left_data.get('forward_pe', 0):.2f}</p>
                            </div>
                """
                
                # 添加各時間範圍的預估
                for timeframe in ['1_year', '2_year', '3_year']:
                    if timeframe in left_data['timeframes']:
                        tf_data = left_data['timeframes'][timeframe]
                        target_low = tf_data.get('target_low', 0)
                        target_high = tf_data.get('target_high', 0)
                        target_mean = tf_data.get('target_mean', 0)
                        potential_return = tf_data.get('potential_return', 0)
                        
                        # 判斷估值狀態
                        if current_price < target_low:
                            status_class = "undervalued"
                            status_text = "可能低估"
                        elif current_price > target_high:
                            status_class = "overvalued"
                            status_text = "可能高估"
                        else:
                            status_class = "fair-value"
                            status_text = "合理估值"
                        
                        html_content += f"""
                            <div class="signal-info">
                                <p><strong>{tf_data['timeframe']}:</strong></p>
                                <p>價格範圍: ${target_low:.2f} - ${target_high:.2f}</p>
                                <p>平均預估: ${target_mean:.2f}</p>
                                <p>預期報酬率: {potential_return:+.2f}%</p>
                                <div class="valuation-status {status_class}">
                                    估值狀態: {status_text}
                                </div>
                            </div>
                        """
            else:
                html_content += """
                            <div class="signal-info">
                                <p>左側分析數據暫時無法獲取</p>
                            </div>
                """
            
            html_content += """
                        </div>
                    </div>
                </div>
            </div>
            """
        
        html_content += f"""
        </div>
        
        <div class="footer">
            <p>⚠️ 免責聲明: 本分析僅供參考，不構成投資建議。投資有風險，請謹慎決策。</p>
            <p>AIStock 批量分析系統 | 生成於 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
        
        # 保存 HTML 文件
        if save_path:
            if not save_path.endswith('.html'):
                save_path += '.html'
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"批量綜合分析報告已儲存至: {save_path}")
            return save_path
        else:
            # 生成預設檔名
            default_path = f"batch_comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(default_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"批量綜合分析報告已儲存至: {default_path}")
            return default_path

    def create_comprehensive_html_report(self, save_path=None):
        """
        創建綜合 HTML 報告，包含技術分析和左側分析
        所有內容都在單一 HTML 文件中，不使用圖片
        """
        if self.data is None or self.signals is None:
            print("請先執行分析")
            return
        
        # 獲取當前訊號和摘要
        current_signal = self.analyzer.get_current_signal()
        summary = self.analyzer.get_signal_summary()
        
        # 獲取左側分析數據
        left_data = self.get_left_analysis_data()
        
        # 創建綜合圖表
        fig = make_subplots(
            rows=8, cols=1,  # 增加一行用於左側分析
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(
                '股價與交易訊號', 
                '成交量', 
                'MACD', 
                'RSI', 
                '隨機指標',
                '訊號強度',
                '技術指標綜合分析',
                '左側分析 - 股價範圍'
            ),
            row_width=[0.15, 0.10, 0.10, 0.10, 0.10, 0.10, 0.15, 0.20]
        )
        
        # 1. K線圖與訊號
        # K線圖
        fig.add_trace(
            go.Candlestick(
                x=self.data.index,
                open=self.data['Open'],
                high=self.data['High'],
                low=self.data['Low'],
                close=self.data['Close'],
                name='K線'
            ),
            row=1, col=1
        )
        
        # 移動平均線
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['SMA_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['SMA_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
        
        # 布林通道
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['BB_Upper'],
                mode='lines',
                name='布林上軌',
                line=dict(color='gray', width=1, dash='dash')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['BB_Lower'],
                mode='lines',
                name='布林下軌',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty'
            ),
            row=1, col=1
        )
        
        # 買入訊號
        buy_signals = self.signals[self.signals['Signal'] == 1]
        if len(buy_signals) > 0:
            fig.add_trace(
                go.Scatter(
                    x=buy_signals.index,
                    y=buy_signals['Price'],
                    mode='markers',
                    name='買入訊號',
                    marker=dict(symbol='triangle-up', size=10, color='green')
                ),
                row=1, col=1
            )
        
        # 賣出訊號
        sell_signals = self.signals[self.signals['Signal'] == -1]
        if len(sell_signals) > 0:
            fig.add_trace(
                go.Scatter(
                    x=sell_signals.index,
                    y=sell_signals['Price'],
                    mode='markers',
                    name='賣出訊號',
                    marker=dict(symbol='triangle-down', size=10, color='red')
                ),
                row=1, col=1
            )
        
        # 2. 成交量
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(self.data['Close'], self.data['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=self.data.index,
                y=self.data['Volume'],
                name='成交量',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # 3. MACD
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='blue', width=1)
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['MACD_Signal'],
                mode='lines',
                name='MACD Signal',
                line=dict(color='red', width=1)
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=self.data.index,
                y=self.data['MACD_Histogram'],
                name='MACD Histogram',
                opacity=0.5
            ),
            row=3, col=1
        )
        
        # 4. RSI
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=1)
            ),
            row=4, col=1
        )
        
        # RSI 超買超賣線
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=4, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=4, col=1)
        
        # 5. 隨機指標
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['Stoch_K'],
                mode='lines',
                name='%K',
                line=dict(color='blue', width=1)
            ),
            row=5, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['Stoch_D'],
                mode='lines',
                name='%D',
                line=dict(color='red', width=1)
            ),
            row=5, col=1
        )
        
        # 隨機指標超買超賣線
        fig.add_hline(y=80, line_dash="dash", line_color="red", row=5, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", row=5, col=1)
        
        # 6. 訊號強度
        fig.add_trace(
            go.Scatter(
                x=self.signals.index,
                y=self.signals['Strength'],
                mode='lines',
                name='訊號強度',
                line=dict(color='orange', width=2)
            ),
            row=6, col=1
        )
        
        # 訊號強度閾值線
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=6, col=1)
        fig.add_hline(y=-30, line_dash="dash", line_color="red", row=6, col=1)
        fig.add_hline(y=0, line_dash="dot", line_color="gray", row=6, col=1)
        
        # 7. 技術指標綜合分析
        # 這裡可以添加更多技術指標的綜合分析
        
        # 8. 左側分析 - 股價範圍圖表
        if left_data and 'error' not in left_data:
            current_price = left_data['current_price']
            timeframes = left_data['timeframes']
            
            # 為每個時間範圍創建範圍條
            colors = ['#2E86AB', '#A23B72', '#F18F01']
            years = ['1_year', '2_year', '3_year']
            
            for i, (year, color) in enumerate(zip(years, colors)):
                if year in timeframes:
                    tf_data = timeframes[year]
                    target_low = tf_data.get('target_low')
                    target_high = tf_data.get('target_high')
                    target_mean = tf_data.get('target_mean')
                    
                    if all([target_low, target_high, target_mean]):
                        # 創建範圍條
                        fig.add_trace(
                            go.Bar(
                                x=[tf_data['timeframe']],
                                y=[target_high - target_low],
                                base=[target_low],
                                name=f'{tf_data["timeframe"]} 範圍',
                                marker_color=color,
                                opacity=0.3,
                                showlegend=False
                            ),
                            row=8, col=1
                        )
                        
                        # 添加平均線
                        fig.add_trace(
                            go.Scatter(
                                x=[tf_data['timeframe']],
                                y=[target_mean],
                                mode='markers',
                                name=f'{tf_data["timeframe"]} 平均',
                                marker=dict(symbol='diamond', size=10, color=color),
                                showlegend=False
                            ),
                            row=8, col=1
                        )
            
            # 添加當前股價線
            fig.add_hline(
                y=current_price, 
                line_dash="solid", 
                line_color="red", 
                line_width=3,
                row=8, col=1,
                annotation_text=f"當前股價: ${current_price:.2f}"
            )
        
        # 更新佈局
        fig.update_layout(
            title=f'{self.analyzer.symbol} 綜合分析報告 (技術分析 + 左側分析)',
            xaxis_rangeslider_visible=False,
            height=1200,  # 增加高度以容納左側分析
            showlegend=True
        )
        
        # 創建 HTML 內容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.analyzer.symbol} 綜合分析報告</title>
    <style>
        body {{
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #007bff;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 2.5em;
        }}
        .analysis-summary {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .technical-analysis, .left-analysis {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }}
        .technical-analysis h3, .left-analysis h3 {{
            color: #007bff;
            margin-top: 0;
        }}
        .signal-info {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .chart-container {{
            margin: 30px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.analyzer.symbol} ({self.analyzer.long_name}) 綜合分析報告</h1>
            <p>技術分析 + 左側分析 | 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="analysis-summary">
            <div class="technical-analysis">
                <h3>📊 技術分析摘要</h3>
                <div class="signal-info">
                    <p><strong>建議操作:</strong> {current_signal['signal']}</p>
                    <p><strong>當前價格:</strong> ${current_signal['price']:.2f}</p>
                    <p><strong>訊號強度:</strong> {current_signal['strength']:.1f}</p>
                    <p><strong>分析期間:</strong> {len(self.data)} 個交易日</p>
                </div>
            </div>
            
            <div class="left-analysis">
                <h3>📈 左側分析摘要</h3>
        """
        
        # 添加左側分析摘要
        if left_data and 'error' not in left_data:
            current_price = left_data['current_price']
            html_content += f"""
                <div class="signal-info">
                    <p><strong>當前股價:</strong> ${current_price:.2f}</p>
                    <p><strong>Forward EPS:</strong> ${left_data.get('forward_eps', 0):.2f}</p>
                    <p><strong>Forward P/E:</strong> {left_data.get('forward_pe', 0):.2f}</p>
                    <p><strong>數據來源:</strong> {', '.join(left_data.get('sources_used', []))}</p>
                </div>
            """
            
            # 添加各時間範圍的預估
            for timeframe in ['1_year', '2_year', '3_year']:
                if timeframe in left_data['timeframes']:
                    tf_data = left_data['timeframes'][timeframe]
                    target_low = tf_data.get('target_low', 0)
                    target_high = tf_data.get('target_high', 0)
                    target_mean = tf_data.get('target_mean', 0)
                    potential_return = tf_data.get('potential_return', 0)
                    
                    # 判斷估值狀態
                    if current_price < target_low:
                        status = "🟢 可能低估"
                    elif current_price > target_high:
                        status = "🔴 可能高估"
                    else:
                        status = "🟡 合理估值"
                    
                    html_content += f"""
                    <div class="signal-info">
                        <p><strong>{tf_data['timeframe']}:</strong></p>
                        <p>價格範圍: ${target_low:.2f} - ${target_high:.2f}</p>
                        <p>平均預估: ${target_mean:.2f}</p>
                        <p>預期報酬率: {potential_return:+.2f}%</p>
                        <p>估值狀態: {status}</p>
                    </div>
                    """
        else:
            html_content += """
                <div class="signal-info">
                    <p>左側分析數據暫時無法獲取</p>
                </div>
            """
        
        html_content += f"""
            </div>
        </div>
        
        <div class="chart-container">
            {fig.to_html(full_html=False, include_plotlyjs=True)}
        </div>
        
        <div class="footer">
            <p>⚠️ 免責聲明: 本分析僅供參考，不構成投資建議。投資有風險，請謹慎決策。</p>
            <p>AIStock 綜合分析系統 | 生成於 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
        
        # 保存 HTML 文件
        if save_path:
            if not save_path.endswith('.html'):
                save_path += '.html'
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"綜合分析報告已儲存至: {save_path}")
            return save_path
        else:
            # 生成預設檔名
            default_path = f"{self.analyzer.symbol}_comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(default_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"綜合分析報告已儲存至: {default_path}")
            return default_path

    def plot_candlestick_with_signals(self, save_path=None):
        """繪製K線圖與交易訊號"""
        if self.data is None or self.signals is None:
            print("請先執行分析")
            return
        
        # 創建子圖
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('股價與訊號', '成交量', 'RSI'),
            row_width=[0.6, 0.2, 0.2]
        )
        
        # K線圖
        fig.add_trace(
            go.Candlestick(
                x=self.data.index,
                open=self.data['Open'],
                high=self.data['High'],
                low=self.data['Low'],
                close=self.data['Close'],
                name='K線'
            ),
            row=1, col=1
        )
        
        # 移動平均線
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['SMA_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['SMA_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
        
        # 布林通道
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['BB_Upper'],
                mode='lines',
                name='布林上軌',
                line=dict(color='gray', width=1, dash='dash')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['BB_Lower'],
                mode='lines',
                name='布林下軌',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty'
            ),
            row=1, col=1
        )
        
        # 買入訊號
        buy_signals = self.signals[self.signals['Signal'] == 1]
        if len(buy_signals) > 0:
            fig.add_trace(
                go.Scatter(
                    x=buy_signals.index,
                    y=buy_signals['Price'],
                    mode='markers',
                    name='買入訊號',
                    marker=dict(color='green', size=10, symbol='triangle-up')
                ),
                row=1, col=1
            )
        
        # 賣出訊號
        sell_signals = self.signals[self.signals['Signal'] == -1]
        if len(sell_signals) > 0:
            fig.add_trace(
                go.Scatter(
                    x=sell_signals.index,
                    y=sell_signals['Price'],
                    mode='markers',
                    name='賣出訊號',
                    marker=dict(color='red', size=10, symbol='triangle-down')
                ),
                row=1, col=1
            )
        
        # 成交量
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(self.data['Close'], self.data['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=self.data.index,
                y=self.data['Volume'],
                name='成交量',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=1)
            ),
            row=3, col=1
        )
        
        # RSI 超買超賣線
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        # 更新佈局
        fig.update_layout(
            title=f'{self.analyzer.symbol} 股票分析圖',
            xaxis_rangeslider_visible=False,
            height=800
        )
        
        if save_path:
            fig.write_html(save_path)
            print(f"圖表已儲存至: {save_path}")
        
        fig.show()
    
    def plot_technical_indicators(self, save_path=None):
        """繪製技術指標圖"""
        if self.data is None:
            print("請先執行分析")
            return
        
        fig, axes = plt.subplots(4, 1, figsize=(15, 12))
        fig.suptitle(f'{self.analyzer.symbol} 技術指標分析', fontsize=16)
        
        # MACD
        axes[0].plot(self.data.index, self.data['MACD'], label='MACD', color='blue')
        axes[0].plot(self.data.index, self.data['MACD_Signal'], label='Signal', color='red')
        axes[0].bar(self.data.index, self.data['MACD_Histogram'], label='Histogram', alpha=0.3)
        axes[0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[0].set_title('MACD')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # RSI
        axes[1].plot(self.data.index, self.data['RSI'], label='RSI', color='purple')
        axes[1].axhline(y=70, color='red', linestyle='--', alpha=0.7, label='超買線')
        axes[1].axhline(y=30, color='green', linestyle='--', alpha=0.7, label='超賣線')
        axes[1].set_title('RSI')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # 隨機指標
        axes[2].plot(self.data.index, self.data['Stoch_K'], label='%K', color='blue')
        axes[2].plot(self.data.index, self.data['Stoch_D'], label='%D', color='red')
        axes[2].axhline(y=80, color='red', linestyle='--', alpha=0.7, label='超買線')
        axes[2].axhline(y=20, color='green', linestyle='--', alpha=0.7, label='超賣線')
        axes[2].set_title('隨機指標')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        # ATR
        axes[3].plot(self.data.index, self.data['ATR'], label='ATR', color='orange')
        axes[3].set_title('ATR (平均真實範圍)')
        axes[3].legend()
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"圖表已儲存至: {save_path}")
        
        plt.show()
    
    def plot_signal_strength(self, save_path=None):
        """繪製訊號強度圖"""
        if self.signals is None:
            print("請先生成訊號")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        fig.suptitle(f'{self.analyzer.symbol} 訊號強度分析', fontsize=16)
        
        # 訊號強度時間序列
        ax1.plot(self.signals.index, self.signals['Strength'], label='訊號強度', color='blue')
        ax1.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='買入閾值')
        ax1.axhline(y=-30, color='red', linestyle='--', alpha=0.7, label='賣出閾值')
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax1.fill_between(self.signals.index, 30, self.signals['Strength'], 
                        where=(self.signals['Strength'] >= 30), alpha=0.3, color='green')
        ax1.fill_between(self.signals.index, -30, self.signals['Strength'], 
                        where=(self.signals['Strength'] <= -30), alpha=0.3, color='red')
        ax1.set_title('訊號強度變化')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 訊號強度分布
        ax2.hist(self.signals['Strength'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax2.axvline(x=30, color='green', linestyle='--', alpha=0.7, label='買入閾值')
        ax2.axvline(x=-30, color='red', linestyle='--', alpha=0.7, label='賣出閾值')
        ax2.set_title('訊號強度分布')
        ax2.set_xlabel('訊號強度')
        ax2.set_ylabel('頻率')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"圖表已儲存至: {save_path}")
        
        plt.show()
    
    def create_dashboard(self, save_path=None):
        """創建綜合儀表板"""
        if self.data is None or self.signals is None:
            print("請先執行完整分析")
            return
        
        # 獲取最新訊號
        current_signal = self.analyzer.get_current_signal()
        summary = self.analyzer.get_signal_summary()
        
        # 創建儀表板
        fig = go.Figure()
        
        # 添加指標卡片
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=current_signal['strength'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "訊號強度"},
            delta={'reference': 0},
            gauge={
                'axis': {'range': [-100, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [-100, -30], 'color': "lightgray"},
                    {'range': [-30, 30], 'color': "yellow"},
                    {'range': [30, 100], 'color': "lightgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 30
                }
            }
        ))
        
        fig.update_layout(
            title=f'{self.analyzer.symbol} 交易訊號儀表板',
            height=400
        )
        
        if save_path:
            fig.write_html(save_path)
            print(f"儀表板已儲存至: {save_path}")
        
        fig.show()
        
        # 打印詳細資訊
        print(f"\n=== {self.analyzer.symbol} 交易訊號儀表板 ===")
        print(f"當前價格: ${current_signal['price']}")
        print(f"建議動作: {current_signal['signal']}")
        print(f"訊號強度: {current_signal['strength']}")
        print(f"\n技術指標詳情:")
        for indicator, value in current_signal['details'].items():
            print(f"  {indicator}: {value}")
        print(f"\n最近30天統計:")
        print(f"  買入訊號: {summary['buy_signals']} 次")
        print(f"  賣出訊號: {summary['sell_signals']} 次")
        print(f"  持有天數: {summary['hold_days']} 天")
        print(f"  平均強度: {summary['avg_strength']}") 

    def create_decision_chart(self, save_path=None):
        """
        創建決策導向的圖表，清楚展示為什麼會得出買入/賣出/保持的建議
        """
        if self.data is None or self.signals is None:
            print("請先執行分析")
            return
        
        # 獲取當前訊號
        current_signal = self.analyzer.get_current_signal()
        
        # 將數值轉換為字符串的映射
        signal_map = {1: "買入", -1: "賣出", 0: "持有"}
        
        # 創建子圖
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=(
                '股價趨勢與支撐阻力', 
                '技術指標決策邏輯', 
                '訊號強度與決策點',
                '綜合建議分析'
            ),
            row_width=[0.3, 0.25, 0.25, 0.2]
        )
        
        # 1. 股價趨勢與支撐阻力
        # K線圖
        fig.add_trace(
            go.Candlestick(
                x=self.data.index,
                open=self.data['Open'],
                high=self.data['High'],
                low=self.data['Low'],
                close=self.data['Close'],
                name='股價'
            ),
            row=1, col=1
        )
        
        # 移動平均線 - 趨勢判斷
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['SMA_20'],
                mode='lines',
                name='20日均線 (短期趨勢)',
                line=dict(color='orange', width=2)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['SMA_50'],
                mode='lines',
                name='50日均線 (長期趨勢)',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # 布林通道 - 支撐阻力
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['BB_Upper'],
                mode='lines',
                name='布林上軌 (阻力位)',
                line=dict(color='red', width=1, dash='dash')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['BB_Lower'],
                mode='lines',
                name='布林下軌 (支撐位)',
                line=dict(color='green', width=1, dash='dash'),
                fill='tonexty'
            ),
            row=1, col=1
        )
        
        # 2. 技術指標決策邏輯
        # RSI - 超買超賣判斷
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['RSI'],
                mode='lines',
                name='RSI (超買超賣)',
                line=dict(color='purple', width=2)
            ),
            row=2, col=1
        )
        
        # RSI 閾值線
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="超買線 (70)", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     annotation_text="超賣線 (30)", row=2, col=1)
        
        # MACD - 動量判斷
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['MACD'],
                mode='lines',
                name='MACD (動量)',
                line=dict(color='blue', width=2)
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['MACD_Signal'],
                mode='lines',
                name='MACD Signal',
                line=dict(color='red', width=1)
            ),
            row=2, col=1
        )
        
        # 3. 訊號強度與決策點
        # 訊號強度
        fig.add_trace(
            go.Scatter(
                x=self.signals.index,
                y=self.signals['Strength'],
                mode='lines+markers',
                name='綜合訊號強度',
                line=dict(color='orange', width=3),
                marker=dict(size=6)
            ),
            row=3, col=1
        )
        
        # 決策閾值
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     annotation_text="買入閾值 (30)", row=3, col=1)
        fig.add_hline(y=-30, line_dash="dash", line_color="red", 
                     annotation_text="賣出閾值 (-30)", row=3, col=1)
        fig.add_hline(y=0, line_dash="dot", line_color="black", 
                     annotation_text="中性線 (0)", row=3, col=1)
        
        # 4. 綜合建議分析 - 使用簡單的條形圖來表示決策
        # 創建決策區域
        decision_colors = {
            '買入': 'green',
            '賣出': 'red', 
            '持有': 'orange'
        }
        
        # 添加決策條形圖
        fig.add_trace(
            go.Bar(
                x=['訊號強度'],
                y=[current_signal['strength']],
                name=f"建議: {current_signal['signal']}",
                marker_color=decision_colors.get(current_signal['signal'], 'gray'),
                text=[f"{current_signal['signal']} ({current_signal['strength']:.1f})"],
                textposition='auto'
            ),
            row=4, col=1
        )
        
        # 添加閾值線
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     annotation_text="買入閾值", row=4, col=1)
        fig.add_hline(y=-30, line_dash="dash", line_color="red", 
                     annotation_text="賣出閾值", row=4, col=1)
        fig.add_hline(y=0, line_dash="dot", line_color="black", 
                     annotation_text="中性線", row=4, col=1)
        
        # 更新佈局
        fig.update_layout(
            title=f'{self.analyzer.symbol} ({self.analyzer.long_name}) - 投資決策分析',
            xaxis_rangeslider_visible=False,
            height=1200,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # 設定Y軸標題
        fig.update_layout(
            yaxis_title="股價",
            yaxis2_title="RSI",
            yaxis3_title="訊號強度",
            yaxis4_title="建議強度"
        )
        
        # 添加決策說明註解
        decision_explanation = self._get_decision_explanation(current_signal)
        
        # 創建 HTML 內容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.analyzer.symbol} 投資決策分析</title>
    <style>
        body {{
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #007bff;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 2.5em;
        }}
        .decision-card {{
            background: linear-gradient(135deg, {decision_colors.get(current_signal['signal'], '#666')} 0%, #fff 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .decision-card h2 {{
            margin: 0;
            font-size: 2em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .decision-card p {{
            margin: 10px 0;
            font-size: 1.2em;
        }}
        .explanation-section {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .explanation-section h3 {{
            color: #007bff;
            margin-bottom: 15px;
        }}
        .indicator-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .indicator-item {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }}
        .indicator-item strong {{
            color: #007bff;
        }}
        .chart-container {{
            margin: 30px 0;
            border: 1px solid #ddd;
            border-radius: 10px;
            overflow: hidden;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
        .risk-warning {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.analyzer.symbol} ({self.analyzer.long_name}) 投資決策分析</h1>
            <p>分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="decision-card">
            <h2>投資建議: {current_signal['signal']}</h2>
            <p>當前價格: ${current_signal['price']:.2f}</p>
            <p>訊號強度: {current_signal['strength']:.1f}</p>
        </div>
        
        <div class="explanation-section">
            <h3>決策邏輯說明</h3>
            <p>{decision_explanation}</p>
            
            <div class="indicator-grid">
                <div class="indicator-item">
                    <strong>移動平均線:</strong> {signal_map.get(current_signal['details']['MA_Signal'], '持有')}
                </div>
                <div class="indicator-item">
                    <strong>MACD動量:</strong> {signal_map.get(current_signal['details']['MACD_Signal'], '持有')}
                </div>
                <div class="indicator-item">
                    <strong>RSI超買超賣:</strong> {signal_map.get(current_signal['details']['RSI_Signal'], '持有')}
                </div>
                <div class="indicator-item">
                    <strong>布林通道:</strong> {signal_map.get(current_signal['details']['BB_Signal'], '持有')}
                </div>
                <div class="indicator-item">
                    <strong>隨機指標:</strong> {signal_map.get(current_signal['details']['Stoch_Signal'], '持有')}
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            {fig.to_html(full_html=False, include_plotlyjs=True)}
        </div>
        
        <div class="risk-warning">
            <strong>⚠️ 風險提醒:</strong> 本分析報告僅供學習和研究使用，不構成投資建議。
            股票投資有風險，請謹慎決策，建議結合基本面分析進行投資決策。
        </div>
        
        <div class="footer">
            <p>AIStock 股票訊號分析系統 | 生成於 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
        
        # 保存 HTML 文件
        if save_path:
            if not save_path.endswith('.html'):
                save_path += '.html'
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"決策分析報告已儲存至: {save_path}")
            return save_path
        else:
            # 生成預設檔名
            default_path = f"{self.analyzer.symbol}_decision_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(default_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"決策分析報告已儲存至: {default_path}")
            return default_path

    def _get_decision_explanation(self, current_signal):
        """
        根據當前訊號生成決策說明
        """
        signal = current_signal['signal']
        strength = current_signal['strength']
        details = current_signal['details']
        
        # 將數值轉換為字符串
        signal_map = {1: "買入", -1: "賣出", 0: "持有"}
        details_text = {}
        for key, value in details.items():
            details_text[key] = signal_map.get(value, "持有")
        
        explanations = {
            '買入': {
                'title': '🟢 買入建議',
                'reason': f'綜合訊號強度為 {strength:.1f}，超過買入閾值 30，顯示多個技術指標同時發出買入訊號。',
                'indicators': []
            },
            '賣出': {
                'title': '🔴 賣出建議', 
                'reason': f'綜合訊號強度為 {strength:.1f}，低於賣出閾值 -30，顯示多個技術指標同時發出賣出訊號。',
                'indicators': []
            },
            '持有': {
                'title': '🟡 持有建議',
                'reason': f'綜合訊號強度為 {strength:.1f}，在 -30 到 30 之間，顯示技術指標信號不明確，建議觀望。',
                'indicators': []
            }
        }
        
        # 分析各指標的貢獻
        for indicator, signal_type in details_text.items():
            if signal_type == '買入':
                explanations['買入']['indicators'].append(indicator)
            elif signal_type == '賣出':
                explanations['賣出']['indicators'].append(indicator)
            else:
                explanations['持有']['indicators'].append(indicator)
        
        # 生成詳細說明
        explanation = explanations[signal]
        indicator_text = '、'.join(explanation['indicators']) if explanation['indicators'] else '無明確訊號'
        
        # 計算加權總和以驗證
        weighted_sum = (
            details['MA_Signal'] * 20 +
            details['MACD_Signal'] * 25 +
            details['RSI_Signal'] * 20 +
            details['BB_Signal'] * 15 +
            details['Stoch_Signal'] * 20
        )
        
        return f"""
        {explanation['title']}
        
        {explanation['reason']}
        
        主要支持指標: {indicator_text}
        
        指標詳細分析:
        - 移動平均線: {details_text['MA_Signal']} (權重: 20)
        - MACD動量: {details_text['MACD_Signal']} (權重: 25)
        - RSI超買超賣: {details_text['RSI_Signal']} (權重: 20)
        - 布林通道: {details_text['BB_Signal']} (權重: 15)
        - 隨機指標: {details_text['Stoch_Signal']} (權重: 20)
        
        加權計算: {weighted_sum:.1f} (應等於總分 {strength:.1f})
        
        建議操作: 根據技術分析，當前時機適合{signal}操作。請結合市場環境、基本面分析以及個人風險承受能力做出最終投資決策。
        """ 

    def create_price_range_visualization(self, save_path=None):
        """
        創建股價範圍可視化圖表
        顯示當前股價在未來三年預估範圍內的位置
        
        Args:
            save_path: 保存路徑
        """
        left_data = self.get_left_analysis_data()
        if not left_data or 'error' in left_data:
            print("無法獲取左側分析數據")
            return None
        
        # 獲取當前股價和預估數據
        current_price = left_data['current_price']
        timeframes = left_data['timeframes']
        
        # 創建圖表
        fig, axes = plt.subplots(3, 1, figsize=(12, 15))
        fig.suptitle(f'{left_data["stock_name"]} ({left_data["symbol"]}) 股價範圍分析', 
                    fontsize=16, fontweight='bold')
        
        colors = ['#2E86AB', '#A23B72', '#F18F01']  # 藍、紫、橙
        years = ['1_year', '2_year', '3_year']
        
        for i, (year, color) in enumerate(zip(years, colors)):
            if year not in timeframes:
                continue
                
            tf_data = timeframes[year]
            target_low = tf_data.get('target_low')
            target_high = tf_data.get('target_high')
            target_mean = tf_data.get('target_mean')
            
            if not all([target_low, target_high, target_mean]):
                continue
            
            ax = axes[i]
            
            # 創建價格範圍條
            price_range = target_high - target_low
            bar_width = 0.6
            
            # 繪製價格範圍條
            ax.barh(0, price_range, height=bar_width, left=target_low, 
                   color=color, alpha=0.3, label='預估價格範圍')
            
            # 繪製平均線
            ax.axvline(x=target_mean, color=color, linestyle='--', linewidth=2, 
                      label=f'平均預估價: ${target_mean:.2f}')
            
            # 繪製當前股價位置
            current_pos = current_price
            if target_low <= current_price <= target_high:
                # 當前股價在範圍內
                ax.scatter(current_pos, 0, color='red', s=200, zorder=5, 
                          label=f'當前股價: ${current_price:.2f}')
                position_status = "在預估範圍內"
                status_color = 'green'
            elif current_price < target_low:
                # 當前股價低於範圍
                ax.scatter(current_pos, 0, color='green', s=200, zorder=5, 
                          label=f'當前股價: ${current_price:.2f} (低估)')
                position_status = "低於預估範圍 (可能低估)"
                status_color = 'green'
            else:
                # 當前股價高於範圍
                ax.scatter(current_pos, 0, color='orange', s=200, zorder=5, 
                          label=f'當前股價: ${current_price:.2f} (高估)')
                position_status = "高於預估範圍 (可能高估)"
                status_color = 'orange'
            
            # 設置圖表屬性
            ax.set_xlim(target_low * 0.9, target_high * 1.1)
            ax.set_ylim(-0.5, 0.5)
            ax.set_yticks([])
            ax.set_xlabel('股價 ($)', fontsize=12)
            ax.set_title(f'{tf_data["timeframe"]} 股價預估範圍', fontsize=14, fontweight='bold')
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3)
            
            # 添加狀態文字
            ax.text(0.02, 0.95, position_status, transform=ax.transAxes, 
                   fontsize=12, fontweight='bold', color=status_color,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
            
            # 添加詳細信息
            info_text = f"""
價格範圍: ${target_low:.2f} - ${target_high:.2f}
平均預估: ${target_mean:.2f}
預期報酬率: {tf_data.get('potential_return', 0):.2f}%
            """
            ax.text(0.02, 0.7, info_text, transform=ax.transAxes, 
                   fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.7))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"股價範圍圖表已保存: {save_path}")
        
        return fig
    
    def create_price_range_html(self, save_path=None):
        """
        創建股價範圍分析的 HTML 報告
        
        Args:
            save_path: 保存路徑
        """
        left_data = self.get_left_analysis_data()
        if not left_data or 'error' in left_data:
            return None
        
        current_price = left_data['current_price']
        timeframes = left_data['timeframes']
        
        # 生成圖表
        fig = self.create_price_range_visualization()
        if fig:
            # 將圖表轉換為 HTML
            import io
            import base64
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode()
            plt.close(fig)
        else:
            img_str = ""
        
        # 創建 HTML 內容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{left_data['stock_name']} 股價範圍分析</title>
    <style>
        body {{
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #007bff;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 2.5em;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .price-info {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .price-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            min-width: 200px;
            margin: 10px;
        }}
        .price-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .price-card .value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #007bff;
        }}
        .chart-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .timeframe-analysis {{
            margin: 20px 0;
        }}
        .timeframe-card {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .timeframe-card h3 {{
            color: #007bff;
            margin-top: 0;
        }}
        .valuation-status {{
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-weight: bold;
        }}
        .undervalued {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .overvalued {{
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .fair-value {{
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{left_data['stock_name']} 股價範圍分析</h1>
            <p>股票代碼: {left_data['symbol']} | 分析日期: {left_data['analysis_date']}</p>
        </div>
        
        <div class="summary">
            <h2>📊 分析摘要</h2>
            <div class="price-info">
                <div class="price-card">
                    <h3>當前股價</h3>
                    <div class="value">${current_price:.2f}</div>
                </div>
                <div class="price-card">
                    <h3>Forward EPS</h3>
                    <div class="value">${left_data.get('forward_eps', 0):.2f}</div>
                </div>
                <div class="price-card">
                    <h3>Forward P/E</h3>
                    <div class="value">{left_data.get('forward_pe', 0):.2f}</div>
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>📈 股價範圍可視化</h2>
            <img src="data:image/png;base64,{img_str}" alt="股價範圍圖表">
        </div>
        
        <div class="timeframe-analysis">
            <h2>📅 各時間範圍分析</h2>
        """
        
        # 添加各時間範圍的詳細分析
        for timeframe in ['1_year', '2_year', '3_year']:
            if timeframe in timeframes:
                tf_data = timeframes[timeframe]
                target_low = tf_data.get('target_low', 0)
                target_high = tf_data.get('target_high', 0)
                target_mean = tf_data.get('target_mean', 0)
                potential_return = tf_data.get('potential_return', 0)
                
                # 判斷估值狀態
                if current_price < target_low:
                    status_class = "undervalued"
                    status_text = "可能低估"
                elif current_price > target_high:
                    status_class = "overvalued"
                    status_text = "可能高估"
                else:
                    status_class = "fair-value"
                    status_text = "合理估值"
                
                html_content += f"""
            <div class="timeframe-card">
                <h3>{tf_data['timeframe']} 預估分析</h3>
                <div class="valuation-status {status_class}">
                    估值狀態: {status_text}
                </div>
                <p><strong>價格範圍:</strong> ${target_low:.2f} - ${target_high:.2f}</p>
                <p><strong>平均預估價:</strong> ${target_mean:.2f}</p>
                <p><strong>預期報酬率:</strong> {potential_return:+.2f}%</p>
                <p><strong>目標日期:</strong> {tf_data['target_date']}</p>
            </div>
                """
        
        html_content += f"""
        </div>
        
        <div class="footer">
            <p>⚠️ 免責聲明: 本分析僅供參考，不構成投資建議。投資有風險，請謹慎決策。</p>
            <p>生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"股價範圍分析報告已保存: {save_path}")
        
        return html_content
    
    def create_batch_technical_summary_chart(self, analyzers):
        """
        為批量分析創建技術分析摘要圖表
        顯示所有股票的訊號強度、建議分布等
        """
        if not analyzers:
            return None
        
        # 收集數據
        symbols = []
        strengths = []
        signals = []
        prices = []
        
        for analyzer in analyzers:
            if analyzer.data is not None and analyzer.signals is not None:
                current_signal = analyzer.get_current_signal()
                symbols.append(analyzer.symbol)
                strengths.append(current_signal['strength'])
                signals.append(current_signal['signal'])
                prices.append(current_signal['price'])
        
        if not symbols:
            return None
        
        # 創建子圖
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('訊號強度分布', '建議分布', '價格比較', '強度排序'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # 1. 訊號強度分布 (柱狀圖)
        colors = ['green' if s == '買入' else 'red' if s == '賣出' else 'orange' for s in signals]
        fig.add_trace(
            go.Bar(
                x=symbols,
                y=strengths,
                marker_color=colors,
                name='訊號強度',
                text=[f'{s:.1f}' for s in strengths],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # 2. 建議分布 (圓餅圖)
        signal_counts = {'買入': 0, '賣出': 0, '持有': 0}
        for signal in signals:
            signal_counts[signal] += 1
        
        fig.add_trace(
            go.Pie(
                labels=list(signal_counts.keys()),
                values=list(signal_counts.values()),
                marker_colors=['green', 'red', 'orange'],
                name='建議分布'
            ),
            row=1, col=2
        )
        
        # 3. 價格比較 (柱狀圖)
        fig.add_trace(
            go.Bar(
                x=symbols,
                y=prices,
                marker_color='blue',
                name='當前價格',
                text=[f'${p:.2f}' for p in prices],
                textposition='auto'
            ),
            row=2, col=1
        )
        
        # 4. 強度排序 (水平柱狀圖)
        sorted_data = sorted(zip(symbols, strengths, signals), key=lambda x: x[1], reverse=True)
        sorted_symbols = [x[0] for x in sorted_data]
        sorted_strengths = [x[1] for x in sorted_data]
        sorted_colors = ['green' if x[2] == '買入' else 'red' if x[2] == '賣出' else 'orange' for x in sorted_data]
        
        fig.add_trace(
            go.Bar(
                y=sorted_symbols,
                x=sorted_strengths,
                orientation='h',
                marker_color=sorted_colors,
                name='強度排序',
                text=[f'{s:.1f}' for s in sorted_strengths],
                textposition='auto'
            ),
            row=2, col=2
        )
        
        # 更新佈局
        fig.update_layout(
            title='批量分析 - 技術分析摘要',
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_batch_left_analysis_summary_chart(self, analyzers):
        """
        為批量分析創建左側分析摘要圖表
        顯示所有股票的估值狀態、預期報酬率等
        """
        if not analyzers:
            return None
        
        # 收集數據
        symbols = []
        current_prices = []
        target_means = []
        potential_returns = []
        valuation_statuses = []
        
        for analyzer in analyzers:
            try:
                left_data = analyze_stock(analyzer.symbol)
                if left_data and 'error' not in left_data and 'timeframes' in left_data:
                    current_price = left_data['current_price']
                    tf_data = left_data['timeframes']['1_year']
                    target_low = tf_data.get('target_low', 0)
                    target_high = tf_data.get('target_high', 0)
                    target_mean = tf_data.get('target_mean', 0)
                    potential_return = tf_data.get('potential_return', 0)
                    
                    # 判斷估值狀態
                    if current_price < target_low:
                        status = '低估'
                        status_color = 'green'
                    elif current_price > target_high:
                        status = '高估'
                        status_color = 'red'
                    else:
                        status = '合理'
                        status_color = 'orange'
                    
                    symbols.append(analyzer.symbol)
                    current_prices.append(current_price)
                    target_means.append(target_mean)
                    potential_returns.append(potential_return)
                    valuation_statuses.append(status_color)
            except:
                continue
        
        if not symbols:
            return None
        
        # 創建子圖
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('當前價格 vs 1年預估', '預期報酬率', '估值狀態分布', '價格範圍比較'),
            specs=[[{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # 1. 當前價格 vs 1年預估 (散點圖)
        fig.add_trace(
            go.Scatter(
                x=symbols,
                y=current_prices,
                mode='markers+text',
                name='當前價格',
                marker=dict(size=10, color='blue'),
                text=[f'${p:.2f}' for p in current_prices],
                textposition='top center'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=symbols,
                y=target_means,
                mode='markers+text',
                name='1年預估',
                marker=dict(size=10, color='red'),
                text=[f'${p:.2f}' for p in target_means],
                textposition='bottom center'
            ),
            row=1, col=1
        )
        
        # 2. 預期報酬率 (柱狀圖)
        colors = ['green' if r > 0 else 'red' for r in potential_returns]
        fig.add_trace(
            go.Bar(
                x=symbols,
                y=potential_returns,
                marker_color=colors,
                name='預期報酬率',
                text=[f'{r:+.1f}%' for r in potential_returns],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        # 3. 估值狀態分布 (圓餅圖)
        status_counts = {'低估': 0, '合理': 0, '高估': 0}
        for status in valuation_statuses:
            if status == 'green':
                status_counts['低估'] += 1
            elif status == 'orange':
                status_counts['合理'] += 1
            else:
                status_counts['高估'] += 1
        
        fig.add_trace(
            go.Pie(
                labels=list(status_counts.keys()),
                values=list(status_counts.values()),
                marker_colors=['green', 'orange', 'red'],
                name='估值狀態'
            ),
            row=2, col=1
        )
        
        # 4. 價格範圍比較 (柱狀圖)
        # 計算價格範圍
        price_ranges = []
        for i, symbol in enumerate(symbols):
            try:
                left_data = analyze_stock(symbol)
                if left_data and 'timeframes' in left_data:
                    tf_data = left_data['timeframes']['1_year']
                    target_low = tf_data.get('target_low', 0)
                    target_high = tf_data.get('target_high', 0)
                    price_range = target_high - target_low
                    price_ranges.append(price_range)
                else:
                    price_ranges.append(0)
            except:
                price_ranges.append(0)
        
        fig.add_trace(
            go.Bar(
                x=symbols,
                y=price_ranges,
                marker_color='purple',
                name='價格範圍',
                text=[f'${r:.2f}' for r in price_ranges],
                textposition='auto'
            ),
            row=2, col=2
        )
        
        # 更新佈局
        fig.update_layout(
            title='批量分析 - 左側分析摘要',
            height=600,
            showlegend=False
        )
        
        return fig
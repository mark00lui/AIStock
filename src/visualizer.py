import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime

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
        
    def create_batch_html_report(self, analyzers, save_path=None):
        """
        為多支股票創建綜合 HTML 報告，包含決策邏輯和指標貢獻分析
        所有內容都在單一 HTML 文件中，使用可折疊式設計
        
        Args:
            analyzers: StockAnalyzer 實例列表
            save_path: 保存路徑
        """
        if not analyzers:
            print("沒有分析器數據")
            return
        
        # 獲取所有股票的當前訊號
        all_results = []
        for analyzer in analyzers:
            if analyzer.data is not None and analyzer.signals is not None:
                current_signal = analyzer.get_current_signal()
                summary = analyzer.get_signal_summary()
                all_results.append({
                    'symbol': analyzer.symbol,
                    'signal': current_signal,
                    'summary': summary,
                    'analyzer': analyzer
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
        
        # 將數值轉換為字符串的映射
        signal_map = {1: "買入", -1: "賣出", 0: "持有"}
        
        # 創建 HTML 內容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>批量股票分析報告</title>
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
        .header p {{
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 1.2em;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .signal-buy {{
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        }}
        .signal-sell {{
            background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);
        }}
        .signal-hold {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .stock-section {{
            margin: 40px 0;
            border: 2px solid #007bff;
            border-radius: 15px;
            overflow: hidden;
        }}
        .stock-header {{
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .stock-header:hover {{
            background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
        }}
        .stock-header h2 {{
            margin: 0;
            font-size: 1.8em;
        }}
        .stock-header .toggle-icon {{
            font-size: 1.5em;
            transition: transform 0.3s;
        }}
        .stock-content {{
            display: none;
            padding: 30px;
            background-color: #f8f9fa;
        }}
        .stock-content.active {{
            display: block;
        }}
        .stock-summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stock-summary-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .stock-summary-card h4 {{
            margin: 0 0 10px 0;
            color: #007bff;
            font-size: 1em;
        }}
        .stock-summary-card .value {{
            font-size: 1.5em;
            font-weight: bold;
            margin: 5px 0;
        }}
        .details-section {{
            margin: 20px 0;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
        }}
        .details-section h3 {{
            color: #007bff;
            margin-bottom: 15px;
        }}
        .details-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
        }}
        .detail-item {{
            background-color: #f8f9fa;
            padding: 12px;
            border-radius: 5px;
            border-left: 3px solid #007bff;
        }}
        .detail-item strong {{
            color: #007bff;
        }}
        .chart-container {{
            margin: 30px 0;
            border: 1px solid #ddd;
            border-radius: 10px;
            overflow: hidden;
            background-color: white;
        }}
        .decision-section {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .decision-section h3 {{
            color: #007bff;
            margin-bottom: 15px;
        }}
        .indicator-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
        .controls {{
            text-align: center;
            margin: 20px 0;
        }}
        .btn {{
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin: 0 10px;
            transition: all 0.3s;
        }}
        .btn:hover {{
            background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
            transform: translateY(-2px);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>批量股票分析報告</h1>
            <p>分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 共分析 {len(analyzers)} 支股票</p>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="toggleAllCharts()">展開/收合所有圖表</button>
        </div>
        
        <div class="summary-grid">
"""
        
        # 添加總體摘要卡片
        for result in all_results:
            analyzer = result['analyzer']
            current_signal = result['signal']
            
            html_content += f"""
            <div class="summary-card signal-{current_signal['signal'].lower()}">
                <h3>{analyzer.symbol}</h3>
                <div class="value">{analyzer.long_name}</div>
                <p>建議: {current_signal['signal']}</p>
                <p>強度: {current_signal['strength']:.1f}</p>
            </div>
"""
        
        html_content += """
        </div>
"""
        
        # 為每個股票創建可折疊的圖表和決策分析
        for i, result in enumerate(all_results):
            analyzer = result['analyzer']
            current_signal = result['signal']
            
            # 獲取決策說明
            decision_explanation = self._get_decision_explanation(current_signal)
            
            # 創建該股票的決策圖表
            stock_fig = make_subplots(
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
            stock_fig.add_trace(
                go.Candlestick(
                    x=analyzer.data.index,
                    open=analyzer.data['Open'],
                    high=analyzer.data['High'],
                    low=analyzer.data['Low'],
                    close=analyzer.data['Close'],
                    name='股價'
                ),
                row=1, col=1
            )
            
            stock_fig.add_trace(
                go.Scatter(
                    x=analyzer.data.index,
                    y=analyzer.data['SMA_20'],
                    mode='lines',
                    name='20日均線 (短期趨勢)',
                    line=dict(color='orange', width=2)
                ),
                row=1, col=1
            )
            
            stock_fig.add_trace(
                go.Scatter(
                    x=analyzer.data.index,
                    y=analyzer.data['SMA_50'],
                    mode='lines',
                    name='50日均線 (長期趨勢)',
                    line=dict(color='blue', width=2)
                ),
                row=1, col=1
            )
            
            stock_fig.add_trace(
                go.Scatter(
                    x=analyzer.data.index,
                    y=analyzer.data['BB_Upper'],
                    mode='lines',
                    name='布林上軌 (阻力位)',
                    line=dict(color='red', width=1, dash='dash')
                ),
                row=1, col=1
            )
            
            stock_fig.add_trace(
                go.Scatter(
                    x=analyzer.data.index,
                    y=analyzer.data['BB_Lower'],
                    mode='lines',
                    name='布林下軌 (支撐位)',
                    line=dict(color='green', width=1, dash='dash'),
                    fill='tonexty'
                ),
                row=1, col=1
            )
            
            # 2. 技術指標決策邏輯
            stock_fig.add_trace(
                go.Scatter(
                    x=analyzer.data.index,
                    y=analyzer.data['RSI'],
                    mode='lines',
                    name='RSI (超買超賣)',
                    line=dict(color='purple', width=2)
                ),
                row=2, col=1
            )
            
            stock_fig.add_hline(y=70, line_dash="dash", line_color="red", 
                             annotation_text="超買線 (70)", row=2, col=1)
            stock_fig.add_hline(y=30, line_dash="dash", line_color="green", 
                             annotation_text="超賣線 (30)", row=2, col=1)
            
            # 3. 訊號強度與決策點
            stock_fig.add_trace(
                go.Scatter(
                    x=analyzer.signals.index,
                    y=analyzer.signals['Strength'],
                    mode='lines+markers',
                    name='綜合訊號強度',
                    line=dict(color='orange', width=3),
                    marker=dict(size=6)
                ),
                row=3, col=1
            )
            
            stock_fig.add_hline(y=30, line_dash="dash", line_color="green", 
                             annotation_text="買入閾值 (30)", row=3, col=1)
            stock_fig.add_hline(y=-30, line_dash="dash", line_color="red", 
                             annotation_text="賣出閾值 (-30)", row=3, col=1)
            stock_fig.add_hline(y=0, line_dash="dot", line_color="black", 
                             annotation_text="中性線 (0)", row=3, col=1)
            
            # 4. 綜合建議分析 - 使用簡單的條形圖來表示決策
            # 創建決策區域
            decision_colors = {
                '買入': 'green',
                '賣出': 'red', 
                '持有': 'orange'
            }
            
            # 添加決策條形圖
            stock_fig.add_trace(
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
            stock_fig.add_hline(y=30, line_dash="dash", line_color="green", 
                             annotation_text="買入閾值", row=4, col=1)
            stock_fig.add_hline(y=-30, line_dash="dash", line_color="red", 
                             annotation_text="賣出閾值", row=4, col=1)
            stock_fig.add_hline(y=0, line_dash="dot", line_color="black", 
                             annotation_text="中性線", row=4, col=1)
            
            # 更新佈局
            stock_fig.update_layout(
                title=f'{current_signal["symbol"]} ({current_signal["long_name"]}) - 投資決策分析',
                xaxis_rangeslider_visible=False,
                height=800,
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
            stock_fig.update_layout(
                yaxis_title="股價",
                yaxis2_title="RSI",
                yaxis3_title="訊號強度",
                yaxis4_title="建議強度"
            )
            
            # 添加決策說明註解
            decision_explanation = self._get_decision_explanation(current_signal)
            
            # 創建 HTML 內容
            html_content += f"""
            <div class="collapsible-chart" id="chart-{i}">
                <div class="chart-header" onclick="toggleChart({i})">
                    <h3>{current_signal['symbol']} ({current_signal['long_name']}) - 投資決策分析</h3>
                    <button class="chart-toggle" id="toggle-{i}">▼</button>
                </div>
                <div class="chart-content" id="content-{i}">
                    <div class="decision-section">
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
                        {stock_fig.to_html(full_html=False, include_plotlyjs=True)}
                    </div>
                </div>
            </div>
        </div>
"""
        
        # 添加頁腳和JavaScript
        html_content += f"""
        <div class="risk-warning">
            <strong>⚠️ 風險提醒:</strong> 本分析報告僅供學習和研究使用，不構成投資建議。
            股票投資有風險，請謹慎決策，建議結合基本面分析進行投資決策。
        </div>
        
        <div class="footer">
            <p>AIStock 股票訊號分析系統 | 生成於 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        function toggleChart(chartId) {{
            const content = document.getElementById('content-' + chartId);
            const header = document.getElementById('chart-' + chartId);
            const icon = header.querySelector('.chart-toggle');
            
            if (content.style.display === 'none' || content.style.display === '') {{
                content.style.display = 'block';
                icon.textContent = '▲';
            }} else {{
                content.style.display = 'none';
                icon.textContent = '▼';
            }}
        }}
        
        function toggleAllCharts() {{
            const contents = document.querySelectorAll('.chart-content');
            const icons = document.querySelectorAll('.chart-toggle');
            
            const allVisible = Array.from(contents).every(content => 
                content.style.display !== 'none' && content.style.display !== ''
            );
            
            contents.forEach((content, index) => {{
                if (allVisible) {{
                    content.style.display = 'none';
                    icons[index].textContent = '▼';
                }} else {{
                    content.style.display = 'block';
                    icons[index].textContent = '▲';
                }}
            }});
        }}
    </script>
</body>
</html>
"""
        
        # 保存 HTML 文件
        if save_path:
            if not save_path.endswith('.html'):
                save_path += '.html'
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"批量分析報告已儲存至: {save_path}")
            return save_path
        else:
            # 生成預設檔名
            symbols_str = '_'.join([r['analyzer'].symbol for r in all_results])
            default_path = f"batch_analysis_{symbols_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(default_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"批量分析報告已儲存至: {default_path}")
            return default_path

    def create_comprehensive_html_report(self, save_path=None):
        """
        創建綜合 HTML 報告，包含所有圖表和數據
        所有內容都在單一 HTML 文件中，不使用圖片
        """
        if self.data is None or self.signals is None:
            print("請先執行分析")
            return
        
        # 獲取當前訊號和摘要
        current_signal = self.analyzer.get_current_signal()
        summary = self.analyzer.get_signal_summary()
        
        # 創建綜合圖表
        fig = make_subplots(
            rows=7, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(
                '股價與交易訊號', 
                '成交量', 
                'MACD', 
                'RSI', 
                '隨機指標',
                '訊號強度',
                '技術指標綜合分析'
            ),
            row_width=[0.20, 0.12, 0.12, 0.12, 0.12, 0.12, 0.20]
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
                marker_color='gray',
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
                line=dict(color='blue', width=2)
            ),
            row=6, col=1
        )
        
        # 訊號強度閾值線
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=6, col=1)
        fig.add_hline(y=-30, line_dash="dash", line_color="red", row=6, col=1)
        fig.add_hline(y=0, line_dash="dot", line_color="black", row=6, col=1)
        
        # 7. 技術指標綜合分析 - 將股價、RSI、MACD、布林通道疊加顯示
        # 股價（左軸）
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['Close'],
                mode='lines',
                name='股價',
                line=dict(color='black', width=2),
                yaxis='y7'
            ),
            row=7, col=1
        )
        
        # RSI（右軸1）
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=1),
                yaxis='y8'
            ),
            row=7, col=1
        )
        
        # MACD（右軸2）
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='blue', width=1),
                yaxis='y9'
            ),
            row=7, col=1
        )
        
        # 布林通道上軌
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['BB_Upper'],
                mode='lines',
                name='布林上軌',
                line=dict(color='gray', width=1, dash='dash'),
                yaxis='y7'
            ),
            row=7, col=1
        )
        
        # 布林通道下軌
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['BB_Lower'],
                mode='lines',
                name='布林下軌',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                yaxis='y7'
            ),
            row=7, col=1
        )
        
        # 訊號強度（右軸3）
        fig.add_trace(
            go.Scatter(
                x=self.signals.index,
                y=self.signals['Strength'],
                mode='lines',
                name='訊號強度',
                line=dict(color='orange', width=2),
                yaxis='y10'
            ),
            row=7, col=1
        )
        
        # 添加閾值線 - 修正版本，使用 add_shape 而不是 add_hline
        # RSI 超買超賣線
        fig.add_shape(
            type="line",
            x0=self.data.index[0], x1=self.data.index[-1],
            y0=70, y1=70,
            line=dict(color="red", width=1, dash="dash"),
            yref="y8"
        )
        fig.add_shape(
            type="line",
            x0=self.data.index[0], x1=self.data.index[-1],
            y0=30, y1=30,
            line=dict(color="green", width=1, dash="dash"),
            yref="y8"
        )
        
        # 訊號強度閾值線
        fig.add_shape(
            type="line",
            x0=self.signals.index[0], x1=self.signals.index[-1],
            y0=30, y1=30,
            line=dict(color="green", width=1, dash="dash"),
            yref="y10"
        )
        fig.add_shape(
            type="line",
            x0=self.signals.index[0], x1=self.signals.index[-1],
            y0=-30, y1=-30,
            line=dict(color="red", width=1, dash="dash"),
            yref="y10"
        )
        
        # 更新佈局
        fig.update_layout(
            title=f'{self.analyzer.symbol} 綜合技術分析報告',
            xaxis_rangeslider_visible=False,
            height=1400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # 設定多個Y軸 - 修正版本
        fig.update_layout(
            yaxis7=dict(title="股價", side="left"),
            yaxis8=dict(title="RSI", side="right", overlaying="y7"),
            yaxis9=dict(title="MACD", side="right", overlaying="y7"),
            yaxis10=dict(title="訊號強度", side="right", overlaying="y7")
        )
        
        # 創建 HTML 內容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.analyzer.symbol} 股票分析報告</title>
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
        .header p {{
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 1.2em;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .signal-buy {{
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        }}
        .signal-sell {{
            background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);
        }}
        .signal-hold {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .details-section {{
            margin: 30px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
        }}
        .details-section h3 {{
            color: #007bff;
            margin-bottom: 15px;
        }}
        .details-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .detail-item {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }}
        .detail-item strong {{
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
            <h1>{self.analyzer.symbol} ({self.analyzer.long_name}) 股票分析報告</h1>
            <p>生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>股票代碼</h3>
                <div class="value">{self.analyzer.symbol}</div>
            </div>
            <div class="summary-card">
                <h3>股票名稱</h3>
                <div class="value">{self.analyzer.long_name}</div>
            </div>
            <div class="summary-card signal-{current_signal['signal'].lower()}">
                <h3>當前價格</h3>
                <div class="value">${current_signal['price']:.2f}</div>
            </div>
            <div class="summary-card signal-{current_signal['signal'].lower()}">
                <h3>建議動作</h3>
                <div class="value">{current_signal['signal']}</div>
            </div>
            <div class="summary-card signal-{current_signal['signal'].lower()}">
                <h3>訊號強度</h3>
                <div class="value">{current_signal['strength']:.1f}</div>
            </div>
            <div class="summary-card">
                <h3>分析期間</h3>
                <div class="value">{self.analyzer.period}</div>
            </div>
        </div>
        
        <div class="details-section">
            <h3>技術指標詳情</h3>
            <div class="details-grid">
                <div class="detail-item">
                    <strong>移動平均線訊號:</strong> {current_signal['details']['MA_Signal']}
                </div>
                <div class="detail-item">
                    <strong>MACD訊號:</strong> {current_signal['details']['MACD_Signal']}
                </div>
                <div class="detail-item">
                    <strong>RSI訊號:</strong> {current_signal['details']['RSI_Signal']}
                </div>
                <div class="detail-item">
                    <strong>布林通道訊號:</strong> {current_signal['details']['BB_Signal']}
                </div>
                <div class="detail-item">
                    <strong>隨機指標訊號:</strong> {current_signal['details']['Stoch_Signal']}
                </div>
            </div>
        </div>
        
        <div class="details-section">
            <h3>最近30天統計</h3>
            <div class="details-grid">
                <div class="detail-item">
                    <strong>買入訊號:</strong> {summary['buy_signals']} 次
                </div>
                <div class="detail-item">
                    <strong>賣出訊號:</strong> {summary['sell_signals']} 次
                </div>
                <div class="detail-item">
                    <strong>持有天數:</strong> {summary['hold_days']} 天
                </div>
                <div class="detail-item">
                    <strong>平均強度:</strong> {summary['avg_strength']}
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
            
            print(f"綜合報告已儲存至: {save_path}")
            return save_path
        else:
            # 生成預設檔名
            default_path = f"{self.analyzer.symbol}_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(default_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"綜合報告已儲存至: {default_path}")
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
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import seaborn as sns

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
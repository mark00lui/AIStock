import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class StockAnalyzer:
    def __init__(self, symbol, period='1y'):
        """
        初始化股票分析器
        
        Args:
            symbol (str): 股票代碼 (例如: 'AAPL', '2330.TW')
            period (str): 資料期間 ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        """
        self.symbol = symbol
        self.period = period
        self.data = None
        self.signals = None
        self.long_name = None  # 股票原始名稱
        
    def fetch_data(self):
        """獲取股票資料"""
        try:
            ticker = yf.Ticker(self.symbol)
            
            # 獲取股票資訊
            info = ticker.info
            if info and 'longName' in info and info['longName']:
                self.long_name = info['longName']
            elif info and 'shortName' in info and info['shortName']:
                self.long_name = info['shortName']
            else:
                self.long_name = self.symbol  # 如果無法獲取名稱，使用股票代碼
            
            # 獲取歷史資料
            self.data = ticker.history(period=self.period)
            
            if self.data is None or len(self.data) == 0:
                print(f"無法獲取 {self.symbol} 的資料，請檢查股票代碼是否正確")
                return False
            
            print(f"成功獲取 {self.symbol} ({self.long_name}) 的資料，共 {len(self.data)} 筆記錄")
            return True
        except Exception as e:
            print(f"獲取資料失敗: {e}")
            self.long_name = self.symbol  # 發生錯誤時使用股票代碼
            return False
    
    def calculate_technical_indicators(self):
        """計算技術指標"""
        if self.data is None or len(self.data) == 0:
            print("請先獲取股票資料")
            return
        
        df = self.data.copy()
        
        # 檢查數據是否足夠
        if len(df) < 50:
            print(f"數據不足，只有 {len(df)} 筆記錄，需要至少 50 筆")
            return
        
        try:
            # 移動平均線
            df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
            df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
            df['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
            df['EMA_26'] = ta.trend.ema_indicator(df['Close'], window=26)
            
            # MACD
            df['MACD'] = ta.trend.macd_diff(df['Close'])
            df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])
            df['MACD_Histogram'] = ta.trend.macd_diff(df['Close'])
            
            # RSI
            df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
            
            # 布林通道
            df['BB_Upper'] = ta.volatility.bollinger_hband(df['Close'])
            df['BB_Lower'] = ta.volatility.bollinger_lband(df['Close'])
            df['BB_Middle'] = ta.volatility.bollinger_mavg(df['Close'])
            
            # 隨機指標
            df['Stoch_K'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])
            df['Stoch_D'] = ta.momentum.stoch_signal(df['High'], df['Low'], df['Close'])
            
            # 成交量指標 (使用簡單移動平均)
            df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
            
            # ATR (平均真實範圍)
            df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])
            
            self.data = df
            print("技術指標計算完成")
        except Exception as e:
            print(f"計算技術指標時發生錯誤: {e}")
            return
    
    def generate_signals(self):
        """生成買賣訊號"""
        if self.data is None:
            print("請先計算技術指標")
            return
        
        df = self.data.copy()
        signals = pd.DataFrame(index=df.index)
        signals['Price'] = df['Close']
        signals['Signal'] = 0  # 0: 持有, 1: 買入, -1: 賣出
        signals['Strength'] = 0  # 訊號強度 (-100 到 100)
        
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
        
        # 綜合訊號強度計算
        for i in range(len(signals)):
            strength = 0
            strength += signals.iloc[i]['MA_Signal'] * 20
            strength += signals.iloc[i]['MACD_Signal'] * 25
            strength += signals.iloc[i]['RSI_Signal'] * 20
            strength += signals.iloc[i]['BB_Signal'] * 15
            strength += signals.iloc[i]['Stoch_Signal'] * 20
            
            signals.iloc[i, signals.columns.get_loc('Strength')] = strength
            
            # 根據強度決定最終訊號
            if strength >= 20:  # 降低買入閾值
                signals.iloc[i, signals.columns.get_loc('Signal')] = 1
            elif strength <= -20:  # 降低賣出閾值
                signals.iloc[i, signals.columns.get_loc('Signal')] = -1
        
        self.signals = signals
        print("訊號生成完成")
    
    def get_current_signal(self):
        """獲取最新的交易訊號"""
        if self.signals is None:
            print("請先生成訊號")
            return None
        
        latest = self.signals.iloc[-1]
        signal_map = {1: "買入", -1: "賣出", 0: "持有"}
        
        return {
            'symbol': self.symbol,
            'long_name': self.long_name,
            'date': latest.name.strftime('%Y-%m-%d'),
            'price': round(latest['Price'], 2),
            'signal': signal_map[latest['Signal']],
            'strength': latest['Strength'],
            'details': {
                'MA_Signal': latest['MA_Signal'],
                'MACD_Signal': latest['MACD_Signal'],
                'RSI_Signal': latest['RSI_Signal'],
                'BB_Signal': latest['BB_Signal'],
                'Stoch_Signal': latest['Stoch_Signal']
            }
        }
    
    def get_signal_summary(self, days=30):
        """獲取最近幾天的訊號摘要"""
        if self.signals is None:
            print("請先生成訊號")
            return None
        
        recent_signals = self.signals.tail(days)
        buy_signals = recent_signals[recent_signals['Signal'] == 1]
        sell_signals = recent_signals[recent_signals['Signal'] == -1]
        
        return {
            'total_days': len(recent_signals),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'hold_days': len(recent_signals) - len(buy_signals) - len(sell_signals),
            'avg_strength': round(recent_signals['Strength'].mean(), 2)
        }
    
    def run_analysis(self):
        """執行完整分析流程"""
        print(f"開始分析 {self.symbol}...")
        
        if not self.fetch_data():
            return False
        
        self.calculate_technical_indicators()
        self.generate_signals()
        
        current_signal = self.get_current_signal()
        summary = self.get_signal_summary()
        
        print("\n=== 分析結果 ===")
        print(f"股票代碼: {self.symbol}")
        print(f"股票名稱: {self.long_name}")
        print(f"當前價格: ${current_signal['price']}")
        print(f"建議動作: {current_signal['signal']}")
        print(f"訊號強度: {current_signal['strength']}")
        
        return True 
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
import warnings
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
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
        
        # 設置重試策略
        self._setup_retry_strategy()
        
    def _setup_retry_strategy(self):
        """設置重試策略"""
        # 創建一個 session 並設置重試策略
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 注意: yfinance 會自動使用系統的 requests session
        
    def fetch_data(self):
        """獲取股票資料"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f"嘗試獲取 {self.symbol} 資料 (第 {attempt + 1} 次)...")
                
                # 創建 ticker 對象
                ticker = yf.Ticker(self.symbol)
                
                # 獲取股票資訊
                try:
                    info = ticker.info
                    if info and 'longName' in info and info['longName']:
                        self.long_name = info['longName']
                    elif info and 'shortName' in info and info['shortName']:
                        self.long_name = info['shortName']
                    else:
                        self.long_name = self.symbol  # 如果無法獲取名稱，使用股票代碼
                except Exception as info_error:
                    print(f"獲取股票資訊失敗: {info_error}")
                    self.long_name = self.symbol
                
                # 獲取歷史資料
                print(f"正在下載 {self.symbol} 的歷史資料 (期間: {self.period})...")
                self.data = ticker.history(period=self.period)
                
                if self.data is None or len(self.data) == 0:
                    print(f"無法獲取 {self.symbol} 的資料，請檢查股票代碼是否正確")
                    if attempt < max_retries - 1:
                        print(f"等待 {retry_delay} 秒後重試...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指數退避
                        continue
                    return False
                
                # 檢查數據質量
                if len(self.data) < 20:
                    print(f"警告: {self.symbol} 只有 {len(self.data)} 筆記錄，可能數據不足")
                
                print(f"成功獲取 {self.symbol} ({self.long_name}) 的資料，共 {len(self.data)} 筆記錄")
                print(f"資料期間: {self.data.index[0].strftime('%Y-%m-%d')} 到 {self.data.index[-1].strftime('%Y-%m-%d')}")
                print(f"最新收盤價: ${self.data['Close'].iloc[-1]:.2f}")
                
                return True
                
            except Exception as e:
                error_msg = str(e)
                print(f"獲取 {self.symbol} 資料失敗 (第 {attempt + 1} 次): {error_msg}")
                
                # 針對特定錯誤提供更詳細的診斷
                if "possibly delisted" in error_msg.lower():
                    print(f"  → {self.symbol} 可能已退市或暫停交易")
                elif "expecting value" in error_msg.lower():
                    print(f"  → {self.symbol} API 回應格式錯誤，可能是網路問題或服務暫時不可用")
                elif "timeout" in error_msg.lower():
                    print(f"  → {self.symbol} 請求超時，可能是網路連接問題")
                elif "connection" in error_msg.lower():
                    print(f"  → {self.symbol} 連接失敗，可能是網路問題")
                
                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒後重試...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指數退避
                else:
                    print(f"已重試 {max_retries} 次，放棄獲取 {self.symbol} 的資料")
                    self.long_name = self.symbol
                    return False
        
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
            df['SMA_120'] = ta.trend.sma_indicator(df['Close'], window=120)
            df['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
            df['EMA_26'] = ta.trend.ema_indicator(df['Close'], window=26)
            
            # MACD
            macd_indicator = ta.trend.MACD(df['Close'])
            df['MACD'] = macd_indicator.macd()
            df['MACD_Signal'] = macd_indicator.macd_signal()
            df['MACD_Histogram'] = macd_indicator.macd_diff()
            
            # RSI
            df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
            
            # 布林通道
            bb_indicator = ta.volatility.BollingerBands(df['Close'])
            df['BB_Upper'] = bb_indicator.bollinger_hband()
            df['BB_Lower'] = bb_indicator.bollinger_lband()
            df['BB_Middle'] = bb_indicator.bollinger_mavg()
            
            # 隨機指標
            stoch_indicator = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
            df['Stoch_K'] = stoch_indicator.stoch()
            df['Stoch_D'] = stoch_indicator.stoch_signal()
            
            # 成交量指標 (使用簡單移動平均)
            df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
            
            # ATR (平均真實範圍)
            df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
            
            # 檢查計算結果
            technical_columns = ['SMA_20', 'SMA_50', 'SMA_120', 'BB_Upper', 'BB_Lower', 'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram']
            for col in technical_columns:
                if col in df.columns:
                    nan_count = df[col].isna().sum()
                    if nan_count > 0:
                        print(f"警告: {col} 有 {nan_count} 個NaN值")
            
            self.data = df
            print("技術指標計算完成")
        except Exception as e:
            print(f"計算技術指標時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return
    
    def calculate_volatility_and_beta(self):
        """計算波動率和Beta值"""
        if self.data is None or len(self.data) == 0:
            print("請先獲取股票資料")
            return None
        
        try:
            # 計算股票日收益率
            stock_returns = self.data['Close'].pct_change().dropna()
            
            # 根據股票代碼確定對應的市場指數
            market_symbol = self._get_market_index()
            if market_symbol is None:
                print(f"無法確定 {self.symbol} 對應的市場指數")
                return None
            
            # 獲取市場指數數據 - 使用與股票相同的時間區間
            print(f"正在獲取市場指數 {market_symbol} 的數據...")
            
            # 計算時間範圍 - 使用字符串格式避免時區問題，並忽略最後一天
            start_date = self.data.index[0].strftime('%Y-%m-%d')
            # 忽略最後一天，避免大盤指數結算時間差異
            end_date = self.data.index[-2].strftime('%Y-%m-%d') if len(self.data) > 1 else self.data.index[-1].strftime('%Y-%m-%d')
            
            # 使用具體的日期範圍而不是 period
            market_data = yf.download(market_symbol, start=start_date, end=end_date, progress=False)
            if market_data is None or len(market_data) == 0:
                print(f"無法獲取市場指數 {market_symbol} 的數據")
                return None
            
            print(f"股票數據期間: {start_date} 到 {end_date}")
            print(f"市場指數數據期間: {market_data.index[0].strftime('%Y-%m-%d')} 到 {market_data.index[-1].strftime('%Y-%m-%d')}")
            
            # 計算市場日收益率
            market_returns = market_data['Close'].pct_change().dropna()
            
            # 對齊數據 - 以大盤指數為準
            print(f"對齊前 - 股票交易日數: {len(stock_returns)}, 市場指數交易日數: {len(market_returns)}")
            
            # 以大盤指數的日期為準，對齊股票數據
            market_dates = market_returns.index.strftime('%Y-%m-%d')
            stock_dates = stock_returns.index.strftime('%Y-%m-%d')
            
            # 找到股票數據中與大盤指數日期匹配的數據
            matching_stock_dates = set(stock_dates) & set(market_dates)
            print(f"大盤指數日期數: {len(market_dates)}")
            print(f"股票與大盤匹配的日期數: {len(matching_stock_dates)}")
            
            if len(matching_stock_dates) < 30:
                print(f"匹配的日期不足，只有 {len(matching_stock_dates)} 個交易日")
                return None
            
            # 以大盤指數的日期為準，重新索引股票數據
            stock_returns_aligned = stock_returns[stock_returns.index.strftime('%Y-%m-%d').isin(market_dates)]
            market_returns_aligned = market_returns  # 大盤數據保持不變
            
            # 確保數據按日期排序
            stock_returns_aligned = stock_returns_aligned.sort_index()
            market_returns_aligned = market_returns_aligned.sort_index()
            
            # 最終對齊檢查 - 使用更保險的方法
            # 將兩個Series的索引轉換為字符串格式進行比較
            stock_dates_str = stock_returns_aligned.index.strftime('%Y-%m-%d')
            market_dates_str = market_returns_aligned.index.strftime('%Y-%m-%d')
            
            # 找到共同的日期字符串
            common_date_strings = set(stock_dates_str) & set(market_dates_str)
            if len(common_date_strings) < 30:
                print(f"共同日期不足，只有 {len(common_date_strings)} 個交易日")
                return None
            
            # 使用共同日期字符串重新索引
            stock_returns_final = stock_returns_aligned[stock_returns_aligned.index.strftime('%Y-%m-%d').isin(common_date_strings)]
            market_returns_final = market_returns_aligned[market_returns_aligned.index.strftime('%Y-%m-%d').isin(common_date_strings)]
            
            # 確保數據按日期排序
            stock_returns_final = stock_returns_final.sort_index()
            market_returns_final = market_returns_final.sort_index()
            
            # 最終長度檢查
            final_length = min(len(stock_returns_final), len(market_returns_final))
            if final_length < 30:
                print(f"最終對齊後數據不足，只有 {final_length} 個交易日")
                return None
            
            # 截取到相同長度
            stock_returns_final = stock_returns_final.head(final_length)
            market_returns_final = market_returns_final.head(final_length)
            
            print(f"最終對齊 - 股票數據: {len(stock_returns_final)}, 市場數據: {len(market_returns_final)}")
            
            # 使用對齊後的數據
            stock_returns = stock_returns_final
            market_returns = market_returns_final
            
            # 計算年化波動率
            volatility = float(stock_returns.std() * np.sqrt(252) * 100)
            
            # 計算Beta值 - 使用更保險的方法
            try:
                # 轉換為NumPy數組並確保是1D數組
                stock_array = stock_returns.values.flatten()
                market_array = market_returns.values.flatten()
                
                # 確保數組長度一致
                if len(stock_array) != len(market_array):
                    print(f"數組長度不匹配: 股票 {len(stock_array)}, 市場 {len(market_array)}")
                    return None
                
                # 檢查數組維度
                if stock_array.ndim != 1 or market_array.ndim != 1:
                    print(f"數組維度錯誤: 股票 {stock_array.ndim}D, 市場 {market_array.ndim}D")
                    return None
                
                # 使用NumPy直接計算協方差和方差，避免時區問題
                covariance = np.cov(stock_array, market_array)[0, 1]
                market_variance = np.var(market_array)
                
                if market_variance == 0:
                    print("市場方差為零，無法計算Beta")
                    return None
                    
                beta = float(covariance / market_variance)
            except Exception as beta_error:
                print(f"Beta計算錯誤: {beta_error}")
                return None
            
            # 計算相關係數 - 使用NumPy
            try:
                correlation = float(np.corrcoef(stock_array, market_array)[0, 1])
            except Exception as corr_error:
                print(f"相關係數計算錯誤: {corr_error}")
                correlation = 0.0
            
            # 計算年化報酬率
            annual_return = float(stock_returns.mean() * 252 * 100)
            market_annual_return = float(market_returns.mean() * 252 * 100)
            
            # 計算夏普比率 (假設無風險利率5%)
            risk_free_rate = 0.05
            sharpe_ratio = float((stock_returns.mean() * 252 - risk_free_rate) / (stock_returns.std() * np.sqrt(252)))
            
            # 風險評估
            risk_level = self._assess_risk_level(volatility, beta)
            beta_risk = self._assess_beta_risk(beta)
            
            return {
                'volatility': volatility,
                'beta': beta,
                'correlation': correlation,
                'annual_return': annual_return,
                'market_annual_return': market_annual_return,
                'sharpe_ratio': sharpe_ratio,
                'risk_level': risk_level,
                'beta_risk': beta_risk,
                'market_symbol': market_symbol,
                'data_points': len(matching_stock_dates)
            }
            
        except Exception as e:
            print(f"計算波動率和Beta時發生錯誤: {e}")
            return None
    
    def _get_market_index(self):
        """根據股票代碼確定對應的市場指數"""
        if self.symbol.endswith('.TW') or self.symbol.endswith('.TWO'):
            # 台灣加權指數 - 嘗試不同的代碼
            return '^TWII'  # 台灣加權指數 (不使用^符號)
        elif self.symbol.endswith('.HK'):
            return '^HSI'   # 恒生指數
        elif self.symbol.endswith('.T'):
            return '^N225'  # 日經225指數
        elif self.symbol.endswith('.L'):
            return '^FTSE'  # 英國富時100指數
        elif self.symbol.endswith('.TO'):
            return '^GSPTSE'  # 加拿大S&P/TSX指數
        elif self.symbol.endswith('.AX'):
            return '^AXJO'  # 澳洲S&P/ASX 200指數
        elif self.symbol.endswith('.DE'):
            return '^GDAXI'  # 德國DAX指數
        elif self.symbol.endswith('.PA'):
            return '^FCHI'  # 法國CAC 40指數
        else:
            # 所有其他股票（包括美股如 TSM, AAPL, NVDA 等）都使用 SPY
            return 'SPY'    # 美股SPY
    
    def _assess_risk_level(self, volatility, beta):
        """評估風險等級"""
        if volatility >= 60:
            return '極高風險'
        elif volatility >= 40:
            return '高風險'
        elif volatility >= 25:
            return '中等風險'
        elif volatility >= 15:
            return '低風險'
        else:
            return '極低風險'
    
    def _assess_beta_risk(self, beta):
        """評估Beta風險"""
        if beta >= 1.5:
            return '高Beta (市場敏感度高)'
        elif beta >= 1.0:
            return '中等Beta (略高於市場)'
        elif beta >= 0.5:
            return '低Beta (相對穩定)'
        else:
            return '極低Beta (防禦性)'
    
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
        """獲取最近幾天的訊號摘要，包含技術指標狀態"""
        if self.signals is None or self.data is None:
            print("請先生成訊號和技術指標")
            return None
        
        recent_signals = self.signals.tail(days)
        buy_signals = recent_signals[recent_signals['Signal'] == 1]
        sell_signals = recent_signals[recent_signals['Signal'] == -1]
        
        # 獲取最新的技術指標值
        latest = self.data.iloc[-1]
        
        # RSI 狀態判斷
        rsi_value = latest.get('RSI', None)
        if rsi_value is not None:
            if rsi_value > 70:
                rsi_status = 'overbought'
            elif rsi_value < 30:
                rsi_status = 'oversold'
            else:
                rsi_status = 'neutral'
        else:
            rsi_status = 'neutral'
        
        # MACD 狀態判斷
        macd_value = latest.get('MACD', None)
        macd_signal = latest.get('MACD_Signal', None)
        if macd_value is not None and macd_signal is not None:
            if macd_value > macd_signal:
                macd_status = 'bullish'
            else:
                macd_status = 'bearish'
        else:
            macd_status = 'neutral'
        
        # 布林通道位置判斷
        close_price = latest.get('Close', None)
        bb_upper = latest.get('BB_Upper', None)
        bb_lower = latest.get('BB_Lower', None)
        if close_price is not None and bb_upper is not None and bb_lower is not None:
            if close_price > bb_upper:
                bb_position = 'above_upper'
                bb_status = 'overbought'
            elif close_price < bb_lower:
                bb_position = 'below_lower'
                bb_status = 'oversold'
            else:
                bb_position = 'within_bands'
                bb_status = 'neutral'
        else:
            bb_position = 'N/A'
            bb_status = 'neutral'
        
        # 均線狀態判斷
        close_price = latest.get('Close', None)
        sma_20 = latest.get('SMA_20', None)
        sma_50 = latest.get('SMA_50', None)
        sma_120 = latest.get('SMA_120', None)
        
        if close_price is not None and sma_20 is not None and sma_50 is not None:
            if close_price > sma_20 and sma_20 > sma_50:
                ma_status = 'bullish'
            elif close_price < sma_20 and sma_20 < sma_50:
                ma_status = 'bearish'
            else:
                ma_status = 'neutral'
        else:
            ma_status = 'neutral'
        
        # 成交量趨勢
        volume = latest.get('Volume', None)
        if volume is not None:
            avg_volume = self.data['Volume'].tail(20).mean()
            if volume > avg_volume * 1.5:
                volume_trend = 'high'
            elif volume < avg_volume * 0.5:
                volume_trend = 'low'
            else:
                volume_trend = 'normal'
        else:
            volume_trend = 'N/A'
        
        # 計算波動率和Beta
        volatility_beta = self.calculate_volatility_and_beta()
        
        return {
            'total_days': len(recent_signals),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'hold_days': len(recent_signals) - len(buy_signals) - len(sell_signals),
            'avg_strength': round(recent_signals['Strength'].mean(), 2),
            # 技術指標值
            'rsi': round(rsi_value, 2) if rsi_value is not None else 'N/A',
            'rsi_status': rsi_status,
            'macd': round(macd_value, 4) if macd_value is not None else 'N/A',
            'macd_status': macd_status,
            'bb_position': bb_position,
            'bb_status': bb_status,
            'ma_status': ma_status,
            'volume': f"{volume:,.0f}" if volume is not None else 'N/A',
            'volume_trend': volume_trend,
            # 波動率和Beta信息
            'volatility': round(volatility_beta['volatility'], 2) if volatility_beta else 'N/A',
            'beta': round(volatility_beta['beta'], 3) if volatility_beta else 'N/A',
            'risk_level': volatility_beta['risk_level'] if volatility_beta else 'N/A',
            'beta_risk': volatility_beta['beta_risk'] if volatility_beta else 'N/A',
            'sharpe_ratio': round(volatility_beta['sharpe_ratio'], 3) if volatility_beta else 'N/A',
            'correlation': round(volatility_beta['correlation'], 3) if volatility_beta else 'N/A',
            'annual_return': round(volatility_beta['annual_return'], 2) if volatility_beta else 'N/A',
            'market_symbol': volatility_beta['market_symbol'] if volatility_beta else 'N/A'
        }
    
    def run_analysis(self):
        """執行完整分析流程"""
        print(f"開始分析 {self.symbol}...")
        
        if not self.fetch_data():
            return False
        
        self.calculate_technical_indicators()
        self.generate_signals()
        
        # 計算波動率和Beta
        volatility_beta = self.calculate_volatility_and_beta()
        
        current_signal = self.get_current_signal()
        summary = self.get_signal_summary()
        
        print("\n=== 分析結果 ===")
        print(f"股票代碼: {self.symbol}")
        print(f"股票名稱: {self.long_name}")
        print(f"當前價格: ${current_signal['price']}")
        print(f"建議動作: {current_signal['signal']}")
        print(f"訊號強度: {current_signal['strength']}")
        
        if volatility_beta:
            print(f"\n=== 風險分析 ===")
            print(f"年化波動率: {volatility_beta['volatility']:.2f}%")
            print(f"Beta值: {volatility_beta['beta']:.3f}")
            print(f"風險等級: {volatility_beta['risk_level']}")
            print(f"Beta風險: {volatility_beta['beta_risk']}")
            print(f"夏普比率: {volatility_beta['sharpe_ratio']:.3f}")
        
        return True
    
    @staticmethod
    def validate_symbol(symbol):
        """
        驗證股票代碼格式
        
        Args:
            symbol (str): 股票代碼
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not symbol or not isinstance(symbol, str):
            return False, "股票代碼不能為空"
        
        symbol = symbol.strip().upper()
        
        # 基本格式檢查
        if len(symbol) < 1 or len(symbol) > 10:
            return False, "股票代碼長度不正確"
        
        # 檢查是否包含非法字符
        if not re.match(r'^[A-Z0-9.]+$', symbol):
            return False, "股票代碼包含非法字符"
        
        return True, ""
    
    @staticmethod
    def get_symbol_info(symbol):
        """
        獲取股票代碼的基本資訊
        
        Args:
            symbol (str): 股票代碼
            
        Returns:
            dict: 股票代碼資訊
        """
        is_valid, error_msg = StockAnalyzer.validate_symbol(symbol)
        
        info = {
            'symbol': symbol,
            'is_valid': is_valid,
            'error': error_msg if not is_valid else None,
            'exchange': None,
            'market': None
        }
        
        if not is_valid:
            return info
        
        # 根據後綴判斷交易所
        if symbol.endswith('.TW'):
            info['exchange'] = 'TWSE'
            info['market'] = 'Taiwan'
        elif symbol.endswith('.HK'):
            info['exchange'] = 'HKEX'
            info['market'] = 'Hong Kong'
        elif symbol.endswith('.T'):
            info['exchange'] = 'TSE'
            info['market'] = 'Tokyo'
        elif '.' in symbol:
            # 其他國際股票
            info['exchange'] = 'International'
            info['market'] = 'Global'
        else:
            # 預設為美股
            info['exchange'] = 'NYSE/NASDAQ'
            info['market'] = 'US'
        
        return info 
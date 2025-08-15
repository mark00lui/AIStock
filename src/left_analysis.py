#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
左側分析模組 - 股價預估分析
提供基於分析師預估和歷史本益比的股價預測功能
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
import warnings
import os
from typing import Dict, List, Optional, Tuple
warnings.filterwarnings('ignore')

class LeftAnalysis:
    """左側分析器 - 專注於基本面分析和股價預估"""
    
    def __init__(self, alpha_vantage_key: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.alpha_vantage_key = alpha_vantage_key or os.getenv('ALPHA_VANTAGE_KEY')
    
    def calculate_historical_pe_ratios(self, symbol: str) -> Optional[Dict]:
        """計算歷史本益比數據"""
        try:
            ticker = yf.Ticker(symbol)
            
            # 獲取歷史股價數據
            hist_data = ticker.history(period="10y")
            
            # 獲取季度 EPS 數據
            earnings = ticker.earnings
            
            if hist_data is None or len(hist_data) == 0 or earnings is None or len(earnings) == 0:
                return None
            
            # 計算歷史本益比
            pe_ratios = []
            
            for i, (date, row) in enumerate(earnings.iterrows()):
                eps = row['Earnings']
                if eps <= 0:
                    continue
                
                # 找到對應的股價數據
                try:
                    price_data = hist_data[hist_data.index >= date]
                    if len(price_data) > 0:
                        price = price_data.iloc[0]['Close']
                        pe_ratio = price / eps
                        pe_ratios.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'price': price,
                            'eps': eps,
                            'pe_ratio': pe_ratio
                        })
                except:
                    continue
            
            if len(pe_ratios) == 0:
                return None
            
            # 計算統計數據
            pe_values = [item['pe_ratio'] for item in pe_ratios]
            
            historical_pe_data = {
                'pe_ratios': pe_ratios,
                'mean_pe': float(np.mean(pe_values)),
                'median_pe': float(np.median(pe_values)),
                'max_pe': float(np.max(pe_values)),
                'min_pe': float(np.min(pe_values)),
                'std_pe': float(np.std(pe_values)),
                'data_points': len(pe_values),
                'period': f"{pe_ratios[0]['date']} 到 {pe_ratios[-1]['date']}"
            }
            
            return historical_pe_data
            
        except Exception as e:
            print(f"計算歷史本益比失敗: {e}")
            return None
    
    def get_yahoo_analyst_estimates(self, symbol: str) -> Dict:
        """從 Yahoo Finance 獲取分析師預估"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            estimates = {
                'source': 'Yahoo Finance',
                'timeframes': {
                    '1_year': {
                        'target_mean': None,
                        'target_median': None,
                        'target_high': None,
                        'target_low': None,
                        'target_count': None,
                        'timeframe': '1年後'
                    },
                    '2_year': {
                        'target_mean': None,
                        'target_median': None,
                        'target_high': None,
                        'target_low': None,
                        'target_count': None,
                        'timeframe': '2年後'
                    },
                    '3_year': {
                        'target_mean': None,
                        'target_median': None,
                        'target_high': None,
                        'target_low': None,
                        'target_count': None,
                        'timeframe': '3年後'
                    }
                },
                'recommendation': None,
                'recommendation_mean': None,
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
            
            # 獲取當前股價作為基準
            current_price = info.get('regularMarketPrice', None)
            
            # Yahoo Finance 的目標價通常是12個月預估
            if 'targetMeanPrice' in info and info['targetMeanPrice']:
                base_target = info['targetMeanPrice']
                estimates['timeframes']['1_year']['target_mean'] = base_target
                
                # 計算2年和3年的預估
                annual_growth_rate = 0.08
                estimates['timeframes']['2_year']['target_mean'] = base_target * (1 + annual_growth_rate)
                estimates['timeframes']['3_year']['target_mean'] = base_target * (1 + annual_growth_rate) ** 2
            
            if 'targetMedianPrice' in info and info['targetMedianPrice']:
                base_median = info['targetMedianPrice']
                estimates['timeframes']['1_year']['target_median'] = base_median
                
                annual_growth_rate = 0.08
                estimates['timeframes']['2_year']['target_median'] = base_median * (1 + annual_growth_rate)
                estimates['timeframes']['3_year']['target_median'] = base_median * (1 + annual_growth_rate) ** 2
            
            # 改進的目標價計算邏輯
            forward_eps = info.get('trailingEps', None)
            forward_pe = info.get('forwardPE', None)
            
            if forward_eps and forward_pe and current_price:
                base_eps_estimate = forward_eps
                pe_high = forward_pe * 1.3
                pe_low = forward_pe * 0.7
                
                target_high_eps = base_eps_estimate * pe_high
                target_low_eps = base_eps_estimate * pe_low
                
                if 'targetHighPrice' in info and info['targetHighPrice']:
                    yahoo_high = info['targetHighPrice']
                    if yahoo_high <= target_high_eps * 1.2:
                        estimates['timeframes']['1_year']['target_high'] = yahoo_high
                    else:
                        estimates['timeframes']['1_year']['target_high'] = target_high_eps
                else:
                    estimates['timeframes']['1_year']['target_high'] = target_high_eps
                
                if 'targetLowPrice' in info and info['targetLowPrice']:
                    yahoo_low = info['targetLowPrice']
                    if yahoo_low >= target_low_eps * 0.8:
                        estimates['timeframes']['1_year']['target_low'] = yahoo_low
                    else:
                        estimates['timeframes']['1_year']['target_low'] = target_low_eps
                else:
                    estimates['timeframes']['1_year']['target_low'] = target_low_eps
                
                # 確保價格合理性
                if estimates['timeframes']['1_year']['target_low']:
                    min_price = current_price * 0.7
                    if estimates['timeframes']['1_year']['target_low'] < min_price:
                        estimates['timeframes']['1_year']['target_low'] = min_price
                
                if estimates['timeframes']['1_year']['target_high']:
                    max_price = current_price * 2.0
                    if estimates['timeframes']['1_year']['target_high'] > max_price:
                        estimates['timeframes']['1_year']['target_high'] = max_price
                
                # 計算2年和3年的上下限
                for timeframe in ['2_year', '3_year']:
                    years = int(timeframe.split('_')[0])
                    
                    if estimates['timeframes']['1_year']['target_high']:
                        high_growth = 0.10
                        estimates['timeframes'][timeframe]['target_high'] = estimates['timeframes']['1_year']['target_high'] * (1 + high_growth) ** (years - 1)
                    
                    if estimates['timeframes']['1_year']['target_low']:
                        low_growth = 0.05
                        estimates['timeframes'][timeframe]['target_low'] = estimates['timeframes']['1_year']['target_low'] * (1 + low_growth) ** (years - 1)
            
            if 'numberOfAnalystOpinions' in info and info['numberOfAnalystOpinions']:
                analyst_count = info['numberOfAnalystOpinions']
                estimates['timeframes']['1_year']['target_count'] = analyst_count
                estimates['timeframes']['2_year']['target_count'] = analyst_count
                estimates['timeframes']['3_year']['target_count'] = analyst_count
            
            if 'recommendationKey' in info and info['recommendationKey']:
                estimates['recommendation'] = info['recommendationKey']
            
            if 'recommendationMean' in info and info['recommendationMean']:
                estimates['recommendation_mean'] = info['recommendationMean']
            
            return estimates
            
        except Exception as e:
            return {'source': 'Yahoo Finance', 'error': str(e)}
    
    def get_eps_based_estimates(self, symbol: str) -> Optional[Dict]:
        """基於歷史本益比和未來 EPS 的預估"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current_price = info.get('regularMarketPrice', None)
            forward_eps = info.get('trailingEps', None)
            
            if not current_price or not forward_eps:
                return None
            
            historical_pe = self.calculate_historical_pe_ratios(symbol)
            
            if not historical_pe:
                current_pe = info.get('trailingPE', None)
                if not current_pe:
                    return None
                
                pe_mean = current_pe
                pe_high = current_pe * 1.3
                pe_low = current_pe * 0.7
            else:
                pe_mean = historical_pe['mean_pe']
                pe_high = historical_pe['max_pe']
                pe_low = historical_pe['min_pe']
            
            eps_growth_rate = 0.08
            
            estimates = {
                'source': 'EPS 基於歷史本益比',
                'timeframes': {
                    '1_year': {
                        'target_mean': None,
                        'target_median': None,
                        'target_high': None,
                        'target_low': None,
                        'target_count': None,
                        'timeframe': '1年後'
                    },
                    '2_year': {
                        'target_mean': None,
                        'target_median': None,
                        'target_high': None,
                        'target_low': None,
                        'target_count': None,
                        'timeframe': '2年後'
                    },
                    '3_year': {
                        'target_mean': None,
                        'target_median': None,
                        'target_high': None,
                        'target_low': None,
                        'target_count': None,
                        'timeframe': '3年後'
                    }
                },
                'recommendation': None,
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'historical_pe_data': historical_pe
            }
            
            # 計算各年度的預估
            for timeframe in ['1_year', '2_year', '3_year']:
                years = int(timeframe.split('_')[0])
                future_eps = forward_eps * (1 + eps_growth_rate) ** years
                
                target_mean = future_eps * pe_mean
                target_high = future_eps * pe_high
                target_low = future_eps * pe_low
                
                estimates['timeframes'][timeframe].update({
                    'target_mean': target_mean,
                    'target_median': target_mean,
                    'target_high': target_high,
                    'target_low': target_low,
                    'target_count': historical_pe['data_points'] if historical_pe else 1,
                    'future_eps': future_eps,
                    'used_pe_mean': pe_mean,
                    'used_pe_high': pe_high,
                    'used_pe_low': pe_low
                })
            
            # 設定建議
            current_pe = current_price / forward_eps if forward_eps > 0 else None
            if current_pe and pe_mean:
                if current_pe < pe_low:
                    estimates['recommendation'] = 'Strong Buy'
                elif current_pe < pe_mean:
                    estimates['recommendation'] = 'Buy'
                elif current_pe < pe_high:
                    estimates['recommendation'] = 'Hold'
                else:
                    estimates['recommendation'] = 'Sell'
            else:
                estimates['recommendation'] = 'Hold'
            
            return estimates
            
        except Exception as e:
            return None
    
    def get_simulated_estimates(self, symbol: str) -> Dict:
        """獲取模擬的分析師預估數據"""
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.info.get('regularMarketPrice', None)
            
            if not current_price:
                return {'source': 'Simulated', 'error': '無法獲取當前股價'}
            
            # 根據股票類型設定不同的預估
            if symbol in ['AAPL', 'MSFT', 'TSLA']:
                # 美股模擬數據
                if symbol == 'AAPL':
                    base_price = current_price
                    target_mean = base_price * 1.15
                    target_high = base_price * 1.25
                    target_low = base_price * 0.85
                elif symbol == 'TSLA':
                    base_price = current_price
                    target_mean = base_price * 1.10
                    target_high = base_price * 1.20
                    target_low = base_price * 0.90
                else:  # MSFT
                    base_price = current_price
                    target_mean = base_price * 1.12
                    target_high = base_price * 1.22
                    target_low = base_price * 0.88
                
                analyst_count = 25
                recommendation = 'Buy'
                
            elif symbol in ['2330.TW', '2317.TW']:
                # 台股模擬數據
                if symbol == '2330.TW':
                    base_price = current_price
                    target_mean = base_price * 1.08
                    target_high = base_price * 1.15
                    target_low = base_price * 0.92
                else:  # 2317.TW
                    base_price = current_price
                    target_mean = base_price * 1.05
                    target_high = base_price * 1.12
                    target_low = base_price * 0.95
                
                analyst_count = 15
                recommendation = 'Hold'
            else:
                # 通用模擬數據
                base_price = current_price
                target_mean = base_price * 1.10
                target_high = base_price * 1.20
                target_low = base_price * 0.90
                analyst_count = 20
                recommendation = 'Hold'
            
            estimates = {
                'source': 'Simulated',
                'timeframes': {
                    '1_year': {
                        'target_mean': target_mean,
                        'target_median': target_mean,
                        'target_high': target_high,
                        'target_low': target_low,
                        'target_count': analyst_count,
                        'timeframe': '1年後'
                    },
                    '2_year': {
                        'target_mean': target_mean * 1.08,
                        'target_median': target_mean * 1.08,
                        'target_high': target_high * 1.10,
                        'target_low': target_low * 1.05,
                        'target_count': analyst_count - 5,
                        'timeframe': '2年後'
                    },
                    '3_year': {
                        'target_mean': target_mean * (1.08 ** 2),
                        'target_median': target_mean * (1.08 ** 2),
                        'target_high': target_high * (1.10 ** 2),
                        'target_low': target_low * (1.05 ** 2),
                        'target_count': analyst_count - 10,
                        'timeframe': '3年後'
                    }
                },
                'recommendation': recommendation,
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
            
            return estimates
            
        except Exception as e:
            return {'source': 'Simulated', 'error': str(e)}
    
    def analyze_stock_price(self, symbol: str) -> Dict:
        """
        分析股票價格預估
        
        Args:
            symbol (str): 股票代碼
            
        Returns:
            Dict: 包含未來三年預估的 JSON 格式數據
        """
        try:
            print(f"開始分析股票: {symbol}")
            
            # 獲取基本信息
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current_price = info.get('regularMarketPrice', None)
            forward_eps = info.get('trailingEps', None)
            forward_pe = info.get('forwardPE', None)
            current_pe = info.get('trailingPE', None)
            
            if not current_price:
                return {
                    'error': f'無法獲取 {symbol} 的當前股價',
                    'symbol': symbol,
                    'timestamp': datetime.now().isoformat()
                }
            
            # 從多個來源獲取預估
            sources = [
                self.get_yahoo_analyst_estimates(symbol),
                self.get_eps_based_estimates(symbol),
                self.get_simulated_estimates(symbol)
            ]
            
            # 收集有效的預估
            valid_sources = []
            for source in sources:
                if source and 'error' not in source and 'timeframes' in source:
                    valid_sources.append(source)
            
            if not valid_sources:
                return {
                    'error': f'無法獲取 {symbol} 的任何預估數據',
                    'symbol': symbol,
                    'timestamp': datetime.now().isoformat()
                }
            
            # 計算聚合統計
            results = {}
            timeframes = ['1_year', '2_year', '3_year']
            
            for timeframe in timeframes:
                all_targets = []
                all_highs = []
                all_lows = []
                all_eps = []
                
                for source in valid_sources:
                    if source['timeframes'][timeframe].get('target_mean'):
                        all_targets.append(source['timeframes'][timeframe]['target_mean'])
                    if source['timeframes'][timeframe].get('target_high'):
                        all_highs.append(source['timeframes'][timeframe]['target_high'])
                    if source['timeframes'][timeframe].get('target_low'):
                        all_lows.append(source['timeframes'][timeframe]['target_low'])
                    if source['timeframes'][timeframe].get('future_eps'):
                        all_eps.append(source['timeframes'][timeframe]['future_eps'])
                
                if all_targets:
                    years_ahead = int(timeframe.split('_')[0])
                    target_date = datetime.now() + timedelta(days=365 * years_ahead)
                    
                    # 計算基於 EPS 的預估
                    eps_based_estimate = None
                    if forward_eps and forward_pe:
                        eps_growth_rate = 0.08
                        future_eps = forward_eps * (1 + eps_growth_rate) ** years_ahead
                        eps_based_estimate = future_eps * forward_pe
                    
                    results[timeframe] = {
                        'timeframe': f"{years_ahead}年後",
                        'target_date': target_date.strftime('%Y-%m-%d'),
                        'sources_count': len(valid_sources),
                        'target_mean': float(np.mean(all_targets)),
                        'target_median': float(np.median(all_targets)),
                        'target_high': float(np.max(all_highs)) if all_highs else None,
                        'target_low': float(np.min(all_lows)) if all_lows else None,
                        'target_std': float(np.std(all_targets)),
                        'potential_return': ((np.mean(all_targets) - current_price) / current_price * 100) if current_price else None,
                        'eps_based_estimate': eps_based_estimate,
                        'future_eps': float(np.mean(all_eps)) if all_eps else None,
                        'confidence_interval': {
                            'lower_68': float(np.mean(all_targets) - np.std(all_targets)),
                            'upper_68': float(np.mean(all_targets) + np.std(all_targets)),
                            'lower_95': float(np.mean(all_targets) - 2 * np.std(all_targets)),
                            'upper_95': float(np.mean(all_targets) + 2 * np.std(all_targets))
                        }
                    }
            
            # 構建返回結果
            response = {
                'symbol': symbol,
                'stock_name': info.get('longName', symbol),
                'current_price': current_price,
                'forward_eps': forward_eps,
                'forward_pe': forward_pe,
                'current_pe': current_pe,
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'timestamp': datetime.now().isoformat(),
                'sources_used': [s['source'] for s in valid_sources],
                'timeframes': results,
                'summary': {
                    'total_sources': len(valid_sources),
                    'analysis_status': 'success'
                }
            }
            
            # 添加歷史本益比數據（如果可用）
            historical_pe = self.calculate_historical_pe_ratios(symbol)
            if historical_pe:
                response['historical_pe'] = historical_pe
            
            print(f"完成分析: {symbol}")
            return response
            
        except Exception as e:
            print(f"分析失敗: {symbol} - {e}")
            return {
                'error': f'分析 {symbol} 時發生錯誤: {str(e)}',
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }

def analyze_stock(symbol: str, alpha_vantage_key: Optional[str] = None) -> Dict:
    """
    便捷函數：分析單一股票
    
    Args:
        symbol (str): 股票代碼
        alpha_vantage_key (str, optional): Alpha Vantage API key
        
    Returns:
        Dict: 分析結果的 JSON 格式數據
    """
    analyzer = LeftAnalysis(alpha_vantage_key)
    return analyzer.analyze_stock_price(symbol)

def analyze_multiple_stocks(symbols: List[str], alpha_vantage_key: Optional[str] = None) -> Dict:
    """
    分析多個股票
    
    Args:
        symbols (List[str]): 股票代碼列表
        alpha_vantage_key (str, optional): Alpha Vantage API key
        
    Returns:
        Dict: 包含所有股票分析結果的 JSON 格式數據
    """
    analyzer = LeftAnalysis(alpha_vantage_key)
    results = []
    
    for symbol in symbols:
        result = analyzer.analyze_stock_price(symbol)
        results.append(result)
    
    return {
        'batch_analysis': True,
        'symbols_analyzed': symbols,
        'total_stocks': len(symbols),
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().isoformat(),
        'results': results
    } 
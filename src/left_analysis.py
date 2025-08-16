#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
左側分析模組 - 股價預估分析
提供基於分析師預估和歷史本益比的股價預測功能
改進版本：增強波動性表達和精確目標價格區間
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
from scipy import stats
warnings.filterwarnings('ignore')

class LeftAnalysis:
    """左側分析器 - 專注於基本面分析和股價預估"""
    
    def __init__(self, alpha_vantage_key: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.alpha_vantage_key = alpha_vantage_key or os.getenv('ALPHA_VANTAGE_KEY')
        
        # 行業特定的 EPS 增長率
        self.industry_eps_growth = {
            'Technology': 0.12,
            'Healthcare': 0.10,
            'Financial': 0.06,
            'Consumer': 0.08,
            'Industrial': 0.07,
            'Energy': 0.05,
            'Materials': 0.06,
            'Utilities': 0.04,
            'Real Estate': 0.05,
            'Communication': 0.09,
            'default': 0.08
        }
    
    def get_industry_category(self, symbol: str) -> str:
        """根據股票代碼判斷行業類別"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            sector = info.get('sector', '').strip()
            
            # 映射到我們的類別
            sector_mapping = {
                'Technology': 'Technology',
                'Healthcare': 'Healthcare',
                'Financial Services': 'Financial',
                'Consumer Cyclical': 'Consumer',
                'Consumer Defensive': 'Consumer',
                'Industrials': 'Industrial',
                'Energy': 'Energy',
                'Basic Materials': 'Materials',
                'Utilities': 'Utilities',
                'Real Estate': 'Real Estate',
                'Communication Services': 'Communication'
            }
            
            return sector_mapping.get(sector, 'default')
        except:
            return 'default'
    
    def calculate_enhanced_historical_pe_ratios(self, symbol: str) -> Optional[Dict]:
        """計算增強的歷史本益比數據，包含波動性和週期性分析"""
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
            
            if len(pe_ratios) < 5:  # 至少需要5個數據點
                return None
            
            # 計算統計數據
            pe_values = [item['pe_ratio'] for item in pe_ratios]
            
            # 基本統計
            mean_pe = float(np.mean(pe_values))
            median_pe = float(np.median(pe_values))
            std_pe = float(np.std(pe_values))
            
            # 分位數分析
            pe_25 = float(np.percentile(pe_values, 25))
            pe_75 = float(np.percentile(pe_values, 75))
            pe_10 = float(np.percentile(pe_values, 10))
            pe_90 = float(np.percentile(pe_values, 90))
            
            # 計算變異係數（CV）來衡量相對波動性
            cv_pe = std_pe / mean_pe if mean_pe > 0 else 0
            
            # 趨勢分析（最近5年 vs 前5年）
            if len(pe_values) >= 10:
                recent_pe = pe_values[-5:]
                older_pe = pe_values[:5]
                recent_mean = np.mean(recent_pe)
                older_mean = np.mean(older_pe)
                pe_trend = (recent_mean - older_mean) / older_mean if older_mean > 0 else 0
            else:
                pe_trend = 0
            
            # 計算動態目標價格區間
            # 基於歷史波動性調整目標價格
            volatility_factor = min(cv_pe * 2, 0.5)  # 限制最大調整幅度為50%
            
            # 計算不同置信區間的目標價格
            target_prices = {
                'conservative_low': mean_pe * (1 - 2 * volatility_factor),    # 保守下限
                'moderate_low': mean_pe * (1 - volatility_factor),            # 適中下限
                'target_mean': mean_pe,                                       # 目標均值
                'moderate_high': mean_pe * (1 + volatility_factor),           # 適中上限
                'aggressive_high': mean_pe * (1 + 2 * volatility_factor)      # 激進上限
            }
            
            # 確保價格合理性
            for key in target_prices:
                target_prices[key] = max(target_prices[key], mean_pe * 0.3)  # 最低不低於均值的30%
                target_prices[key] = min(target_prices[key], mean_pe * 3.0)  # 最高不高於均值的3倍
            
            historical_pe_data = {
                'pe_ratios': pe_ratios,
                'basic_stats': {
                    'mean_pe': mean_pe,
                    'median_pe': median_pe,
                    'std_pe': std_pe,
                    'min_pe': float(np.min(pe_values)),
                    'max_pe': float(np.max(pe_values)),
                    'data_points': len(pe_values)
                },
                'percentile_stats': {
                    'pe_10': pe_10,
                    'pe_25': pe_25,
                    'pe_75': pe_75,
                    'pe_90': pe_90
                },
                'volatility_analysis': {
                    'coefficient_of_variation': cv_pe,
                    'volatility_factor': volatility_factor,
                    'pe_trend': pe_trend
                },
                'target_price_ranges': target_prices,
                'period': f"{pe_ratios[0]['date']} 到 {pe_ratios[-1]['date']}"
            }
            
            return historical_pe_data
            
        except Exception as e:
            print(f"計算增強歷史本益比失敗: {e}")
            return None
    
    def calculate_dynamic_eps_growth(self, symbol: str, base_eps: float) -> Dict:
        """計算動態 EPS 增長率，考慮行業特性和經濟週期"""
        try:
            industry = self.get_industry_category(symbol)
            base_growth_rate = self.industry_eps_growth.get(industry, self.industry_eps_growth['default'])
            
            # 獲取公司基本信息
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 調整因子
            adjustments = {
                'market_cap': 1.0,
                'profitability': 1.0,
                'debt_level': 1.0,
                'recent_performance': 1.0
            }
            
            # 市值調整（大公司通常增長較慢但穩定）
            market_cap = info.get('marketCap', 0)
            if market_cap > 100e9:  # 1000億以上
                adjustments['market_cap'] = 0.8
            elif market_cap > 10e9:  # 100億以上
                adjustments['market_cap'] = 0.9
            elif market_cap < 1e9:  # 10億以下
                adjustments['market_cap'] = 1.2
            
            # 盈利能力調整
            profit_margin = info.get('profitMargins', 0)
            if profit_margin and profit_margin > 0.2:
                adjustments['profitability'] = 1.1
            elif profit_margin and profit_margin < 0.05:
                adjustments['profitability'] = 0.9
            
            # 債務水平調整
            debt_to_equity = info.get('debtToEquity', 0)
            if debt_to_equity and debt_to_equity > 1.0:
                adjustments['debt_level'] = 0.9
            elif debt_to_equity and debt_to_equity < 0.3:
                adjustments['debt_level'] = 1.05
            
            # 計算綜合調整因子
            total_adjustment = np.prod(list(adjustments.values()))
            
            # 計算各年度的動態增長率
            eps_growth_rates = {}
            for year in [1, 2, 3]:
                # 增長率隨時間遞減（長期預測更保守）
                time_decay = 1.0 - (year - 1) * 0.1  # 每年遞減10%
                adjusted_growth = base_growth_rate * total_adjustment * time_decay
                
                # 添加隨機波動（模擬不確定性）
                uncertainty_factor = np.random.normal(1.0, 0.1)  # 10%的標準差
                final_growth = max(adjusted_growth * uncertainty_factor, 0.02)  # 最低2%
                
                eps_growth_rates[f'{year}_year'] = {
                    'growth_rate': final_growth,
                    'adjusted_growth': adjusted_growth,
                    'uncertainty_factor': uncertainty_factor,
                    'adjustments': adjustments.copy()
                }
            
            return eps_growth_rates
            
        except Exception as e:
            print(f"計算動態EPS增長失敗: {e}")
            # 返回默認值
            return {
                '1_year': {'growth_rate': 0.08, 'adjusted_growth': 0.08, 'uncertainty_factor': 1.0, 'adjustments': {}},
                '2_year': {'growth_rate': 0.07, 'adjusted_growth': 0.07, 'uncertainty_factor': 1.0, 'adjustments': {}},
                '3_year': {'growth_rate': 0.06, 'adjusted_growth': 0.06, 'uncertainty_factor': 1.0, 'adjustments': {}}
            }
    
    def calculate_enhanced_target_prices(self, symbol: str, current_price: float, forward_eps: float) -> Dict:
        """計算增強的目標價格，包含多個置信區間"""
        try:
            historical_pe = self.calculate_enhanced_historical_pe_ratios(symbol)
            eps_growth_rates = self.calculate_dynamic_eps_growth(symbol, forward_eps)
            
            if not historical_pe:
                # 如果沒有歷史數據，使用當前P/E作為基準
                ticker = yf.Ticker(symbol)
                info = ticker.info
                current_pe = info.get('trailingPE', 15)
                
                target_prices = {
                    'conservative_low': current_pe * 0.7,
                    'moderate_low': current_pe * 0.85,
                    'target_mean': current_pe,
                    'moderate_high': current_pe * 1.15,
                    'aggressive_high': current_pe * 1.3
                }
            else:
                target_prices = historical_pe['target_price_ranges']
            
            # 計算各年度的目標價格
            enhanced_estimates = {}
            
            for year in [1, 2, 3]:
                year_key = f'{year}_year'
                growth_data = eps_growth_rates[year_key]
                future_eps = forward_eps * (1 + growth_data['growth_rate']) ** year
                
                # 計算不同置信區間的目標價格
                year_estimates = {}
                for confidence_level, pe_ratio in target_prices.items():
                    target_price = future_eps * pe_ratio
                    
                    # 添加風險調整
                    risk_adjustment = 1.0
                    if confidence_level in ['conservative_low', 'moderate_low']:
                        risk_adjustment = 0.95  # 保守估計稍微下調
                    elif confidence_level in ['moderate_high', 'aggressive_high']:
                        risk_adjustment = 1.05  # 樂觀估計稍微上調
                    
                    year_estimates[confidence_level] = {
                        'target_price': target_price * risk_adjustment,
                        'future_eps': future_eps,
                        'used_pe_ratio': pe_ratio,
                        'risk_adjustment': risk_adjustment,
                        'growth_rate': growth_data['growth_rate']
                    }
                
                # 計算建議的買賣區間
                conservative_low = year_estimates['conservative_low']['target_price']
                moderate_low = year_estimates['moderate_low']['target_price']
                target_mean = year_estimates['target_mean']['target_price']
                moderate_high = year_estimates['moderate_high']['target_price']
                aggressive_high = year_estimates['aggressive_high']['target_price']
                
                # 買賣建議邏輯
                if current_price < conservative_low:
                    action = 'Strong Buy'
                    confidence = 'High'
                elif current_price < moderate_low:
                    action = 'Buy'
                    confidence = 'Medium'
                elif current_price < target_mean:
                    action = 'Hold/Buy'
                    confidence = 'Medium'
                elif current_price < moderate_high:
                    action = 'Hold'
                    confidence = 'Medium'
                elif current_price < aggressive_high:
                    action = 'Hold/Sell'
                    confidence = 'Medium'
                else:
                    action = 'Sell'
                    confidence = 'High'
                
                enhanced_estimates[year_key] = {
                    'timeframe': f'{year}年後',
                    'target_prices': year_estimates,
                    'summary': {
                        'target_mean': target_mean,
                        'target_median': target_mean,  # 簡化處理
                        'target_high': aggressive_high,
                        'target_low': conservative_low,
                        'buy_zone': f'${conservative_low:.2f} - ${moderate_low:.2f}',
                        'hold_zone': f'${moderate_low:.2f} - ${moderate_high:.2f}',
                        'sell_zone': f'${moderate_high:.2f} - ${aggressive_high:.2f}',
                        'recommended_action': action,
                        'confidence': confidence,
                        'potential_return': ((target_mean - current_price) / current_price * 100) if current_price else None
                    },
                    'eps_analysis': {
                        'current_eps': forward_eps,
                        'future_eps': future_eps,
                        'growth_rate': growth_data['growth_rate'],
                        'growth_adjustments': growth_data['adjustments']
                    }
                }
            
            return enhanced_estimates
            
        except Exception as e:
            print(f"計算增強目標價格失敗: {e}")
            return {}

    def get_enhanced_eps_based_estimates(self, symbol: str) -> Optional[Dict]:
        """基於增強歷史本益比和動態 EPS 的預估"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current_price = info.get('regularMarketPrice', None)
            forward_eps = info.get('trailingEps', None)
            
            if not current_price or not forward_eps:
                return None
            
            # 計算增強的目標價格
            enhanced_estimates = self.calculate_enhanced_target_prices(symbol, current_price, forward_eps)
            
            if not enhanced_estimates:
                return None
            
            # 構建返回結果
            estimates = {
                'source': 'Enhanced EPS 基於歷史本益比',
                'timeframes': {},
                'recommendation': None,
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'analysis_metadata': {
                    'current_price': current_price,
                    'forward_eps': forward_eps,
                    'current_pe': current_price / forward_eps if forward_eps > 0 else None,
                    'industry_category': self.get_industry_category(symbol)
                }
            }
            
            # 轉換格式以保持兼容性
            for year_key, year_data in enhanced_estimates.items():
                summary = year_data['summary']
                estimates['timeframes'][year_key] = {
                    'target_mean': summary['target_mean'],
                    'target_median': summary['target_median'],
                    'target_high': summary['target_high'],
                    'target_low': summary['target_low'],
                    'target_count': 1,  # 單一來源
                    'timeframe': year_data['timeframe'],
                    'future_eps': year_data['eps_analysis']['future_eps'],
                    'recommended_action': summary['recommended_action'],
                    'confidence': summary['confidence'],
                    'buy_zone': summary['buy_zone'],
                    'hold_zone': summary['hold_zone'],
                    'sell_zone': summary['sell_zone'],
                    'potential_return': summary['potential_return']
                }
            
            # 設定整體建議（基於1年預估）
            if '1_year' in estimates['timeframes']:
                estimates['recommendation'] = estimates['timeframes']['1_year']['recommended_action']
            
            return estimates
            
        except Exception as e:
            print(f"增強EPS預估失敗: {e}")
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
        分析股票價格預估（增強版本）
        
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
            
            # 優先使用增強的EPS預估
            enhanced_estimates = self.get_enhanced_eps_based_estimates(symbol)
            
            # 從多個來源獲取預估
            sources = [
                enhanced_estimates,
                self.get_yahoo_analyst_estimates(symbol),
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
                all_actions = []
                all_confidences = []
                
                for source in valid_sources:
                    if source['timeframes'][timeframe].get('target_mean'):
                        all_targets.append(source['timeframes'][timeframe]['target_mean'])
                    if source['timeframes'][timeframe].get('target_high'):
                        all_highs.append(source['timeframes'][timeframe]['target_high'])
                    if source['timeframes'][timeframe].get('target_low'):
                        all_lows.append(source['timeframes'][timeframe]['target_low'])
                    if source['timeframes'][timeframe].get('future_eps'):
                        all_eps.append(source['timeframes'][timeframe]['future_eps'])
                    if source['timeframes'][timeframe].get('recommended_action'):
                        all_actions.append(source['timeframes'][timeframe]['recommended_action'])
                    if source['timeframes'][timeframe].get('confidence'):
                        all_confidences.append(source['timeframes'][timeframe]['confidence'])
                
                if all_targets:
                    years_ahead = int(timeframe.split('_')[0])
                    target_date = datetime.now() + timedelta(days=365 * years_ahead)
                    
                    # 計算統計數據
                    target_mean = float(np.mean(all_targets))
                    target_median = float(np.median(all_targets))
                    target_std = float(np.std(all_targets))
                    
                    # 計算置信區間
                    confidence_interval = {
                        'lower_68': float(target_mean - target_std),
                        'upper_68': float(target_mean + target_std),
                        'lower_95': float(target_mean - 2 * target_std),
                        'upper_95': float(target_mean + 2 * target_std)
                    }
                    
                    # 確定建議動作（優先使用增強預估的建議）
                    recommended_action = 'Hold'
                    confidence = 'Medium'
                    if enhanced_estimates and timeframe in enhanced_estimates['timeframes']:
                        recommended_action = enhanced_estimates['timeframes'][timeframe]['recommended_action']
                        confidence = enhanced_estimates['timeframes'][timeframe]['confidence']
                    
                    results[timeframe] = {
                        'timeframe': f"{years_ahead}年後",
                        'target_date': target_date.strftime('%Y-%m-%d'),
                        'sources_count': len(valid_sources),
                        'target_mean': target_mean,
                        'target_median': target_median,
                        'target_high': float(np.max(all_highs)) if all_highs else None,
                        'target_low': float(np.min(all_lows)) if all_lows else None,
                        'target_std': target_std,
                        'potential_return': ((target_mean - current_price) / current_price * 100) if current_price else None,
                        'future_eps': float(np.mean(all_eps)) if all_eps else None,
                        'confidence_interval': confidence_interval,
                        'recommended_action': recommended_action,
                        'confidence': confidence,
                        'buy_zone': enhanced_estimates['timeframes'][timeframe]['buy_zone'] if enhanced_estimates else None,
                        'hold_zone': enhanced_estimates['timeframes'][timeframe]['hold_zone'] if enhanced_estimates else None,
                        'sell_zone': enhanced_estimates['timeframes'][timeframe]['sell_zone'] if enhanced_estimates else None
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
                    'analysis_status': 'success',
                    'enhanced_analysis': enhanced_estimates is not None
                }
            }
            
            # 添加歷史本益比數據（如果可用）
            historical_pe = self.calculate_enhanced_historical_pe_ratios(symbol)
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
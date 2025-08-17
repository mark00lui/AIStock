#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gemini AI 股票分析模組
使用 Google Gemini API 進行股票分析和建議
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiStockAnalyzer:
    """
    Gemini AI 股票分析器
    """
    
    def __init__(self, api_key: str):
        """
        初始化 Gemini 分析器
        
        Args:
            api_key (str): Gemini API 金鑰
        """
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
        self.headers = {
            "Content-Type": "application/json"
        }
        
    def _make_api_request(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        發送 API 請求到 Gemini
        
        Args:
            prompt (str): 發送給 Gemini 的提示詞
            
        Returns:
            Optional[Dict[str, Any]]: API 響應或 None
        """
        try:
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048
                }
            }
            
            url = f"{self.base_url}?key={self.api_key}"
            
            logger.info("發送請求到 Gemini API...")
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Gemini API 請求成功")
                return result
            else:
                logger.error(f"API 請求失敗: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("API 請求超時")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API 請求異常: {e}")
            return None
        except Exception as e:
            logger.error(f"未知錯誤: {e}")
            return None
    
    def _extract_json_from_response(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        從 Gemini 響應中提取 JSON 數據
        
        Args:
            response (Dict[str, Any]): Gemini API 響應
            
        Returns:
            Optional[Dict[str, Any]]: 解析的 JSON 數據或 None
        """
        try:
            if 'candidates' in response and len(response['candidates']) > 0:
                content = response['candidates'][0]['content']
                if 'parts' in content and len(content['parts']) > 0:
                    text = content['parts'][0]['text']
                    
                    # 嘗試提取 JSON 部分
                    start_idx = text.find('{')
                    end_idx = text.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx != 0:
                        json_str = text[start_idx:end_idx]
                        return json.loads(json_str)
                    else:
                        logger.error("響應中未找到有效的 JSON 格式")
                        return None
            else:
                logger.error("API 響應格式不正確")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析錯誤: {e}")
            return None
        except Exception as e:
            logger.error(f"提取 JSON 時發生錯誤: {e}")
            return None
    
    def analyze_stock(self, symbol: str, current_price: float = None, 
                     company_name: str = None) -> Dict[str, Any]:
        """
        分析股票並返回結構化結果
        
        Args:
            symbol (str): 股票代碼
            current_price (float, optional): 當前價格
            company_name (str, optional): 公司名稱
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        try:
            # 構建分析提示詞
            prompt = self._build_analysis_prompt(symbol, current_price, company_name)
            
            # 發送 API 請求
            response = self._make_api_request(prompt)
            
            if response is None:
                return self._create_error_response("API 請求失敗")
            
            # 提取 JSON 數據
            result = self._extract_json_from_response(response)
            
            if result is None:
                return self._create_error_response("無法解析 API 響應")
            
            # 添加元數據
            result['metadata'] = {
                'symbol': symbol,
                'analysis_date': datetime.now().isoformat(),
                'api_source': 'gemini',
                'status': 'success'
            }
            
            logger.info(f"股票 {symbol} 分析完成")
            return result
            
        except Exception as e:
            logger.error(f"分析股票 {symbol} 時發生錯誤: {e}")
            return self._create_error_response(f"分析過程發生錯誤: {str(e)}")
    
    def _build_analysis_prompt(self, symbol: str, current_price: float = None, 
                              company_name: str = None) -> str:
        """
        構建分析提示詞
        
        Args:
            symbol (str): 股票代碼
            current_price (float, optional): 當前價格
            company_name (str, optional): 公司名稱
            
        Returns:
            str: 完整的提示詞
        """
        company_info = f" ({company_name})" if company_name else ""
        price_info = f" 當前價格: ${current_price}" if current_price else ""
        
        prompt = f"""
請分析股票 {symbol}{company_info}{price_info}，並提供詳細的投資建議。

請以以下 JSON 格式返回分析結果：

{{
    "symbol": "{symbol}",
    "analysis_summary": {{
        "overall_sentiment": "bullish/bearish/neutral",
        "confidence_level": "high/medium/low",
        "risk_level": "low/medium/high",
        "time_horizon": "short_term/medium_term/long_term"
    }},
    "fundamental_analysis": {{
        "company_strength": "strong/moderate/weak",
        "financial_health": "excellent/good/fair/poor",
        "growth_potential": "high/medium/low",
        "competitive_position": "strong/moderate/weak",
        "key_strengths": ["優勢1", "優勢2", "優勢3"],
        "key_risks": ["風險1", "風險2", "風險3"]
    }},
    "technical_analysis": {{
        "trend_direction": "uptrend/downtrend/sideways",
        "support_level": "價格水平",
        "resistance_level": "價格水平",
        "technical_indicators": {{
            "rsi_signal": "oversold/neutral/overbought",
            "macd_signal": "bullish/bearish/neutral",
            "moving_averages": "bullish/bearish/neutral"
        }}
    }},
    "investment_recommendation": {{
        "action": "buy/hold/sell",
        "target_price": "目標價格",
        "stop_loss": "止損價格",
        "position_size": "small/medium/large",
        "entry_strategy": "立即買入/等待回調/分批建倉",
        "exit_strategy": "長期持有/設定止盈/技術止損"
    }},
    "market_context": {{
        "sector_outlook": "positive/neutral/negative",
        "market_sentiment": "bullish/bearish/neutral",
        "economic_factors": ["經濟因素1", "經濟因素2"],
        "sector_trends": ["行業趨勢1", "行業趨勢2"]
    }},
    "detailed_reasoning": {{
        "bullish_factors": ["看漲因素1", "看漲因素2", "看漲因素3"],
        "bearish_factors": ["看跌因素1", "看跌因素2"],
        "neutral_factors": ["中性因素1", "中性因素2"],
        "key_insights": ["關鍵洞察1", "關鍵洞察2", "關鍵洞察3"]
    }}
}}

請確保：
1. 分析基於最新的市場信息和公司基本面
2. 提供具體的價格目標和風險管理建議
3. 考慮宏觀經濟環境和行業趨勢
4. 給出明確的買入/持有/賣出建議
5. 返回格式必須是有效的 JSON

只返回 JSON 格式的結果，不要包含其他文字說明。
"""
        
        return prompt
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        創建錯誤響應
        
        Args:
            error_message (str): 錯誤信息
            
        Returns:
            Dict[str, Any]: 錯誤響應格式
        """
        return {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "api_source": "gemini",
                "status": "error"
            },
            "error": {
                "message": error_message,
                "type": "api_error"
            }
        }
    
    def get_stock_news_analysis(self, symbol: str, news_count: int = 5) -> Dict[str, Any]:
        """
        分析股票相關新聞
        
        Args:
            symbol (str): 股票代碼
            news_count (int): 分析的新聞數量
            
        Returns:
            Dict[str, Any]: 新聞分析結果
        """
        prompt = f"""
請分析 {symbol} 相關的最新新聞和市場動態，並提供新聞影響分析。

請以以下 JSON 格式返回分析結果：

{{
    "symbol": "{symbol}",
    "news_analysis": {{
        "overall_sentiment": "positive/negative/neutral",
        "news_impact": "high/medium/low",
        "key_events": ["重要事件1", "重要事件2"],
        "market_reaction": "預期市場反應"
    }},
    "recent_developments": [
        {{
            "event": "事件描述",
            "impact": "positive/negative/neutral",
            "significance": "high/medium/low",
            "description": "詳細說明"
        }}
    ],
    "sentiment_breakdown": {{
        "positive_news": ["正面新聞1", "正面新聞2"],
        "negative_news": ["負面新聞1", "負面新聞2"],
        "neutral_news": ["中性新聞1", "中性新聞2"]
    }}
}}

只返回 JSON 格式的結果。
"""
        
        try:
            response = self._make_api_request(prompt)
            
            if response is None:
                return self._create_error_response("新聞分析 API 請求失敗")
            
            result = self._extract_json_from_response(response)
            
            if result is None:
                return self._create_error_response("無法解析新聞分析響應")
            
            result['metadata'] = {
                'symbol': symbol,
                'analysis_date': datetime.now().isoformat(),
                'api_source': 'gemini',
                'analysis_type': 'news',
                'status': 'success'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"分析 {symbol} 新聞時發生錯誤: {e}")
            return self._create_error_response(f"新聞分析錯誤: {str(e)}")


def test_gemini_analyzer():
    """
    測試 Gemini 分析器
    """
    print("🧪 開始測試 Gemini 股票分析器...")
    
    # 請替換為您的實際 API 金鑰
    api_key = input("請輸入您的 Gemini API 金鑰: ").strip()
    
    if not api_key:
        print("❌ 未提供 API 金鑰，測試終止")
        return
    
    # 創建分析器實例
    analyzer = GeminiStockAnalyzer(api_key)
    
    # 測試股票列表
    test_stocks = [
        {"symbol": "AAPL", "price": 150.0, "name": "Apple Inc."},
        {"symbol": "GOOGL", "price": 2800.0, "name": "Alphabet Inc."},
        {"symbol": "TSLA", "price": 800.0, "name": "Tesla Inc."}
    ]
    
    print(f"\n📊 開始分析 {len(test_stocks)} 支股票...")
    
    for i, stock in enumerate(test_stocks, 1):
        print(f"\n🔍 分析股票 {i}/{len(test_stocks)}: {stock['symbol']}")
        
        try:
            # 進行股票分析
            result = analyzer.analyze_stock(
                symbol=stock['symbol'],
                current_price=stock['price'],
                company_name=stock['name']
            )
            
            if result.get('metadata', {}).get('status') == 'success':
                print(f"✅ {stock['symbol']} 分析成功")
                
                # 顯示關鍵信息
                analysis = result.get('analysis_summary', {})
                recommendation = result.get('investment_recommendation', {})
                
                print(f"   整體情緒: {analysis.get('overall_sentiment', 'N/A')}")
                print(f"   信心等級: {analysis.get('confidence_level', 'N/A')}")
                print(f"   建議動作: {recommendation.get('action', 'N/A')}")
                print(f"   目標價格: {recommendation.get('target_price', 'N/A')}")
                
                # 保存結果到文件
                filename = f"gemini_analysis_{stock['symbol']}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"   📄 結果已保存到: {filename}")
                
            else:
                print(f"❌ {stock['symbol']} 分析失敗")
                error_msg = result.get('error', {}).get('message', '未知錯誤')
                print(f"   錯誤信息: {error_msg}")
            
            # 添加延遲避免 API 限制
            if i < len(test_stocks):
                print("   ⏳ 等待 3 秒後繼續...")
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ 分析 {stock['symbol']} 時發生異常: {e}")
    
    print(f"\n🎉 Gemini 分析器測試完成！")
    print("📁 請檢查當前目錄中的 JSON 文件查看詳細結果")


if __name__ == "__main__":
    test_gemini_analyzer()

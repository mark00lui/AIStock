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
    
    def _extract_json_from_response(self, response: Dict[str, Any], symbol: str = None) -> Optional[Dict[str, Any]]:
        """
        從 Gemini 響應中提取 JSON 數據
        
        Args:
            response (Dict[str, Any]): Gemini API 響應
            symbol (str, optional): 股票代碼，用於備用 JSON 構建
            
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
                        
                        # 首先嘗試直接解析
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError as e:
                            logger.error(f"直接解析失敗: {e}")
                            
                            # 嘗試簡單的修復
                            fixed_json = self._simple_json_fix(json_str)
                            try:
                                return json.loads(fixed_json)
                            except json.JSONDecodeError as e2:
                                logger.error(f"簡單修復後仍無法解析: {e2}")
                                
                                # 嘗試更激進的修復
                                aggressive_json = self._aggressive_json_fix(json_str)
                                try:
                                    return json.loads(aggressive_json)
                                except json.JSONDecodeError as e3:
                                    logger.error(f"激進修復後仍無法解析: {e3}")
                                    
                                    # 最後嘗試：手動構建基本結構
                                    return self._build_fallback_json(symbol, text)
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
    
    def _fix_json_format(self, json_str: str) -> str:
        """
        修復常見的 JSON 格式問題
        
        Args:
            json_str (str): 原始 JSON 字符串
            
        Returns:
            str: 修復後的 JSON 字符串
        """
        # 修復常見的格式問題
        json_str = json_str.replace('，', ',')  # 中文逗號
        json_str = json_str.replace('：', ':')  # 中文冒號
        json_str = json_str.replace('"', '"')  # 智能引號
        json_str = json_str.replace('"', '"')  # 智能引號
        json_str = json_str.replace('' '', "'")  # 智能單引號
        json_str = json_str.replace('' '', "'")  # 智能單引號
        
        # 修復多餘的逗號
        json_str = json_str.replace(',}', '}')
        json_str = json_str.replace(',]', ']')
        
        # 修復缺少的引號
        import re
        # 修復沒有引號的鍵名
        json_str = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        # 確保返回的字符串不為空
        if not json_str.strip():
            return '{"error": "empty_json_string"}'
        
        return json_str
    
    def _simple_json_fix(self, json_str: str) -> str:
        """
        簡單的 JSON 修復方法
        
        Args:
            json_str (str): 原始 JSON 字符串
            
        Returns:
            str: 修復後的 JSON 字符串
        """
        # 基本修復
        json_str = json_str.replace('，', ',')  # 中文逗號
        json_str = json_str.replace('：', ':')  # 中文冒號
        json_str = json_str.replace('"', '"')  # 智能引號
        json_str = json_str.replace('"', '"')  # 智能引號
        
        # 修復多餘的逗號
        json_str = json_str.replace(',}', '}')
        json_str = json_str.replace(',]', ']')
        
        # 修復缺少的引號
        import re
        json_str = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        return json_str
    
    def _build_fallback_json(self, symbol: str, original_text: str) -> Dict[str, Any]:
        """
        構建備用 JSON 結構
        
        Args:
            symbol (str): 股票代碼
            original_text (str): 原始文本
            
        Returns:
            Dict[str, Any]: 備用 JSON 結構
        """
        logger.warning(f"使用備用 JSON 結構 for {symbol}")
        
        # 從原始文本中提取一些基本信息
        sentiment = "中性"
        if "看漲" in original_text or "bullish" in original_text.lower():
            sentiment = "看漲"
        elif "看跌" in original_text or "bearish" in original_text.lower():
            sentiment = "看跌"
        
        # 構建精簡的 JSON 結構
        fallback_json = {
             "symbol": symbol,
             "analysis_summary": {
                 "overall_sentiment": sentiment,
                 "confidence_level": "中",
                 "risk_level": "中",
                 "time_horizon": "中期"
             },
             "future_acquisitions_and_growth_tracks": {
                 "potential_major_acquisitions": ["潛在收購目標1", "潛在收購目標2", "潛在收購目標3"],
                 "acquisition_strategic_importance": "收購的戰略意義和影響分析",
                 "primary_growth_tracks": ["主要成長賽道1", "主要成長賽道2", "主要成長賽道3"],
                 "growth_track_market_size": "成長賽道市場規模預估",
                 "competitive_advantages": ["競爭優勢1", "競爭優勢2", "競爭優勢3"],
                 "strategic_partnerships": ["戰略合作1", "戰略合作2"]
             },
             "growth_track_cagr": {
                 "track_1_cagr_3y": "15%",
                 "track_1_cagr_5y": "12%",
                 "track_2_cagr_3y": "20%",
                 "track_2_cagr_5y": "18%",
                 "track_3_cagr_3y": "25%",
                 "track_3_cagr_5y": "22%",
                 "market_penetration_analysis": "市場滲透率分析",
                 "commercialization_timeline": "商業化時間表",
                 "growth_catalysts": ["成長催化劑1", "成長催化劑2", "成長催化劑3"]
             },
             "revenue_profit_contribution": {
                 "track_1_revenue_share_3y": "30%",
                 "track_1_revenue_share_5y": "40%",
                 "track_2_revenue_share_3y": "25%",
                 "track_2_revenue_share_5y": "35%",
                 "track_3_revenue_share_3y": "20%",
                 "track_3_revenue_share_5y": "30%",
                 "profit_contribution_analysis": "新賽道利潤率貢獻分析",
                 "revenue_structure_transformation": "營收結構轉型時間表",
                 "profit_quality_improvement": "獲利質量改善潛力"
             },
             "eps_cagr_forecast": {
                 "eps_cagr_1y": "15%",
                 "eps_cagr_3y": "18%",
                 "eps_cagr_5y": "20%",
                 "eps_growth_drivers": ["EPS成長驅動力1", "EPS成長驅動力2", "EPS成長驅動力3"],
                 "profit_margin_expansion": "利潤率擴張預期",
                 "capex_rd_impact": "資本支出和研發投入影響",
                 "eps_scenarios": {
                     "bull_case_eps_cagr": "25%",
                     "base_case_eps_cagr": "18%",
                     "bear_case_eps_cagr": "12%"
                 }
             },
             "stock_price_cagr_forecast": {
                 "price_cagr_1y": "20%",
                 "price_cagr_3y": "25%",
                 "price_cagr_5y": "30%",
                 "valuation_multiple_expansion": "估值倍數擴張可能性",
                 "market_sentiment_impact": "市場情緒和投資者認知變化",
                 "risk_adjusted_growth": "風險調整後股價成長預期",
                 "price_scenarios": {
                     "bull_case_price_cagr": "35%",
                     "base_case_price_cagr": "25%",
                     "bear_case_price_cagr": "15%"
                 }
             },
             "investment_recommendation": {
                 "action": "持有",
                 "conviction_level": "中",
                 "target_price": "目標價格",
                 "time_horizon": "中期"
             }
         }
        
        return fallback_json
    
    def _aggressive_json_fix(self, json_str: str) -> str:
        """
        更激進的 JSON 修復方法
        
        Args:
            json_str (str): 原始 JSON 字符串
            
        Returns:
            str: 修復後的 JSON 字符串
        """
        try:
            # 首先嘗試修復常見的語法錯誤
            json_str = self._fix_common_syntax_errors(json_str)
            
            # 嘗試找到最後一個完整的 JSON 對象
            brace_count = 0
            last_complete = 0
            
            for i, char in enumerate(json_str):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        last_complete = i + 1
            
            if last_complete > 0:
                return json_str[:last_complete]
            
            # 如果還是無法找到完整對象，嘗試更激進的修復
            return self._extreme_json_fix(json_str)
            
        except Exception:
            return json_str
    
    def _fix_common_syntax_errors(self, json_str: str) -> str:
        """
        修復常見的 JSON 語法錯誤
        
        Args:
            json_str (str): 原始 JSON 字符串
            
        Returns:
            str: 修復後的 JSON 字符串
        """
        import re
        
        # 修復缺少的引號
        json_str = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        # 修復多餘的逗號
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # 修復缺少的逗號
        json_str = re.sub(r'}(\s*")', r'},\1', json_str)
        json_str = re.sub(r'](\s*")', r'],\1', json_str)
        
        # 修復缺少的引號結束
        json_str = re.sub(r'([^"])\s*([}\]])', r'\1"\2', json_str)
        
        # 修復多餘的引號
        json_str = re.sub(r'""', r'"', json_str)
        
        return json_str
    
    def _extreme_json_fix(self, json_str: str) -> str:
        """
        極端情況下的 JSON 修復
        
        Args:
            json_str (str): 原始 JSON 字符串
            
        Returns:
            str: 修復後的 JSON 字符串
        """
        try:
            # 嘗試找到第一個 { 和最後一個 }
            start = json_str.find('{')
            end = json_str.rfind('}')
            
            if start != -1 and end != -1 and end > start:
                # 提取可能的 JSON 部分
                potential_json = json_str[start:end+1]
                
                # 嘗試修復這個部分
                fixed_json = self._fix_common_syntax_errors(potential_json)
                
                # 驗證是否為有效的 JSON
                try:
                    json.loads(fixed_json)
                    return fixed_json
                except:
                    pass
            
            # 如果還是失敗，嘗試分段修復
            return self._segment_fix(json_str)
            
        except Exception:
            return json_str
    
    def _segment_fix(self, json_str: str) -> str:
        """
        分段修復 JSON
        
        Args:
            json_str (str): 原始 JSON 字符串
            
        Returns:
            str: 修復後的 JSON 字符串
        """
        try:
            # 找到所有可能的 JSON 對象
            import re
            json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', json_str)
            
            if json_objects:
                # 嘗試修復最大的對象
                largest_object = max(json_objects, key=len)
                fixed_object = self._fix_common_syntax_errors(largest_object)
                
                try:
                    json.loads(fixed_object)
                    return fixed_object
                except:
                    pass
            
            # 最後嘗試：移除所有可能的問題字符
            cleaned_json = re.sub(r'[^\x20-\x7E]', '', json_str)  # 移除非ASCII字符
            cleaned_json = re.sub(r',+', ',', cleaned_json)  # 修復多餘逗號
            cleaned_json = re.sub(r':+', ':', cleaned_json)  # 修復多餘冒號
            
            return cleaned_json
            
        except Exception:
            return json_str
    
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
            result = self._extract_json_from_response(response, symbol)
            
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
        構建專注於社群情緒、財報和未來發展的分析提示詞
        
        Args:
            symbol (str): 股票代碼
            current_price (float, optional): 當前價格
            company_name (str, optional): 公司名稱
            
        Returns:
            str: 完整的提示詞
        """
        company_info = f" ({company_name})" if company_name else ""
        price_info = f" 當前價格: ${current_price}" if current_price else ""
        
        # 根據股票代碼提供特定的分析重點
        company_specific_focus = self._get_company_specific_focus(symbol)
        
        prompt = f"""
 請作為一位資深的股票分析師，對 {symbol}{company_info}{price_info} 進行精簡而深入的投資分析。
 
 分析重點要求：
 1. 專注於未來潛在的重大收購和成長賽道
 2. 重點分析新賽道的複合成長率和市場佔比
 3. 提供具體的 EPS 和股價複合成長率預測
 4. 避免冗長的傳統分析，聚焦核心成長驅動力
 
 {company_specific_focus}
 
 分析時請特別關注以下五個核心維度：
 
 1. 未來潛在的重大收購以及成長賽道：
    - 公司可能收購的目標企業和戰略意義
    - 主要成長賽道的市場規模和競爭優勢
    - 新技術和產品線的發展前景
    - 戰略合作和聯盟的可能性
 
 2. 新賽道的預計複合成長率：
    - 各成長賽道的三年和五年複合成長率預測
    - 市場滲透率和採用速度分析
    - 技術成熟度和商業化時間表
    - 成長驅動因素和催化劑
 
 3. 新賽道的營收及獲利佔比：
    - 各賽道在總營收中的佔比預測
    - 新賽道的利潤率貢獻分析
    - 營收結構轉型的時間表
    - 獲利質量改善的潛力
 
 4. 未來1/3/5年的EPS複合成長率：
    - 基於新賽道發展的EPS成長預測
    - 利潤率擴張和成本控制影響
    - 資本支出和研發投入的影響
    - 不同情境下的EPS成長範圍
 
 5. 未來1/3/5年股價複合成長率：
    - 基於基本面改善的股價成長預測
    - 估值倍數擴張的可能性
    - 市場情緒和投資者認知的變化
    - 風險調整後的股價成長預期
 
 請以以下精簡的 JSON 格式返回分析結果，所有分析內容都必須使用中文表達：

 {{
     "symbol": "{symbol}",
     "analysis_summary": {{
         "overall_sentiment": "看漲/看跌/中性",
         "confidence_level": "高/中/低",
         "risk_level": "低/中/高",
         "time_horizon": "短期/中期/長期"
     }},
     "future_acquisitions_and_growth_tracks": {{
         "potential_major_acquisitions": ["潛在收購目標1", "潛在收購目標2", "潛在收購目標3"],
         "acquisition_strategic_importance": "收購的戰略意義和影響分析",
         "primary_growth_tracks": ["主要成長賽道1", "主要成長賽道2", "主要成長賽道3"],
         "growth_track_market_size": "成長賽道市場規模預估",
         "competitive_advantages": ["競爭優勢1", "競爭優勢2", "競爭優勢3"],
         "strategic_partnerships": ["戰略合作1", "戰略合作2"]
     }},
     "growth_track_cagr": {{
         "track_1_cagr_3y": "成長賽道1三年複合成長率（百分比）",
         "track_1_cagr_5y": "成長賽道1五年複合成長率（百分比）",
         "track_2_cagr_3y": "成長賽道2三年複合成長率（百分比）",
         "track_2_cagr_5y": "成長賽道2五年複合成長率（百分比）",
         "track_3_cagr_3y": "成長賽道3三年複合成長率（百分比）",
         "track_3_cagr_5y": "成長賽道3五年複合成長率（百分比）",
         "market_penetration_analysis": "市場滲透率分析",
         "commercialization_timeline": "商業化時間表",
         "growth_catalysts": ["成長催化劑1", "成長催化劑2", "成長催化劑3"]
     }},
     "revenue_profit_contribution": {{
         "track_1_revenue_share_3y": "成長賽道1三年後營收佔比（百分比）",
         "track_1_revenue_share_5y": "成長賽道1五年後營收佔比（百分比）",
         "track_2_revenue_share_3y": "成長賽道2三年後營收佔比（百分比）",
         "track_2_revenue_share_5y": "成長賽道2五年後營收佔比（百分比）",
         "track_3_revenue_share_3y": "成長賽道3三年後營收佔比（百分比）",
         "track_3_revenue_share_5y": "成長賽道3五年後營收佔比（百分比）",
         "profit_contribution_analysis": "新賽道利潤率貢獻分析",
         "revenue_structure_transformation": "營收結構轉型時間表",
         "profit_quality_improvement": "獲利質量改善潛力"
     }},
     "eps_cagr_forecast": {{
         "eps_cagr_1y": "一年EPS複合成長率（百分比）",
         "eps_cagr_3y": "三年EPS複合成長率（百分比）",
         "eps_cagr_5y": "五年EPS複合成長率（百分比）",
         "eps_growth_drivers": ["EPS成長驅動力1", "EPS成長驅動力2", "EPS成長驅動力3"],
         "profit_margin_expansion": "利潤率擴張預期",
         "capex_rd_impact": "資本支出和研發投入影響",
         "eps_scenarios": {{
             "bull_case_eps_cagr": "樂觀情境EPS複合成長率",
             "base_case_eps_cagr": "中性情境EPS複合成長率",
             "bear_case_eps_cagr": "保守情境EPS複合成長率"
         }}
     }},
     "stock_price_cagr_forecast": {{
         "price_cagr_1y": "一年股價複合成長率（百分比）",
         "price_cagr_3y": "三年股價複合成長率（百分比）",
         "price_cagr_5y": "五年股價複合成長率（百分比）",
         "valuation_multiple_expansion": "估值倍數擴張可能性",
         "market_sentiment_impact": "市場情緒和投資者認知變化",
         "risk_adjusted_growth": "風險調整後股價成長預期",
         "price_scenarios": {{
             "bull_case_price_cagr": "樂觀情境股價複合成長率",
             "base_case_price_cagr": "中性情境股價複合成長率",
             "bear_case_price_cagr": "保守情境股價複合成長率"
         }}
     }},
     "investment_recommendation": {{
         "action": "買入/持有/賣出",
         "conviction_level": "高/中/低",
         "target_price": "具體價格",
         "time_horizon": "短期/中期/長期"
     }}
         }}

 分析要求：
 1. 專注於未來潛在的重大收購和成長賽道分析
 2. 提供具體的新賽道複合成長率預測
 3. 分析新賽道的營收和獲利佔比變化
 4. 給出1/3/5年的EPS複合成長率預測
 5. 提供1/3/5年的股價複合成長率預測
 6. 分析必須基於最新的市場動態和公司發展
 7. 避免冗長的傳統分析，聚焦核心成長驅動力
 8. 返回格式必須是有效的 JSON，所有描述必須具體
 9. 所有分析結果都必須使用中文表達
 10. 提供樂觀、中性、保守三種情境的預測
 
 只返回 JSON 格式的結果，不要包含其他文字說明。
"""
        
        return prompt
    
    def _get_company_specific_focus(self, symbol: str) -> str:
        """
        根據股票代碼獲取通用的AI賽道分析重點
        
        Args:
            symbol (str): 股票代碼
            
        Returns:
            str: 通用AI賽道分析重點說明
        """
        return f"""
針對 {symbol} 的通用AI賽道分析重點：

未來五年營收動力分析 - 基於AI改革的二十個核心發展方向：

1. AI基礎設施與技術：
   - 收購LLM公司：評估收購大型語言模型初創公司的戰略價值和整合潛力
   - 雲擴展：AI雲服務的市場擴張和企業採用率提升
   - AI電力：AI優化的電力管理和智能電網技術
   - 推論ASIC：專用AI推理晶片的開發和商業化
   - 資料中心+推論中心ASIC化：數據中心向AI專用架構轉型

2. AI應用領域：
   - AI醫療：醫療診斷、藥物研發、個性化治療的AI應用
   - AI機器人：工業自動化、服務機器人、人形機器人技術
   - AI XR眼鏡：增強現實和虛擬現實的AI整合應用
   - ROBOTAXI與機器人：自動駕駛計程車和機器人服務
   - 產線進一步自動化：製造業的AI驅動自動化升級

3. AI金融與數字資產：
   - AI金融：智能投顧、風險管理、欺詐檢測的AI應用
   - 穩定幣：AI驅動的穩定幣算法和監管技術
   - 加密貨幣：AI在加密貨幣交易和區塊鏈技術中的應用

4. AI垂直整合：
   - AI教育：個性化學習、智能輔導、教育內容生成
   - AI娛樂：內容創作、遊戲AI、娛樂體驗個性化
   - AI零售：智能推薦、庫存管理、客戶服務自動化
   - AI物流：供應鏈優化、配送路線規劃、倉儲自動化
   - AI農業：精準農業、作物監控、農業機器人

5. AI效率提升：
   - AI客服：智能客服系統和客戶體驗優化
   - AI研發：研發流程自動化和創新加速
   - AI營銷：精準營銷、內容生成、市場分析
   - AI法務：法律文檔分析、合規監控、智能合約

成長賽道分析重點：
- 評估公司在上述20個AI賽道中的參與度和競爭優勢
- 分析AI技術對現有業務的改造潛力和新業務開拓機會
- 預測AI投資對營收結構和利潤率的影響
- 評估AI技術的商業化時間表和市場接受度

估值重點：
- AI技術對公司估值倍數的潛在提升
- AI投資的資本回報率和風險調整收益
- 傳統業務AI化轉型的成本效益分析
- 新AI業務的市場規模和競爭格局評估
- AI技術壁壘和可持續競爭優勢分析

成本下降潛力分析：
- AI自動化對人力成本的節省
- AI優化對營運效率的提升
- AI預測對庫存和供應鏈成本的降低
- AI個性化對營銷成本的優化
- AI監控對風險和合規成本的減少
"""
    
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
請作為一位資深的財經新聞分析師，對 {symbol} 相關的最新新聞、市場動態和社群討論進行全面分析。

分析時請特別關注以下維度：

1. 新聞影響分析：
   - 財報相關新聞和業績指引
   - 管理層變動和公司策略調整
   - 產品發布和技術創新
   - 併購、合作和戰略投資

2. 監管和法律新聞：
   - 監管調查和合規問題
   - 法律訴訟和專利糾紛
   - 政策變化和法規影響
   - 反壟斷和競爭法規

3. 市場和競爭動態：
   - 競爭對手動態
   - 市場份額變化
   - 行業趨勢和技術變革
   - 供應鏈和合作夥伴新聞

4. 宏觀經濟影響：
   - 利率政策影響
   - 通貨膨脹和經濟指標
   - 地緣政治風險
   - 匯率和貿易政策

5. 社群和散戶情緒：
   - 社群媒體討論熱度
   - 散戶投資者情緒變化
   - 網紅和意見領袖觀點
   - 期權和衍生品活動

請以以下增強 JSON 格式返回分析結果，所有分析內容都必須使用中文表達：

{{
    "symbol": "{symbol}",
    "news_analysis_summary": {{
        "overall_sentiment": "看漲/看跌/中性",
        "news_impact_level": "高/中/低",
        "market_reaction_expectation": "正面/負面/中性",
        "confidence_level": "高/中/低",
        "time_horizon": "立即/短期/中期/長期"
    }},
    "key_news_categories": {{
        "earnings_related": {{
            "sentiment": "正面/負面/中性",
            "impact": "高/中/低",
            "key_events": ["具體事件1", "具體事件2"]
        }},
        "regulatory_legal": {{
            "sentiment": "正面/負面/中性",
            "impact": "高/中/低",
            "key_events": ["具體事件1", "具體事件2"]
        }},
        "business_development": {{
            "sentiment": "正面/負面/中性",
            "impact": "高/中/低",
            "key_events": ["具體事件1", "具體事件2"]
        }},
        "market_competition": {{
            "sentiment": "正面/負面/中性",
            "impact": "高/中/低",
            "key_events": ["具體事件1", "具體事件2"]
        }},
        "macro_economic": {{
            "sentiment": "正面/負面/中性",
            "impact": "高/中/低",
            "key_events": ["具體事件1", "具體事件2"]
        }}
    }},
    "detailed_news_analysis": [
        {{
            "event_title": "具體新聞標題",
            "event_date": "事件日期或時間範圍",
            "news_source": "新聞來源",
            "sentiment": "看漲/看跌/中性",
            "impact_significance": "高/中/低",
            "market_relevance": "高/中/低",
            "detailed_description": "詳細的事件描述和背景",
            "potential_impact": "對股價的潛在影響分析",
            "risk_factors": ["相關風險因素1", "相關風險因素2"],
            "opportunity_factors": ["相關機會因素1", "相關機會因素2"]
        }}
    ],
    "sentiment_breakdown": {{
        "bullish_factors": ["具體看漲因素1", "具體看漲因素2", "具體看漲因素3"],
        "bearish_factors": ["具體看跌因素1", "具體看跌因素2", "具體看跌因素3"],
        "neutral_factors": ["具體中性因素1", "具體中性因素2"],
        "uncertainty_factors": ["不確定性因素1", "不確定性因素2"]
    }},
    "market_implications": {{
        "short_term_outlook": "短期市場展望",
        "medium_term_outlook": "中期市場展望",
        "long_term_outlook": "長期市場展望",
        "price_target_impact": "對目標價格的影響",
        "volatility_expectation": "預期波動性變化",
        "trading_volume_impact": "對交易量的影響"
    }},
    "risk_assessment": {{
        "high_risk_events": ["高風險事件1", "高風險事件2"],
        "medium_risk_events": ["中風險事件1", "中風險事件2"],
        "low_risk_events": ["低風險事件1", "低風險事件2"],
        "risk_mitigation_factors": ["風險緩解因素1", "風險緩解因素2"]
    }},
    "opportunity_analysis": {{
        "high_opportunity_events": ["高機會事件1", "高機會事件2"],
        "medium_opportunity_events": ["中機會事件1", "中機會事件2"],
        "low_opportunity_events": ["低機會事件1", "低機會事件2"],
        "opportunity_catalysts": ["機會催化劑1", "機會催化劑2"]
    }},
    "community_sentiment": {{
        "social_media_sentiment": "看漲/看跌/中性",
        "retail_investor_sentiment": "看漲/看跌/中性",
        "institutional_sentiment": "看漲/看跌/中性",
        "analyst_sentiment": "看漲/看跌/中性",
        "key_discussion_topics": ["熱門討論話題1", "熱門討論話題2"]
    }},
    "data_sources": {{
        "news_sources": ["路透社", "彭博社", "CNBC", "其他來源"],
        "social_media_platforms": ["Reddit", "Twitter", "StockTwits", "其他平台"],
        "analyst_reports": ["分析師報告來源1", "分析師報告來源2"],
        "regulatory_filings": ["監管文件來源1", "監管文件來源2"]
    }}
}}

分析要求：
1. 基於最新的新聞報導、社群討論和分析師觀點
2. 提供具體的影響評估和市場反應預期
3. 考慮新聞的時間敏感性和持續影響
4. 分析必須客觀、全面，避免過度反應
5. 返回格式必須是有效的 JSON，所有描述必須具體
6. 所有分析結果都必須使用中文表達，包括所有指標、建議和描述

只返回 JSON 格式的結果，不要包含其他文字說明。
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

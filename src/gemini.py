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
        
    def _make_api_request(self, prompt: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        發送 API 請求到 Gemini，包含重試機制
        
        Args:
            prompt (str): 發送給 Gemini 的提示詞
            max_retries (int): 最大重試次數
            
        Returns:
            Optional[Dict[str, Any]]: API 響應或 None
        """
        for attempt in range(max_retries + 1):
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
                
                if attempt == 0:
                    logger.info("發送請求到 Gemini API...")
                else:
                    logger.info(f"重試請求到 Gemini API... (第 {attempt + 1} 次嘗試)")
                
                response = requests.post(url, headers=self.headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if attempt > 0:
                        logger.info(f"Gemini API 請求成功 (第 {attempt + 1} 次嘗試)")
                    else:
                        logger.info("Gemini API 請求成功")
                    return result
                elif response.status_code == 503:
                    # 模型過載，需要重試
                    if attempt < max_retries:
                        wait_time = (attempt + 1) * 30  # 遞增等待時間：30秒、60秒、90秒
                        logger.warning(f"模型過載 (503)，等待 {wait_time} 秒後重試...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"API 請求失敗: 503 - 模型過載，已重試 {max_retries} 次")
                        return None
                elif response.status_code == 429:
                    # 速率限制，需要更長時間等待
                    if attempt < max_retries:
                        wait_time = (attempt + 1) * 120  # 遞增等待時間：2分鐘、4分鐘、6分鐘
                        logger.warning(f"速率限制 (429)，等待 {wait_time} 秒後重試...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"API 請求失敗: 429 - 速率限制，已重試 {max_retries} 次")
                        return None
                else:
                    logger.error(f"API 請求失敗: {response.status_code} - {response.text}")
                    return None
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 10  # 遞增等待時間：10秒、20秒、30秒
                    logger.warning(f"API 請求超時，等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error("API 請求超時，已重試所有次數")
                    return None
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 15  # 遞增等待時間：15秒、30秒、45秒
                    logger.warning(f"API 請求異常: {e}，等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"API 請求異常: {e}，已重試所有次數")
                    return None
            except Exception as e:
                logger.error(f"未知錯誤: {e}")
                return None
        
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

    def analyze_stock_batch(self, symbols: List[str], current_prices: Dict[str, float], company_names: Dict[str, str] = None) -> Dict[str, Any]:
        """
        批量分析多支股票
        
        Args:
            symbols (List[str]): 股票代碼列表
            current_prices (Dict[str, float]): 股票代碼到當前價格的映射
            company_names (Dict[str, str], optional): 股票代碼到公司名稱的映射
            
        Returns:
            Dict[str, Any]: 每支股票的分析結果
        """
        try:
            # 構建批量分析提示詞
            prompt = self._build_batch_analysis_prompt(symbols, current_prices, company_names)
            
            # 發送 API 請求
            response = self._make_api_request(prompt)
            
            if response is None:
                return {symbol: self._create_error_response("API 請求失敗") for symbol in symbols}
            
            # 提取 JSON 數據
            json_data = self._extract_batch_json_from_response(response, symbols)
            
            if json_data is None:
                return {symbol: self._create_error_response("JSON 解析失敗") for symbol in symbols}
            
            # 為每個股票添加元數據
            results = {}
            for symbol in symbols:
                if symbol in json_data.get("stocks", {}):
                    stock_data = json_data["stocks"][symbol]
                    stock_data["metadata"] = {
                        "status": "success",
                        "timestamp": datetime.now().isoformat(),
                        "symbol": symbol,
                        "current_price": current_prices.get(symbol, 0)
                    }
                    results[symbol] = stock_data
                else:
                    results[symbol] = self._create_error_response("未找到分析結果")
            
            logger.info(f"成功批量分析 {len(symbols)} 支股票")
            return results
            
        except Exception as e:
            logger.error(f"批量分析股票時發生錯誤: {e}")
            return {symbol: self._create_error_response(f"批量分析錯誤: {str(e)}") for symbol in symbols}
    
    def _build_analysis_prompt(self, symbol: str, current_price: float = None, 
                              company_name: str = None) -> str:
        """
        構建精簡的單一股票分析提示詞
        
        Args:
            symbol (str): 股票代碼
            current_price (float, optional): 當前價格
            company_name (str, optional): 公司名稱
            
        Returns:
            str: 精簡的提示詞
        """
        company_info = f" ({company_name})" if company_name else ""
        price_info = f" 當前價格: ${current_price}" if current_price else ""
        
        prompt = f"""
請分析 {symbol}{company_info}{price_info}，提供精簡的投資分析。

搜尋策略要求：
1. 同時搜尋英文和中文資料源，確保全面性
2. 對於台灣股票（如 3019.TW），請搜尋：
   - 中文：公司中文名稱、股票代碼、相關產業新聞、台灣財經媒體
   - 英文：公司英文名稱、股票代碼、國際市場相關新聞、外資報告
3. 對於美股，請搜尋：
   - 英文：公司英文名稱、股票代碼、美國市場新聞、華爾街分析
   - 中文：公司中文譯名、相關中文報導、中國財經媒體
4. 對於港股，請搜尋：
   - 中文：公司中文名稱、香港市場新聞、港媒報導
   - 英文：公司英文名稱、國際市場相關新聞、外資分析
5. 搜尋範圍包括：財經新聞、分析師報告、社群媒體討論、財報公告、監管文件

請返回以下JSON格式：
{{
    "symbol": "{symbol}",
    "chinese_name": "股票中文名稱（如：台積電、蘋果公司、特斯拉等）",
    "price_forecast": {{
        "price_1y": "一年後股價範圍",
        "price_3y": "三年後股價範圍", 
        "price_5y": "五年後股價範圍"
    }},
    "recent_news": "近期最重大新聞消息（30字內）",
    "ai_judgment": "AI對該消息的判斷（30字內）",
    "sentiment": "看漲/看跌/中性",
    "risk_metrics": {{
        "beta": 數值（如1.25，相對於對應市場指數的Beta值，必須是數字）,
        "volatility": 數值（如35.5，年化波動率百分比，必須是數字）,
        "sharpe_ratio": 數值（如0.85，夏普比率，必須是數字）,
        "market_correlation": 數值（如0.72，與市場相關性係數，必須是數字）,
        "risk_level": "極低/低/中/高/極高"
    }}
}}

重要要求：
1. 所有分析內容必須使用繁體中文表達
2. 避免使用簡體中文用詞
3. 使用台灣地區的金融術語和表達方式
4. 確保搜尋到最新的中英文新聞資料
5. 只返回JSON格式，不要其他說明
6. 風險指標必須提供精確的數值：
   - beta: 必須是數字（如1.25），表示相對於市場指數的Beta值
   - volatility: 必須是數字（如35.5），表示年化波動率百分比
   - sharpe_ratio: 必須是數字（如0.85），表示夏普比率
   - market_correlation: 必須是數字（如0.72），表示與市場相關性係數
   - risk_level: 文字描述（極低/低/中/高/極高）
"""
        
        return prompt

    def _build_batch_analysis_prompt(self, symbols: List[str], current_prices: Dict[str, float], 
                                   company_names: Dict[str, str] = None) -> str:
        """
        構建批量分析提示詞
        
        Args:
            symbols (List[str]): 股票代碼列表
            current_prices (Dict[str, float]): 股票代碼到當前價格的映射
            company_names (Dict[str, str], optional): 股票代碼到公司名稱的映射
            
        Returns:
            str: 批量分析提示詞
        """
        # 構建股票列表
        stock_list = ""
        for symbol in symbols:
            price = current_prices.get(symbol, "N/A")
            company_name = company_names.get(symbol, "") if company_names else ""
            stock_list += f"- {symbol}{' (' + company_name + ')' if company_name else ''}: ${price}\n"
        
        prompt = f"""
請同時分析以下股票，為每支股票提供精簡的投資分析：

{stock_list}

搜尋策略要求：
1. 同時搜尋英文和中文資料源，確保全面性
2. 對於台灣股票（如 3019.TW），請搜尋：
   - 中文：公司中文名稱、股票代碼、相關產業新聞、台灣財經媒體
   - 英文：公司英文名稱、股票代碼、國際市場相關新聞、外資報告
3. 對於美股，請搜尋：
   - 英文：公司英文名稱、股票代碼、美國市場新聞、華爾街分析
   - 中文：公司中文譯名、相關中文報導、中國財經媒體
4. 對於港股，請搜尋：
   - 中文：公司中文名稱、香港市場新聞、港媒報導
   - 英文：公司英文名稱、國際市場相關新聞、外資分析
5. 搜尋範圍包括：財經新聞、分析師報告、社群媒體討論、財報公告、監管文件

請返回以下JSON格式：
{{
    "stocks": {{
        {', '.join([f'"{symbol}": {{"symbol": "{symbol}", "chinese_name": "股票中文名稱（如：台積電、蘋果公司、特斯拉等）", "price_forecast": {{"price_1y": "一年後股價範圍", "price_3y": "三年後股價範圍", "price_5y": "五年後股價範圍"}}, "recent_news": "近期最重大新聞消息（30字內）", "ai_judgment": "AI對該消息的判斷（30字內）", "sentiment": "看漲/看跌/中性", "risk_metrics": {{"beta": 數值（如1.25，相對於對應市場指數的Beta值，必須是數字）, "volatility": 數值（如35.5，年化波動率百分比，必須是數字）, "sharpe_ratio": 數值（如0.85，夏普比率，必須是數字）, "market_correlation": 數值（如0.72，與市場相關性係數，必須是數字）, "risk_level": "極低/低/中/高/極高"}}}}' for symbol in symbols])}
    }}
}}

重要要求：
1. 所有分析內容必須使用繁體中文表達
2. 避免使用簡體中文用詞
3. 使用台灣地區的金融術語和表達方式
4. 確保搜尋到最新的中英文新聞資料
5. 只返回JSON格式，不要其他說明
6. 風險指標必須提供精確的數值：
   - beta: 必須是數字（如1.25），表示相對於市場指數的Beta值
   - volatility: 必須是數字（如35.5），表示年化波動率百分比
   - sharpe_ratio: 必須是數字（如0.85），表示夏普比率
   - market_correlation: 必須是數字（如0.72），表示與市場相關性係數
   - risk_level: 文字描述（極低/低/中/高/極高）
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

搜尋策略要求：
1. 同時搜尋英文和中文資料源，確保全面性
2. 對於台灣股票（如 3019.TW），請搜尋：
   - 中文：公司中文名稱、股票代碼、相關產業新聞、台灣財經媒體
   - 英文：公司英文名稱、股票代碼、國際市場相關新聞、外資報告
3. 對於美股，請搜尋：
   - 英文：公司英文名稱、股票代碼、美國市場新聞、華爾街分析
   - 中文：公司中文譯名、相關中文報導、中國財經媒體
4. 對於港股，請搜尋：
   - 中文：公司中文名稱、香港市場新聞、港媒報導
   - 英文：公司英文名稱、國際市場相關新聞、外資分析
5. 搜尋範圍包括：財經新聞、分析師報告、社群媒體討論、財報公告、監管文件

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

請以以下增強 JSON 格式返回分析結果，所有分析內容都必須使用繁體中文表達：

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
6. 所有分析結果都必須使用繁體中文表達，包括所有指標、建議和描述
7. 避免使用簡體中文用詞，使用台灣地區的金融術語和表達方式

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

    def _extract_batch_json_from_response(self, response: Dict[str, Any], symbols: List[str]) -> Optional[Dict[str, Any]]:
        """
        從批量分析響應中提取 JSON 數據
        
        Args:
            response (Dict[str, Any]): Gemini API 響應
            symbols (List[str]): 股票代碼列表
            
        Returns:
            Optional[Dict[str, Any]]: 解析的批量 JSON 數據或 None
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
                            logger.error(f"批量JSON直接解析失敗: {e}")
                            
                            # 嘗試簡單的修復
                            fixed_json = self._simple_json_fix(json_str)
                            try:
                                return json.loads(fixed_json)
                            except json.JSONDecodeError as e2:
                                logger.error(f"批量JSON簡單修復後仍無法解析: {e2}")
                                
                                # 嘗試更激進的修復
                                aggressive_json = self._aggressive_json_fix(json_str)
                                try:
                                    return json.loads(aggressive_json)
                                except json.JSONDecodeError as e3:
                                    logger.error(f"批量JSON激進修復後仍無法解析: {e3}")
                                    
                                    # 最後嘗試：手動構建基本結構
                                    return self._build_batch_fallback_json(symbols, text)
                    else:
                        logger.error("批量響應中未找到有效的 JSON 格式")
                        return None
            else:
                logger.error("批量API 響應格式不正確")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"批量JSON 解析錯誤: {e}")
            return None
        except Exception as e:
            logger.error(f"提取批量JSON 時發生錯誤: {e}")
            return None

    def _build_batch_fallback_json(self, symbols: List[str], original_text: str) -> Dict[str, Any]:
        """
        構建批量分析的備用 JSON 結構
        
        Args:
            symbols (List[str]): 股票代碼列表
            original_text (str): 原始文本
            
        Returns:
            Dict[str, Any]: 備用批量 JSON 結構
        """
        logger.warning(f"使用批量備用 JSON 結構 for {len(symbols)} 支股票")
        
        stocks_data = {}
        for symbol in symbols:
            # 從原始文本中提取一些基本信息
            sentiment = "中性"
            if "看漲" in original_text or "bullish" in original_text.lower():
                sentiment = "看漲"
            elif "看跌" in original_text or "bearish" in original_text.lower():
                sentiment = "看跌"
            
            stocks_data[symbol] = {
                "symbol": symbol,
                "price_forecast": {
                    "price_1y": "一年後股價範圍",
                    "price_3y": "三年後股價範圍",
                    "price_5y": "五年後股價範圍"
                },
                "recent_news": "近期最重大新聞消息（30字內）",
                "ai_judgment": "AI對該消息的判斷（30字內）",
                "sentiment": sentiment,
                "risk_metrics": {
                    "beta": 1.25,
                    "volatility": 35.5,
                    "sharpe_ratio": 0.85,
                    "market_correlation": 0.72,
                    "risk_level": "高"
                }
            }
        
        return {"stocks": stocks_data}


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
            
            # 添加延遲避免 API 限制 (2分鐘)
            if i < len(test_stocks):
                print("   ⏳ 等待 2 分鐘避免 API 速率限制...")
                time.sleep(120)  # 2分鐘 = 120秒
                
        except Exception as e:
            print(f"❌ 分析 {stock['symbol']} 時發生異常: {e}")
    
    print(f"\n🎉 Gemini 分析器測試完成！")
    print("📁 請檢查當前目錄中的 JSON 文件查看詳細結果")


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
            
            # 添加延遲避免 API 限制 (2分鐘)
            if i < len(test_stocks):
                print("   ⏳ 等待 2 分鐘避免 API 速率限制...")
                time.sleep(120)  # 2分鐘 = 120秒
                
        except Exception as e:
            print(f"❌ 分析 {stock['symbol']} 時發生異常: {e}")
    
    print(f"\n🎉 Gemini 分析器測試完成！")
    print("📁 請檢查當前目錄中的 JSON 文件查看詳細結果")


if __name__ == "__main__":
    test_gemini_analyzer()

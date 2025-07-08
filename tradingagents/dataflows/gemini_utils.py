"""
Утилиты для работы с Google Gemini API
"""

import google.generativeai as genai
from typing import Dict, List, Optional
import json


class GeminiClient:
    """Клиент для работы с Google Gemini API"""
    
    def __init__(self, api_key: str = None):
        """
        Инициализация клиента Gemini
        
        Args:
            api_key: API ключ Google
        """
        if api_key:
            genai.configure(api_key=api_key)
        
        self.pro_model = genai.GenerativeModel('gemini-2.5-pro')
        self.flash_model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Настройки генерации
        self.generation_config = {
            'temperature': 0.7,
            'top_p': 0.8,
            'top_k': 40,
            'max_output_tokens': 4096,
        }
    
    def analyze_with_pro(self, prompt: str, context: str = None) -> Dict:
        """
        Глубокий анализ с использованием Gemini Pro
        
        Args:
            prompt: Основной запрос
            context: Дополнительный контекст
        
        Returns:
            Dict: Результат анализа
        """
        system_prompt = """
        Вы - эксперт по анализу российского фондового рынка с глубокими знаниями:
        - Российской экономики и фондового рынка
        - Особенностей торговли на MOEX
        - Влияния геополитических факторов
        - Отраслевой специфики российских компаний
        - Валютного регулирования и санкций
        
        Проводите детальный анализ с учетом российской специфики.
        """
        
        full_prompt = system_prompt + "\n\n"
        
        if context:
            full_prompt += f"Контекст: {context}\n\n"
        
        full_prompt += f"Запрос: {prompt}"
        
        try:
            response = self.pro_model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            
            return {
                "content": response.text,
                "model": "gemini-2.5-pro",
                "usage": {
                    "prompt_tokens": len(full_prompt.split()),
                    "completion_tokens": len(response.text.split()) if response.text else 0
                }
            }
            
        except Exception as e:
            print(f"Ошибка Gemini Pro: {e}")
            return {"content": f"Ошибка анализа: {e}", "model": "gemini-2.5-pro"}
    
    def quick_analysis(self, prompt: str, context: str = None) -> Dict:
        """
        Быстрый анализ с использованием Gemini Flash
        
        Args:
            prompt: Основной запрос
            context: Дополнительный контекст
        
        Returns:
            Dict: Результат быстрого анализа
        """
        system_prompt = """
        Вы - аналитик российского фондового рынка. 
        Предоставляйте краткие, точные и практичные ответы с учетом российской специфики.
        """
        
        full_prompt = system_prompt + "\n\n"
        
        if context:
            full_prompt += f"Контекст: {context}\n\n"
        
        full_prompt += f"Запрос: {prompt}"
        
        try:
            response = self.flash_model.generate_content(
                full_prompt,
                generation_config={
                    **self.generation_config,
                    'max_output_tokens': 2048
                }
            )
            
            return {
                "content": response.text,
                "model": "gemini-2.5-flash",
                "usage": {
                    "prompt_tokens": len(full_prompt.split()),
                    "completion_tokens": len(response.text.split()) if response.text else 0
                }
            }
            
        except Exception as e:
            print(f"Ошибка Gemini Flash: {e}")
            return {"content": f"Ошибка анализа: {e}", "model": "gemini-2.5-flash"}
    
    def analyze_market_data(self, market_data: str, company_name: str) -> str:
        """Анализ рыночных данных российской компании"""
        prompt = f"""
        Проанализируйте рыночные данные для российской компании {company_name}.
        
        Рыночные данные:
        {market_data}
        
        Учтите специфику российского рынка:
        - Влияние санкций и геополитики
        - Особенности торговых сессий MOEX
        - Валютные риски (рубль/доллар/евро)
        - Отраслевые особенности
        - Сезонность российского рынка
        
        Предоставьте:
        1. Технический анализ с российской спецификой
        2. Анализ ликвидности и объемов
        3. Ключевые уровни в рублях
        4. Влияние макроэкономических факторов РФ
        5. Рекомендации для российских инвесторов
        """
        
        result = self.analyze_with_pro(prompt)
        return result["content"]
    
    def analyze_news_sentiment(self, news_data: str, company_name: str) -> str:
        """Анализ новостного фона российской компании"""
        prompt = f"""
        Проанализируйте новостной фон для российской компании {company_name}.
        
        Новостные данные:
        {news_data}
        
        Учтите российскую специфику:
        - Влияние государственной политики
        - Санкционные риски
        - Отношения с государством
        - Валютное регулирование
        - Отраслевое регулирование
        
        Предоставьте:
        1. Тональность с учетом российского контекста
        2. Геополитические риски и возможности
        3. Регулятивные изменения
        4. Влияние на экспортные/импортные операции
        5. Стратегические рекомендации для РФ рынка
        """
        
        result = self.analyze_with_pro(prompt)
        return result["content"]
    
    def analyze_fundamentals(self, fundamental_data: str, company_name: str) -> str:
        """Анализ фундаментальных показателей российской компании"""
        prompt = f"""
        Проанализируйте фундаментальные показатели российской компании {company_name}.
        
        Фундаментальные данные:
        {fundamental_data}
        
        Учтите российскую специфику:
        - Российские стандарты отчетности (РСБУ/МСФО)
        - Налоговое планирование в РФ
        - Валютные операции и хеджирование
        - Дивидендная политика российских компаний
        - Отраслевые мультипликаторы РФ рынка
        
        Предоставьте:
        1. Анализ по российским стандартам
        2. Справедливая стоимость в рублях
        3. Сравнение с российскими аналогами
        4. Дивидендная привлекательность
        5. ESG факторы для российского рынка
        """
        
        result = self.analyze_with_pro(prompt)
        return result["content"]
    
    def make_trading_decision(self, all_data: str, company_name: str) -> str:
        """Принятие торгового решения для российского рынка"""
        prompt = f"""
        Примите торговое решение для российской компании {company_name} на основе всех данных.
        
        Все данные для анализа:
        {all_data}
        
        Учтите российскую специфику:
        - Время торговых сессий MOEX (10:00-18:45 МСК)
        - Валютные ограничения для резидентов/нерезидентов
        - Налогообложение операций с ценными бумагами в РФ
        - Особенности расчетов T+2
        - Влияние ключевой ставки ЦБ РФ
        
        Предоставьте решение для российского инвестора:
        1. Четкое решение: ПОКУПАТЬ/ПРОДАВАТЬ/ДЕРЖАТЬ
        2. Обоснование с учетом российских реалий
        3. Целевые уровни в рублях
        4. Стоп-лосс с учетом волатильности РФ рынка
        5. Горизонт инвестирования
        6. Размер позиции (% портфеля)
        7. Российские риски (санкции, валютные, регулятивные)
        8. Налоговые последствия
        
        Завершите: ФИНАЛЬНОЕ ТОРГОВОЕ РЕШЕНИЕ: **ПОКУПАТЬ/ДЕРЖАТЬ/ПРОДАВАТЬ**
        """
        
        result = self.analyze_with_pro(prompt)
        return result["content"]


def create_gemini_analyst(api_key: str = None) -> GeminiClient:
    """Создать аналитика на базе Gemini"""
    return GeminiClient(api_key=api_key)


def analyze_russian_market_with_gemini(
    market_data: str,
    news_data: str,
    fundamental_data: str,
    company_name: str,
    api_key: str = None
) -> Dict[str, str]:
    """
    Комплексный анализ российского рынка с помощью Gemini
    
    Args:
        market_data: Рыночные данные
        news_data: Новостные данные  
        fundamental_data: Фундаментальные данные
        company_name: Название компании
        api_key: API ключ Google
    
    Returns:
        Dict: Результаты анализа по категориям
    """
    analyst = create_gemini_analyst(api_key)
    
    results = {}
    
    # Анализ рыночных данных
    if market_data:
        results["market_analysis"] = analyst.analyze_market_data(market_data, company_name)
    
    # Анализ новостей
    if news_data:
        results["news_analysis"] = analyst.analyze_news_sentiment(news_data, company_name)
    
    # Анализ фундаментальных показателей
    if fundamental_data:
        results["fundamental_analysis"] = analyst.analyze_fundamentals(fundamental_data, company_name)
    
    # Итоговое решение
    all_data = f"""
    Рыночные данные: {market_data}
    
    Новостные данные: {news_data}
    
    Фундаментальные данные: {fundamental_data}
    """
    
    results["trading_decision"] = analyst.make_trading_decision(all_data, company_name)
    
    return results
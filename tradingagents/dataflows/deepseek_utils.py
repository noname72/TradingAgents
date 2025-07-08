"""
Утилиты для работы с Deepseek API
"""

from openai import OpenAI
from typing import Dict, List, Optional
import json


class DeepseekClient:
    """Клиент для работы с Deepseek API"""
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.deepseek.com"):
        """
        Инициализация клиента Deepseek
        
        Args:
            api_key: API ключ Deepseek
            base_url: Базовый URL API
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.reasoning_model = "deepseek-reasoner"
        self.chat_model = "deepseek-chat"
    
    def analyze_with_reasoning(self, prompt: str, context: str = None) -> Dict:
        """
        Анализ с использованием модели рассуждений
        
        Args:
            prompt: Основной запрос
            context: Дополнительный контекст
        
        Returns:
            Dict: Результат анализа с рассуждениями
        """
        messages = [
            {
                "role": "system",
                "content": "Вы - эксперт по анализу российского фондового рынка. Проводите глубокий анализ с пошаговыми рассуждениями."
            }
        ]
        
        if context:
            messages.append({
                "role": "user", 
                "content": f"Контекст: {context}\n\nЗапрос: {prompt}"
            })
        else:
            messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.reasoning_model,
                messages=messages,
                temperature=0.7,
                max_tokens=4000
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": self.reasoning_model,
                "usage": response.usage.dict() if response.usage else None
            }
            
        except Exception as e:
            print(f"Ошибка Deepseek Reasoner: {e}")
            return {"content": f"Ошибка анализа: {e}", "model": self.reasoning_model}
    
    def quick_analysis(self, prompt: str, context: str = None) -> Dict:
        """
        Быстрый анализ с использованием chat модели
        
        Args:
            prompt: Основной запрос
            context: Дополнительный контекст
        
        Returns:
            Dict: Результат быстрого анализа
        """
        messages = [
            {
                "role": "system",
                "content": "Вы - аналитик российского фондового рынка. Предоставляйте краткие и точные ответы."
            }
        ]
        
        if context:
            messages.append({
                "role": "user",
                "content": f"Контекст: {context}\n\nЗапрос: {prompt}"
            })
        else:
            messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=0.5,
                max_tokens=2000
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": self.chat_model,
                "usage": response.usage.dict() if response.usage else None
            }
            
        except Exception as e:
            print(f"Ошибка Deepseek Chat: {e}")
            return {"content": f"Ошибка анализа: {e}", "model": self.chat_model}
    
    def analyze_market_data(self, market_data: str, company_name: str) -> str:
        """Анализ рыночных данных"""
        prompt = f"""
        Проанализируйте рыночные данные для компании {company_name} на российском фондовом рынке.
        
        Рыночные данные:
        {market_data}
        
        Предоставьте:
        1. Технический анализ ценовых движений
        2. Анализ объемов торгов
        3. Ключевые уровни поддержки и сопротивления
        4. Краткосрочные и среднесрочные тренды
        5. Рекомендации для трейдеров
        """
        
        result = self.analyze_with_reasoning(prompt)
        return result["content"]
    
    def analyze_news_sentiment(self, news_data: str, company_name: str) -> str:
        """Анализ новостного фона и настроений"""
        prompt = f"""
        Проанализируйте новостной фон и настроения для компании {company_name} на российском рынке.
        
        Новостные данные:
        {news_data}
        
        Предоставьте:
        1. Общую тональность новостей (позитивная/негативная/нейтральная)
        2. Ключевые события, влияющие на котировки
        3. Анализ рисков и возможностей
        4. Влияние на краткосрочные и долгосрочные перспективы
        5. Рекомендации по торговой стратегии
        """
        
        result = self.analyze_with_reasoning(prompt)
        return result["content"]
    
    def analyze_fundamentals(self, fundamental_data: str, company_name: str) -> str:
        """Анализ фундаментальных показателей"""
        prompt = f"""
        Проанализируйте фундаментальные показатели компании {company_name} на российском рынке.
        
        Фундаментальные данные:
        {fundamental_data}
        
        Предоставьте:
        1. Анализ финансовых показателей
        2. Оценку справедливой стоимости
        3. Сравнение с отраслевыми мультипликаторами
        4. Анализ дивидендной политики
        5. Долгосрочные инвестиционные перспективы
        """
        
        result = self.analyze_with_reasoning(prompt)
        return result["content"]
    
    def make_trading_decision(self, all_data: str, company_name: str) -> str:
        """Принятие торгового решения на основе всех данных"""
        prompt = f"""
        На основе всех доступных данных примите торговое решение для {company_name} на российском фондовом рынке.
        
        Все данные для анализа:
        {all_data}
        
        Предоставьте:
        1. Четкое торговое решение: ПОКУПАТЬ/ПРОДАВАТЬ/ДЕРЖАТЬ
        2. Обоснование решения
        3. Целевые уровни цены
        4. Уровни стоп-лосса
        5. Временной горизонт рекомендации
        6. Размер позиции (% от портфеля)
        7. Основные риски
        
        Завершите ответ четким решением: ФИНАЛЬНОЕ ТОРГОВОЕ РЕШЕНИЕ: **ПОКУПАТЬ/ДЕРЖАТЬ/ПРОДАВАТЬ**
        """
        
        result = self.analyze_with_reasoning(prompt)
        return result["content"]


def create_deepseek_analyst(api_key: str = None) -> DeepseekClient:
    """Создать аналитика на базе Deepseek"""
    return DeepseekClient(api_key=api_key)


def analyze_russian_market_with_deepseek(
    market_data: str,
    news_data: str, 
    fundamental_data: str,
    company_name: str,
    api_key: str = None
) -> Dict[str, str]:
    """
    Комплексный анализ российского рынка с помощью Deepseek
    
    Args:
        market_data: Рыночные данные
        news_data: Новостные данные
        fundamental_data: Фундаментальные данные
        company_name: Название компании
        api_key: API ключ Deepseek
    
    Returns:
        Dict: Результаты анализа по категориям
    """
    analyst = create_deepseek_analyst(api_key)
    
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
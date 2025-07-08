"""
Утилиты для российских торговых агентов
"""

from langchain_core.tools import tool
from typing import Annotated
from datetime import datetime, timedelta
import os

from tradingagents.dataflows.russian_interface import (
    get_russian_market_data,
    get_russian_company_info,
    get_russian_news_rbc,
    get_russian_news_smartlab,
    get_russian_market_overview,
    search_russian_securities,
    get_russian_technical_indicators,
    analyze_with_russian_ai,
    get_russian_dividends_info,
    get_russian_index_data,
    get_company_name_russian
)


class RussianToolkit:
    """Набор инструментов для работы с российским рынком"""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    @staticmethod
    @tool
    def get_moex_market_data(
        symbol: Annotated[str, "Тикер российской компании на MOEX"],
        start_date: Annotated[str, "Дата начала в формате YYYY-MM-DD"],
        end_date: Annotated[str, "Дата окончания в формате YYYY-MM-DD"]
    ) -> str:
        """
        Получить рыночные данные российской компании с Московской биржи
        
        Args:
            symbol: Тикер компании на MOEX (например, SBER, GAZP, LKOH)
            start_date: Дата начала в формате YYYY-MM-DD
            end_date: Дата окончания в формате YYYY-MM-DD
        
        Returns:
            str: Рыночные данные в формате CSV
        """
        return get_russian_market_data(symbol, start_date, end_date)
    
    @staticmethod
    @tool
    def get_russian_company_info(
        symbol: Annotated[str, "Тикер российской компании на MOEX"]
    ) -> str:
        """
        Получить информацию о российской компании
        
        Args:
            symbol: Тикер компании на MOEX
        
        Returns:
            str: Подробная информация о компании
        """
        return get_russian_company_info(symbol)
    
    @staticmethod
    @tool
    def get_rbc_news(
        query: Annotated[str, "Название компании или тикер для поиска новостей"],
        curr_date: Annotated[str, "Текущая дата в формате YYYY-MM-DD"],
        look_back_days: Annotated[int, "Количество дней назад для поиска"] = 7
    ) -> str:
        """
        Получить новости о российской компании с РБК
        
        Args:
            query: Название компании или тикер
            curr_date: Текущая дата
            look_back_days: Количество дней для поиска назад
        
        Returns:
            str: Новости с РБК
        """
        return get_russian_news_rbc(query, curr_date, look_back_days)
    
    @staticmethod
    @tool
    def get_smartlab_news(
        query: Annotated[str, "Название компании или тикер для поиска новостей"],
        curr_date: Annotated[str, "Текущая дата в формате YYYY-MM-DD"],
        look_back_days: Annotated[int, "Количество дней назад для поиска"] = 7
    ) -> str:
        """
        Получить новости о российской компании с Smart-Lab
        
        Args:
            query: Название компании или тикер
            curr_date: Текущая дата
            look_back_days: Количество дней для поиска назад
        
        Returns:
            str: Новости с Smart-Lab
        """
        return get_russian_news_smartlab(query, curr_date, look_back_days)
    
    @staticmethod
    @tool
    def get_market_overview_russia(
        curr_date: Annotated[str, "Текущая дата в формате YYYY-MM-DD"]
    ) -> str:
        """
        Получить обзор российского фондового рынка
        
        Args:
            curr_date: Текущая дата
        
        Returns:
            str: Обзор российского рынка
        """
        return get_russian_market_overview(curr_date)
    
    @staticmethod
    @tool
    def search_russian_stocks(
        query: Annotated[str, "Поисковый запрос для поиска российских акций"]
    ) -> str:
        """
        Поиск российских ценных бумаг на MOEX
        
        Args:
            query: Поисковый запрос (название компании или часть названия)
        
        Returns:
            str: Результаты поиска российских акций
        """
        return search_russian_securities(query)
    
    @staticmethod
    @tool
    def get_russian_dividends(
        symbol: Annotated[str, "Тикер российской компании"]
    ) -> str:
        """
        Получить информацию о дивидендах российской компании
        
        Args:
            symbol: Тикер компании на MOEX
        
        Returns:
            str: История дивидендных выплат
        """
        return get_russian_dividends_info(symbol)
    
    @staticmethod
    @tool
    def get_russian_index_info(
        index_name: Annotated[str, "Название российского индекса"] = "IMOEX"
    ) -> str:
        """
        Получить данные по российскому фондовому индексу
        
        Args:
            index_name: Название индекса (IMOEX, RTSI и др.)
        
        Returns:
            str: Данные индекса
        """
        return get_russian_index_data(index_name)
    
    @staticmethod
    @tool
    def analyze_with_deepseek(
        symbol: Annotated[str, "Тикер российской компании"],
        market_data: Annotated[str, "Рыночные данные компании"],
        news_data: Annotated[str, "Новостные данные"],
        fundamental_data: Annotated[str, "Фундаментальные данные"]
    ) -> str:
        """
        Анализ российской компании с помощью Deepseek AI
        
        Args:
            symbol: Тикер компании
            market_data: Рыночные данные
            news_data: Новостные данные
            fundamental_data: Фундаментальные данные
        
        Returns:
            str: Результат анализа Deepseek
        """
        return analyze_with_russian_ai(symbol, market_data, news_data, fundamental_data, "deepseek")
    
    @staticmethod
    @tool
    def analyze_with_gemini(
        symbol: Annotated[str, "Тикер российской компании"],
        market_data: Annotated[str, "Рыночные данные компании"],
        news_data: Annotated[str, "Новостные данные"],
        fundamental_data: Annotated[str, "Фундаментальные данные"]
    ) -> str:
        """
        Анализ российской компании с помощью Google Gemini
        
        Args:
            symbol: Тикер компании
            market_data: Рыночные данные
            news_data: Новостные данные
            fundamental_data: Фундаментальные данные
        
        Returns:
            str: Результат анализа Gemini
        """
        return analyze_with_russian_ai(symbol, market_data, news_data, fundamental_data, "gemini")


def create_russian_market_analyst(llm, toolkit):
    """Создать аналитика российского рынка"""
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    def russian_market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = get_company_name_russian(ticker)
        
        tools = [
            toolkit.get_moex_market_data,
            toolkit.get_russian_company_info,
        ]
        
        system_message = f"""
        Вы - эксперт по анализу российского фондового рынка. Ваша задача - провести комплексный анализ российской компании {company_name} ({ticker}) на Московской бирже.

        Особенности российского рынка, которые необходимо учитывать:
        - Время торговых сессий MOEX: 10:00-18:45 МСК
        - Влияние геополитических факторов и санкций
        - Валютные риски (курс рубля к доллару и евро)
        - Особенности российского корпоративного управления
        - Влияние государственной политики на отдельные отрасли
        - Сезонность российского рынка
        - Специфика российских дивидендных выплат

        Проведите анализ:
        1. Получите рыночные данные компании за последние 30 дней
        2. Изучите информацию о компании и её текущие показатели
        3. Проанализируйте ценовую динамику с учетом российской специфики
        4. Оцените ликвидность и объемы торгов
        5. Определите ключевые уровни поддержки и сопротивления в рублях

        Предоставьте детальный отчет с таблицей ключевых показателей в конце.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "Вы - помощник-аналитик российского фондового рынка, работающий в команде."
             " Используйте предоставленные инструменты для анализа российских компаний."
             " Если вы не можете полностью ответить, это нормально - другой помощник продолжит работу."
             " Доступные инструменты: {tool_names}.\n{system_message}"
             "Текущая дата: {current_date}. Анализируемая компания: {ticker} ({company_name})"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        prompt = prompt.partial(company_name=company_name)
        
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])
        
        report = ""
        if len(result.tool_calls) == 0:
            report = result.content
        
        return {
            "messages": [result],
            "market_report": report,
        }
    
    return russian_market_analyst_node


def create_russian_news_analyst(llm, toolkit):
    """Создать аналитика российских новостей"""
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    def russian_news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = get_company_name_russian(ticker)
        
        tools = [
            toolkit.get_rbc_news,
            toolkit.get_smartlab_news,
            toolkit.get_market_overview_russia,
        ]
        
        system_message = f"""
        Вы - аналитик российских финансовых новостей. Ваша задача - проанализировать новостной фон для российской компании {company_name} ({ticker}).

        Особенности анализа российских новостей:
        - Влияние государственной политики на бизнес
        - Санкционные риски и ограничения
        - Валютное регулирование и ограничения ЦБ РФ
        - Отраслевое регулирование в России
        - Геополитические факторы
        - Налоговые изменения и льготы
        - ESG факторы в российском контексте

        Проведите анализ:
        1. Соберите новости о компании с РБК за последнюю неделю
        2. Получите новости и аналитику с Smart-Lab
        3. Изучите общий обзор российского рынка
        4. Проанализируйте тональность новостей
        5. Выявите ключевые события, влияющие на котировки
        6. Оцените геополитические и регулятивные риски

        Предоставьте детальный отчет с таблицей ключевых новостных событий.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Вы - аналитик российских финансовых новостей, работающий в команде."
             " Используйте российские источники новостей для анализа."
             " Доступные инструменты: {tool_names}.\n{system_message}"
             "Текущая дата: {current_date}. Анализируемая компания: {ticker} ({company_name})"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        prompt = prompt.partial(company_name=company_name)
        
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])
        
        report = ""
        if len(result.tool_calls) == 0:
            report = result.content
        
        return {
            "messages": [result],
            "news_report": report,
        }
    
    return russian_news_analyst_node


def create_russian_fundamental_analyst(llm, toolkit):
    """Создать аналитика фундаментальных показателей российских компаний"""
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    def russian_fundamental_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = get_company_name_russian(ticker)
        
        tools = [
            toolkit.get_russian_company_info,
            toolkit.get_russian_dividends,
            toolkit.get_russian_index_info,
        ]
        
        system_message = f"""
        Вы - аналитик фундаментальных показателей российских компаний. Ваша задача - провести фундаментальный анализ {company_name} ({ticker}).

        Особенности российского фундаментального анализа:
        - Российские стандарты отчетности (РСБУ vs МСФО)
        - Влияние валютных курсов на экспортеров/импортеров
        - Особенности российской дивидендной политики
        - Государственное участие в капитале
        - Отраслевые мультипликаторы российского рынка
        - Налоговое планирование в РФ
        - ESG факторы для российских компаний

        Проведите анализ:
        1. Изучите основную информацию о компании
        2. Проанализируйте дивидендную историю и политику
        3. Сравните с отраслевыми показателями
        4. Оцените влияние макроэкономических факторов РФ
        5. Проанализируйте корпоративное управление
        6. Оцените ESG риски и возможности

        Предоставьте детальный отчет с таблицей ключевых финансовых показателей.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Вы - аналитик фундаментальных показателей российских компаний."
             " Используйте доступные инструменты для анализа."
             " Доступные инструменты: {tool_names}.\n{system_message}"
             "Текущая дата: {current_date}. Анализируемая компания: {ticker} ({company_name})"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        prompt = prompt.partial(company_name=company_name)
        
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])
        
        report = ""
        if len(result.tool_calls) == 0:
            report = result.content
        
        return {
            "messages": [result],
            "fundamentals_report": report,
        }
    
    return russian_fundamental_analyst_node
"""
Интерфейс для работы с российскими источниками данных
"""

from typing import Annotated, Dict, List
from datetime import datetime, timedelta
import pandas as pd

from .moex_utils import MOEXUtils, get_moex_data, get_moex_security_info, search_moex_securities
from .rbc_news_utils import get_rbc_news, get_rbc_market_overview
from .smartlab_utils import get_smartlab_news, get_smartlab_market_sentiment
from .deepseek_utils import analyze_russian_market_with_deepseek
from .gemini_utils import analyze_russian_market_with_gemini
from .config import get_config


def get_russian_market_data(
    symbol: Annotated[str, "Тикер российской компании на MOEX"],
    start_date: Annotated[str, "Дата начала в формате YYYY-MM-DD"],
    end_date: Annotated[str, "Дата окончания в формате YYYY-MM-DD"]
) -> str:
    """
    Получить рыночные данные российской компании с MOEX
    
    Args:
        symbol: Тикер компании на MOEX (например, SBER, GAZP)
        start_date: Дата начала в формате YYYY-MM-DD
        end_date: Дата окончания в формате YYYY-MM-DD
    
    Returns:
        str: Отформатированные рыночные данные
    """
    return get_moex_data(symbol, start_date, end_date)


def get_russian_company_info(
    symbol: Annotated[str, "Тикер российской компании на MOEX"]
) -> str:
    """
    Получить информацию о российской компании
    
    Args:
        symbol: Тикер компании на MOEX
    
    Returns:
        str: Информация о компании
    """
    return get_moex_security_info(symbol)


def get_russian_news_rbc(
    query: Annotated[str, "Поисковый запрос или тикер компании"] = None,
    curr_date: Annotated[str, "Текущая дата в формате YYYY-MM-DD"] = None,
    look_back_days: Annotated[int, "Количество дней назад"] = 7
) -> str:
    """
    Получить новости с РБК
    
    Args:
        query: Поисковый запрос или тикер компании
        curr_date: Текущая дата
        look_back_days: Количество дней для поиска назад
    
    Returns:
        str: Новости РБК
    """
    return get_rbc_news(query, curr_date, look_back_days)


def get_russian_news_smartlab(
    query: Annotated[str, "Поисковый запрос или тикер компании"] = None,
    curr_date: Annotated[str, "Текущая дата в формате YYYY-MM-DD"] = None,
    look_back_days: Annotated[int, "Количество дней назад"] = 7
) -> str:
    """
    Получить новости с Smart-Lab
    
    Args:
        query: Поисковый запрос или тикер компании
        curr_date: Текущая дата
        look_back_days: Количество дней для поиска назад
    
    Returns:
        str: Новости Smart-Lab
    """
    return get_smartlab_news(query, curr_date, look_back_days)


def get_russian_market_overview(
    curr_date: Annotated[str, "Текущая дата в формате YYYY-MM-DD"] = None
) -> str:
    """
    Получить обзор российского рынка
    
    Args:
        curr_date: Текущая дата
    
    Returns:
        str: Обзор рынка
    """
    rbc_overview = get_rbc_market_overview(curr_date)
    smartlab_sentiment = get_smartlab_market_sentiment(curr_date)
    
    return f"{rbc_overview}\n\n{smartlab_sentiment}"


def search_russian_securities(
    query: Annotated[str, "Поисковый запрос для поиска ценных бумаг"]
) -> str:
    """
    Поиск российских ценных бумаг на MOEX
    
    Args:
        query: Поисковый запрос
    
    Returns:
        str: Результаты поиска
    """
    return search_moex_securities(query)


def get_russian_technical_indicators(
    symbol: Annotated[str, "Тикер российской компании"],
    indicator: Annotated[str, "Технический индикатор"],
    curr_date: Annotated[str, "Текущая дата в формате YYYY-MM-DD"],
    look_back_days: Annotated[int, "Количество дней назад"] = 30
) -> str:
    """
    Получить технические индикаторы для российской компании
    
    Args:
        symbol: Тикер компании
        indicator: Название индикатора
        curr_date: Текущая дата
        look_back_days: Период расчета
    
    Returns:
        str: Значения технических индикаторов
    """
    # Получаем данные MOEX
    end_date = curr_date
    start_date = (datetime.strptime(curr_date, "%Y-%m-%d") - timedelta(days=look_back_days)).strftime("%Y-%m-%d")
    
    moex_data = get_moex_data(symbol, start_date, end_date)
    
    # Здесь можно добавить расчет технических индикаторов
    # Пока возвращаем базовую информацию
    return f"## Технические индикаторы для {symbol}\n\n{moex_data}"


def analyze_with_russian_ai(
    symbol: Annotated[str, "Тикер российской компании"],
    market_data: Annotated[str, "Рыночные данные"],
    news_data: Annotated[str, "Новостные данные"],
    fundamental_data: Annotated[str, "Фундаментальные данные"],
    ai_provider: Annotated[str, "Провайдер ИИ: deepseek или gemini"] = "deepseek"
) -> str:
    """
    Анализ с помощью российских AI моделей
    
    Args:
        symbol: Тикер компании
        market_data: Рыночные данные
        news_data: Новостные данные
        fundamental_data: Фундаментальные данные
        ai_provider: Провайдер ИИ
    
    Returns:
        str: Результат анализа
    """
    config = get_config()
    
    # Получаем название компании
    company_info = get_moex_security_info(symbol)
    company_name = symbol  # Можно извлечь из company_info
    
    if ai_provider.lower() == "deepseek":
        api_key = config.get("deepseek_api_key")
        results = analyze_russian_market_with_deepseek(
            market_data, news_data, fundamental_data, company_name, api_key
        )
    elif ai_provider.lower() == "gemini":
        api_key = config.get("gemini_api_key")
        results = analyze_russian_market_with_gemini(
            market_data, news_data, fundamental_data, company_name, api_key
        )
    else:
        return f"Неподдерживаемый провайдер ИИ: {ai_provider}"
    
    # Форматируем результаты
    formatted_result = f"## Анализ {company_name} с помощью {ai_provider.upper()}\n\n"
    
    for category, analysis in results.items():
        formatted_result += f"### {category.replace('_', ' ').title()}\n{analysis}\n\n"
    
    return formatted_result


def get_russian_dividends_info(
    symbol: Annotated[str, "Тикер российской компании"]
) -> str:
    """
    Получить информацию о дивидендах российской компании
    
    Args:
        symbol: Тикер компании
    
    Returns:
        str: Информация о дивидендах
    """
    moex = MOEXUtils()
    dividends_df = moex.get_dividends(symbol)
    
    if dividends_df.empty:
        return f"Информация о дивидендах для {symbol} не найдена"
    
    result = f"## Дивиденды {symbol}\n\n"
    
    # Форматируем данные о дивидендах
    for _, row in dividends_df.head(10).iterrows():
        result += f"### Дивиденд от {row.get('registryclosedate', 'N/A')}\n"
        result += f"- Размер: {row.get('value', 'N/A')} руб.\n"
        result += f"- Валюта: {row.get('currencyid', 'RUB')}\n\n"
    
    return result


def get_russian_index_data(
    index_name: Annotated[str, "Название индекса"] = "IMOEX"
) -> str:
    """
    Получить данные по российскому индексу
    
    Args:
        index_name: Название индекса (IMOEX, RTSI и др.)
    
    Returns:
        str: Данные индекса
    """
    moex = MOEXUtils()
    index_data = moex.get_index_data(index_name)
    
    if not index_data:
        return f"Данные по индексу {index_name} не найдены"
    
    result = f"## Индекс {index_name}\n\n"
    
    important_fields = ['LAST', 'CHANGE', 'PRCCHANGE', 'OPEN', 'HIGH', 'LOW']
    for field in important_fields:
        if field in index_data and index_data[field]:
            result += f"- {field}: {index_data[field]}\n"
    
    return result


# Маппинг российских компаний
RUSSIAN_COMPANIES = {
    'SBER': 'Сбербанк',
    'GAZP': 'Газпром', 
    'LKOH': 'Лукойл',
    'YNDX': 'Яндекс',
    'ROSN': 'Роснефть',
    'NVTK': 'Новатэк',
    'PLZL': 'Полюс',
    'GMKN': 'Норникель',
    'MGNT': 'Магнит',
    'MTSS': 'МТС',
    'RTKM': 'Ростелеком',
    'AFLT': 'Аэрофлот',
    'VTBR': 'ВТБ',
    'TATN': 'Татнефть',
    'SNGS': 'Сургутнефтегаз',
    'NLMK': 'НЛМК',
    'CHMF': 'Северсталь',
    'ALRS': 'Алроса',
    'MOEX': 'Московская биржа',
    'MAIL': 'Mail.ru',
    'OZON': 'Озон',
    'FIXP': 'Fix Price'
}


def get_company_name_russian(ticker: str) -> str:
    """Получить русское название компании по тикеру"""
    return RUSSIAN_COMPANIES.get(ticker.upper(), ticker)
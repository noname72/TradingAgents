"""
Утилиты для работы с API Московской биржи (MOEX)
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import json


class MOEXUtils:
    """Класс для работы с API Московской биржи"""
    
    BASE_URL = "https://iss.moex.com/iss"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TradingAgents/1.0'
        })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Выполнить запрос к API MOEX"""
        url = f"{self.BASE_URL}/{endpoint}.json"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса к MOEX API: {e}")
            return {}
    
    def get_securities_list(self, market: str = "shares", board: str = "TQBR") -> pd.DataFrame:
        """Получить список торгуемых инструментов"""
        endpoint = f"engines/stock/markets/{market}/boards/{board}/securities"
        data = self._make_request(endpoint)
        
        if not data or 'securities' not in data:
            return pd.DataFrame()
        
        securities = data['securities']['data']
        columns = data['securities']['columns']
        
        return pd.DataFrame(securities, columns=columns)
    
    def get_security_info(self, secid: str) -> Dict:
        """Получить информацию о ценной бумаге"""
        endpoint = f"securities/{secid}"
        data = self._make_request(endpoint)
        
        if not data or 'description' not in data:
            return {}
        
        info = {}
        for item in data['description']['data']:
            if len(item) >= 3:
                info[item[0]] = item[2]
        
        return info
    
    def get_candles(self, secid: str, start_date: str, end_date: str, 
                   interval: int = 24) -> pd.DataFrame:
        """
        Получить свечи для инструмента
        
        Args:
            secid: Код инструмента
            start_date: Дата начала в формате YYYY-MM-DD
            end_date: Дата окончания в формате YYYY-MM-DD
            interval: Интервал в минутах (1, 10, 60, 24*60=1440 для дневных)
        """
        endpoint = f"engines/stock/markets/shares/securities/{secid}/candles"
        params = {
            'from': start_date,
            'till': end_date,
            'interval': interval
        }
        
        data = self._make_request(endpoint, params)
        
        if not data or 'candles' not in data:
            return pd.DataFrame()
        
        candles = data['candles']['data']
        columns = data['candles']['columns']
        
        df = pd.DataFrame(candles, columns=columns)
        
        if not df.empty:
            df['begin'] = pd.to_datetime(df['begin'])
            df = df.sort_values('begin')
        
        return df
    
    def get_orderbook(self, secid: str) -> Dict:
        """Получить стакан заявок"""
        endpoint = f"engines/stock/markets/shares/boards/TQBR/securities/{secid}/orderbook"
        data = self._make_request(endpoint)
        
        if not data or 'orderbook' not in data:
            return {}
        
        return {
            'bids': data['orderbook']['data'],
            'columns': data['orderbook']['columns']
        }
    
    def get_trades(self, secid: str, start_date: str = None) -> pd.DataFrame:
        """Получить сделки по инструменту"""
        endpoint = f"engines/stock/markets/shares/boards/TQBR/securities/{secid}/trades"
        params = {}
        
        if start_date:
            params['from'] = start_date
        
        data = self._make_request(endpoint, params)
        
        if not data or 'trades' not in data:
            return pd.DataFrame()
        
        trades = data['trades']['data']
        columns = data['trades']['columns']
        
        df = pd.DataFrame(trades, columns=columns)
        
        if not df.empty:
            df['tradetime'] = pd.to_datetime(df['tradetime'])
        
        return df
    
    def get_market_data(self, secid: str) -> Dict:
        """Получить текущие рыночные данные"""
        endpoint = f"engines/stock/markets/shares/boards/TQBR/securities/{secid}"
        data = self._make_request(endpoint)
        
        if not data or 'securities' not in data:
            return {}
        
        securities_data = data['securities']['data']
        securities_columns = data['securities']['columns']
        
        if securities_data:
            return dict(zip(securities_columns, securities_data[0]))
        
        return {}
    
    def search_securities(self, query: str) -> List[Dict]:
        """Поиск ценных бумаг по названию или коду"""
        endpoint = "securities"
        params = {'q': query}
        
        data = self._make_request(endpoint, params)
        
        if not data or 'securities' not in data:
            return []
        
        securities = data['securities']['data']
        columns = data['securities']['columns']
        
        results = []
        for security in securities:
            if len(security) >= len(columns):
                results.append(dict(zip(columns, security)))
        
        return results
    
    def get_dividends(self, secid: str) -> pd.DataFrame:
        """Получить информацию о дивидендах"""
        endpoint = f"securities/{secid}/dividends"
        data = self._make_request(endpoint)
        
        if not data or 'dividends' not in data:
            return pd.DataFrame()
        
        dividends = data['dividends']['data']
        columns = data['dividends']['columns']
        
        df = pd.DataFrame(dividends, columns=columns)
        
        if not df.empty and 'registryclosedate' in df.columns:
            df['registryclosedate'] = pd.to_datetime(df['registryclosedate'])
        
        return df
    
    def get_index_data(self, index_name: str = "IMOEX") -> Dict:
        """Получить данные по индексу"""
        endpoint = f"engines/stock/markets/index/securities/{index_name}"
        data = self._make_request(endpoint)
        
        if not data or 'securities' not in data:
            return {}
        
        securities_data = data['securities']['data']
        securities_columns = data['securities']['columns']
        
        if securities_data:
            return dict(zip(securities_columns, securities_data[0]))
        
        return {}


def get_moex_data(symbol: str, start_date: str, end_date: str) -> str:
    """
    Получить данные MOEX для символа в указанном диапазоне дат
    
    Args:
        symbol: Код инструмента на MOEX
        start_date: Дата начала в формате YYYY-MM-DD
        end_date: Дата окончания в формате YYYY-MM-DD
    
    Returns:
        str: Отформатированные данные в виде строки
    """
    moex = MOEXUtils()
    
    # Получаем свечи
    candles_df = moex.get_candles(symbol, start_date, end_date)
    
    if candles_df.empty:
        return f"Данные для {symbol} за период {start_date} - {end_date} не найдены"
    
    # Переименовываем колонки для совместимости
    column_mapping = {
        'begin': 'Date',
        'open': 'Open',
        'high': 'High', 
        'low': 'Low',
        'close': 'Close',
        'value': 'Volume'
    }
    
    candles_df = candles_df.rename(columns=column_mapping)
    
    # Форматируем дату
    candles_df['Date'] = candles_df['Date'].dt.strftime('%Y-%m-%d')
    
    # Создаем заголовок
    header = f"# Данные MOEX для {symbol} с {start_date} по {end_date}\n"
    header += f"# Всего записей: {len(candles_df)}\n"
    header += f"# Данные получены: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    return header + candles_df.to_csv(index=False)


def get_moex_security_info(symbol: str) -> str:
    """Получить информацию о ценной бумаге MOEX"""
    moex = MOEXUtils()
    
    # Получаем информацию о бумаге
    info = moex.get_security_info(symbol)
    
    if not info:
        return f"Информация о {symbol} не найдена"
    
    # Получаем текущие рыночные данные
    market_data = moex.get_market_data(symbol)
    
    result = f"## Информация о ценной бумаге {symbol}\n\n"
    
    # Основная информация
    if info:
        result += "### Основные данные:\n"
        for key, value in info.items():
            if value:
                result += f"- {key}: {value}\n"
        result += "\n"
    
    # Рыночные данные
    if market_data:
        result += "### Текущие рыночные данные:\n"
        important_fields = ['LAST', 'CHANGE', 'PRCCHANGE', 'VOLTODAY', 'VALTODAY']
        for field in important_fields:
            if field in market_data and market_data[field]:
                result += f"- {field}: {market_data[field]}\n"
    
    return result


def search_moex_securities(query: str) -> str:
    """Поиск ценных бумаг на MOEX"""
    moex = MOEXUtils()
    
    results = moex.search_securities(query)
    
    if not results:
        return f"Ценные бумаги по запросу '{query}' не найдены"
    
    result_str = f"## Результаты поиска по запросу '{query}':\n\n"
    
    for i, security in enumerate(results[:10], 1):  # Ограничиваем 10 результатами
        result_str += f"### {i}. {security.get('SECNAME', 'Без названия')}\n"
        result_str += f"- Код: {security.get('SECID', 'N/A')}\n"
        result_str += f"- Тип: {security.get('TYPE', 'N/A')}\n"
        result_str += f"- Рынок: {security.get('MARKET', 'N/A')}\n\n"
    
    return result_str
"""
Утилиты для парсинга новостей с РБК
"""

import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
import time
import re


class RBCNewsParser:
    """Парсер новостей РБК"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_rss_news(self, category: str = "economics") -> List[Dict]:
        """
        Получить новости через RSS
        
        Args:
            category: Категория новостей (economics, stock, business)
        """
        rss_urls = {
            "economics": "https://rssexport.rbc.ru/rbcnews/news/20/full.rss",
            "stock": "https://rssexport.rbc.ru/rbcnews/news/stock/full.rss", 
            "business": "https://rssexport.rbc.ru/rbcnews/news/business/full.rss"
        }
        
        url = rss_urls.get(category, rss_urls["economics"])
        
        try:
            feed = feedparser.parse(url)
            news_list = []
            
            for entry in feed.entries:
                news_item = {
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published,
                    'summary': entry.get('summary', ''),
                    'category': category
                }
                
                # Парсим дату
                try:
                    news_item['published_date'] = datetime.strptime(
                        entry.published, '%a, %d %b %Y %H:%M:%S %z'
                    ).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    news_item['published_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                news_list.append(news_item)
            
            return news_list
            
        except Exception as e:
            print(f"Ошибка получения RSS РБК: {e}")
            return []
    
    def get_market_news(self, days_back: int = 7) -> List[Dict]:
        """Получить рыночные новости за последние дни"""
        all_news = []
        
        # Получаем новости из разных категорий
        categories = ["economics", "stock", "business"]
        
        for category in categories:
            news = self.get_rss_news(category)
            
            # Фильтруем по дате
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for item in news:
                try:
                    news_date = datetime.strptime(item['published_date'], '%Y-%m-%d %H:%M:%S')
                    if news_date >= cutoff_date:
                        all_news.append(item)
                except:
                    continue
        
        # Сортируем по дате
        all_news.sort(key=lambda x: x['published_date'], reverse=True)
        
        return all_news
    
    def search_company_news(self, company_name: str, ticker: str = None, days_back: int = 7) -> List[Dict]:
        """Поиск новостей о конкретной компании"""
        all_news = self.get_market_news(days_back)
        
        # Ключевые слова для поиска
        search_terms = [company_name.lower()]
        if ticker:
            search_terms.append(ticker.lower())
        
        # Дополнительные варианты названий компаний
        company_variations = {
            'SBER': ['сбербанк', 'сбер'],
            'GAZP': ['газпром'],
            'LKOH': ['лукойл'],
            'YNDX': ['яндекс'],
            'ROSN': ['роснефть'],
            'NVTK': ['новатэк'],
            'PLZL': ['полюс'],
            'GMKN': ['норникель'],
            'MGNT': ['магнит'],
            'MTSS': ['мтс'],
            'RTKM': ['ростелеком'],
            'AFLT': ['аэрофлот'],
            'VTBR': ['втб'],
            'TATN': ['татнефть'],
            'SNGS': ['сургутнефтегаз'],
            'NLMK': ['нлмк'],
            'CHMF': ['северсталь'],
            'ALRS': ['алроса'],
            'MOEX': ['московская биржа', 'мосбиржа'],
            'MAIL': ['mail.ru'],
            'OZON': ['озон'],
            'FIXP': ['fix price']
        }
        
        if ticker and ticker.upper() in company_variations:
            search_terms.extend(company_variations[ticker.upper()])
        
        filtered_news = []
        
        for news_item in all_news:
            title_lower = news_item['title'].lower()
            summary_lower = news_item['summary'].lower()
            
            # Проверяем наличие ключевых слов
            for term in search_terms:
                if term in title_lower or term in summary_lower:
                    filtered_news.append(news_item)
                    break
        
        return filtered_news


def get_rbc_news(query: str = None, curr_date: str = None, look_back_days: int = 7) -> str:
    """
    Получить новости РБК
    
    Args:
        query: Поисковый запрос (название компании или тикер)
        curr_date: Текущая дата в формате YYYY-MM-DD
        look_back_days: Количество дней назад для поиска
    
    Returns:
        str: Отформатированные новости
    """
    parser = RBCNewsParser()
    
    if query:
        # Поиск новостей о конкретной компании
        news_list = parser.search_company_news(query, query, look_back_days)
        header = f"## Новости РБК о {query} за последние {look_back_days} дней:\n\n"
    else:
        # Общие рыночные новости
        news_list = parser.get_market_news(look_back_days)
        header = f"## Рыночные новости РБК за последние {look_back_days} дней:\n\n"
    
    if not news_list:
        return header + "Новости не найдены."
    
    news_str = ""
    for news in news_list[:20]:  # Ограничиваем 20 новостями
        news_str += f"### {news['title']} ({news['published_date']})\n"
        news_str += f"**Категория:** {news['category']}\n"
        if news['summary']:
            news_str += f"{news['summary']}\n"
        news_str += f"**Ссылка:** {news['link']}\n\n"
    
    return header + news_str


def get_rbc_market_overview(curr_date: str = None) -> str:
    """Получить обзор рынка от РБК"""
    parser = RBCNewsParser()
    
    # Получаем последние экономические новости
    economics_news = parser.get_rss_news("economics")
    stock_news = parser.get_rss_news("stock")
    
    result = "## Обзор рынка от РБК\n\n"
    
    if economics_news:
        result += "### Экономические новости:\n"
        for news in economics_news[:5]:
            result += f"- **{news['title']}** ({news['published_date']})\n"
            if news['summary']:
                result += f"  {news['summary'][:200]}...\n"
        result += "\n"
    
    if stock_news:
        result += "### Фондовый рынок:\n"
        for news in stock_news[:5]:
            result += f"- **{news['title']}** ({news['published_date']})\n"
            if news['summary']:
                result += f"  {news['summary'][:200]}...\n"
        result += "\n"
    
    return result
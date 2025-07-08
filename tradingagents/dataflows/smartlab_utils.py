"""
Утилиты для парсинга новостей с Smart-Lab.ru
"""

import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
import re
from bs4 import BeautifulSoup


class SmartLabParser:
    """Парсер новостей Smart-Lab.ru"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.rss_url = "https://smart-lab.ru/rss/"
    
    def get_rss_feed(self) -> List[Dict]:
        """Получить RSS ленту Smart-Lab"""
        try:
            feed = feedparser.parse(self.rss_url)
            news_list = []
            
            for entry in feed.entries:
                # Очищаем HTML теги из описания
                description = re.sub(r'<[^>]+>', '', entry.get('description', ''))
                
                news_item = {
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published,
                    'description': description,
                    'author': entry.get('author', 'Smart-Lab'),
                    'category': self._extract_category(entry.title)
                }
                
                # Парсим дату
                try:
                    news_item['published_date'] = datetime.strptime(
                        entry.published, '%a, %d %b %Y %H:%M:%S %z'
                    ).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        news_item['published_date'] = datetime.strptime(
                            entry.published, '%a, %d %b %Y %H:%M:%S %Z'
                        ).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        news_item['published_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                news_list.append(news_item)
            
            return news_list
            
        except Exception as e:
            print(f"Ошибка получения RSS Smart-Lab: {e}")
            return []
    
    def _extract_category(self, title: str) -> str:
        """Определить категорию новости по заголовку"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['дивиденд', 'выплат', 'доходность']):
            return 'dividends'
        elif any(word in title_lower for word in ['отчет', 'финанс', 'прибыль', 'выручка']):
            return 'financials'
        elif any(word in title_lower for word in ['цб', 'ключевая ставка', 'инфляция']):
            return 'monetary_policy'
        elif any(word in title_lower for word in ['нефть', 'газ', 'золото', 'валют']):
            return 'commodities'
        elif any(word in title_lower for word in ['сша', 'китай', 'европа', 'санкции']):
            return 'geopolitics'
        else:
            return 'general'
    
    def filter_by_date(self, news_list: List[Dict], days_back: int = 7) -> List[Dict]:
        """Фильтровать новости по дате"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        filtered_news = []
        
        for news in news_list:
            try:
                news_date = datetime.strptime(news['published_date'], '%Y-%m-%d %H:%M:%S')
                if news_date >= cutoff_date:
                    filtered_news.append(news)
            except:
                continue
        
        return filtered_news
    
    def search_company_news(self, company_name: str, ticker: str = None, days_back: int = 7) -> List[Dict]:
        """Поиск новостей о конкретной компании"""
        all_news = self.get_rss_feed()
        filtered_by_date = self.filter_by_date(all_news, days_back)
        
        # Ключевые слова для поиска
        search_terms = [company_name.lower()]
        if ticker:
            search_terms.append(ticker.lower())
        
        # Дополнительные варианты названий компаний
        company_variations = {
            'SBER': ['сбербанк', 'сбер', 'sber'],
            'GAZP': ['газпром', 'gazprom'],
            'LKOH': ['лукойл', 'lukoil'],
            'YNDX': ['яндекс', 'yandex'],
            'ROSN': ['роснефть', 'rosneft'],
            'NVTK': ['новатэк', 'novatek'],
            'PLZL': ['полюс', 'polyus'],
            'GMKN': ['норникель', 'nornickel'],
            'MGNT': ['магнит', 'magnit'],
            'MTSS': ['мтс', 'mts'],
            'RTKM': ['ростелеком', 'rostelecom'],
            'AFLT': ['аэрофлот', 'aeroflot'],
            'VTBR': ['втб', 'vtb'],
            'TATN': ['татнефть', 'tatneft'],
            'SNGS': ['сургутнефтегаз', 'surgutneftegas'],
            'NLMK': ['нлмк', 'nlmk'],
            'CHMF': ['северсталь', 'severstal'],
            'ALRS': ['алроса', 'alrosa'],
            'MOEX': ['московская биржа', 'мосбиржа', 'moex'],
            'MAIL': ['mail.ru', 'мейл'],
            'OZON': ['озон', 'ozon'],
            'FIXP': ['fix price', 'фикс прайс']
        }
        
        if ticker and ticker.upper() in company_variations:
            search_terms.extend(company_variations[ticker.upper()])
        
        company_news = []
        
        for news_item in filtered_by_date:
            title_lower = news_item['title'].lower()
            description_lower = news_item['description'].lower()
            
            # Проверяем наличие ключевых слов
            for term in search_terms:
                if term in title_lower or term in description_lower:
                    company_news.append(news_item)
                    break
        
        return company_news
    
    def get_market_sentiment(self, days_back: int = 7) -> Dict:
        """Анализ настроений рынка по новостям Smart-Lab"""
        news_list = self.get_rss_feed()
        filtered_news = self.filter_by_date(news_list, days_back)
        
        # Подсчет по категориям
        categories = {}
        sentiment_keywords = {
            'positive': ['рост', 'прибыль', 'увеличение', 'успех', 'позитив', 'подъем'],
            'negative': ['падение', 'убыток', 'снижение', 'кризис', 'проблем', 'спад'],
            'neutral': ['стабильн', 'без изменений', 'прогноз', 'ожидание']
        }
        
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for news in filtered_news:
            category = news['category']
            categories[category] = categories.get(category, 0) + 1
            
            # Анализ тональности
            text = (news['title'] + ' ' + news['description']).lower()
            
            pos_score = sum(1 for word in sentiment_keywords['positive'] if word in text)
            neg_score = sum(1 for word in sentiment_keywords['negative'] if word in text)
            
            if pos_score > neg_score:
                sentiment_counts['positive'] += 1
            elif neg_score > pos_score:
                sentiment_counts['negative'] += 1
            else:
                sentiment_counts['neutral'] += 1
        
        return {
            'total_news': len(filtered_news),
            'categories': categories,
            'sentiment': sentiment_counts,
            'period_days': days_back
        }


def get_smartlab_news(query: str = None, curr_date: str = None, look_back_days: int = 7) -> str:
    """
    Получить новости Smart-Lab
    
    Args:
        query: Поисковый запрос (название компании или тикер)
        curr_date: Текущая дата в формате YYYY-MM-DD
        look_back_days: Количество дней назад для поиска
    
    Returns:
        str: Отформатированные новости
    """
    parser = SmartLabParser()
    
    if query:
        # Поиск новостей о конкретной компании
        news_list = parser.search_company_news(query, query, look_back_days)
        header = f"## Новости Smart-Lab о {query} за последние {look_back_days} дней:\n\n"
    else:
        # Общие новости
        all_news = parser.get_rss_feed()
        news_list = parser.filter_by_date(all_news, look_back_days)
        header = f"## Новости Smart-Lab за последние {look_back_days} дней:\n\n"
    
    if not news_list:
        return header + "Новости не найдены."
    
    news_str = ""
    for news in news_list[:15]:  # Ограничиваем 15 новостями
        news_str += f"### {news['title']}\n"
        news_str += f"**Дата:** {news['published_date']}\n"
        news_str += f"**Автор:** {news['author']}\n"
        news_str += f"**Категория:** {news['category']}\n"
        if news['description']:
            news_str += f"{news['description'][:300]}...\n"
        news_str += f"**Ссылка:** {news['link']}\n\n"
    
    return header + news_str


def get_smartlab_market_sentiment(curr_date: str = None, look_back_days: int = 7) -> str:
    """Получить анализ настроений рынка от Smart-Lab"""
    parser = SmartLabParser()
    sentiment_data = parser.get_market_sentiment(look_back_days)
    
    result = f"## Анализ настроений рынка Smart-Lab за {look_back_days} дней\n\n"
    
    result += f"**Всего новостей:** {sentiment_data['total_news']}\n\n"
    
    # Тональность
    sentiment = sentiment_data['sentiment']
    total_sentiment = sum(sentiment.values())
    
    if total_sentiment > 0:
        result += "### Тональность новостей:\n"
        result += f"- Позитивные: {sentiment['positive']} ({sentiment['positive']/total_sentiment*100:.1f}%)\n"
        result += f"- Негативные: {sentiment['negative']} ({sentiment['negative']/total_sentiment*100:.1f}%)\n"
        result += f"- Нейтральные: {sentiment['neutral']} ({sentiment['neutral']/total_sentiment*100:.1f}%)\n\n"
    
    # Категории
    if sentiment_data['categories']:
        result += "### Распределение по категориям:\n"
        for category, count in sorted(sentiment_data['categories'].items(), key=lambda x: x[1], reverse=True):
            result += f"- {category}: {count}\n"
    
    return result
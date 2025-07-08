"""
Конфигурация для российского торгового фреймворка
"""

import os

RUSSIAN_CONFIG = {
    # Основные настройки
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results_russia"),
    "data_dir": os.getenv("TRADINGAGENTS_DATA_DIR", "./data_russia"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache_russia",
    ),
    
    # Настройки LLM для российского рынка
    "llm_provider": "deepseek",  # deepseek, gemini, openai
    "deep_think_llm": "deepseek-reasoner",  # Для глубокого анализа
    "quick_think_llm": "deepseek-chat",     # Для быстрых операций
    "backend_url": "https://api.deepseek.com",
    
    # Альтернативные настройки для Gemini
    "gemini_deep_model": "gemini-2.5-pro",
    "gemini_fast_model": "gemini-2.5-flash",
    
    # API ключи (устанавливаются через переменные окружения)
    "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY"),
    "gemini_api_key": os.getenv("GEMINI_API_KEY"),
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    
    # Настройки дебатов и обсуждений
    "max_debate_rounds": 2,  # Увеличено для более глубокого анализа
    "max_risk_discuss_rounds": 2,
    "max_recur_limit": 150,
    
    # Настройки инструментов
    "online_tools": True,  # Всегда используем онлайн инструменты для российского рынка
    "use_russian_sources": True,  # Использовать российские источники данных
    
    # Настройки российского рынка
    "market_timezone": "Europe/Moscow",
    "trading_hours": {
        "start": "10:00",
        "end": "18:45",
        "currency_start": "10:00", 
        "currency_end": "23:50"
    },
    "base_currency": "RUB",
    "settlement_period": "T+2",  # Период расчетов на MOEX
    
    # Источники данных
    "data_sources": {
        "market_data": "moex",
        "news_sources": ["rbc", "smartlab", "moex_news"],
        "fundamental_data": "moex",
        "sentiment_sources": ["smartlab", "rbc"]
    },
    
    # Настройки для российских компаний
    "default_companies": [
        "SBER", "GAZP", "LKOH", "YNDX", "ROSN", "NVTK", 
        "PLZL", "GMKN", "MGNT", "MTSS", "VTBR", "MOEX"
    ],
    
    # Индексы для анализа
    "market_indices": ["IMOEX", "RTSI", "MOEXFN", "MOEXOG", "MOEXMM"],
    
    # Настройки риск-менеджмента для российского рынка
    "risk_settings": {
        "max_position_size": 0.1,  # Максимальный размер позиции 10%
        "currency_hedge_threshold": 0.05,  # Порог валютного хеджирования
        "sanction_risk_factor": 1.5,  # Коэффициент санкционного риска
        "liquidity_threshold": 1000000,  # Минимальный дневной оборот в рублях
    },
    
    # Налоговые настройки РФ
    "tax_settings": {
        "dividend_tax_rate": 0.13,  # Налог на дивиденды для резидентов
        "capital_gains_tax_rate": 0.13,  # Налог на прирост капитала
        "broker_commission": 0.003,  # Типичная комиссия брокера
        "exchange_fee": 0.0001,  # Биржевой сбор
    },
    
    # Настройки уведомлений
    "notifications": {
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        "email_notifications": False,
    },
    
    # Настройки логирования
    "logging": {
        "level": "INFO",
        "file": "trading_agents_russia.log",
        "max_size": "10MB",
        "backup_count": 5,
    }
}

# Функции для работы с конфигурацией
def get_russian_config():
    """Получить конфигурацию для российского рынка"""
    return RUSSIAN_CONFIG.copy()

def update_russian_config(updates):
    """Обновить конфигурацию"""
    RUSSIAN_CONFIG.update(updates)

def set_llm_provider(provider, deep_model=None, fast_model=None, api_key=None, backend_url=None):
    """
    Установить провайдера LLM
    
    Args:
        provider: deepseek, gemini, openai
        deep_model: Модель для глубокого анализа
        fast_model: Модель для быстрых операций
        api_key: API ключ
        backend_url: URL API
    """
    RUSSIAN_CONFIG["llm_provider"] = provider.lower()
    
    if provider.lower() == "deepseek":
        RUSSIAN_CONFIG["deep_think_llm"] = deep_model or "deepseek-reasoner"
        RUSSIAN_CONFIG["quick_think_llm"] = fast_model or "deepseek-chat"
        RUSSIAN_CONFIG["backend_url"] = backend_url or "https://api.deepseek.com"
        if api_key:
            RUSSIAN_CONFIG["deepseek_api_key"] = api_key
            
    elif provider.lower() == "gemini":
        RUSSIAN_CONFIG["deep_think_llm"] = deep_model or "gemini-2.5-pro"
        RUSSIAN_CONFIG["quick_think_llm"] = fast_model or "gemini-2.5-flash"
        if api_key:
            RUSSIAN_CONFIG["gemini_api_key"] = api_key
            
    elif provider.lower() == "openai":
        RUSSIAN_CONFIG["deep_think_llm"] = deep_model or "gpt-4"
        RUSSIAN_CONFIG["quick_think_llm"] = fast_model or "gpt-3.5-turbo"
        RUSSIAN_CONFIG["backend_url"] = backend_url or "https://api.openai.com/v1"
        if api_key:
            RUSSIAN_CONFIG["openai_api_key"] = api_key

def validate_config():
    """Проверить корректность конфигурации"""
    required_keys = ["llm_provider", "deep_think_llm", "quick_think_llm"]
    
    for key in required_keys:
        if key not in RUSSIAN_CONFIG:
            raise ValueError(f"Отсутствует обязательный параметр конфигурации: {key}")
    
    provider = RUSSIAN_CONFIG["llm_provider"]
    api_key_map = {
        "deepseek": "deepseek_api_key",
        "gemini": "gemini_api_key", 
        "openai": "openai_api_key"
    }
    
    if provider in api_key_map:
        api_key = RUSSIAN_CONFIG.get(api_key_map[provider])
        if not api_key:
            print(f"Предупреждение: Не установлен API ключ для {provider}")
    
    return True

# Проверяем конфигурацию при импорте
validate_config()
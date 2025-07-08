# 🇷🇺 Российский торговый фреймворк

> **Адаптация TradingAgents для российского фондового рынка**
>
> Мульти-агентная система на базе LLM для анализа и торговли на Московской бирже (MOEX)

## 📋 Содержание

- [Обзор](#обзор)
- [Особенности российской версии](#особенности-российской-версии)
- [Установка](#установка)
- [Настройка API](#настройка-api)
- [Быстрый старт](#быстрый-старт)
- [Источники данных](#источники-данных)
- [Интеграция с AI](#интеграция-с-ai)
- [CLI интерфейс](#cli-интерфейс)
- [Примеры использования](#примеры-использования)
- [Конфигурация](#конфигурация)
- [Архитектура](#архитектура)
- [Ограничения и риски](#ограничения-и-риски)

## 🎯 Обзор

Российский торговый фреймворк - это адаптация оригинального TradingAgents для работы с российским фондовым рынком. Система использует специализированных AI-агентов для анализа российских компаний, торгующихся на Московской бирже (MOEX).

### Ключевые возможности

- 📊 **Анализ MOEX**: Интеграция с официальным API Московской биржи
- 🤖 **AI-агенты**: Поддержка Deepseek и Google Gemini с русскоязычными промптами
- 📰 **Российские новости**: Парсинг РБК, Smart-Lab и других источников
- 💼 **Портфельный анализ**: Анализ нескольких российских акций одновременно
- 🎛️ **CLI интерфейс**: Удобный интерфейс командной строки на русском языке
- 📈 **Технический анализ**: Адаптированные индикаторы для российского рынка

## 🇷🇺 Особенности российской версии

### Интеграция с MOEX API
- Получение котировок и торговых данных через официальное API
- Поддержка российских тикеров (SBER, GAZP, LKOH и др.)
- Учет времени торговых сессий MOEX (10:00-18:45 МСК)
- Работа с рублевыми котировками

### Российские источники данных
- **РБК**: Экономические новости и аналитика
- **Smart-Lab**: Инвестиционное сообщество и аналитика
- **MOEX**: Официальные данные биржи
- **Дивиденды**: История выплат российских компаний

### AI модели с поддержкой русского языка
- **Deepseek**: Специализированные модели для финансового анализа
- **Google Gemini**: Продвинутые модели с хорошей поддержкой русского
- **Русскоязычные промпты**: Все инструкции адаптированы для российского рынка

### Учет российской специфики
- Влияние санкций и геополитических факторов
- Валютные риски (курс рубля)
- Российское корпоративное управление
- Налогообложение операций с ценными бумагами в РФ
- Особенности дивидендной политики российских компаний

## 🚀 Установка

### Требования
- Python 3.10+
- Доступ к интернету для API вызовов
- API ключи для выбранных AI провайдеров

### Клонирование репозитория
```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

### Создание виртуального окружения
```bash
# Conda
conda create -n russian-trading python=3.10
conda activate russian-trading

# Или venv
python -m venv russian-trading
source russian-trading/bin/activate  # Linux/Mac
# russian-trading\Scripts\activate  # Windows
```

### Установка зависимостей
```bash
pip install -r requirements.txt
```

## 🔑 Настройка API

### Обязательные API ключи

Установите переменные окружения для выбранного AI провайдера:

#### Deepseek (рекомендуется)
```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key"
```

#### Google Gemini
```bash
export GEMINI_API_KEY="your_gemini_api_key"
```

#### OpenAI (опционально)
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

### Получение API ключей

1. **Deepseek**: Регистрация на [platform.deepseek.com](https://platform.deepseek.com)
2. **Google Gemini**: Получение ключа в [Google AI Studio](https://aistudio.google.com)
3. **OpenAI**: Регистрация на [platform.openai.com](https://platform.openai.com)

## ⚡ Быстрый старт

### 1. Простой анализ компании

```python
from tradingagents.graph.russian_trading_graph import RussianTradingAgentsGraph
from tradingagents.russian_config import set_llm_provider
import os

# Настройка Deepseek
set_llm_provider(
    provider="deepseek",
    deep_model="deepseek-reasoner",
    fast_model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

# Создание торгового графа
graph = RussianTradingAgentsGraph(
    selected_analysts=["market", "news", "fundamentals"],
    debug=True
)

# Анализ Сбербанка
final_state, decision = graph.propagate("SBER", "2024-12-20")
print(f"Решение для SBER: {decision}")
```

### 2. Анализ портфеля

```python
# Анализ нескольких компаний
portfolio_tickers = ["SBER", "GAZP", "LKOH", "YNDX"]
results = graph.analyze_portfolio(portfolio_tickers, "2024-12-20")

print(results["portfolio_summary"])
for ticker, recommendation in results["recommendations"].items():
    print(f"{ticker}: {recommendation}")
```

### 3. CLI интерфейс

```bash
# Интерактивный анализ
python -m cli.russian_main analyze

# Анализ портфеля
python -m cli.russian_main portfolio --tickers "SBER,GAZP,LKOH" --provider deepseek

# Обзор рынка
python -m cli.russian_main market-overview --provider gemini
```

## 📊 Источники данных

### MOEX API
- **Котировки**: Исторические и текущие цены
- **Объемы**: Данные о торговых оборотах
- **Дивиденды**: История выплат
- **Индексы**: IMOEX, RTSI и другие

### Новостные источники
- **РБК**: Экономические новости через RSS
- **Smart-Lab**: Аналитика и настроения инвесторов
- **MOEX News**: Официальные новости биржи

### Фундаментальные данные
- Информация о компаниях через MOEX API
- Дивидендная история
- Корпоративные события

## 🤖 Интеграция с AI

### Deepseek (рекомендуется)

```python
from tradingagents.russian_config import set_llm_provider

set_llm_provider(
    provider="deepseek",
    deep_model="deepseek-reasoner",  # Для глубокого анализа
    fast_model="deepseek-chat",      # Для быстрых операций
    api_key="your_deepseek_key"
)
```

**Преимущества Deepseek:**
- Специализация на аналитических задачах
- Хорошая поддержка русского языка
- Модель рассуждений для сложного анализа
- Конкурентные цены

### Google Gemini

```python
set_llm_provider(
    provider="gemini",
    deep_model="gemini-2.5-pro",    # Для сложных задач
    fast_model="gemini-2.5-flash",  # Для быстрых операций
    api_key="your_gemini_key"
)
```

**Преимущества Gemini:**
- Отличная поддержка русского языка
- Большой контекст
- Мультимодальные возможности
- Интеграция с Google сервисами

## 🖥️ CLI интерфейс

### Основные команды

```bash
# Интерактивный анализ с выбором параметров
python -m cli.russian_main analyze

# Анализ портфеля
python -m cli.russian_main portfolio \
  --tickers "SBER,GAZP,LKOH,YNDX" \
  --date "2024-12-20" \
  --provider deepseek

# Обзор российского рынка
python -m cli.russian_main market-overview \
  --date "2024-12-20" \
  --provider gemini
```

### Интерактивный режим

CLI предоставляет пошаговый интерфейс для:
1. Выбора тикера российской компании
2. Установки даты анализа
3. Выбора команды аналитиков
4. Настройки глубины исследования
5. Выбора AI провайдера и моделей

## 📚 Примеры использования

### Анализ Газпрома с Deepseek

```python
from tradingagents.graph.russian_trading_graph import RussianTradingAgentsGraph
from tradingagents.russian_config import get_russian_config, set_llm_provider

# Настройка
set_llm_provider("deepseek", api_key="your_key")
config = get_russian_config()

# Создание графа
graph = RussianTradingAgentsGraph(
    selected_analysts=["market", "news", "fundamentals"],
    config=config,
    debug=True
)

# Анализ
final_state, decision = graph.propagate("GAZP", "2024-12-20")

print(f"Решение: {decision}")
print(f"Рыночный анализ: {final_state['market_report'][:200]}...")
print(f"Новостной анализ: {final_state['news_report'][:200]}...")
```

### Сравнение банковского сектора

```python
# Анализ банков
bank_tickers = ["SBER", "VTBR", "AFKS", "RUAL"]
results = graph.analyze_portfolio(bank_tickers, "2024-12-20")

# Вывод рекомендаций
for ticker, rec in results["recommendations"].items():
    print(f"{ticker}: {rec}")
```

### Мониторинг индексов

```python
# Получение данных по индексам
summary = graph.get_russian_market_summary("2024-12-20")

print("Состояние индексов:")
for index, data in summary["indices"].items():
    print(f"{index}: {data}")
```

## ⚙️ Конфигурация

### Основные параметры

```python
from tradingagents.russian_config import get_russian_config, update_russian_config

config = get_russian_config()

# Настройка дебатов
update_russian_config({
    "max_debate_rounds": 3,           # Раунды дебатов
    "max_risk_discuss_rounds": 2,     # Раунды обсуждения рисков
    "max_recur_limit": 200,           # Лимит рекурсии
})

# Настройка рынка
update_russian_config({
    "market_timezone": "Europe/Moscow",
    "base_currency": "RUB",
    "settlement_period": "T+2",
})
```

### Риск-менеджмент

```python
# Настройки рисков для российского рынка
update_russian_config({
    "risk_settings": {
        "max_position_size": 0.1,        # Макс. размер позиции 10%
        "sanction_risk_factor": 1.5,     # Коэффициент санкционного риска
        "currency_hedge_threshold": 0.05, # Порог валютного хеджирования
        "liquidity_threshold": 1000000,   # Мин. дневной оборот в рублях
    }
})
```

### Налоговые настройки

```python
# Налогообложение в РФ
update_russian_config({
    "tax_settings": {
        "dividend_tax_rate": 0.13,      # Налог на дивиденды
        "capital_gains_tax_rate": 0.13, # Налог на прирост капитала
        "broker_commission": 0.003,      # Комиссия брокера
        "exchange_fee": 0.0001,         # Биржевой сбор
    }
})
```

## 🏗️ Архитектура

### Команды агентов

1. **Команда аналитиков**
   - Аналитик рынка MOEX
   - Новостной аналитик (РБК, Smart-Lab)
   - Фундаментальный аналитик

2. **Команда исследований**
   - Бычий исследователь
   - Медвежий исследователь
   - Менеджер исследований

3. **Команда трейдеров**
   - Трейдер

4. **Команда риск-менеджмента**
   - Агрессивный аналитик
   - Консервативный аналитик
   - Нейтральный аналитик

5. **Управление портфелем**
   - Портфельный менеджер

### Поток данных

```
MOEX API → Аналитики → Исследователи → Трейдер → Риск-менеджмент → Финальное решение
    ↑
Новости (РБК, Smart-Lab)
```

### Интеграция AI

- **Deepseek Reasoner**: Глубокий анализ с рассуждениями
- **Deepseek Chat**: Быстрые операции
- **Gemini Pro**: Сложные аналитические задачи
- **Gemini Flash**: Оперативные решения

## ⚠️ Ограничения и риски

### Технические ограничения

- **API лимиты**: Ограничения MOEX API и AI провайдеров
- **Задержки данных**: Возможные задержки в получении данных
- **Доступность**: Зависимость от внешних сервисов

### Финансовые риски

- **Не является финансовой консультацией**: Система предназначена для исследований
- **Санкционные риски**: Учитывайте ограничения для российских активов
- **Валютные риски**: Волатильность рубля может влиять на результаты
- **Ликвидность**: Некоторые российские акции могут иметь низкую ликвидность

### Рекомендации по использованию

1. **Тестирование**: Всегда тестируйте стратегии на исторических данных
2. **Диверсификация**: Не полагайтесь только на AI рекомендации
3. **Риск-менеджмент**: Используйте стоп-лоссы и лимиты позиций
4. **Мониторинг**: Регулярно отслеживайте изменения в регулировании
5. **Обновления**: Следите за обновлениями системы и моделей

## 📞 Поддержка

### Документация
- [Оригинальный TradingAgents](https://github.com/TauricResearch/TradingAgents)
- [MOEX API документация](https://iss.moex.com/iss/reference/)
- [Deepseek API](https://platform.deepseek.com/api-docs/)
- [Google Gemini API](https://ai.google.dev/docs)

### Сообщество
- [Discord сервер](https://discord.com/invite/hk9PGKShPK)
- [Telegram канал](https://t.me/tauric_research)
- [GitHub Issues](https://github.com/TauricResearch/TradingAgents/issues)

### Контакты
- Email: support@tauric.ai
- Website: [tauric.ai](https://tauric.ai)
- Twitter: [@TauricResearch](https://twitter.com/TauricResearch)

---

**Отказ от ответственности**: Данная система предназначена исключительно для исследовательских и образовательных целей. Не является финансовой консультацией. Торговля на финансовых рынках связана с высокими рисками. Всегда консультируйтесь с квалифицированными финансовыми консультантами перед принятием инвестиционных решений.
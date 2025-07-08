"""
Примеры использования российского торгового фреймворка
"""

import os
from datetime import date, timedelta
from tradingagents.graph.russian_trading_graph import RussianTradingAgentsGraph
from tradingagents.russian_config import set_llm_provider, get_russian_config


def example_1_basic_analysis():
    """Пример 1: Базовый анализ российской компании"""
    print("=" * 60)
    print("ПРИМЕР 1: Базовый анализ Сбербанка")
    print("=" * 60)
    
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
        debug=False  # Отключаем отладку для чистого вывода
    )
    
    # Анализ Сбербанка
    ticker = "SBER"
    analysis_date = "2024-12-20"
    
    print(f"🔍 Анализ {ticker} на дату {analysis_date}")
    
    try:
        final_state, decision = graph.propagate(ticker, analysis_date)
        
        print(f"\n🎯 ФИНАЛЬНОЕ РЕШЕНИЕ: {decision}")
        
        # Краткая сводка по каждому отчету
        if final_state.get("market_report"):
            print(f"\n📊 Рыночный анализ (краткая выдержка):")
            print(final_state["market_report"][:300] + "...")
        
        if final_state.get("news_report"):
            print(f"\n📰 Новостной анализ (краткая выдержка):")
            print(final_state["news_report"][:300] + "...")
        
        if final_state.get("fundamentals_report"):
            print(f"\n💼 Фундаментальный анализ (краткая выдержка):")
            print(final_state["fundamentals_report"][:300] + "...")
            
        print(f"\n✅ Анализ {ticker} завершен успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка анализа {ticker}: {e}")


def example_2_portfolio_analysis():
    """Пример 2: Анализ портфеля российских акций"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 2: Анализ портфеля российских акций")
    print("=" * 60)
    
    # Настройка Gemini для разнообразия
    set_llm_provider(
        provider="gemini",
        deep_model="gemini-2.5-pro",
        fast_model="gemini-2.5-flash",
        api_key=os.getenv("GEMINI_API_KEY")
    )
    
    # Создание торгового графа
    graph = RussianTradingAgentsGraph(
        selected_analysts=["market", "news"],  # Только рынок и новости для скорости
        debug=False
    )
    
    # Портфель голубых фишек
    portfolio_tickers = ["SBER", "GAZP", "LKOH", "YNDX"]
    analysis_date = "2024-12-20"
    
    print(f"💼 Анализ портфеля: {', '.join(portfolio_tickers)}")
    print(f"📅 Дата анализа: {analysis_date}")
    
    try:
        results = graph.analyze_portfolio(portfolio_tickers, analysis_date)
        
        # Выводим сводку
        print(results["portfolio_summary"])
        
        # Детальные рекомендации
        print("\n📋 Детальные рекомендации:")
        for ticker, recommendation in results["recommendations"].items():
            if "ERROR" in recommendation:
                print(f"  ❌ {ticker}: ОШИБКА")
            elif any(word in recommendation.upper() for word in ["ПОКУПАТЬ", "BUY"]):
                print(f"  🟢 {ticker}: ПОКУПАТЬ")
            elif any(word in recommendation.upper() for word in ["ПРОДАВАТЬ", "SELL"]):
                print(f"  🔴 {ticker}: ПРОДАВАТЬ")
            else:
                print(f"  🟡 {ticker}: ДЕРЖАТЬ")
        
        print(f"\n✅ Анализ портфеля завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка анализа портфеля: {e}")


def example_3_market_overview():
    """Пример 3: Обзор российского рынка"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 3: Обзор российского рынка")
    print("=" * 60)
    
    # Используем Deepseek для обзора рынка
    set_llm_provider(
        provider="deepseek",
        deep_model="deepseek-reasoner",
        fast_model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY")
    )
    
    graph = RussianTradingAgentsGraph(debug=False)
    
    analysis_date = "2024-12-20"
    
    print(f"🏛️ Обзор российского рынка на {analysis_date}")
    
    try:
        summary = graph.get_russian_market_summary(analysis_date)
        
        print(f"\n🤖 Используемая модель: {summary['config']}")
        print(f"📅 Дата: {summary['date']}")
        
        # Состояние индексов
        print(f"\n📈 Основные российские индексы:")
        for index, data in summary["indices"].items():
            if "Ошибка" not in data:
                print(f"  ✅ {index}: Данные получены")
            else:
                print(f"  ❌ {index}: Ошибка получения данных")
        
        # Обзор рынка
        if summary["market_overview"]:
            print(f"\n📰 Обзор рынка:")
            # Показываем первые 500 символов
            overview_text = summary["market_overview"][:500]
            if len(summary["market_overview"]) > 500:
                overview_text += "..."
            print(overview_text)
        
        print(f"\n✅ Обзор рынка получен!")
        
    except Exception as e:
        print(f"❌ Ошибка получения обзора рынка: {e}")


def example_4_sector_analysis():
    """Пример 4: Анализ сектора (банки)"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 4: Анализ банковского сектора")
    print("=" * 60)
    
    # Настройка
    set_llm_provider(
        provider="deepseek",
        deep_model="deepseek-reasoner",
        fast_model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY")
    )
    
    graph = RussianTradingAgentsGraph(
        selected_analysts=["market", "fundamentals"],
        debug=False
    )
    
    # Банковский сектор
    bank_tickers = ["SBER", "VTBR", "AFKS"]  # Сбербанк, ВТБ, АФК Система
    analysis_date = "2024-12-20"
    
    print(f"🏦 Анализ банковского сектора: {', '.join(bank_tickers)}")
    
    try:
        results = graph.analyze_portfolio(bank_tickers, analysis_date)
        
        print(f"\n📊 Результаты анализа банковского сектора:")
        
        buy_recommendations = []
        hold_recommendations = []
        sell_recommendations = []
        
        for ticker, rec in results["recommendations"].items():
            if any(word in rec.upper() for word in ["ПОКУПАТЬ", "BUY"]):
                buy_recommendations.append(ticker)
            elif any(word in rec.upper() for word in ["ПРОДАВАТЬ", "SELL"]):
                sell_recommendations.append(ticker)
            else:
                hold_recommendations.append(ticker)
        
        print(f"🟢 Рекомендации к покупке: {', '.join(buy_recommendations) if buy_recommendations else 'Нет'}")
        print(f"🟡 Рекомендации держать: {', '.join(hold_recommendations) if hold_recommendations else 'Нет'}")
        print(f"🔴 Рекомендации к продаже: {', '.join(sell_recommendations) if sell_recommendations else 'Нет'}")
        
        # Общий вывод по сектору
        if len(buy_recommendations) > len(sell_recommendations):
            print(f"\n💡 Общий вывод: Банковский сектор выглядит привлекательно")
        elif len(sell_recommendations) > len(buy_recommendations):
            print(f"\n💡 Общий вывод: Банковский сектор находится под давлением")
        else:
            print(f"\n💡 Общий вывод: Банковский сектор в состоянии неопределенности")
        
        print(f"\n✅ Анализ банковского сектора завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка анализа банковского сектора: {e}")


def example_5_custom_config():
    """Пример 5: Использование кастомной конфигурации"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 5: Кастомная конфигурация")
    print("=" * 60)
    
    # Получаем базовую конфигурацию
    config = get_russian_config()
    
    # Настраиваем для более глубокого анализа
    config.update({
        "max_debate_rounds": 3,  # Больше раундов дебатов
        "max_risk_discuss_rounds": 3,
        "llm_provider": "deepseek",
        "deep_think_llm": "deepseek-reasoner",
        "quick_think_llm": "deepseek-chat",
        "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY")
    })
    
    print("⚙️ Используется кастомная конфигурация:")
    print(f"  - Раунды дебатов: {config['max_debate_rounds']}")
    print(f"  - Раунды обсуждения рисков: {config['max_risk_discuss_rounds']}")
    print(f"  - Провайдер LLM: {config['llm_provider']}")
    print(f"  - Модель глубокого анализа: {config['deep_think_llm']}")
    
    # Создание графа с кастомной конфигурацией
    graph = RussianTradingAgentsGraph(
        selected_analysts=["market", "news", "fundamentals"],
        config=config,
        debug=False
    )
    
    # Анализ Яндекса (технологическая компания)
    ticker = "YNDX"
    analysis_date = "2024-12-20"
    
    print(f"\n🔍 Глубокий анализ {ticker} с кастомной конфигурацией")
    
    try:
        final_state, decision = graph.propagate(ticker, analysis_date)
        
        print(f"\n🎯 ФИНАЛЬНОЕ РЕШЕНИЕ для {ticker}: {decision}")
        
        # Показываем, что было больше дебатов
        if final_state.get("investment_debate_state"):
            debate_history = final_state["investment_debate_state"].get("history", "")
            debate_rounds = debate_history.count("Bull Analyst:") + debate_history.count("Bear Analyst:")
            print(f"📊 Проведено раундов дебатов: {debate_rounds}")
        
        print(f"\n✅ Глубокий анализ {ticker} завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка глубокого анализа {ticker}: {e}")


def main():
    """Запуск всех примеров"""
    print("🇷🇺 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ РОССИЙСКОГО ТОРГОВОГО ФРЕЙМВОРКА")
    print("=" * 80)
    
    # Проверяем наличие API ключей
    if not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("❌ Ошибка: Не установлены API ключи!")
        print("Установите DEEPSEEK_API_KEY или GEMINI_API_KEY")
        return
    
    try:
        # Запускаем примеры
        example_1_basic_analysis()
        example_2_portfolio_analysis()
        example_3_market_overview()
        example_4_sector_analysis()
        example_5_custom_config()
        
        print("\n" + "=" * 80)
        print("✅ ВСЕ ПРИМЕРЫ ВЫПОЛНЕНЫ УСПЕШНО!")
        print("📁 Результаты сохранены в папке results_russia/")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Выполнение прервано пользователем")
    except Exception as e:
        print(f"\n\n❌ Общая ошибка выполнения примеров: {e}")


if __name__ == "__main__":
    main()
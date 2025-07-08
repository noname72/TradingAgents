"""
Пример использования российского торгового фреймворка
"""

from tradingagents.graph.russian_trading_graph import RussianTradingAgentsGraph
from tradingagents.russian_config import get_russian_config, set_llm_provider
import os
from datetime import date, timedelta

def main():
    """Основная функция демонстрации"""
    
    print("🇷🇺 Торговый фреймворк для российского рынка")
    print("=" * 50)
    
    # Настройка провайдера LLM (выберите один)
    
    # Вариант 1: Deepseek (рекомендуется)
    set_llm_provider(
        provider="deepseek",
        deep_model="deepseek-reasoner",
        fast_model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        backend_url="https://api.deepseek.com"
    )
    
    # Вариант 2: Google Gemini
    # set_llm_provider(
    #     provider="gemini",
    #     deep_model="gemini-2.5-pro",
    #     fast_model="gemini-2.5-flash",
    #     api_key=os.getenv("GEMINI_API_KEY")
    # )
    
    # Получаем конфигурацию
    config = get_russian_config()
    
    # Создаем торговый граф
    russian_graph = RussianTradingAgentsGraph(
        selected_analysts=["market", "news", "fundamentals"],
        debug=True,
        config=config
    )
    
    print(f"✅ Инициализация завершена. Провайдер: {config['llm_provider']}")
    print(f"📊 Модели: {config['deep_think_llm']} / {config['quick_think_llm']}")
    
    # Пример 1: Анализ одной компании
    print("\n" + "="*50)
    print("📈 Анализ компании Сбербанк (SBER)")
    print("="*50)
    
    ticker = "SBER"
    analysis_date = "2024-12-20"
    
    try:
        final_state, decision = russian_graph.propagate(ticker, analysis_date)
        
        print(f"\n🎯 ФИНАЛЬНОЕ РЕШЕНИЕ для {ticker}: {decision}")
        print(f"📅 Дата анализа: {analysis_date}")
        
        # Выводим краткую сводку
        if final_state.get("market_report"):
            print(f"\n📊 Рыночный анализ (первые 200 символов):")
            print(final_state["market_report"][:200] + "...")
        
        if final_state.get("news_report"):
            print(f"\n📰 Новостной анализ (первые 200 символов):")
            print(final_state["news_report"][:200] + "...")
            
    except Exception as e:
        print(f"❌ Ошибка анализа {ticker}: {e}")
    
    # Пример 2: Анализ портфеля
    print("\n" + "="*50)
    print("💼 Анализ портфеля российских акций")
    print("="*50)
    
    portfolio_tickers = ["GAZP", "LKOH", "YNDX"]
    
    try:
        portfolio_results = russian_graph.analyze_portfolio(
            tickers=portfolio_tickers,
            date_str=analysis_date
        )
        
        print(portfolio_results["portfolio_summary"])
        
        print("\n📋 Детальные рекомендации:")
        for ticker, recommendation in portfolio_results["recommendations"].items():
            print(f"  {ticker}: {recommendation}")
            
    except Exception as e:
        print(f"❌ Ошибка анализа портфеля: {e}")
    
    # Пример 3: Обзор рынка
    print("\n" + "="*50)
    print("🏛️ Обзор российского рынка")
    print("="*50)
    
    try:
        market_summary = russian_graph.get_russian_market_summary(analysis_date)
        
        print(f"📅 Дата: {market_summary['date']}")
        print(f"🤖 Модель: {market_summary['config']}")
        
        print("\n📈 Основные индексы:")
        for index, data in market_summary["indices"].items():
            if "Ошибка" not in data:
                print(f"  {index}: Данные получены")
            else:
                print(f"  {index}: {data}")
                
        if market_summary["market_overview"]:
            print(f"\n📰 Обзор рынка (первые 300 символов):")
            print(market_summary["market_overview"][:300] + "...")
            
    except Exception as e:
        print(f"❌ Ошибка получения обзора рынка: {e}")
    
    print("\n" + "="*50)
    print("✅ Демонстрация завершена!")
    print("📁 Результаты сохранены в папке results_russia/")
    print("="*50)


if __name__ == "__main__":
    main()
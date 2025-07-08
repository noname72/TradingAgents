"""
Основной класс торгового графа для российского рынка
"""

import os
from pathlib import Path
import json
from datetime import date
from typing import Dict, Any, Tuple, List, Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.russian_config import get_russian_config, RUSSIAN_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)
from tradingagents.agents.utils.russian_agent_utils import (
    RussianToolkit,
    create_russian_market_analyst,
    create_russian_news_analyst,
    create_russian_fundamental_analyst
)
from tradingagents.dataflows.config import set_config

from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor


class RussianTradingAgentsGraph:
    """Основной класс для торгового фреймворка российского рынка"""

    def __init__(
        self,
        selected_analysts=["market", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
    ):
        """
        Инициализация торгового графа для российского рынка

        Args:
            selected_analysts: Список типов аналитиков для включения
            debug: Режим отладки
            config: Словарь конфигурации. Если None, используется российская конфигурация
        """
        self.debug = debug
        self.config = config or get_russian_config()

        # Обновляем конфигурацию интерфейса
        set_config(self.config)

        # Создаем необходимые директории
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache_russia"),
            exist_ok=True,
        )

        # Инициализируем LLM в зависимости от провайдера
        self._initialize_llms()

        # Инициализируем российский набор инструментов
        self.toolkit = RussianToolkit(config=self.config)

        # Инициализируем память для российского рынка
        self._initialize_memories()

        # Создаем узлы инструментов
        self.tool_nodes = self._create_russian_tool_nodes()

        # Инициализируем компоненты
        self.conditional_logic = ConditionalLogic(
            max_debate_rounds=self.config["max_debate_rounds"],
            max_risk_discuss_rounds=self.config["max_risk_discuss_rounds"]
        )
        
        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.toolkit,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
        )

        self.propagator = Propagator(max_recur_limit=self.config["max_recur_limit"])
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        # Отслеживание состояния
        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}

        # Настраиваем граф для российского рынка
        self.graph = self._setup_russian_graph(selected_analysts)

    def _initialize_llms(self):
        """Инициализация LLM в зависимости от провайдера"""
        provider = self.config["llm_provider"].lower()
        
        if provider == "deepseek":
            api_key = self.config.get("deepseek_api_key")
            if not api_key:
                raise ValueError("Не установлен DEEPSEEK_API_KEY")
            
            self.deep_thinking_llm = ChatOpenAI(
                model=self.config["deep_think_llm"],
                base_url=self.config["backend_url"],
                api_key=api_key
            )
            self.quick_thinking_llm = ChatOpenAI(
                model=self.config["quick_think_llm"],
                base_url=self.config["backend_url"],
                api_key=api_key
            )
            
        elif provider == "gemini":
            api_key = self.config.get("gemini_api_key")
            if not api_key:
                raise ValueError("Не установлен GEMINI_API_KEY")
            
            self.deep_thinking_llm = ChatGoogleGenerativeAI(
                model=self.config["deep_think_llm"],
                google_api_key=api_key
            )
            self.quick_thinking_llm = ChatGoogleGenerativeAI(
                model=self.config["quick_think_llm"],
                google_api_key=api_key
            )
            
        elif provider == "openai":
            api_key = self.config.get("openai_api_key")
            if not api_key:
                raise ValueError("Не установлен OPENAI_API_KEY")
            
            self.deep_thinking_llm = ChatOpenAI(
                model=self.config["deep_think_llm"],
                base_url=self.config.get("backend_url", "https://api.openai.com/v1"),
                api_key=api_key
            )
            self.quick_thinking_llm = ChatOpenAI(
                model=self.config["quick_think_llm"],
                base_url=self.config.get("backend_url", "https://api.openai.com/v1"),
                api_key=api_key
            )
        else:
            raise ValueError(f"Неподдерживаемый провайдер LLM: {provider}")

    def _initialize_memories(self):
        """Инициализация памяти для российского рынка"""
        self.bull_memory = FinancialSituationMemory("russian_bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("russian_bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("russian_trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("russian_invest_judge_memory", self.config)
        self.risk_manager_memory = FinancialSituationMemory("russian_risk_manager_memory", self.config)

    def _create_russian_tool_nodes(self) -> Dict[str, ToolNode]:
        """Создать узлы инструментов для российских источников данных"""
        return {
            "market": ToolNode([
                self.toolkit.get_moex_market_data,
                self.toolkit.get_russian_company_info,
            ]),
            "news": ToolNode([
                self.toolkit.get_rbc_news,
                self.toolkit.get_smartlab_news,
                self.toolkit.get_market_overview_russia,
            ]),
            "fundamentals": ToolNode([
                self.toolkit.get_russian_company_info,
                self.toolkit.get_russian_dividends,
                self.toolkit.get_russian_index_info,
            ]),
        }

    def _setup_russian_graph(self, selected_analysts):
        """Настроить граф для российского рынка"""
        # Переопределяем создание аналитиков для российского рынка
        original_setup = self.graph_setup.setup_graph
        
        def russian_setup_graph(analysts):
            # Создаем российских аналитиков
            analyst_nodes = {}
            delete_nodes = {}
            tool_nodes = {}

            if "market" in analysts:
                analyst_nodes["market"] = create_russian_market_analyst(
                    self.quick_thinking_llm, self.toolkit
                )
                delete_nodes["market"] = create_msg_delete()
                tool_nodes["market"] = self.tool_nodes["market"]

            if "news" in analysts:
                analyst_nodes["news"] = create_russian_news_analyst(
                    self.quick_thinking_llm, self.toolkit
                )
                delete_nodes["news"] = create_msg_delete()
                tool_nodes["news"] = self.tool_nodes["news"]

            if "fundamentals" in analysts:
                analyst_nodes["fundamentals"] = create_russian_fundamental_analyst(
                    self.quick_thinking_llm, self.toolkit
                )
                delete_nodes["fundamentals"] = create_msg_delete()
                tool_nodes["fundamentals"] = self.tool_nodes["fundamentals"]

            # Используем оригинальную логику для остальной части графа
            # но с российскими аналитиками
            self.graph_setup.tool_nodes.update(tool_nodes)
            return original_setup(analysts)

        return russian_setup_graph(selected_analysts)

    def propagate(self, company_ticker, trade_date):
        """
        Запустить торговый граф для российской компании
        
        Args:
            company_ticker: Тикер российской компании (например, SBER, GAZP)
            trade_date: Дата торговли
        
        Returns:
            Tuple: (финальное состояние, торговое решение)
        """
        self.ticker = company_ticker.upper()

        # Инициализируем состояние
        init_agent_state = self.propagator.create_initial_state(
            self.ticker, trade_date
        )
        args = self.propagator.get_graph_args()

        if self.debug:
            # Режим отладки с трассировкой
            trace = []
            print(f"🇷🇺 Анализ российской компании {self.ticker} на дату {trade_date}")
            
            for chunk in self.graph.stream(init_agent_state, **args):
                if len(chunk["messages"]) == 0:
                    pass
                else:
                    if self.debug:
                        print(f"📊 Обработка: {chunk.get('sender', 'Unknown')}")
                    trace.append(chunk)

            final_state = trace[-1]
        else:
            # Стандартный режим без трассировки
            final_state = self.graph.invoke(init_agent_state, **args)

        # Сохраняем текущее состояние для рефлексии
        self.curr_state = final_state

        # Логируем состояние
        self._log_russian_state(trade_date, final_state)

        # Возвращаем решение и обработанный сигнал
        return final_state, self.process_signal(final_state["final_trade_decision"])

    def _log_russian_state(self, trade_date, final_state):
        """Логирование состояния для российского рынка"""
        self.log_states_dict[str(trade_date)] = {
            "company_ticker": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "market_report": final_state.get("market_report", ""),
            "news_report": final_state.get("news_report", ""),
            "fundamentals_report": final_state.get("fundamentals_report", ""),
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"]["current_response"],
                "judge_decision": final_state["investment_debate_state"]["judge_decision"],
            },
            "trader_investment_decision": final_state.get("trader_investment_plan", ""),
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state.get("investment_plan", ""),
            "final_trade_decision": final_state.get("final_trade_decision", ""),
            "config_used": {
                "llm_provider": self.config["llm_provider"],
                "deep_model": self.config["deep_think_llm"],
                "fast_model": self.config["quick_think_llm"],
            }
        }

        # Сохраняем в файл
        directory = Path(f"results_russia/{self.ticker}/RussianTradingStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"results_russia/{self.ticker}/RussianTradingStrategy_logs/full_states_log_{trade_date}.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(self.log_states_dict, f, indent=4, ensure_ascii=False)

    def reflect_and_remember(self, returns_losses):
        """Рефлексия решений и обновление памяти на основе доходности"""
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal):
        """Обработать сигнал для извлечения основного решения"""
        return self.signal_processor.process_signal(full_signal)

    def get_russian_market_summary(self, date_str: str = None) -> Dict[str, Any]:
        """
        Получить сводку по российскому рынку
        
        Args:
            date_str: Дата в формате YYYY-MM-DD
        
        Returns:
            Dict: Сводка по рынку
        """
        from tradingagents.dataflows.russian_interface import (
            get_russian_index_data,
            get_russian_market_overview
        )
        
        if not date_str:
            date_str = date.today().strftime("%Y-%m-%d")
        
        summary = {
            "date": date_str,
            "indices": {},
            "market_overview": "",
            "config": self.config["llm_provider"]
        }
        
        # Получаем данные по основным индексам
        for index in self.config["market_indices"]:
            try:
                index_data = get_russian_index_data(index)
                summary["indices"][index] = index_data
            except Exception as e:
                summary["indices"][index] = f"Ошибка получения данных: {e}"
        
        # Получаем обзор рынка
        try:
            summary["market_overview"] = get_russian_market_overview(date_str)
        except Exception as e:
            summary["market_overview"] = f"Ошибка получения обзора: {e}"
        
        return summary

    def analyze_portfolio(self, tickers: List[str], date_str: str = None) -> Dict[str, Any]:
        """
        Анализ портфеля российских акций
        
        Args:
            tickers: Список тикеров российских компаний
            date_str: Дата анализа
        
        Returns:
            Dict: Результаты анализа портфеля
        """
        if not date_str:
            date_str = date.today().strftime("%Y-%m-%d")
        
        portfolio_analysis = {
            "date": date_str,
            "companies": {},
            "portfolio_summary": "",
            "recommendations": {}
        }
        
        for ticker in tickers:
            try:
                print(f"🔍 Анализ {ticker}...")
                final_state, decision = self.propagate(ticker, date_str)
                
                portfolio_analysis["companies"][ticker] = {
                    "decision": decision,
                    "market_report": final_state.get("market_report", ""),
                    "news_report": final_state.get("news_report", ""),
                    "fundamentals_report": final_state.get("fundamentals_report", ""),
                    "final_decision": final_state.get("final_trade_decision", "")
                }
                
                portfolio_analysis["recommendations"][ticker] = decision
                
            except Exception as e:
                portfolio_analysis["companies"][ticker] = {
                    "error": str(e),
                    "decision": "ERROR"
                }
                portfolio_analysis["recommendations"][ticker] = "ERROR"
        
        # Создаем сводку портфеля
        buy_count = sum(1 for d in portfolio_analysis["recommendations"].values() if "ПОКУПАТЬ" in d.upper() or "BUY" in d.upper())
        hold_count = sum(1 for d in portfolio_analysis["recommendations"].values() if "ДЕРЖАТЬ" in d.upper() or "HOLD" in d.upper())
        sell_count = sum(1 for d in portfolio_analysis["recommendations"].values() if "ПРОДАВАТЬ" in d.upper() or "SELL" in d.upper())
        
        portfolio_analysis["portfolio_summary"] = f"""
        ## Сводка по портфелю на {date_str}
        
        **Всего компаний:** {len(tickers)}
        - Рекомендации к покупке: {buy_count}
        - Рекомендации держать: {hold_count}  
        - Рекомендации к продаже: {sell_count}
        
        **Использованная модель:** {self.config['llm_provider']} ({self.config['deep_think_llm']})
        """
        
        return portfolio_analysis
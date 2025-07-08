"""
CLI для российского торгового фреймворка
"""

from typing import Optional
import datetime
import typer
from pathlib import Path
from functools import wraps
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from rich.table import Table
from collections import deque
import time
from rich.tree import Tree
from rich import box
from rich.align import Align
from rich.rule import Rule

from tradingagents.graph.russian_trading_graph import RussianTradingAgentsGraph
from tradingagents.russian_config import get_russian_config, set_llm_provider
from cli.models import AnalystType
from cli.utils import *

console = Console()

app = typer.Typer(
    name="RussianTradingAgents",
    help="Российский торговый фреймворк: Мульти-агентная система для анализа российского фондового рынка",
    add_completion=True,
)

# Буфер сообщений для российского интерфейса
class RussianMessageBuffer:
    def __init__(self, max_length=100):
        self.messages = deque(maxlen=max_length)
        self.tool_calls = deque(maxlen=max_length)
        self.current_report = None
        self.final_report = None
        self.agent_status = {
            # Команда аналитиков
            "Аналитик рынка": "ожидание",
            "Новостной аналитик": "ожидание", 
            "Фундаментальный аналитик": "ожидание",
            # Команда исследователей
            "Бычий исследователь": "ожидание",
            "Медвежий исследователь": "ожидание",
            "Менеджер исследований": "ожидание",
            # Команда трейдеров
            "Трейдер": "ожидание",
            # Команда риск-менеджмента
            "Агрессивный аналитик": "ожидание",
            "Нейтральный аналитик": "ожидание",
            "Консервативный аналитик": "ожидание",
            # Команда управления портфелем
            "Портфельный менеджер": "ожидание",
        }
        self.current_agent = None
        self.report_sections = {
            "market_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }

    def add_message(self, message_type, content):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, message_type, content))

    def add_tool_call(self, tool_name, args):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tool_calls.append((timestamp, tool_name, args))

    def update_agent_status(self, agent, status):
        if agent in self.agent_status:
            self.agent_status[agent] = status
            self.current_agent = agent

    def update_report_section(self, section_name, content):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            self._update_current_report()

    def _update_current_report(self):
        latest_section = None
        latest_content = None

        for section, content in self.report_sections.items():
            if content is not None:
                latest_section = section
                latest_content = content
               
        if latest_section and latest_content:
            section_titles = {
                "market_report": "Анализ рынка",
                "news_report": "Новостной анализ",
                "fundamentals_report": "Фундаментальный анализ",
                "investment_plan": "Решение команды исследований",
                "trader_investment_plan": "План команды трейдеров",
                "final_trade_decision": "Решение управления портфелем",
            }
            self.current_report = (
                f"### {section_titles[latest_section]}\n{latest_content}"
            )

        self._update_final_report()

    def _update_final_report(self):
        report_parts = []

        # Отчеты команды аналитиков
        if any(
            self.report_sections[section]
            for section in [
                "market_report",
                "news_report", 
                "fundamentals_report",
            ]
        ):
            report_parts.append("## Отчеты команды аналитиков")
            if self.report_sections["market_report"]:
                report_parts.append(
                    f"### Анализ рынка\n{self.report_sections['market_report']}"
                )
            if self.report_sections["news_report"]:
                report_parts.append(
                    f"### Новостной анализ\n{self.report_sections['news_report']}"
                )
            if self.report_sections["fundamentals_report"]:
                report_parts.append(
                    f"### Фундаментальный анализ\n{self.report_sections['fundamentals_report']}"
                )

        # Отчеты команды исследований
        if self.report_sections["investment_plan"]:
            report_parts.append("## Решение команды исследований")
            report_parts.append(f"{self.report_sections['investment_plan']}")

        # Отчеты команды трейдеров
        if self.report_sections["trader_investment_plan"]:
            report_parts.append("## План команды трейдеров")
            report_parts.append(f"{self.report_sections['trader_investment_plan']}")

        # Решение управления портфелем
        if self.report_sections["final_trade_decision"]:
            report_parts.append("## Решение управления портфелем")
            report_parts.append(f"{self.report_sections['final_trade_decision']}")

        self.final_report = "\n\n".join(report_parts) if report_parts else None


message_buffer = RussianMessageBuffer()


def create_russian_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )
    layout["main"].split_column(
        Layout(name="upper", ratio=3), Layout(name="analysis", ratio=5)
    )
    layout["upper"].split_row(
        Layout(name="progress", ratio=2), Layout(name="messages", ratio=3)
    )
    return layout


def update_russian_display(layout, spinner_text=None):
    # Заголовок
    layout["header"].update(
        Panel(
            "[bold green]Российский торговый фреймворк[/bold green]\n"
            "[dim]© [Tauric Research](https://github.com/TauricResearch) - Адаптация для РФ рынка[/dim]",
            title="🇷🇺 Российские торговые агенты",
            border_style="green",
            padding=(1, 2),
            expand=True,
        )
    )

    # Панель прогресса с российскими командами
    progress_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        box=box.SIMPLE_HEAD,
        title=None,
        padding=(0, 2),
        expand=True,
    )
    progress_table.add_column("Команда", style="cyan", justify="center", width=20)
    progress_table.add_column("Агент", style="green", justify="center", width=25)
    progress_table.add_column("Статус", style="yellow", justify="center", width=15)

    # Группировка агентов по командам
    teams = {
        "Аналитики": [
            "Аналитик рынка",
            "Новостной аналитик",
            "Фундаментальный аналитик",
        ],
        "Исследователи": ["Бычий исследователь", "Медвежий исследователь", "Менеджер исследований"],
        "Трейдеры": ["Трейдер"],
        "Риск-менеджмент": ["Агрессивный аналитик", "Нейтральный аналитик", "Консервативный аналитик"],
        "Портфель": ["Портфельный менеджер"],
    }

    for team, agents in teams.items():
        first_agent = agents[0]
        status = message_buffer.agent_status[first_agent]
        
        status_colors = {
            "ожидание": "yellow",
            "выполняется": "blue", 
            "завершено": "green",
            "ошибка": "red",
        }
        
        if status == "выполняется":
            spinner = Spinner("dots", text="[blue]выполняется[/blue]", style="bold cyan")
            status_cell = spinner
        else:
            status_color = status_colors.get(status, "white")
            status_cell = f"[{status_color}]{status}[/{status_color}]"
        
        progress_table.add_row(team, first_agent, status_cell)

        for agent in agents[1:]:
            status = message_buffer.agent_status[agent]
            if status == "выполняется":
                spinner = Spinner("dots", text="[blue]выполняется[/blue]", style="bold cyan")
                status_cell = spinner
            else:
                status_color = status_colors.get(status, "white")
                status_cell = f"[{status_color}]{status}[/{status_color}]"
            progress_table.add_row("", agent, status_cell)

        progress_table.add_row("─" * 20, "─" * 25, "─" * 15, style="dim")

    layout["progress"].update(
        Panel(progress_table, title="Прогресс", border_style="cyan", padding=(1, 2))
    )

    # Панель сообщений
    messages_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        expand=True,
        box=box.MINIMAL,
        show_lines=True,
        padding=(0, 1),
    )
    messages_table.add_column("Время", style="cyan", width=8, justify="center")
    messages_table.add_column("Тип", style="green", width=12, justify="center")
    messages_table.add_column("Содержание", style="white", no_wrap=False, ratio=1)

    # Объединяем вызовы инструментов и сообщения
    all_messages = []

    for timestamp, tool_name, args in message_buffer.tool_calls:
        if isinstance(args, str) and len(args) > 100:
            args = args[:97] + "..."
        all_messages.append((timestamp, "Инструмент", f"{tool_name}: {args}"))

    for timestamp, msg_type, content in message_buffer.messages:
        content_str = content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                    elif item.get('type') == 'tool_use':
                        text_parts.append(f"[Инструмент: {item.get('name', 'неизвестно')}]")
                else:
                    text_parts.append(str(item))
            content_str = ' '.join(text_parts)
        elif not isinstance(content_str, str):
            content_str = str(content)
            
        if len(content_str) > 200:
            content_str = content_str[:197] + "..."
        all_messages.append((timestamp, msg_type, content_str))

    all_messages.sort(key=lambda x: x[0])
    max_messages = 12
    recent_messages = all_messages[-max_messages:]

    for timestamp, msg_type, content in recent_messages:
        wrapped_content = Text(content, overflow="fold")
        messages_table.add_row(timestamp, msg_type, wrapped_content)

    if spinner_text:
        messages_table.add_row("", "Процесс", spinner_text)

    if len(all_messages) > max_messages:
        messages_table.footer = (
            f"[dim]Показано последних {max_messages} из {len(all_messages)} сообщений[/dim]"
        )

    layout["messages"].update(
        Panel(
            messages_table,
            title="Сообщения и инструменты",
            border_style="blue",
            padding=(1, 2),
        )
    )

    # Панель анализа
    if message_buffer.current_report:
        layout["analysis"].update(
            Panel(
                Markdown(message_buffer.current_report),
                title="Текущий отчет",
                border_style="green",
                padding=(1, 2),
            )
        )
    else:
        layout["analysis"].update(
            Panel(
                "[italic]Ожидание отчета анализа...[/italic]",
                title="Текущий отчет",
                border_style="green",
                padding=(1, 2),
            )
        )

    # Подвал со статистикой
    tool_calls_count = len(message_buffer.tool_calls)
    llm_calls_count = sum(
        1 for _, msg_type, _ in message_buffer.messages if msg_type == "Рассуждение"
    )
    reports_count = sum(
        1 for content in message_buffer.report_sections.values() if content is not None
    )

    stats_table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    stats_table.add_column("Статистика", justify="center")
    stats_table.add_row(
        f"Вызовы инструментов: {tool_calls_count} | Вызовы LLM: {llm_calls_count} | Отчеты: {reports_count}"
    )

    layout["footer"].update(Panel(stats_table, border_style="grey50"))


def get_russian_user_selections():
    """Получить все пользовательские настройки для российского анализа"""
    
    # ASCII арт приветствие
    welcome_ascii = """
  🇷🇺 Российские торговые агенты 🇷🇺
    
   ████████╗██████╗  █████╗ ██████╗ ██╗███╗   ██╗ ██████╗ 
   ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝ 
      ██║   ██████╔╝███████║██║  ██║██║██╔██╗ ██║██║  ███╗
      ██║   ██╔══██╗██╔══██║██║  ██║██║██║╚██╗██║██║   ██║
      ██║   ██║  ██║██║  ██║██████╔╝██║██║ ╚████║╚██████╔╝
      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
    """

    welcome_content = f"{welcome_ascii}\n"
    welcome_content += "[bold green]Российский торговый фреймворк: Мульти-агентная система для анализа MOEX[/bold green]\n\n"
    welcome_content += "[bold]Этапы работы:[/bold]\n"
    welcome_content += "I. Команда аналитиков → II. Команда исследований → III. Трейдер → IV. Риск-менеджмент → V. Управление портфелем\n\n"
    welcome_content += "[dim]Адаптировано для российского рынка на базе [Tauric Research](https://github.com/TauricResearch)[/dim]"

    welcome_box = Panel(
        welcome_content,
        border_style="green",
        padding=(1, 2),
        title="🇷🇺 Российские торговые агенты",
        subtitle="Анализ российского фондового рынка",
    )
    console.print(Align.center(welcome_box))
    console.print()

    def create_question_box(title, prompt, default=None):
        box_content = f"[bold]{title}[/bold]\n"
        box_content += f"[dim]{prompt}[/dim]"
        if default:
            box_content += f"\n[dim]По умолчанию: {default}[/dim]"
        return Panel(box_content, border_style="blue", padding=(1, 2))

    # Шаг 1: Тикер российской компании
    console.print(
        create_question_box(
            "Шаг 1: Тикер компании", "Введите тикер российской компании на MOEX", "SBER"
        )
    )
    selected_ticker = get_russian_ticker()

    # Шаг 2: Дата анализа
    default_date = datetime.datetime.now().strftime("%Y-%m-%d")
    console.print(
        create_question_box(
            "Шаг 2: Дата анализа",
            "Введите дату анализа (YYYY-MM-DD)",
            default_date,
        )
    )
    analysis_date = get_analysis_date()

    # Шаг 3: Выбор аналитиков
    console.print(
        create_question_box(
            "Шаг 3: Команда аналитиков", "Выберите аналитиков для анализа российского рынка"
        )
    )
    selected_analysts = select_russian_analysts()
    console.print(
        f"[green]Выбранные аналитики:[/green] {', '.join(selected_analysts)}"
    )

    # Шаг 4: Глубина исследования
    console.print(
        create_question_box(
            "Шаг 4: Глубина исследования", "Выберите уровень глубины исследования"
        )
    )
    selected_research_depth = select_research_depth()

    # Шаг 5: Провайдер LLM
    console.print(
        create_question_box(
            "Шаг 5: Провайдер ИИ", "Выберите провайдера искусственного интеллекта"
        )
    )
    selected_llm_provider = select_russian_llm_provider()
    
    # Шаг 6: Модели мышления
    console.print(
        create_question_box(
            "Шаг 6: Модели анализа", "Выберите модели для анализа"
        )
    )
    selected_deep_thinker = select_russian_deep_thinking_agent(selected_llm_provider)
    selected_shallow_thinker = select_russian_shallow_thinking_agent(selected_llm_provider)

    return {
        "ticker": selected_ticker,
        "analysis_date": analysis_date,
        "analysts": selected_analysts,
        "research_depth": selected_research_depth,
        "llm_provider": selected_llm_provider,
        "deep_thinker": selected_deep_thinker,
        "shallow_thinker": selected_shallow_thinker,
    }


def get_russian_ticker():
    """Получить тикер российской компании"""
    return typer.prompt("", default="SBER").upper()


def select_russian_analysts():
    """Выбрать российских аналитиков"""
    import questionary
    
    choices = questionary.checkbox(
        "Выберите команду аналитиков:",
        choices=[
            questionary.Choice("Аналитик рынка MOEX", value="market"),
            questionary.Choice("Новостной аналитик (РБК, Smart-Lab)", value="news"),
            questionary.Choice("Фундаментальный аналитик", value="fundamentals"),
        ],
        instruction="\n- Пробел для выбора/отмены\n- 'a' для выбора/отмены всех\n- Enter для завершения",
        validate=lambda x: len(x) > 0 or "Необходимо выбрать хотя бы одного аналитика.",
        style=questionary.Style([
            ("checkbox-selected", "fg:green"),
            ("selected", "fg:green noinherit"),
            ("highlighted", "noinherit"),
            ("pointer", "noinherit"),
        ]),
    ).ask()

    if not choices:
        console.print("\n[red]Аналитики не выбраны. Выход...[/red]")
        exit(1)

    return choices


def select_russian_llm_provider():
    """Выбрать российского провайдера LLM"""
    import questionary
    
    providers = [
        ("Deepseek (рекомендуется для российского рынка)", "deepseek"),
        ("Google Gemini (хорошая поддержка русского языка)", "gemini"),
        ("OpenAI (базовая поддержка)", "openai"),
    ]
    
    choice = questionary.select(
        "Выберите провайдера ИИ:",
        choices=[
            questionary.Choice(display, value=value) for display, value in providers
        ],
        instruction="\n- Стрелки для навигации\n- Enter для выбора",
        style=questionary.Style([
            ("selected", "fg:yellow noinherit"),
            ("highlighted", "fg:yellow noinherit"),
            ("pointer", "fg:yellow noinherit"),
        ]),
    ).ask()

    if choice is None:
        console.print("\n[red]Провайдер не выбран. Выход...[/red]")
        exit(1)

    return choice


def select_russian_deep_thinking_agent(provider):
    """Выбрать модель для глубокого анализа"""
    import questionary
    
    models = {
        "deepseek": [
            ("Deepseek Reasoner - Модель с рассуждениями для глубокого анализа", "deepseek-reasoner"),
            ("Deepseek Chat - Универсальная модель", "deepseek-chat"),
        ],
        "gemini": [
            ("Gemini 2.5 Pro - Продвинутая модель для сложных задач", "gemini-2.5-pro"),
            ("Gemini 2.5 Flash - Быстрая и эффективная модель", "gemini-2.5-flash"),
        ],
        "openai": [
            ("GPT-4 - Продвинутая модель OpenAI", "gpt-4"),
            ("GPT-3.5 Turbo - Быстрая модель", "gpt-3.5-turbo"),
        ]
    }
    
    choice = questionary.select(
        "Выберите модель для глубокого анализа:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in models[provider]
        ],
        instruction="\n- Стрелки для навигации\n- Enter для выбора",
        style=questionary.Style([
            ("selected", "fg:magenta noinherit"),
            ("highlighted", "fg:magenta noinherit"),
            ("pointer", "fg:magenta noinherit"),
        ]),
    ).ask()

    if choice is None:
        console.print("\n[red]Модель не выбрана. Выход...[/red]")
        exit(1)

    return choice


def select_russian_shallow_thinking_agent(provider):
    """Выбрать модель для быстрого анализа"""
    import questionary
    
    models = {
        "deepseek": [
            ("Deepseek Chat - Быстрая модель для оперативных задач", "deepseek-chat"),
            ("Deepseek Reasoner - Модель с рассуждениями", "deepseek-reasoner"),
        ],
        "gemini": [
            ("Gemini 2.5 Flash - Быстрая и эффективная модель", "gemini-2.5-flash"),
            ("Gemini 2.5 Pro - Продвинутая модель", "gemini-2.5-pro"),
        ],
        "openai": [
            ("GPT-3.5 Turbo - Быстрая модель", "gpt-3.5-turbo"),
            ("GPT-4 - Продвинутая модель", "gpt-4"),
        ]
    }
    
    choice = questionary.select(
        "Выберите модель для быстрого анализа:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in models[provider]
        ],
        instruction="\n- Стрелки для навигации\n- Enter для выбора",
        style=questionary.Style([
            ("selected", "fg:magenta noinherit"),
            ("highlighted", "fg:magenta noinherit"),
            ("pointer", "fg:magenta noinherit"),
        ]),
    ).ask()

    if choice is None:
        console.print("\n[red]Модель не выбрана. Выход...[/red]")
        exit(1)

    return choice


def run_russian_analysis():
    """Запустить анализ российского рынка"""
    # Получаем настройки пользователя
    selections = get_russian_user_selections()

    # Настраиваем провайдера LLM
    set_llm_provider(
        provider=selections["llm_provider"],
        deep_model=selections["deep_thinker"],
        fast_model=selections["shallow_thinker"]
    )

    # Создаем конфигурацию
    config = get_russian_config()
    config["max_debate_rounds"] = selections["research_depth"]
    config["max_risk_discuss_rounds"] = selections["research_depth"]

    # Инициализируем граф
    graph = RussianTradingAgentsGraph(
        selected_analysts=selections["analysts"], 
        config=config, 
        debug=True
    )

    # Создаем директорию результатов
    results_dir = Path(config["results_dir"]) / selections["ticker"] / selections["analysis_date"]
    results_dir.mkdir(parents=True, exist_ok=True)
    report_dir = results_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    log_file = results_dir / "message_tool.log"
    log_file.touch(exist_ok=True)

    # Декораторы для сохранения
    def save_message_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, message_type, content = obj.messages[-1]
            content = content.replace("\n", " ")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} [{message_type}] {content}\n")
        return wrapper
    
    def save_tool_call_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, tool_name, args = obj.tool_calls[-1]
            args_str = ", ".join(f"{k}={v}" for k, v in args.items())
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} [Вызов инструмента] {tool_name}({args_str})\n")
        return wrapper

    def save_report_section_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(section_name, content):
            func(section_name, content)
            if section_name in obj.report_sections and obj.report_sections[section_name] is not None:
                content = obj.report_sections[section_name]
                if content:
                    file_name = f"{section_name}.md"
                    with open(report_dir / file_name, "w", encoding="utf-8") as f:
                        f.write(content)
        return wrapper

    message_buffer.add_message = save_message_decorator(message_buffer, "add_message")
    message_buffer.add_tool_call = save_tool_call_decorator(message_buffer, "add_tool_call")
    message_buffer.update_report_section = save_report_section_decorator(message_buffer, "update_report_section")

    # Запускаем интерфейс
    layout = create_russian_layout()

    with Live(layout, refresh_per_second=4) as live:
        update_russian_display(layout)

        # Добавляем начальные сообщения
        message_buffer.add_message("Система", f"Выбранный тикер: {selections['ticker']}")
        message_buffer.add_message("Система", f"Дата анализа: {selections['analysis_date']}")
        message_buffer.add_message("Система", f"Провайдер ИИ: {selections['llm_provider']}")
        message_buffer.add_message("Система", f"Выбранные аналитики: {', '.join(selections['analysts'])}")
        update_russian_display(layout)

        # Сбрасываем статусы агентов
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "ожидание")

        # Сбрасываем секции отчетов
        for section in message_buffer.report_sections:
            message_buffer.report_sections[section] = None
        message_buffer.current_report = None
        message_buffer.final_report = None

        # Устанавливаем первого аналитика в статус выполнения
        first_analyst_map = {
            "market": "Аналитик рынка",
            "news": "Новостной аналитик", 
            "fundamentals": "Фундаментальный аналитик"
        }
        
        if selections['analysts']:
            first_analyst = first_analyst_map.get(selections['analysts'][0])
            if first_analyst:
                message_buffer.update_agent_status(first_analyst, "выполняется")
        
        update_russian_display(layout)

        # Создаем текст спиннера
        spinner_text = f"Анализ {selections['ticker']} на {selections['analysis_date']}..."
        update_russian_display(layout, spinner_text)

        # Запускаем анализ
        try:
            final_state, decision = graph.propagate(selections["ticker"], selections["analysis_date"])
            
            # Обновляем статусы всех агентов на завершено
            for agent in message_buffer.agent_status:
                message_buffer.update_agent_status(agent, "завершено")

            message_buffer.add_message("Анализ", f"Анализ {selections['ticker']} завершен")
            
            # Обновляем секции отчетов
            for section in message_buffer.report_sections.keys():
                if section in final_state:
                    message_buffer.update_report_section(section, final_state[section])

            update_russian_display(layout)
            
            # Показываем финальный результат
            console.print(f"\n🎯 [bold green]ФИНАЛЬНОЕ РЕШЕНИЕ для {selections['ticker']}: {decision}[/bold green]")
            
        except Exception as e:
            console.print(f"\n❌ [red]Ошибка анализа: {e}[/red]")
            for agent in message_buffer.agent_status:
                message_buffer.update_agent_status(agent, "ошибка")
            update_russian_display(layout)


@app.command()
def analyze():
    """Запустить анализ российского рынка"""
    run_russian_analysis()


@app.command()
def portfolio(
    tickers: str = typer.Option(..., help="Тикеры через запятую (например: SBER,GAZP,LKOH)"),
    date: str = typer.Option(None, help="Дата анализа (YYYY-MM-DD)"),
    provider: str = typer.Option("deepseek", help="Провайдер ИИ (deepseek/gemini/openai)")
):
    """Анализ портфеля российских акций"""
    
    if not date:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    
    console.print(f"🇷🇺 [bold]Анализ портфеля российских акций[/bold]")
    console.print(f"📅 Дата: {date}")
    console.print(f"🤖 Провайдер: {provider}")
    console.print(f"📊 Тикеры: {', '.join(ticker_list)}")
    console.print()
    
    # Настраиваем провайдера
    if provider == "deepseek":
        set_llm_provider("deepseek", "deepseek-reasoner", "deepseek-chat")
    elif provider == "gemini":
        set_llm_provider("gemini", "gemini-2.5-pro", "gemini-2.5-flash")
    elif provider == "openai":
        set_llm_provider("openai", "gpt-4", "gpt-3.5-turbo")
    
    config = get_russian_config()
    graph = RussianTradingAgentsGraph(debug=False, config=config)
    
    try:
        results = graph.analyze_portfolio(ticker_list, date)
        
        console.print(results["portfolio_summary"])
        
        console.print("\n📋 [bold]Детальные рекомендации:[/bold]")
        for ticker, recommendation in results["recommendations"].items():
            if "ERROR" in recommendation:
                console.print(f"  {ticker}: [red]ОШИБКА[/red]")
            elif any(word in recommendation.upper() for word in ["ПОКУПАТЬ", "BUY"]):
                console.print(f"  {ticker}: [green]ПОКУПАТЬ[/green]")
            elif any(word in recommendation.upper() for word in ["ПРОДАВАТЬ", "SELL"]):
                console.print(f"  {ticker}: [red]ПРОДАВАТЬ[/red]")
            else:
                console.print(f"  {ticker}: [yellow]ДЕРЖАТЬ[/yellow]")
                
    except Exception as e:
        console.print(f"❌ [red]Ошибка анализа портфеля: {e}[/red]")


@app.command()
def market_overview(
    date: str = typer.Option(None, help="Дата обзора (YYYY-MM-DD)"),
    provider: str = typer.Option("deepseek", help="Провайдер ИИ")
):
    """Обзор российского рынка"""
    
    if not date:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    console.print(f"🇷🇺 [bold]Обзор российского рынка[/bold]")
    console.print(f"📅 Дата: {date}")
    console.print()
    
    # Настраиваем провайдера
    if provider == "deepseek":
        set_llm_provider("deepseek", "deepseek-reasoner", "deepseek-chat")
    elif provider == "gemini":
        set_llm_provider("gemini", "gemini-2.5-pro", "gemini-2.5-flash")
    
    config = get_russian_config()
    graph = RussianTradingAgentsGraph(debug=False, config=config)
    
    try:
        summary = graph.get_russian_market_summary(date)
        
        console.print(f"🤖 [bold]Модель:[/bold] {summary['config']}")
        
        console.print("\n📈 [bold]Основные индексы:[/bold]")
        for index, data in summary["indices"].items():
            if "Ошибка" not in data:
                console.print(f"  ✅ {index}: Данные получены")
            else:
                console.print(f"  ❌ {index}: Ошибка")
        
        if summary["market_overview"]:
            console.print(f"\n📰 [bold]Обзор рынка:[/bold]")
            # Показываем первые 500 символов
            overview_text = summary["market_overview"][:500]
            if len(summary["market_overview"]) > 500:
                overview_text += "..."
            console.print(overview_text)
            
    except Exception as e:
        console.print(f"❌ [red]Ошибка получения обзора: {e}[/red]")


if __name__ == "__main__":
    app()
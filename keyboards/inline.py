from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Добавить доход", callback_data="add_income")],
        [InlineKeyboardButton(text="💸 Добавить расход", callback_data="add_expense")],
        [InlineKeyboardButton(text="📊 Отчёт за месяц", callback_data="month_report")],
        [InlineKeyboardButton(text="📈 Общий отчёт", callback_data="total_report")],
        [InlineKeyboardButton(text="📉 График", callback_data="chart_report")],
        [InlineKeyboardButton(text="📥 Экспорт в Excel", callback_data="export_excel")],
    ])


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])


def get_report_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Текущий месяц", callback_data="report_current")],
        [InlineKeyboardButton(text="Прошлый месяц", callback_data="report_prev")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_menu")],
    ])


def get_export_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Скачать Excel", callback_data="download_excel")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_menu")],
    ])
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from keyboards import get_main_menu
from database import Database

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, db: Database):
    await db.add_user(message.from_user.id, message.from_user.username or "unknown")
    await message.answer(
        "Привет! Я бот для учёта доходов и расходов. Выбери действие:",
        reply_markup=get_main_menu()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 <b>Доступные команды:</b>\n\n"
        "/start — главное меню\n"
        "/help — помощь\n\n"
        "Используй кнопки для добавления доходов/расходов, просмотра отчётов, графиков и экспорта.",
        parse_mode="HTML"
    )
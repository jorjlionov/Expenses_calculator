from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import get_main_menu, get_cancel_keyboard
from database import Database

router = Router()


class ExpenseForm(StatesGroup):
    waiting_for_amount = State()


async def safe_edit_or_answer(callback: CallbackQuery, text: str, reply_markup=None, parse_mode=None):
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)


@router.callback_query(F.data == "add_income")
async def add_income_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ExpenseForm.waiting_for_amount)
    await state.update_data(t_type="income")
    await safe_edit_or_answer(
        callback,
        "💰 Введи сумму и категорию дохода через пробел:\n<i>Например: 50000 зарплата</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "add_expense")
async def add_expense_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ExpenseForm.waiting_for_amount)
    await state.update_data(t_type="expense")
    await safe_edit_or_answer(
        callback,
        "💸 Введи сумму и категорию расхода через пробел:\n<i>Например: 1500 продукты</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit_or_answer(callback, "Действие отменено.", reply_markup=get_main_menu())
    await callback.answer()


@router.message(ExpenseForm.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext, db: Database):
    data = await state.get_data()
    t_type = data.get("t_type")

    try:
        parts = message.text.strip().split(maxsplit=1)
        if len(parts) < 2:
            raise ValueError
        amount = float(parts[0])
        category = parts[1]
    except ValueError:
        await message.answer(
            "❌ Неверный формат. Введи сумму и категорию через пробел.",
            reply_markup=get_cancel_keyboard()
        )
        return

    try:
        await db.add_transaction(message.from_user.id, t_type, amount, category)
        emoji = "💰" if t_type == "income" else "💸"
        word = "Доход" if t_type == "income" else "Расход"
        await message.answer(
            f"{emoji} <b>{word}</b> {amount} ({category}) успешно добавлен!",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении: {e}", reply_markup=get_main_menu())
    finally:
        await state.clear()
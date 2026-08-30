from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime
from keyboards import get_main_menu, get_report_menu
from database import Database
from services import generate_chart
from aiogram.types import FSInputFile
import os

router = Router()


async def safe_edit_or_answer(callback: CallbackQuery, text: str, reply_markup=None, parse_mode=None):
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)


@router.callback_query(F.data == "month_report")
async def month_report_menu(callback: CallbackQuery):
    await safe_edit_or_answer(
        callback,
        "📊 Выбери период для отчёта:",
        reply_markup=get_report_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "report_current")
async def report_current(callback: CallbackQuery, db: Database):
    ym = datetime.now().strftime("%Y-%m")
    await send_report(callback, db, ym, "текущий месяц")


@router.callback_query(F.data == "report_prev")
async def report_prev(callback: CallbackQuery, db: Database):
    now = datetime.now()
    year = now.year
    month = now.month - 1
    if month == 0:
        month = 12
        year -= 1
    ym = f"{year}-{month:02d}"
    await send_report(callback, db, ym, "прошлый месяц")


async def send_report(callback: CallbackQuery, db: Database, ym: str, label: str):
    try:
        rows = await db.get_monthly_report(callback.from_user.id, ym)
        if not rows:
            await safe_edit_or_answer(
                callback,
                f"😶‍🌫️ За {label} нет записей.",
                reply_markup=get_main_menu()
            )
            await callback.answer()
            return

        report = f"📊 <b>Отчёт за {ym}:</b>\n\n"
        total_income = 0
        total_expense = 0
        data = []

        for row in rows:
            row_dict = dict(row)
            data.append(row_dict)
            t_type = row_dict["type"]
            total = row_dict["total"]
            category = row_dict["category"]
            report += f"{'💰' if t_type == 'income' else '💸'} {t_type.capitalize()}: {total} ({category})\n"
            if t_type == "income":
                total_income += total
            else:
                total_expense += total

        report += f"\n<b>Итого:</b>\n💰 Доходы: {total_income}\n💸 Расходы: {total_expense}\n"
        report += f"📈 Баланс: <b>{total_income - total_expense}</b>"

        await safe_edit_or_answer(
            callback,
            report,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    except Exception as e:
        await safe_edit_or_answer(
            callback,
            f"❌ Ошибка: {e}",
            reply_markup=get_main_menu()
        )
    await callback.answer()


@router.callback_query(F.data == "total_report")
async def total_report(callback: CallbackQuery, db: Database):
    try:
        rows = await db.get_total_report(callback.from_user.id)
        if not rows:
            await safe_edit_or_answer(
                callback,
                "😶‍🌫️ Нет записей за всё время.",
                reply_markup=get_main_menu()
            )
            await callback.answer()
            return

        report = "📈 <b>Общий отчёт:</b>\n\n"
        total_income = 0
        total_expense = 0

        for row in rows:
            row_dict = dict(row)
            t_type = row_dict["type"]
            total = row_dict["total"]
            report += f"{'💰' if t_type == 'income' else '💸'} {t_type.capitalize()}: {total}\n"
            if t_type == "income":
                total_income += total
            else:
                total_expense += total

        report += f"\n📈 Баланс: <b>{total_income - total_expense}</b>"
        await safe_edit_or_answer(
            callback,
            report,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    except Exception as e:
        await safe_edit_or_answer(
            callback,
            f"❌ Ошибка: {e}",
            reply_markup=get_main_menu()
        )
    await callback.answer()


@router.callback_query(F.data == "chart_report")
async def chart_report(callback: CallbackQuery, db: Database):
    try:
        ym = datetime.now().strftime("%Y-%m")
        rows = await db.get_monthly_report(callback.from_user.id, ym)
        if not rows:
            await safe_edit_or_answer(
                callback,
                "😶‍🌫️ Нет данных для графика.",
                reply_markup=get_main_menu()
            )
            await callback.answer()
            return

        data = [dict(row) for row in rows]
        chart_path = await generate_chart(data, callback.from_user.id, ym)

        try:
            await callback.message.delete()
        except Exception:
            pass

        await callback.message.answer_photo(
            FSInputFile(chart_path),
            caption=f"📉 График за {ym}",
            reply_markup=get_main_menu()
        )

        if os.path.exists(chart_path):
            os.remove(chart_path)
    except Exception as e:
        await safe_edit_or_answer(
            callback,
            f"❌ Ошибка при создании графика: {e}",
            reply_markup=get_main_menu()
        )
    await callback.answer()


@router.callback_query(F.data == "back_menu")
async def back_to_menu(callback: CallbackQuery):
    await safe_edit_or_answer(
        callback,
        "Главное меню:",
        reply_markup=get_main_menu()
    )
    await callback.answer()
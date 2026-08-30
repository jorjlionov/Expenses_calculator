from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from keyboards import get_main_menu, get_export_menu
from database import Database
from services import generate_excel
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


@router.callback_query(F.data == "export_excel")
async def export_menu(callback: CallbackQuery):
    await safe_edit_or_answer(
        callback,
        "📥 Экспорт всех транзакций в Excel:",
        reply_markup=get_export_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "download_excel")
async def download_excel(callback: CallbackQuery, db: Database):
    try:
        rows = await db.get_all_transactions(callback.from_user.id)
        if not rows:
            await safe_edit_or_answer(
                callback,
                "😶‍🌫️ Нет данных для экспорта.",
                reply_markup=get_main_menu()
            )
            await callback.answer()
            return

        data = [dict(row) for row in rows]
        excel_path = await generate_excel(data, callback.from_user.id)

        try:
            await callback.message.delete()
        except Exception:
            pass

        await callback.message.answer_document(
            FSInputFile(excel_path),
            caption="📥 Ваш отчёт в Excel",
            reply_markup=get_main_menu()
        )

        if os.path.exists(excel_path):
            os.remove(excel_path)
    except Exception as e:
        await safe_edit_or_answer(
            callback,
            f"❌ Ошибка при экспорте: {e}",
            reply_markup=get_main_menu()
        )
    await callback.answer()
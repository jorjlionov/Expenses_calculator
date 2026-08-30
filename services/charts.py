import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import List
import os

# Шрифт с кириллицей
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False


async def generate_chart(data: List[dict], user_id: int, period: str) -> str:
    """Генерирует круговую диаграмму доходов/расходов."""
    incomes = {row["category"]: row["total"] for row in data if row["type"] == "income"}
    expenses = {row["category"]: row["total"] for row in data if row["type"] == "expense"}

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f"Отчёт: {period}", fontsize=14, fontweight="bold")

    colors_income = ["#2ecc71", "#27ae60", "#1abc9c", "#16a085"]
    colors_expense = ["#e74c3c", "#c0392b", "#e67e22", "#d35400"]

    if incomes:
        axes[0].pie(
            incomes.values(),
            labels=incomes.keys(),
            autopct="%1.1f%%",
            colors=colors_income[:len(incomes)],
            startangle=90,
        )
        axes[0].set_title("Доходы", fontsize=12)
    else:
        axes[0].text(0.5, 0.5, "Нет данных", ha="center", va="center")
        axes[0].set_title("Доходы", fontsize=12)

    if expenses:
        axes[1].pie(
            expenses.values(),
            labels=expenses.keys(),
            autopct="%1.1f%%",
            colors=colors_expense[:len(expenses)],
            startangle=90,
        )
        axes[1].set_title("Расходы", fontsize=12)
    else:
        axes[1].text(0.5, 0.5, "Нет данных", ha="center", va="center")
        axes[1].set_title("Расходы", fontsize=12)

    plt.tight_layout()
    path = f"chart_{user_id}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path
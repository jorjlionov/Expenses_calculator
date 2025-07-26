import telebot as t
import sqlite3 as sql
from datetime import datetime
import random as r
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or '7801880044:AAEXNKInMFvEosUPhtU3klUb9h_fJw_RA2w'

abc = '💴💵💶💷💸💳'

bot = t.TeleBot(TELEGRAM_BOT_TOKEN)

# Подключение к базе данных
conn = sql.connect('finance.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT
)
''')

# Создание таблицы транзакций
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    amount REAL,
    category TEXT,
    date TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
''')

# Миграция: добавляем столбец user_id, если его нет
try:
    cursor.execute("SELECT user_id FROM transactions LIMIT 1")
except sql.OperationalError:
    # Если столбца user_id нет, добавляем его
    cursor.execute('ALTER TABLE transactions ADD COLUMN user_id INTEGER')
conn.commit()

def get_random_emoji():
    return abc[r.randint(0, 5)]

@bot.message_handler(commands=['start'])
def welcome_send(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    cursor.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()

    bot.reply_to(
        message,
        "Привет! Я бот для учёта доходов и расходов. \n\n"
        "Доступные команды:\n"
        "/add_salary — добавить доход\n"
        "/add_expense — добавить расход\n"
        "/month_report — отчёт за месяц\n"
        "/total_report — общий отчёт"
    )

@bot.message_handler(commands=['add_salary'])
def add_salary(message):
    bot.send_message(message.chat.id, 'Отправьте свой доход, например: 50000 зарплата')
    bot.register_next_step_handler(message, process_salary)

def process_salary(message):
    try:
        user_id = message.from_user.id
        amount, category = message.text.split(maxsplit=1)
        amount = float(amount)
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        emoji = get_random_emoji()

        cursor.execute('''
        INSERT INTO transactions (user_id, type, amount, category, date)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, 'income', amount, category, date))
        conn.commit()

        bot.reply_to(message, f'Доход {amount}{emoji} ({category}) успешно добавлен!')
    except ValueError:
        if message.text.startswith('/'):
            bot.reply_to(message, 'Пожалуйста, сначала введите сумму и категорию.')
        else:
            bot.reply_to(message, 'Неверный формат. Введите сумму и категорию через пробел.')

@bot.message_handler(commands=['add_expense'])
def add_expense(message):
    bot.send_message(message.chat.id, 'Введите сумму расхода и категорию, например: 100 еда')
    bot.register_next_step_handler(message, process_expenses)

def process_expenses(message):
    try:
        user_id = message.from_user.id
        amount, category = message.text.split(maxsplit=1)
        amount = float(amount)
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        emoji = get_random_emoji()

        cursor.execute('''
        INSERT INTO transactions (user_id, type, amount, category, date)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, 'expense', amount, category, date))
        conn.commit()

        bot.reply_to(message, f'Расход {amount}{emoji} ({category}) успешно добавлен!')
    except ValueError:
        if message.text.startswith('/'):
            bot.reply_to(message, 'Пожалуйста, сначала введите сумму и категорию.')
        else:
            bot.reply_to(message, 'Неверный формат. Введите сумму и категорию через пробел.')

@bot.message_handler(commands=['month_report'])
def monthly_report(message):
    user_id = message.from_user.id
    current_month = datetime.now().strftime('%Y-%m')

    cursor.execute('''
    SELECT type, SUM(amount), category FROM transactions
    WHERE user_id = ? AND strftime('%Y-%m', date) = ?
    GROUP BY type, category
    ''', (user_id, current_month))
    results = cursor.fetchall()

    if not results:
        bot.reply_to(message, 'За этот месяц нет записей 😶‍🌫️')
        return

    report = f'Отчёт за {current_month}: \n'
    total_income = 0
    total_expense = 0
    
    for row in results:
        transaction_type, total, category = row
        report += f'{transaction_type.capitalize()}: {total} ({category})\n'
        
        if transaction_type == 'income':
            total_income += total
        elif transaction_type == 'expense':
            total_expense += total
    
    balance = total_income - total_expense
    report += f'\nИтого:\nДоходы: {total_income}\nРасходы: {total_expense}\n'
    
    if balance > 0:
        report += f'Общий результат: +{balance}р (прибыль)'
    elif balance < 0:
        report += f'Общий результат: {balance}р (расход)'
    else:
        report += 'Общий результат: 0₽ (сбалансировано)'

    bot.reply_to(message, report)

@bot.message_handler(commands=['total_report'])
def total_report(message):
    user_id = message.from_user.id

    cursor.execute('''
    SELECT type, SUM(amount) FROM transactions
    WHERE user_id = ?
    GROUP BY type
    ''', (user_id,))
    results = cursor.fetchall()

    if not results:
        bot.reply_to(message, "Нет записей за всё время.")
        return

    report = "Общий отчёт:\n"
    total_income = 0
    total_expense = 0
    
    for row in results:
        transaction_type, total = row
        report += f"{transaction_type.capitalize()}: {total}\n"
        
        if transaction_type == 'income':
            total_income += total
        elif transaction_type == 'expense':
            total_expense += total
    
    balance = total_income - total_expense
    report += f'\nИтого:\nДоходы: {total_income}\nРасходы: {total_expense}\n'
    
    if balance > 0:
        report += f'Общий результат: +{balance}₽ (прибыль)'
    elif balance < 0:
        report += f'Общий результат: {balance}₽ (расход)'
    else:
        report += 'Общий результат: 0₽ (сбалансировано)'

    bot.reply_to(message, report)

if __name__ == "__main__":
    bot.polling(none_stop=True)

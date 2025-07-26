import telebot as t
import sqlite3 as sql
from datetime import datetime
import random as r
import os
from dotenv import load_dotenv  # Добавьте эту строку в импорты

# Загрузка переменных окружения из .env файла


# Получение токена из переменных окружения
TELEGRAM_BOT_TOKEN = '7801880044:AAHU2ZX9ah1C5gXN3cKmOOcpL8w1ogTW3so' 
  
abc = '💴💵💶💷💸💳'

bot = t.TeleBot(TELEGRAM_BOT_TOKEN)

# Подключение к базе данных
conn = sql.connect('finance.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы транзакций
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    amount REAL,
    category TEXT,
    date TEXT
)
''')

# Создание таблицы пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT
)
''')
conn.commit()

# Функция для получения случайного эмодзи
def get_random_emoji():
    return abc[r.randint(0, 5)]

# Приветственное сообщение
@bot.message_handler(commands=['start'])
def welcome_send(message):
    bot.reply_to(
        message,
        "Привет! Я бот для учёта доходов и расходов. \n\n"
        "Доступные команды:\n"
        "/add_salary — добавить доход\n"
        "/add_expense — добавить расход\n"
        "/monthly_report — отчёт за месяц\n"
        "/total_report — общий отчёт"
    )

# Добавление дохода
@bot.message_handler(commands=['add_salary'])
def add_salary(message):
    bot.send_message(message.chat.id, 'Отправьте свой доход, например: 50000 зарплата')
    bot.register_next_step_handler(message, process_salary)

def process_salary(message):
    try:
        amount, category = message.text.split(maxsplit=1)
        amount = float(amount)
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        emoji = get_random_emoji()

        cursor.execute('''
        INSERT INTO transactions (type, amount, category, date)
        VALUES (?, ?, ?, ?)
        ''', ('income', amount, category, date))
        conn.commit()

        bot.reply_to(message, f'Доход {amount}{emoji} ({category}) успешно добавлен!')
        #доп. проверка
    except ValueError:
        if message.text == '/add_expense':
            add_expense(message)
        elif message.text == '/month_report':
            monthly_report(message)
        elif message.text == '/total_report':
            total_report(message)
        else:        
            bot.reply_to(message, 'Неверно оформлена форма суммы и категории. Пожалуйста, введите сумму и категорию через пробел.')

# Добавление расхода
@bot.message_handler(commands=['add_expense'])
def add_expense(message):
    bot.send_message(message.chat.id, 'Введите сумму расхода и категорию, например: 100 еда')
    bot.register_next_step_handler(message, process_expenses)

def process_expenses(message):
    try:
        amount, category = message.text.split(maxsplit=1)
        amount = float(amount)
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        emoji = get_random_emoji()

        cursor.execute('''
        INSERT INTO transactions (type, amount, category, date)
        VALUES (?, ?, ?, ?)
        ''', ('expense', amount, category, date))
        conn.commit()

        bot.reply_to(message, f'Расход {amount}{emoji} ({category}) успешно добавлен!')
    except ValueError:
        if message.text == '/add_salary':
            add_expense(message)
        elif message.text == '/month_report':
            monthly_report(message)
        elif message.text == '/total_report':
            total_report(message)
        else:        
            bot.reply_to(message, 'Неверно оформлена форма суммы и категории. Пожалуйста, введите сумму и категорию через пробел.')
        
# Отчёт за месяц
@bot.message_handler(commands=['month_report'])
def monthly_report(message):
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('''
    SELECT type, SUM(amount), category FROM transactions
    WHERE strftime('%Y-%m', date) = ?
    GROUP BY type, category
    ''', (current_month,))
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

# Общий отчёт
@bot.message_handler(commands=['total_report'])
def total_report(message):
    cursor.execute('''
    SELECT type, SUM(amount) FROM transactions
    GROUP BY type
    ''')
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

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
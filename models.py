from peewee import *

# Подключаемся к базе данных SQLite
db = SqliteDatabase('finance.db')

# Модель для финансовых операций
class Transaction(Model):
    amount = FloatField()  # Сумма операции
    category = CharField() # Категория (например, "Еда", "Транспорт")
    date = CharField()     # Дата операции (в формате строки "YYYY-MM-DD")
    type = CharField(choices=['Доход', 'Расход'])  # Тип: доход или расход

    class Meta:
        database = db

# Модель для целей
class Goal(Model):
    title = CharField()          # Название цели
    target_amount = FloatField() # Целевая сумма
    current_amount = FloatField(default=0)  # Текущая сумма
    deadline = CharField()       # Дедлайн (в формате строки "YYYY-MM-DD")

    class Meta:
        database = db

# Создаем таблицы в базе данных (если они еще не созданы)
db.connect()
db.create_tables([Transaction, Goal], safe=True)
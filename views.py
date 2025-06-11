from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, 
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox, QMenu,
    QComboBox, QHBoxLayout, QFileDialog, QGraphicsOpacityEffect, QLabel,QCalendarWidget
)
from PyQt6.QtCore import Qt, QPropertyAnimation
from models import Goal, Transaction
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from datetime import datetime

# Диалог для добавления цели с анимацией появления (fade in)
class AddGoalDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить цель")

        # Поля для ввода данных
        self.title_input = QLineEdit()
        self.target_amount_input = QLineEdit()
        self.current_amount_input = QLineEdit()
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.selected_date_label = QLabel("Выберите дату")

        # Кнопки "ОК" и "Отмена"
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # Форма для размещения полей
        form_layout = QFormLayout()
        form_layout.addRow("Название цели:", self.title_input)
        form_layout.addRow("Целевая сумма:", self.target_amount_input)
        form_layout.addRow("Текущая сумма:", self.current_amount_input)
        form_layout.addRow("Дедлайн:", self.selected_date_label)
        form_layout.addRow(self.calendar)
        form_layout.addRow(buttons)

        self.setLayout(form_layout)

        self.calendar.selectionChanged.connect(self.update_selected_date)

        # Подготовка анимации появления диалога
        self.setWindowOpacity(0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)

    def showEvent(self, event):
        self.fade_animation.start()
        super().showEvent(event)

    def update_selected_date(self):
        # Обновляет выбранную дату в метке
        selected_date = self.calendar.selectedDate()
        self.selected_date_label.setText(selected_date.toString("dd.MM.yyyy"))

    def get_data(self):
        # Возвращает введенные данные
        return {
            "title": self.title_input.text(),
            "target_amount": self.target_amount_input.text(),
            "current_amount": self.current_amount_input.text(),
            "deadline": self.calendar.selectedDate().toString("yyyy-MM-dd"),
        }
class BalanceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.fade_animation = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Таблица для отображения баланса
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Категория", "Сумма"])
        layout.addWidget(self.table)

        self.setLayout(layout)

# Вкладка для работы с целями с анимацией fade in
class GoalsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.fade_animation = None  # Для хранения ссылки на анимацию
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Таблица для отображения целей
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Название", "Целевая сумма", "Текущая сумма", "Дедлайн"])
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)

        # Кнопка для добавления цели
        self.add_button = QPushButton("Добавить цель")
        self.add_button.clicked.connect(self.show_add_goal_dialog)
        layout.addWidget(self.add_button)

        self.setLayout(layout)
        self.load_goals()

    def showEvent(self, event):
        # Анимация появления вкладки
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self.fade_animation = QPropertyAnimation(effect, b"opacity")
        self.fade_animation.setDuration(1000)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()
        super().showEvent(event)

    def load_goals(self):
        # Загружает цели из базы данных и отображает их в таблице
        try:
            self.table.setRowCount(0)
            for goal in Goal.select():
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(goal.title))
                self.table.setItem(row_position, 1, QTableWidgetItem(str(goal.target_amount)))
                self.table.setItem(row_position, 2, QTableWidgetItem(str(goal.current_amount)))
                self.table.setItem(row_position, 3, QTableWidgetItem(goal.deadline))
        except Exception as e:
            print(f"Ошибка при загрузке целей: {e}")

    def show_add_goal_dialog(self):
        # Окно добавления цели
        dialog = AddGoalDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_data()
                target_amount = float(data["target_amount"])
                current_amount = float(data["current_amount"])
                Goal.create(
                    title=data["title"],
                    target_amount=target_amount,
                    current_amount=current_amount,
                    deadline=data["deadline"],
                )
                self.load_goals()
            except ValueError:
                QMessageBox.critical(self, "Ошибка", "Сумма должна быть числом!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить цель: {e}")

    def show_context_menu(self, position):
        """Показывает контекстное меню для таблицы целей."""
        menu = QMenu(self)
        delete_action = menu.addAction("Удалить цель")
        delete_action.triggered.connect(self.delete_selected_goal)
        menu.exec(self.table.viewport().mapToGlobal(position))

    def delete_selected_goal(self):
        # Удаляет выбранную цель
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            goal_id = Goal.select()[selected_row].id
            reply = QMessageBox.question(
                self, "Удаление цели", "Вы уверены, что хотите удалить эту цель?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                Goal.delete_by_id(goal_id)
                self.load_goals()

# Диалог для добавления операции с анимацией появления (fade in)
class AddTransactionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить операцию")

        # Поля для ввода данных
        self.amount_input = QLineEdit()
        self.category_input = QLineEdit()
        self.calendar2 = QCalendarWidget()
        self.calendar2.setGridVisible(True)
        self.select_date = QLabel('Выберите дату')
        self.type_input = QLineEdit()

        # Кнопки "ОК" и "Отмена"
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # Форма для размещения полей
        form_layout = QFormLayout()
        form_layout.addRow("Сумма:", self.amount_input)
        form_layout.addRow("Категория:", self.category_input)
        form_layout.addRow("Дата:", self.select_date)
        form_layout.addRow(self.calendar2)
        form_layout.addRow("Тип (Доход/Расход):", self.type_input)
        form_layout.addRow(buttons)

        self.setLayout(form_layout)

        self.calendar2.selectionChanged.connect(self.update_selected_date)

        # Подготовка анимации появления диалога
        self.setWindowOpacity(0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)

    def update_selected_date(self):
        # Обновляет выбранную дату в метке
        selected_date = self.calendar2.selectedDate()
        self.select_date.setText(selected_date.toString("dd.MM.yyyy"))

    def showEvent(self, event):
        self.fade_animation.start()
        super().showEvent(event)

    def get_data(self):
        # Возвращает введенные данные
        return {
            "Сумма": self.amount_input.text(),
            "Категория": self.category_input.text(),
            "Дата": self.calendar2.selectedDate().toString("yyyy-MM-dd"),
            "Тип": self.type_input.text(),
        }


# Вкладка для работы с операциями с анимацией fade in
class TransactionsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.fade_animation = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Таблица для отображения операций
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Сумма", "Категория", "Дата", "Тип"])
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)

        # Кнопка для добавления операции
        self.add_button = QPushButton("Добавить операцию")
        self.add_button.clicked.connect(self.show_add_transaction_dialog)
        layout.addWidget(self.add_button)

        self.setLayout(layout)
        self.load_transactions()

    def showEvent(self, event):
        # Анимация появления вкладки
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self.fade_animation = QPropertyAnimation(effect, b"opacity")
        self.fade_animation.setDuration(1000)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()
        super().showEvent(event)

    def load_transactions(self):
        # Загружает операции из базы данных и отображает их в таблице
        try:
            self.table.setRowCount(0)
            for transaction in Transaction.select():
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(str(transaction.amount)))
                self.table.setItem(row_position, 1, QTableWidgetItem(transaction.category))
                self.table.setItem(row_position, 2, QTableWidgetItem(transaction.date))
                self.table.setItem(row_position, 3, QTableWidgetItem(transaction.type))
        except Exception as e:
            print(f"Ошибка при загрузке операций: {e}")

    def show_add_transaction_dialog(self):
        # Показывает диалог для добавления операции
        dialog = AddTransactionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_data()
                amount = float(data["Сумма"])
                Transaction.create(
                    amount=amount,
                    category=data["Категория"],
                    date=data["Дата"],
                    type=data["Тип"],
                )
                self.load_transactions()
            except ValueError:
                QMessageBox.critical(self, "Ошибка", "Сумма должна быть числом!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить операцию: {e}")

    def show_context_menu(self, position):
        # Показывает контекстное меню для таблицы операций
        menu = QMenu(self)
        delete_action = menu.addAction("Удалить операцию")
        delete_action.triggered.connect(self.delete_selected_transaction)
        menu.exec(self.table.viewport().mapToGlobal(position))

    def delete_selected_transaction(self):
        # Удаляет выбранную операцию
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            transaction_id = Transaction.select()[selected_row].id
            reply = QMessageBox.question(
                self, "Удаление операции", "Вы уверены, что хотите удалить эту операцию?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                Transaction.delete_by_id(transaction_id)
                self.load_transactions()

# Вкладка для аналитики с анимацией fade in
class AnalyticsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.fade_animation = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Выбор типа графика
        self.chart_type = QComboBox()
        self.chart_type.addItems([
            "Круговая (категории)", 
            "Столбчатая (доходы/расходы)",
            "Линейная (динамика)"
        ])
        self.chart_type.currentTextChanged.connect(self.update_chart)
        
        # Кнопки экспорта
        self.export_btn = QPushButton("Экспорт в Excel")
        self.export_btn.clicked.connect(self.export_to_excel)
        
        self.export_chart_btn = QPushButton("Сохранить график")
        self.export_chart_btn.clicked.connect(self.export_chart)

        # Виджет для графика
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        
        # Размещение элементов управления
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.chart_type)
        controls_layout.addWidget(self.export_btn)
        controls_layout.addWidget(self.export_chart_btn)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        self.update_chart()

    def showEvent(self, event):
        # Анимация появления вкладки
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self.fade_animation = QPropertyAnimation(effect, b"opacity")
        self.fade_animation.setDuration(1000)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()
        super().showEvent(event)

    def update_chart(self):
        # Обновляет график
        self.figure.clear()
        chart_type = self.chart_type.currentText()
        
        if chart_type == "Круговая (категории)":
            self.create_pie_chart()
        elif chart_type == "Столбчатая (доходы/расходы)":
            self.create_bar_chart()
        elif chart_type == "Линейная (динамика)":
            self.create_line_chart()
            
        self.canvas.draw()

    def create_pie_chart(self):
        # Создает круговую диаграмму по категориям расходов
        try:
            query = Transaction.select().where(Transaction.type == "Расход")
            df = pd.DataFrame([{"Категории": t.category, "amount": t.amount} for t in query])
            if df.empty:
                raise ValueError("Нет данных для построения графика")
            df = df.groupby("Категории").sum()
            ax = self.figure.add_subplot(111)
            ax.pie(df["amount"], labels=df.index, autopct="%1.1f%%")
            ax.set_title("Расходы по категориям")
        except Exception as e:
            print(f"Ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def create_bar_chart(self):
        # Создает столбчатую диаграмму доходов/расходов по категориям
        try:
            query = Transaction.select()
            df = pd.DataFrame([{
                "Категории": t.category,
                "amount": t.amount,
                "Тип": t.type
            } for t in query])
            if df.empty:
                raise ValueError("Нет данных для построения графика")
            df = df.groupby(["Категории", "Тип"]).sum().unstack(fill_value=0)
            ax = self.figure.add_subplot(111)
            df["amount"].plot(kind="bar", ax=ax, stacked=True)
            ax.set_title("Доходы/расходы по категориям")
        except Exception as e:
            print(f"Ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def create_line_chart(self):
        # Создает линейный график доходов/расходов по датам
        try:
            query = Transaction.select()
            df = pd.DataFrame([{
                "Дата": datetime.strptime(t.date, "%Y-%m-%d"),
                "amount": t.amount,
                "Тип": t.type
            } for t in query])
            if df.empty:
                raise ValueError("Нет данных для построения графика")
            df = df.groupby(["Дата", "Тип"]).sum().unstack(fill_value=0)
            ax = self.figure.add_subplot(111)
            if "Доход" in df["amount"].columns:
                df["amount"]["Доход"].plot(ax=ax, label="Доход")
            if "Расход" in df["amount"].columns:
                df["amount"]["Расход"].plot(ax=ax, label="Расход")
            ax.set_title("Динамика доходов и расходов")
            ax.legend()
        except Exception as e:
            print(f"Ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def export_to_excel(self):
        # Экспортирует все транзакции в Excel
        try:
            query = Transaction.select()
            df = pd.DataFrame([{
                "Дата": t.date,
                "Категория": t.category,
                "Сумма": t.amount,
                "Тип": t.type
            } for t in query])
            path, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", "Excel Files (*.xlsx)")
            if path:
                df.to_excel(path, index=False)
                QMessageBox.information(self, "Успех", "Данные экспортированы в Excel!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать данные: {e}")

    def export_chart(self):
        # Сохраняет текущий график в файл
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Сохранить график", "", "PNG Files (*.png);;PDF Files (*.pdf)")
            if path:
                self.figure.savefig(path)
                QMessageBox.information(self, "Успех", "График сохранен!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить график: {e}")

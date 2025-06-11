import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from views import TransactionsTab, GoalsTab, AnalyticsTab
from PyQt6.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Основные настройки окна
        self.setWindowTitle("Домашние финансы")
        self.setGeometry(100, 100, 1200, 800)
        
        # Инициализация анимированных элементов
        self.init_ui()
        
        self.setWindowIcon(QIcon("money.ico"))
        

    def init_ui(self):
        """Создание элементов интерфейса"""
        # Создаем вкладки
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Добавляем виджеты вкладок
        self.transactions_tab = TransactionsTab()
        self.goals_tab = GoalsTab()
        self.analytics_tab = AnalyticsTab()
        
        self.tabs.addTab(self.transactions_tab, "Операции")
        self.tabs.addTab(self.goals_tab, "Цели")
        self.tabs.addTab(self.analytics_tab, "Аналитика")
        
        self.setCentralWidget(self.tabs)

    def showEvent(self, event):
        """Запуск анимации при показе окна"""
        super().showEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setWindowIcon(QIcon("money.ico"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
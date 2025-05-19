from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QApplication
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import os
import sys

# 导入 pages.py 中的 create_page 函数

from pages import create_page

class MainAppWindow(QMainWindow):
    def __init__(self, parent=None, db_manager=None):  # 添加db_manager参数
        super().__init__(parent)
        self.db_manager = db_manager  # 保存db_manager引用
        self.setWindowTitle('系统主界面')
        self.setFixedSize(1200, 800)
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #2c3e50;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 10, 0, 10)
        sidebar_layout.setSpacing(5)

        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            {"text": "数据源模块", "icon": "首页.png"},
            {"text": "检索模块", "icon": "检索.png"},
            {"text": "规则模块", "icon": "规则.png"},
            {"text": "可视化模块", "icon": "可视化.png"},
            {"text": "用户管理", "icon": "用户管理.png"},
            {"text": "帮助中心", "icon": "帮助中心.png"}
        ]

        for i, item in enumerate(nav_items):
            btn = QPushButton(item["text"])
            btn.setCheckable(True)
            btn.setFixedHeight(40)

            icon_path = os.path.join("res", item["icon"])
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(20, 20))

            btn.setStyleSheet(self.get_button_style())
            btn.clicked.connect(lambda _, x=i: self.switch_page(x))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # Developer info
        developer_label = QLabel("开发者：人工智能2班刘俊豪")
        developer_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding-left: 15px; margin-top: 20px;")
        sidebar_layout.addWidget(developer_label)

        # Right stacked pages
        self.stacked_pages = QStackedWidget()
        self.stacked_pages.setStyleSheet("background-color: #ecf0f1;")

        # Create pages using the imported function
        for i, item in enumerate(nav_items):
            page = create_page(item["text"], self.db_manager)  # 传递db_manager
            self.stacked_pages.addWidget(page)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_pages)
        self.nav_buttons[0].setChecked(True)

    def get_button_style(self):
        return '''
            QPushButton {
                color: #bdc3c7;
                text-align: left;
                padding-left: 15px;
                border: none;
                font-size: 14px;
                border-radius: 4px;
                margin: 0 8px;
            }
            QPushButton:hover {
                background-color: #34495e;
                color: #ecf0f1;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QPushButton:checked:hover {
                background-color: #2980b9;
            }
        '''

    def switch_page(self, index):
        for btn in self.nav_buttons:
            btn.setChecked(False)
        self.nav_buttons[index].setChecked(True)
        self.stacked_pages.setCurrentIndex(index)

    def closeEvent(self, event):
        """Override close event to ensure proper cleanup"""
        print("Main application window closing...")
        QApplication.quit()  # Ensure the application quits completely
        event.accept()

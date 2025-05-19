import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import DatabaseManager
from main_window import MainAppWindow

class LoginPage(QWidget):
    def __init__(self, main_window, db):
        super().__init__()
        self.main_window = main_window
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        self.title = QLabel('用户登录')
        self.title.setAlignment(Qt.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText('用户名')

        self.password = QLineEdit()
        self.password.setPlaceholderText('密码')
        self.password.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton('登录')
        self.login_btn.clicked.connect(self.check_credentials)

        self.register_btn = QPushButton('没有账号？立即注册')
        self.register_btn.clicked.connect(lambda: self.main_window.stacked_widget.setCurrentIndex(1))

        for widget in [self.title, self.username, self.password, self.login_btn, self.register_btn]:
            layout.addWidget(widget)

        self.add_developer_info(layout)

    def check_credentials(self):
        username = self.username.text()
        password = self.password.text()

        if not username or not password:
            QMessageBox.warning(self, '错误', '请输入用户名和密码')
            return

        if self.db.validate_user(username, password):
            QMessageBox.information(self, '成功', '登录成功！')
            self.main_app_window = MainAppWindow(db_manager=self.db)  # 传递db_manager
            self.main_app_window.show()
            self.main_window.hide()  # 隐藏主窗口而不仅仅是登录页面
        else:
            QMessageBox.critical(self, '错误', '用户名或密码错误')

    def add_developer_info(self, layout):
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        developer_label = QLabel('开发者：刘俊豪')
        developer_label.setStyleSheet('font-size: 10px; color: #666; margin-right: 5px;')
        bottom_layout.addWidget(developer_label)
        layout.addLayout(bottom_layout)

class RegisterPage(QWidget):
    def __init__(self, main_window, db):
        super().__init__()
        self.main_window = main_window
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        self.title = QLabel('用户注册')
        self.title.setAlignment(Qt.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText('用户名')

        self.password = QLineEdit()
        self.password.setPlaceholderText('密码')
        self.password.setEchoMode(QLineEdit.Password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText('确认密码')
        self.confirm_password.setEchoMode(QLineEdit.Password)

        self.register_btn = QPushButton('注册')
        self.register_btn.clicked.connect(self.register_user)

        self.back_btn = QPushButton('返回登录')
        self.back_btn.clicked.connect(lambda: self.main_window.stacked_widget.setCurrentIndex(0))

        for widget in [self.title, self.username, self.password,
                       self.confirm_password, self.register_btn, self.back_btn]:
            layout.addWidget(widget)

        self.add_developer_info(layout)

    def register_user(self):
        username = self.username.text()
        password = self.password.text()
        confirm = self.confirm_password.text()

        if not username or not password:
            QMessageBox.warning(self, '错误', '请输入用户名和密码')
            return

        if password != confirm:
            QMessageBox.warning(self, '错误', '两次输入的密码不一致')
            return

        if self.db.register_user(username, password):
            QMessageBox.information(self, '成功', '注册成功！')
            self.main_window.stacked_widget.setCurrentIndex(0)
        else:
            QMessageBox.critical(self, '错误', '用户名已存在')

    def add_developer_info(self, layout):
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        developer_label = QLabel('开发者：刘俊豪')
        developer_label.setStyleSheet('font-size: 10px; color: #666; margin-right: 5px;')
        bottom_layout.addWidget(developer_label)
        layout.addLayout(bottom_layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.main_app_window = None  # Initialize as None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('用户认证系统')
        self.setFixedSize(400, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.stacked_widget = QStackedWidget()
        self.login_page = LoginPage(self, self.db)
        self.register_page = RegisterPage(self, self.db)

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.register_page)

        main_layout.addWidget(self.stacked_widget)
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet('''
            QWidget {
                background-color: #f0f2f5;
            }
            QLabel {
                font-size: 24px;
                color: #1877f2;
                font-weight: bold;
                margin-bottom: 20px;
            }
            QLineEdit {
                padding: 12px;
                border: 1px solid #dddfe2;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton {
                padding: 12px;
                background-color: #1877f2;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
            #register_btn, #back_btn {
                background-color: #42b72a;
            }
            #register_btn:hover, #back_btn:hover {
                background-color: #36a420;
            }
        ''')

    def check_credentials(self):
        username = self.username.text()
        password = self.password.text()

        if not username or not password:
            QMessageBox.warning(self, '错误', '请输入用户名和密码')
            return

        if self.db.validate_user(username, password):
            QMessageBox.information(self, '成功', '登录成功！')
            self.main_app_window = MainAppWindow(db_manager=self.db)  # 传递db_manager
            self.main_app_window.show()
            self.main_window.hide()  # 隐藏主窗口而不仅仅是登录页面
        else:
            QMessageBox.critical(self, '错误', '用户名或密码错误')

    def open_main_app_window(self):
        """Open the MainAppWindow when login is successful"""
        if self.main_app_window is None:
            self.main_app_window = MainAppWindow()
            # 修改信号连接方式
            self.main_app_window.closeEvent = self.handle_main_window_close

        # 先显示主窗口，再隐藏登录窗口
        self.main_app_window.show()
        self.main_window.hide()  # 隐藏主窗口而不仅仅是登录页面

    def handle_main_window_close(self, event):
        """自定义主窗口关闭事件处理"""
        # 完全退出应用程序
        QApplication.quit()
        event.accept()

    def closeEvent(self, event):
        """处理登录窗口关闭事件"""
        print("Application is closing...")
        if hasattr(self, 'main_app_window') and self.main_app_window:
            self.main_app_window.close()
        QApplication.quit()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont('Arial', 12))
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
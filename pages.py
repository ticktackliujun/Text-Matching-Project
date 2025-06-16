from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QLineEdit, QPushButton, QFileDialog, QGroupBox, QTextEdit,
                             QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSplitter, QListWidget, QListWidgetItem,
                             QTabWidget, QFormLayout, QCheckBox, QSpinBox, QDoubleSpinBox, QProgressBar, QMenu, QAction,
                             QApplication)
from PyQt5.QtCore import Qt, QSize, QFileInfo
from PyQt5.QtGui import QFont, QIcon, QPixmap, QGuiApplication
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QDialogButtonBox,
    QMessageBox, QHeaderView
)

from Demo1.valuation_worker import EvaluationWorker
from worker_thread import IndexWorker
from search_worker import SearchWorker
import os
from PyQt5.QtCore import Qt
import csv
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QSplitter, QGroupBox, QCheckBox, QLineEdit,
                             QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
                             QDialog, QSlider, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon
import csv
import chardet
import matplotlib

from collections import defaultdict
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = ["SimHei"]  # 全局中文支持
plt.rcParams['axes.unicode_minus'] = False

def create_page(page_title, db_manager=None):
    page = QWidget()
    page.setStyleSheet("background-color: #f8f9fa;")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(15)

    if page_title == "数据源模块":
        return create_data_source_page()
    elif page_title == "检索模块":
        return create_search_page()
    elif page_title == "动态观察":
        return create_visualization_page()
    elif page_title == "用户管理":
        return create_user_management_page(db_manager)  # 传递db_manager
    elif page_title == "帮助中心":
        return create_help_center_page()
    elif page_title == "性能评估":
        return create_evaluation_page()
    return page


def create_data_source_page():
    page = QWidget()
    page.setStyleSheet("background-color: #f8f9fa;"
                       "font-family: 'SimHei';"
                       " font-size: 16px;")
    main_layout = QVBoxLayout(page)

    # 标题和操作栏
    header = QWidget()
    header_layout = QHBoxLayout(header)
    title = QLabel("文件索引管理")
    title.setStyleSheet("font-size: 24px; color: #2c3e50; font-weight: bold;")

    header_layout.addWidget(title)
    header_layout.addStretch()
    main_layout.addWidget(header)

    # 功能区：目录选择和过滤设置
    function_area = QGroupBox("索引设置")
    function_area.setStyleSheet("""
        QGroupBox {
            font-size: 16px;
            color: #3498db;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
        }
    """)
    function_layout = QGridLayout(function_area)

    # 目录选择
    dir_label = QLabel("选择目录:")
    dir_path = QLineEdit()
    dir_path.setReadOnly(True)
    dir_path.setStyleSheet("padding: 5px; border: 1px solid #ddd; border-radius: 4px;")

    browse_btn = QPushButton("浏览...")
    browse_btn.setStyleSheet("""
        QPushButton {
            padding: 5px 10px;
            background-color: #3498db;
            color: white;
            border-radius: 4px;
        }
        QPushButton:hover { background-color: #2980b9; }
    """)

    # 文件类型过滤
    filter_label = QLabel("文件类型过滤:")
    filter_types = QLineEdit()
    filter_types.setPlaceholderText("输入扩展名，用逗号分隔(如: txt,docx,pdf)")
    filter_types.setStyleSheet("padding: 5px; border: 1px solid #ddd; border-radius: 4px;")

    # 索引按钮
    index_btn = QPushButton("开始索引")
    index_btn.setIcon(QIcon.fromTheme("system-search"))
    index_btn.setStyleSheet("""
        QPushButton {
            padding: 8px 20px;
            background-color: #27ae60;
            color: white;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover { background-color: #219653; }
    """)

    # 状态栏
    status_label = QLabel("就绪")
    status_label.setStyleSheet("color: #7f8c8d;")

    # 布局设置
    function_layout.addWidget(dir_label, 0, 0)
    function_layout.addWidget(dir_path, 0, 1)
    function_layout.addWidget(browse_btn, 0, 2)
    function_layout.addWidget(filter_label, 1, 0)
    function_layout.addWidget(filter_types, 1, 1)
    function_layout.addWidget(index_btn, 1, 2)
    function_layout.addWidget(status_label, 2, 0, 1, 3)  # 跨列显示

    main_layout.addWidget(function_area)

    # 文件类型筛选器
    filter_bar = QWidget()
    filter_layout = QHBoxLayout(filter_bar)
    filter_layout.setContentsMargins(0, 0, 0, 0)

    file_type_buttons = {}
    for file_type in ["全部", "txt", "docx", "pdf", "pptx", "html"]:
        btn = QPushButton(file_type)
        btn.setCheckable(True)
        btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                margin-right: 5px;
                border-radius: 4px;
                background-color: #ecf0f1;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
            }
            QPushButton:hover { background-color: #d5dbdb; }
        """)
        filter_layout.addWidget(btn)
        file_type_buttons[file_type] = btn

    # 默认选中"全部"
    file_type_buttons["全部"].setChecked(True)

    filter_layout.addStretch()
    main_layout.addWidget(filter_bar)

    # 主内容区分割器
    splitter = QSplitter(Qt.Horizontal)

    # 文件列表区域
    file_list_area = QWidget()
    file_list_layout = QVBoxLayout(file_list_area)

    file_list = QListWidget()
    file_list.setStyleSheet("""
        QListWidget {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        QListWidget::item {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        QListWidget::item:hover {
            background-color: #f0f7fd;
        }
        QListWidget::item:selected {
            background-color: #d4e6f7;
        }
    """)

    file_list_layout.addWidget(file_list)
    splitter.addWidget(file_list_area)

    # 文件预览区域
    preview_area = QTabWidget()
    preview_area.setStyleSheet("""
        QTabWidget::pane {
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
        }
        QTabBar::tab {
            padding: 8px 15px;
            background: #ecf0f1;
            border: 1px solid #ddd;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background: white;
            border-bottom: 1px solid white;
            margin-bottom: -1px;
        }
    """)

    # 文本预览
    text_preview = QTextEdit()
    text_preview.setReadOnly(True)
    text_preview.setStyleSheet("border: none;")
    text_preview.setPlaceholderText("文件内容将显示在这里...")

    # 文件信息
    info_preview = QTextEdit()
    info_preview.setReadOnly(True)
    info_preview.setStyleSheet("border: none;")
    info_preview.setPlaceholderText("文件信息将显示在这里...")

    preview_area.addTab(text_preview, "文本预览")
    preview_area.addTab(info_preview, "文件信息")

    splitter.addWidget(preview_area)
    splitter.setSizes([300, 700])  # 初始大小比例

    main_layout.addWidget(splitter, 1)  # 占据剩余空间

    # 索引工作线程
    index_worker = None
    index_dialog = None  # 索引对话框

    # 功能实现
    def browse_directory():
        directory = QFileDialog.getExistingDirectory(page, "选择目录")
        if directory:
            dir_path.setText(directory)

    browse_btn.clicked.connect(browse_directory)

    def update_status(message):
        status_label.setText(message)

    def start_indexing():
        global index_worker, index_dialog
        directory = dir_path.text()
        if not directory:
            QMessageBox.warning(page, "警告", "请先选择目录")
            return

        index_btn.setEnabled(False)
        index_btn.setText("索引中...")

        filter_text = filter_types.text().strip()
        extensions = [ext.strip().lower() for ext in filter_text.split(',')] if filter_text else []

        # 创建索引对话框
        index_dialog = QDialog(page)
        index_dialog.setWindowTitle("正在索引文件")
        index_dialog.setMinimumSize(400, 200)
        index_dialog.setWindowModality(Qt.WindowModal)  # 模态对话框
        index_dialog.setStyleSheet("background-color: #f8f9fa;")

        dialog_layout = QVBoxLayout(index_dialog)

        # 状态标签
        dialog_status = QLabel("准备开始索引...")
        dialog_status.setStyleSheet("margin: 10px; color: #333;")
        dialog_layout.addWidget(dialog_status)

        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setStyleSheet("QProgressBar { border-radius: 4px; }")
        dialog_layout.addWidget(progress_bar)

        # 按钮区域
        button_layout = QHBoxLayout()
        finish_btn = QPushButton("完成")
        finish_btn.setEnabled(False)  # 初始禁用
        finish_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #27ae60;
                color: white;
                border-radius: 4px;
                margin-right: 10px;
            }
            QPushButton:hover { background-color: #219653; }
        """)

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)

        button_layout.addStretch()
        button_layout.addWidget(finish_btn)
        button_layout.addWidget(cancel_btn)
        dialog_layout.addLayout(button_layout)

        # 创建并启动线程
        index_worker = IndexWorker(directory, extensions)
        indexed_files = []  # 存储索引结果的局部变量

        # 连接信号
        def update_progress(progress, message):
            progress_bar.setValue(progress)
            dialog_status.setText(message)

        def on_indexing_finished(files):
            nonlocal indexed_files
            indexed_files = files  # 保存索引结果
            finish_btn.setEnabled(True)
            dialog_status.setText(f"索引完成，共找到 {len(files)} 个文件")

        index_worker.progress_updated.connect(update_progress)
        index_worker.indexing_finished.connect(on_indexing_finished)
        index_worker.indexing_canceled.connect(lambda: [
            dialog_status.setText("索引已取消"),
            index_dialog.close()
        ])

        # 完成按钮功能
        def on_finish_clicked():
            index_dialog.close()
            process_indexed_files(indexed_files)  # 使用保存的索引结果

        finish_btn.clicked.connect(on_finish_clicked)

        # 取消按钮功能
        def on_cancel_clicked():
            if index_worker:
                index_worker.cancel()
            index_dialog.close()
            index_btn.setEnabled(True)
            index_btn.setText("开始索引")
            update_status("索引已取消")

        cancel_btn.clicked.connect(on_cancel_clicked)

        # 对话框关闭时的处理
        def on_dialog_closed():
            if index_worker and index_worker.isRunning():
                index_worker.cancel()
            index_btn.setEnabled(True)
            index_btn.setText("开始索引")

        index_dialog.finished.connect(on_dialog_closed)

        # 显示对话框并启动线程
        index_worker.start()
        index_dialog.exec_()
    def process_indexed_files(files):
        """处理索引完成后的文件列表"""
        # 清空文件列表
        file_list.clear()

        # 保存文件列表到txt
        try:
            with open("file_list.txt", 'w', encoding='utf-8') as f:
                for file_path in files:
                    f.write(file_path + '\n')
        except Exception as e:
            print(f"保存文件列表失败: {str(e)}")
            update_status(f"保存文件列表失败: {str(e)}")

        # 添加文件到列表
        for file_path in files:
            file_info = QFileInfo(file_path)
            item = QListWidgetItem(file_info.fileName())
            item.setData(Qt.UserRole, {
                'path': file_path,
                'size': file_info.size(),
                'created': file_info.created(),
                'modified': file_info.lastModified()
            })
            file_list.addItem(item)

        # 显示完成信息
        update_status(f"索引完成，共找到 {len(files)} 个文件")

    index_btn.clicked.connect(start_indexing)

    def filter_files_by_type():
        selected_type = None
        for file_type, btn in file_type_buttons.items():
            if btn.isChecked():
                selected_type = file_type.lower()
                break

        if selected_type == "全部":
            # 显示所有文件
            for i in range(file_list.count()):
                file_list.item(i).setHidden(False)
        else:
            # 根据类型过滤
            for i in range(file_list.count()):
                item = file_list.item(i)
                file_path = item.data(Qt.UserRole)['path']
                if file_path.lower().endswith(f'.{selected_type}'):
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    # 连接类型筛选按钮
    for file_type, btn in file_type_buttons.items():
        btn.toggled.connect(filter_files_by_type)

    def show_file_info(item):
        file_data = item.data(Qt.UserRole)
        file_path = file_data['path']

        # 更新文件信息
        info_text = f"""
        文件路径: {file_path}
        文件大小: {file_data['size']} 字节
        创建时间: {file_data['created'].toString('yyyy-MM-dd hh:mm:ss')}
        修改时间: {file_data['modified'].toString('yyyy-MM-dd hh:mm:ss')}
        """
        info_preview.setText(info_text)

        # 尝试预览文本内容
        try:
            if file_path.lower().endswith(('.txt', '.md', '.csv', '.json', '.xml', '.html', '.css', '.js')):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1024 * 10)  # 读取前10KB
                    text_preview.setText(content)
            else:
                text_preview.setText(f"无法预览此类型的文件: {os.path.splitext(file_path)[1]}")
        except Exception as e:
            text_preview.setText(f"预览失败: {str(e)}")

    file_list.itemClicked.connect(show_file_info)

    # 实现二次过滤功能
    def open_secondary_filter():
        # 检查是否有文件列表
        if not os.path.exists("file_list.txt"):
            QMessageBox.warning(page, "警告", "请先完成索引操作")
            return

        # 读取文件列表
        try:
            with open("file_list.txt", 'r', encoding='utf-8') as f:
                all_files = [line.strip() for line in f if line.strip()]
        except Exception as e:
            QMessageBox.critical(page, "错误", f"读取文件列表失败: {str(e)}")
            return

        # 创建过滤对话框
        filter_dialog = QDialog(page)
        filter_dialog.setWindowTitle("二次过滤")
        filter_dialog.setMinimumSize(800, 600)
        filter_dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #f0f7fd;
            }
        """)

        # 对话框布局
        layout = QVBoxLayout(filter_dialog)

        # 搜索框
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("输入关键词过滤文件...")
        search_btn = QPushButton("搜索")
        search_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #3498db;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        # 操作按钮
        btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("全选")
        invert_select_btn = QPushButton("反选")
        clear_select_btn = QPushButton("清空")

        for btn in [select_all_btn, invert_select_btn, clear_select_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 5px 10px;
                    background-color: #ecf0f1;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #d5dbdb; }
            """)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        # 文件列表
        file_list_widget = QListWidget()
        file_list_widget.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(file_list_widget)

        # 填充文件列表
        for file_path in all_files:
            item = QListWidgetItem(file_path)
            item.setCheckState(Qt.Unchecked)
            file_list_widget.addItem(item)

        # 底部按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(filter_dialog.accept)
        button_box.rejected.connect(filter_dialog.reject)
        layout.addWidget(button_box)

        # 搜索功能
        def perform_search():
            keyword = search_input.text().lower()
            for i in range(file_list_widget.count()):
                item = file_list_widget.item(i)
                file_path = item.text().lower()
                item.setHidden(keyword not in file_path)

        search_input.textChanged.connect(perform_search)
        search_btn.clicked.connect(perform_search)

        # 选择功能
        def select_all():
            for i in range(file_list_widget.count()):
                item = file_list_widget.item(i)
                if not item.isHidden():
                    item.setCheckState(Qt.Checked)

        def invert_selection():
            for i in range(file_list_widget.count()):
                item = file_list_widget.item(i)
                if not item.isHidden():
                    item.setCheckState(Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked)

        def clear_selection():
            for i in range(file_list_widget.count()):
                item = file_list_widget.item(i)
                item.setCheckState(Qt.Unchecked)

        select_all_btn.clicked.connect(select_all)
        invert_select_btn.clicked.connect(invert_selection)
        clear_select_btn.clicked.connect(clear_selection)

        # 执行对话框
        if filter_dialog.exec_() == QDialog.Accepted:
            # 获取选中的文件
            selected_files = []
            for i in range(file_list_widget.count()):
                item = file_list_widget.item(i)
                if item.checkState() == Qt.Checked:
                    selected_files.append(item.text())

            if selected_files:
                # 更新file_list.txt
                try:
                    with open("file_list.txt", 'w', encoding='utf-8') as f:
                        f.write('\n'.join(selected_files))

                    # 更新主界面文件列表
                    file_list.clear()
                    for file_path in selected_files:
                        file_info = QFileInfo(file_path)
                        item = QListWidgetItem(file_info.fileName())
                        item.setData(Qt.UserRole, {
                            'path': file_path,
                            'size': file_info.size(),
                            'created': file_info.created(),
                            'modified': file_info.lastModified()
                        })
                        file_list.addItem(item)

                    update_status(f"二次过滤完成，剩余 {len(selected_files)} 个文件")
                except Exception as e:
                    QMessageBox.critical(page, "错误", f"保存过滤结果失败: {str(e)}")
            else:
                QMessageBox.information(page, "提示", "没有选择任何文件，保持原列表不变")

    # 连接二次过滤按钮
    secondary_filter_btn = QPushButton("二次过滤")
    secondary_filter_btn.setStyleSheet("""
           QPushButton {
               padding: 8px 20px;
               background-color: #f39c12;
               color: white;
               border-radius: 4px;
               font-weight: bold;
           }
           QPushButton:hover { background-color: #e67e22; }
       """)
    function_layout.addWidget(secondary_filter_btn, 3, 2)  # 添加到第三行第三列
    secondary_filter_btn.clicked.connect(open_secondary_filter)

    return page


def create_search_page():
    page = QWidget()
    # 设置支持中文的字体
    font = QFont()
    font.setFamily("SimHei")  # 使用黑体等中文字体
    page.setFont(font)

    page.setStyleSheet("""
        QWidget {
            font-family: "SimHei", "  ", " ";
            background-color: #f8f9fa;
        }
    """)
    layout = QVBoxLayout(page)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(15)

    # 搜索控制区
    control_panel = QWidget()
    control_layout = QHBoxLayout(control_panel)

    # 搜索算法选择
    algo_group = QGroupBox("检索算法")
    algo_group.setStyleSheet("QGroupBox { font-size: 14px; color: #3498db; }")
    algo_layout = QVBoxLayout(algo_group)

    algo_combo = QComboBox()
    algo_combo.addItems(["关键词检索", "TF-IDF", "布尔模型", "向量空间模型"])
    algo_combo.setStyleSheet("padding: 8px; border-radius: 4px;")
    algo_layout.addWidget(algo_combo)

    # 算法参数（修改为单文件最大结果数）
    param_group = QGroupBox("算法参数")
    param_layout = QFormLayout(param_group)

    threshold_spin = QDoubleSpinBox()
    threshold_spin.setRange(0.0, 1.0)
    threshold_spin.setValue(0.5)
    threshold_spin.setSingleStep(0.1)

    file_max_results_spin = QSpinBox()
    file_max_results_spin.setRange(1, 1000)
    file_max_results_spin.setValue(10)  # 默认显示每个文件前10条结果

    param_layout.addRow("相似度阈值:", threshold_spin)
    param_layout.addRow("单文件最大结果数:", file_max_results_spin)

    # 搜索框
    search_box = QLineEdit()
    search_box.setPlaceholderText("输入检索关键词...")
    search_box.setStyleSheet("""
        QLineEdit {
            padding: 10px;
            border: 2px solid #3498db;
            border-radius: 4px;
            font-size: 16px;
        }
    """)

    # 搜索按钮
    search_btn = QPushButton("开始检索")
    search_btn.setIcon(QIcon.fromTheme("system-search"))
    search_btn.setStyleSheet("""
        QPushButton {
            padding: 10px 25px;
            background-color: #27ae60;
            color: white;
            border-radius: 4px;
            font-weight: bold;
            font-size: 16px;
        }
        QPushButton:hover { background-color: #219653; }
    """)

    control_layout.addWidget(algo_group)
    control_layout.addWidget(param_group)
    control_layout.addWidget(search_box)
    control_layout.addWidget(search_btn)
    layout.addWidget(control_panel)

    # 进度条
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setTextVisible(True)
    progress_bar.setStyleSheet("QProgressBar { border-radius: 4px; height: 20px; }")
    layout.addWidget(progress_bar)

    # 结果展示区（增加行号列）
    result_tabs = QTabWidget()
    result_tabs.setStyleSheet("""
        QTabWidget::pane { border: 1px solid #ddd; border-radius: 4px; }
        QTabBar::tab { padding: 8px 15px; background: #ecf0f1; }
        QTabBar::tab:selected { background: white; }
    """)

    # 表格视图（8列，包含行号、算法和耗时）
    table_view = QTableWidget()
    table_view.setColumnCount(8)
    table_view.setHorizontalHeaderLabels(["文件名", "路径", "行号", "关键词", "匹配内容", "置信度", "算法", "耗时(ms)"])
    table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    table_view.verticalHeader().setVisible(False)
    table_view.setAlternatingRowColors(True)
    table_view.setSelectionBehavior(QTableWidget.SelectRows)
    table_view.setEditTriggers(QTableWidget.NoEditTriggers)

    # 添加右键菜单支持
    table_view.setContextMenuPolicy(Qt.CustomContextMenu)

    # 统一的复制到剪贴板函数
    def copy_to_clipboard(text):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(page, "成功", f"已复制：{text}")

    # 右键菜单处理函数
    def show_table_context_menu(pos):
        selected_rows = table_view.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        name_item = table_view.item(row, 0)
        path_item = table_view.item(row, 1)
        line_item = table_view.item(row, 2)

        has_name = name_item and name_item.text().strip()
        has_path = path_item and path_item.text().strip()
        has_line = line_item and line_item.text().strip()

        menu = QMenu()
        if has_name:
            copy_name_action = QAction("复制文件名", table_view)
            copy_name_action.triggered.connect(lambda: copy_to_clipboard(name_item.text()))
            menu.addAction(copy_name_action)
        if has_path:
            copy_path_action = QAction("复制文件路径", table_view)
            copy_path_action.triggered.connect(lambda: copy_to_clipboard(path_item.text()))
            menu.addAction(copy_path_action)
        if has_line:
            copy_line_action = QAction("复制行号", table_view)
            copy_line_action.triggered.connect(lambda: copy_to_clipboard(line_item.text()))
            menu.addAction(copy_line_action)

        if menu.actions():
            menu.exec_(table_view.mapToGlobal(pos))

    table_view.customContextMenuRequested.connect(show_table_context_menu)

    result_tabs.addTab(table_view, "表格视图")
    layout.addWidget(result_tabs, 1)

    # 状态栏
    status_bar = QWidget()
    status_layout = QHBoxLayout(status_bar)

    result_count_label = QLabel("共找到 0 条结果")
    result_count_label.setStyleSheet("font-weight: bold;")

    # 添加耗时显示标签
    time_label = QLabel("耗时: -")
    time_label.setStyleSheet("font-weight: bold; color: #3498db;")

    export_btn = QPushButton("导出结果")
    export_btn.setStyleSheet("""
        QPushButton {
            padding: 5px 15px;
            background-color: #3498db;
            color: white;
            border-radius: 4px;
        }
        QPushButton:hover { background-color: #2980b9; }
    """)

    status_layout.addWidget(result_count_label)
    status_layout.addWidget(time_label)
    status_layout.addStretch()
    status_layout.addWidget(export_btn)
    layout.addWidget(status_bar)

    # 搜索工作线程和耗时变量
    search_worker = None
    search_elapsed_time = 0

    def start_search():
        nonlocal search_worker, search_elapsed_time

        keyword = search_box.text().strip()
        if not keyword:
            QMessageBox.warning(page, "警告", "请输入搜索关键词")
            return

        file_list_path = "file_list.txt"
        if not os.path.exists(file_list_path):
            QMessageBox.warning(page, "警告", "请先在数据源模块索引文件")
            return

        algorithm_map = {
            "关键词检索": "keyword",
            "TF-IDF": "tfidf",
            "布尔模型": "boolean",
            "向量空间模型": "vector"
        }
        algorithm = algorithm_map.get(algo_combo.currentText(), "keyword")
        threshold = threshold_spin.value()
        file_max_results = file_max_results_spin.value()

        search_btn.setEnabled(False)
        search_btn.setText("搜索中...")
        table_view.setRowCount(0)
        progress_bar.setValue(0)
        result_count_label.setText("共找到 0 条结果")
        time_label.setText("耗时: -")

        search_worker = SearchWorker(file_list_path, keyword, algorithm, threshold, file_max_results)
        search_worker.search_progress.connect(update_search_progress)
        search_worker.search_finished.connect(show_search_results)
        search_worker.error_occurred.connect(show_search_error)
        search_worker.start()

    def update_search_progress(progress, message):
        progress_bar.setValue(progress)
        search_btn.setText(f"搜索中...{progress}%")

    def show_search_results(results, elapsed_time):
        nonlocal search_elapsed_time
        search_elapsed_time = elapsed_time

        current_threshold = threshold_spin.value()
        filtered_results = [r for r in results if r['confidence'] >= current_threshold]
        sorted_results = sorted(filtered_results, key=lambda x: x['confidence'], reverse=True)

        table_view.setRowCount(len(sorted_results))
        for row, result in enumerate(sorted_results):
            table_view.setItem(row, 0, QTableWidgetItem(result['file']))
            table_view.setItem(row, 1, QTableWidgetItem(result['path']))
            table_view.setItem(row, 2, QTableWidgetItem(str(result.get('line', 'N/A'))))
            table_view.setItem(row, 3, QTableWidgetItem(result['keyword']))
            table_view.setItem(row, 4, QTableWidgetItem(result['context']))
            table_view.setItem(row, 5, QTableWidgetItem(str(result['confidence'])))
            table_view.setItem(row, 6, QTableWidgetItem(algo_combo.currentText()))
            table_view.setItem(row, 7, QTableWidgetItem(str(elapsed_time)))

        result_count_label.setText(f"共找到 {len(sorted_results)} 条结果")
        time_label.setText(f"耗时: {elapsed_time}ms")
        search_btn.setEnabled(True)
        search_btn.setText("开始检索")
        progress_bar.setValue(100)

    def show_search_error(message):
        QMessageBox.critical(page, "错误", message)
        search_btn.setEnabled(True)
        search_btn.setText("开始检索")
        progress_bar.setValue(0)
        time_label.setText("耗时: -")

    def export_results():
        nonlocal search_elapsed_time
        if not search_worker or not search_worker.results:
            QMessageBox.warning(page, "警告", "没有可导出的结果")
            return

        algorithm = algo_combo.currentText()
        keyword = search_box.text().strip()

        # 构建默认文件名
        default_file_name = f"{algorithm}_{keyword[:20]}_results.csv"

        output_path, _ = QFileDialog.getSaveFileName(
            page, "导出结果", default_file_name, "CSV文件 (*.csv)")

        if output_path:
            try:
                # 正确调用静态方法
                SearchWorker.export_to_csv(
                    search_worker.results,
                    output_path,
                    algorithm,
                    keyword,
                    search_elapsed_time
                )
                QMessageBox.information(page, "成功", f"结果已导出到 {output_path}")
            except Exception as e:
                QMessageBox.critical(page, "错误", f"导出文件时发生错误: {str(e)}")
    # 连接信号
    search_btn.clicked.connect(start_search)
    export_btn.clicked.connect(export_results)

    return page

def create_visualization_page():
    page = QWidget()
    page.setStyleSheet("""
          QWidget {
              font-family: 'SimHei';
              font-size: 16px;
          }
          QPushButton {
              background-color: #4CAF50;
              color: white;
              border: none;
              padding: 6px 12px;
              border-radius: 4px;
          }
          QPushButton:hover {
              background-color: #45a049;
          }
          QPushButton:disabled {
              background-color: #cccccc;
          }
          QComboBox {
              padding: 4px;
              border: 1px solid #ddd;
              border-radius: 4px;
          }
          QLineEdit {
              padding: 4px;
              border: 1px solid #ddd;
              border-radius: 4px;
          }
          QSlider::groove:horizontal {
              height: 8px;
              background: #ddd;
              border-radius: 4px;
          }
          QSlider::handle:horizontal {
              width: 16px;
              height: 16px;
              background: #4CAF50;
              border-radius: 8px;
              margin: -4px 0;
          }
          QTableWidget {
              border: 1px solid #ddd;
              border-radius: 4px;
          }
          QHeaderView::section {
              background-color: #f0f0f0;
              padding: 4px;
              border: none;
          }
      """)

    layout = QVBoxLayout(page)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(15)

    # ---------- 文件导入组件 ----------
    file_control = QWidget()
    file_layout = QHBoxLayout(file_control)
    file_label = QLabel("CSV文件路径:")
    file_path = QLineEdit()
    file_path.setReadOnly(True)
    btn_import = QPushButton("导入文件")
    btn_import.setIcon(QIcon.fromTheme("document-open"))
    file_layout.addWidget(file_label)
    file_layout.addWidget(file_path, 1)
    file_layout.addWidget(btn_import)
    layout.addWidget(file_control)

    # ---------- 控制组件 ----------
    control_panel = QWidget()
    control_layout = QHBoxLayout(control_panel)
    chart_combo = QComboBox()
    chart_combo.addItems(["折线图", "饼图"])  # 添加饼图选项
    keyword_combo = QComboBox()
    keyword_combo.addItem("请选择关键词")
    btn_visualize = QPushButton("生成可视化图表")
    btn_visualize.setIcon(QIcon.fromTheme("view-statistics"))

    control_layout.addWidget(QLabel("图表类型:"))
    control_layout.addWidget(chart_combo)
    control_layout.addWidget(QLabel("分析关键词:"))
    control_layout.addWidget(keyword_combo)
    control_layout.addStretch()
    control_layout.addWidget(btn_visualize)
    layout.addWidget(control_panel)

    # ---------- 筛选面板 ----------
    viz_area = QSplitter(Qt.Horizontal)
    filter_panel = QWidget()
    filter_layout = QVBoxLayout(filter_panel)
    filter_panel.setStyleSheet("""
          background-color: white;
          border-radius: 4px;
          border: 1px solid #ddd;
      """)
    filter_panel.setFixedWidth(250)
    filter_layout.addStretch()
    viz_area.addWidget(filter_panel)

    # ---------- 数据表格 ----------
    data_table = QTableWidget()
    data_table.setColumnCount(5)
    data_table.setHorizontalHeaderLabels(["file", "path", "line", "keyword", "confidence"])
    data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    data_table.verticalHeader().setVisible(False)

    chart_container = QWidget()
    chart_layout = QVBoxLayout(chart_container)
    chart_layout.addWidget(data_table)
    viz_area.addWidget(chart_container)
    layout.addWidget(viz_area, 1)

    # 全局数据存储（设置为page的属性）
    page.global_data = {"csv_data": None, "file_path": ""}
    # ---------- 动态图表类 ----------
    class DynamicLineChart(QDialog):
        def __init__(self, keyword, data, parent, file_path=None):
            super().__init__(parent)
            self.setWindowTitle(f"{keyword}-词汇折线图")
            self.setWindowIcon(QIcon.fromTheme("view-statistics"))
            self.raw_data = data
            self.points = []
            self.current_index = 0
            self.timer = QTimer(self)
            self.setMinimumSize(850, 650)
            self.file_path = file_path
            self.csv_data = parent.global_data["csv_data"]  # 获取完整的CSV数据
            self.keyword = keyword


            # 禁用父窗口的生成按钮
            parent.findChild(QPushButton, "生成可视化图表").setEnabled(False)

            self.setup_chinese_font()
            self.prepare_data()
            self.init_ui()
            self.init_chart()

        def setup_chinese_font(self):
            plt.rcParams["font.family"] = ["SimHei"]
            plt.rcParams["axes.unicode_minus"] = False

        def prepare_data(self):
            """准备绘图数据，x坐标为1,2,3..."""
            self.points = []
            for idx, (_, y) in enumerate(self.raw_data, 1):
                y_clamped = max(0, min(1, y))
                self.points.append((idx, y_clamped))
            self.total_points = len(self.points)

        def init_ui(self):
            layout = QVBoxLayout(self)
            self.figure = Figure(figsize=(12, 9), facecolor='none')
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setStyleSheet("background-color: transparent;")
            layout.addWidget(self.canvas)

            # 控制面板
            control_bar = QHBoxLayout()
            self.mode_selector = QComboBox()
            self.mode_selector.addItems(["动态生成", "一键生成"])
            self.start_btn = QPushButton("开始生成")
            self.start_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            self.progress_label = QLabel(f"进度: 0/{self.total_points}")

            # 滑块区域
            self.slider_container = QWidget()
            slider_layout = QHBoxLayout(self.slider_container)
            self.slider_label = QLabel("浏览位置:")
            self.slider = QSlider(Qt.Horizontal)
            self.slider.setMinimum(1)
            self.slider.setMaximum(self.total_points)
            self.slider.setValue(1)
            self.slider.setEnabled(False)
            self.slider.setVisible(False)  # 初始隐藏

            slider_layout.addWidget(self.slider_label)
            slider_layout.addWidget(self.slider)
            self.slider_container.setVisible(False)

            control_bar.addWidget(QLabel("模式:"))
            control_bar.addWidget(self.mode_selector)
            control_bar.addWidget(self.start_btn)
            control_bar.addWidget(self.progress_label)
            control_bar.addWidget(self.slider_container)
            layout.addLayout(control_bar)

            self.start_btn.clicked.connect(self.start_animation)
            self.timer.timeout.connect(self.add_point)
            self.slider.valueChanged.connect(self.on_slider_changed)

        def init_chart(self):
            self.ax = self.figure.add_subplot(111)
            self.ax.set_title(f"{self.windowTitle()}", pad=20)

            # 完全隐藏坐标轴（包括边框）
            self.ax.set_axis_off()

            # 初始化线条
            self.line, = self.ax.plot([], [], 'b-', marker='o', markersize=8, linewidth=2)

            # 设置坐标范围
            self.ax.set_xlim(0, self.total_points + 1)
            self.ax.set_ylim(0, 1.5)  # 增加Y轴范围以容纳标注

            # 添加文件信息标注（位于图表左上角）
            if self.file_path:
                filename = os.path.basename(self.file_path)
                # 第一行：filename：xxxx.csv
                self.ax.text(0.02, 0.95, f"filename：{filename}", transform=self.ax.transAxes,
                             fontsize=10, fontweight='bold', color='#333',
                             bbox=dict(boxstyle="round,pad=0.3", fc='white', ec='#999', alpha=0.8))

                # 计算平均置信度（如果有数据）
                if self.points:
                    avg_confidence = sum(y for _, y in self.points) / len(self.points)
                    # 第二行：confidence：0.1（保留两位小数）
                    self.ax.text(0.02, 0.90, f"confidence：{avg_confidence:.2f}", transform=self.ax.transAxes,
                                 fontsize=10, fontweight='bold', color='#333',
                                 bbox=dict(boxstyle="round,pad=0.3", fc='white', ec='#999', alpha=0.8))

        def start_animation(self):
            self.timer.stop()
            self.current_index = 0
            self.ax.clear()
            self.init_chart()
            self.start_btn.setEnabled(False)  # 禁用开始按钮

            if self.mode_selector.currentText() == "动态生成":
                self.timer.start(1000)  # 加快动画速度
            else:
                self.current_index = self.total_points
                self.update_chart()
                self.on_generation_complete()

        def add_point(self):
            if self.current_index < self.total_points:
                self.current_index += 1
                self.update_chart()
                self.progress_label.setText(f"进度: {self.current_index}/{self.total_points}")
            else:
                self.on_generation_complete()

        def on_generation_complete(self):
            """生成完成后的处理"""
            self.timer.stop()
            self.start_btn.setEnabled(False)
            self.mode_selector.setEnabled(False)

            # 如果数据点多于10个，显示滑块
            if self.total_points > 10:
                self.slider.setMinimum(1)
                self.slider.setMaximum(self.total_points - 9)  # 保持显示10个点
                self.slider.setValue(1)
                self.slider.setEnabled(True)
                self.slider.setVisible(True)
                self.slider_container.setVisible(True)
                self.slider_label.setVisible(True)

        def on_slider_changed(self, value):
            """滑块值改变时的回调"""
            start = value
            end = min(start + 9, self.total_points)  # 显示10个点
            self.ax.set_xlim(start, end)
            self.canvas.draw_idle()

        def update_chart(self):
            try:
                x_data = [x for x, _ in self.points[:self.current_index]]
                y_data = [y for _, y in self.points[:self.current_index]]

                # 更新线条数据
                self.line.set_data(x_data, y_data)

                # 清除之前的标注
                for text in self.ax.texts:
                    if text.get_text().startswith(("filename：", "confidence：")):
                        continue  # 保留文件信息标注
                    text.remove()

                # 添加三行标注（序号、文件名、置信度）
                for x, y in zip(x_data, y_data):
                    # 获取当前数据点的原始数据
                    row_data = None
                    if x - 1 < len(self.csv_data):
                        row = self.csv_data[x - 1]
                        if row.get('keyword') == self.keyword:
                            row_data = row

                    # 获取文件名
                    filename = ""
                    if row_data:
                        filename = row_data.get('file', row_data.get('filename', ''))
                        if not filename:  # 如果file字段不存在，尝试从path字段提取
                            path = row_data.get('path', '')
                            if path:
                                filename = os.path.basename(path)

                    # 处理文件名显示格式
                    display_filename = filename
                    if filename:
                        name, ext = os.path.splitext(filename)
                        if len(name) > 5:  # 如果文件名长度大于5
                            display_filename = f"{name[:3]}..{ext}" if ext else f"{name[:3]}.."
                        else:
                            display_filename = filename

                    # 获取置信度
                    confidence = y
                    if row_data and 'confidence' in row_data:
                        try:
                            confidence = float(row_data['confidence'])
                        except (ValueError, TypeError):
                            pass

                    # 新增：序号标注（蓝色框，在最上方）
                    self.ax.annotate(
                        f"#{x}",  # 使用x作为序号（从1开始）
                        xy=(x, y),
                        xytext=(0, 55),  # 上方偏移55点（在文件名标注框上方）
                        textcoords='offset points',
                        ha='center',
                        va='bottom',
                        bbox=dict(
                            boxstyle="round,pad=0.3",
                            fc="#e6f4ff",  # 浅蓝色背景
                            ec="#1890ff",  # 蓝色边框
                            lw=1.5,
                            alpha=0.9
                        ),
                        fontsize=10,
                        fontweight='bold',
                        color="#0050b3"  # 深蓝色文字
                    )

                    # 文件名标注（绿框，在中间）
                    self.ax.annotate(
                        f"{display_filename}" if display_filename else f"数据点 {x}",
                        xy=(x, y),
                        xytext=(0, 25),  # 上方偏移25点（在序号标注框下方）
                        textcoords='offset points',
                        ha='center',
                        va='bottom',
                        bbox=dict(
                            boxstyle="round,pad=0.3",
                            fc="#e6f7e6",
                            ec="#4CAF50",
                            lw=1.5,
                            alpha=0.9
                        ),
                        fontsize=10,
                        fontweight='bold',
                        color="#2E7D32"
                    )

                    # 置信度标注（红框，在下方）
                    self.ax.annotate(
                        f"confidence: {confidence:.2f}",
                        xy=(x, y),
                        xytext=(0, -25),  # 下方偏移25点
                        textcoords='offset points',
                        ha='center',
                        va='top',
                        bbox=dict(
                            boxstyle="round,pad=0.3",
                            fc="#ffebee",
                            ec="#f44336",
                            lw=1.5,
                            alpha=0.9
                        ),
                        fontsize=10,
                        fontweight='bold',
                        color="#C62828"
                    )

                # 自动调整视图
                if self.current_index > 10:
                    start = max(1, self.current_index - 9)
                    self.ax.set_xlim(start, self.current_index)
                else:
                    self.ax.set_xlim(0, self.current_index + 1)

                self.canvas.draw_idle()
            except Exception as e:
                self.timer.stop()
                QMessageBox.warning(self, "错误", f"更新图表失败: {str(e)}")
        def closeEvent(self, event):
            """关闭窗口时重新启用生成按钮"""
            self.parent().findChild(QPushButton, "生成可视化图表").setEnabled(True)
            event.accept()

    class DynamicPieChart(QDialog):
        def __init__(self, keyword, data, parent, file_path=None):
            super().__init__(parent)
            self.setWindowTitle(f"{keyword}-文件分布饼图")
            self.setWindowIcon(QIcon.fromTheme("view-statistics"))
            self.raw_data = data
            self.setMinimumSize(850, 650)
            self.file_path = file_path
            self.csv_data = parent.global_data["csv_data"]  # 获取完整的CSV数据
            self.keyword = keyword

            # 禁用父窗口的生成按钮
            parent.findChild(QPushButton, "生成可视化图表").setEnabled(False)

            self.setup_chinese_font()
            self.prepare_data()
            self.init_ui()
            self.init_chart()

        def setup_chinese_font(self):
            plt.rcParams["font.family"] = ["SimHei"]
            plt.rcParams["axes.unicode_minus"] = False

        def prepare_data(self):
            """准备饼图数据：统计各文件出现的次数"""
            self.file_counts = defaultdict(int)
            total = 0

            for row in self.csv_data:
                if row.get('keyword') == self.keyword:
                    filename = row.get('file', '')
                    if not filename:  # 如果file字段不存在，尝试从path字段提取
                        path = row.get('path', '')
                        if path:
                            filename = os.path.basename(path)
                    if filename:
                        self.file_counts[filename] += 1
                        total += 1

            # 计算百分比并排序（从大到小）
            self.sorted_files = sorted(
                self.file_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )

            # 准备饼图数据
            self.labels = []
            self.sizes = []
            self.percentages = []

            for filename, count in self.sorted_files:
                self.labels.append(filename)
                self.sizes.append(count)
                self.percentages.append(count / total * 100)

        def init_ui(self):
            layout = QVBoxLayout(self)
            self.figure = Figure(figsize=(12, 9), facecolor='none')
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setStyleSheet("background-color: transparent;")
            layout.addWidget(self.canvas)

            # 控制面板
            control_bar = QHBoxLayout()
            self.explode_slider = QSlider(Qt.Horizontal)
            self.explode_slider.setMinimum(0)
            self.explode_slider.setMaximum(20)
            self.explode_slider.setValue(5)
            self.explode_slider.valueChanged.connect(self.update_explode)

            control_bar.addWidget(QLabel("分离程度:"))
            control_bar.addWidget(self.explode_slider)
            control_bar.addStretch()

            self.save_btn = QPushButton("保存图表")
            self.save_btn.setIcon(QIcon.fromTheme("document-save"))
            self.save_btn.clicked.connect(self.save_chart)
            control_bar.addWidget(self.save_btn)

            layout.addLayout(control_bar)

        def init_chart(self):
            self.ax = self.figure.add_subplot(111)
            self.ax.set_title(f"{self.keyword} - 文件分布", pad=20, fontsize=14, fontweight='bold')

            # 生成颜色列表（使用tab20色系，可以支持最多20种不同颜色）
            colors = plt.cm.tab20.colors
            if len(self.sizes) > 20:
                colors = plt.cm.tab20b.colors + plt.cm.tab20c.colors

            # 计算分离程度（突出显示前3个最大的部分）
            explode = [0] * len(self.sizes)
            for i in range(min(3, len(explode))):
                explode[i] = 0.05 * (self.explode_slider.value() / 5)

            # 绘制饼图
            self.wedges, self.texts, self.autotexts = self.ax.pie(
                self.sizes,
                explode=explode,
                labels=self.labels,
                autopct='%1.1f%%',
                shadow=True,
                startangle=140,
                colors=colors[:len(self.sizes)],
                textprops={'fontsize': 10}
            )

            # 设置标签样式，防止重叠
            plt.setp(self.autotexts, size=10, weight="bold")
            plt.setp(self.texts, size=10)

            # 添加图例（放在图表右侧）
            self.ax.legend(
                self.wedges,
                [f"{label} ({size}次)" for label, size in zip(self.labels, self.sizes)],
                title="文件分布",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=10
            )

            # 添加总次数标注
            total = sum(self.sizes)
            self.ax.annotate(
                f"总出现次数: {total}",
                xy=(0.5, -0.1),
                xycoords='axes fraction',
                ha='center',
                va='center',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=1, alpha=0.8),
                fontsize=12
            )

            self.canvas.draw()

        def update_explode(self, value):
            """更新饼图分离程度"""
            explode = [0] * len(self.sizes)
            for i in range(min(3, len(explode))):
                explode[i] = 0.05 * (value / 5)

            # 重新绘制饼图
            self.ax.clear()
            self.wedges, self.texts, self.autotexts = self.ax.pie(
                self.sizes,
                explode=explode,
                labels=self.labels,
                autopct='%1.1f%%',
                shadow=True,
                startangle=140,
                colors=plt.cm.tab20.colors[:len(self.sizes)],
                textprops={'fontsize': 10}
            )

            # 重新设置标签和图例
            plt.setp(self.autotexts, size=10, weight="bold")
            plt.setp(self.texts, size=10)
            self.ax.legend(
                self.wedges,
                [f"{label} ({size}次)" for label, size in zip(self.labels, self.sizes)],
                title="文件分布",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=10
            )

            self.ax.set_title(f"{self.keyword} - 文件分布", pad=20, fontsize=14, fontweight='bold')
            self.ax.annotate(
                f"总出现次数: {sum(self.sizes)}",
                xy=(0.5, -0.1),
                xycoords='axes fraction',
                ha='center',
                va='center',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=1, alpha=0.8),
                fontsize=12
            )

            self.canvas.draw()

        def save_chart(self):
            """保存图表为图片"""
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存图表",
                f"{self.keyword}_文件分布.png",
                "PNG Images (*.png);;JPEG Images (*.jpg);;All Files (*)"
            )

            if file_path:
                try:
                    self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                    QMessageBox.information(
                        self,
                        "保存成功",
                        f"图表已保存为:\n{file_path}",
                        QMessageBox.Ok
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "保存失败",
                        f"无法保存图表:\n{str(e)}",
                        QMessageBox.Ok
                    )

        def closeEvent(self, event):
            """关闭窗口时重新启用生成按钮"""
            self.parent().findChild(QPushButton, "生成可视化图表").setEnabled(True)
            event.accept()

    # ---------- 内部函数 ----------
    def _import_csv():
        file_path_csv, _ = QFileDialog.getOpenFileName(
            page, "导入CSV文件", "", "CSV Files (*.csv)"
        )
        if not file_path_csv:
            return

        try:
            # 检测文件编码
            with open(file_path_csv, 'rb') as f:
                raw_data = f.read(100000)
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'

            # 读取CSV数据
            with open(file_path_csv, 'r', encoding=encoding, errors='replace') as f:
                reader = csv.DictReader(f)
                data = list(reader)

                if not data:
                    raise ValueError("CSV文件为空或格式不正确")

                # 验证必要字段
                required_fields = {'keyword', 'confidence', 'file'}
                if not required_fields.issubset(data[0].keys()):
                    missing = required_fields - set(data[0].keys())
                    raise ValueError(f"缺少必要字段: {', '.join(missing)}")

                page.global_data["csv_data"] = data  # 存储到page的属性
                page.global_data["file_path"] = file_path_csv  # 存储文件路径

                # 更新关键词下拉框
                keywords = sorted(list({row['keyword'] for row in data if row['keyword'].strip()}))
                keyword_combo.clear()
                keyword_combo.addItems(["请选择关键词"] + keywords)

                # 更新表格显示
                data_table.setRowCount(0)
                f.seek(0)
                reader = csv.reader(f)
                headers = next(reader)
                data_table.setColumnCount(len(headers))
                data_table.setHorizontalHeaderLabels(headers)

                for row_idx, row in enumerate(reader):
                    data_table.insertRow(row_idx)
                    for col_idx, val in enumerate(row):
                        data_table.setItem(row_idx, col_idx, QTableWidgetItem(val))

            file_path.setText(file_path_csv)
        except Exception as e:
            QMessageBox.critical(
                page, "错误",
                f"文件导入失败:\n{str(e)}\n请确保文件格式正确且包含keyword、confidence和file列",
                QMessageBox.Ok
            )

    def _generate_chart():
        csv_path = file_path.text()
        keyword = keyword_combo.currentText()
        chart_type = chart_combo.currentText()

        if not csv_path:
            QMessageBox.warning(page, "提示", "请先导入CSV文件", QMessageBox.Ok)
            return
        if keyword == "请选择关键词":
            QMessageBox.warning(page, "提示", "请选择要分析的关键词", QMessageBox.Ok)
            return

        try:
            csv_data = page.global_data.get("csv_data")  # 从page的属性获取
            if not csv_data:
                with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
                    csv_data = list(csv.DictReader(f))
                    page.global_data["csv_data"] = csv_data  # 存储到page的属性

            if chart_type == "折线图":
                # 提取并验证数据
                filtered_data = []
                for idx, row in enumerate(csv_data, 1):
                    if row.get('keyword') == keyword:
                        try:
                            confidence = float(row.get('confidence', 0))
                            if 0 <= confidence <= 1:
                                filtered_data.append((idx, confidence))
                            else:
                                print(f"警告: 关键词 '{keyword}' 的置信度值 {confidence} 超出范围 [0,1]")
                        except (ValueError, TypeError):
                            continue

                if not filtered_data:
                    QMessageBox.warning(
                        page, "提示",
                        f"没有找到关键词'{keyword}'的有效数据\n请检查数据格式",
                        QMessageBox.Ok
                    )
                    return

                # 显示动态折线图
                chart = DynamicLineChart(keyword, filtered_data, page, page.global_data["file_path"])
                chart.exec_()

            elif chart_type == "饼图":
                # 检查是否有足够的数据
                file_counts = defaultdict(int)
                for row in csv_data:
                    if row.get('keyword') == keyword:
                        filename = row.get('file', '')
                        if not filename:  # 如果file字段不存在，尝试从path字段提取
                            path = row.get('path', '')
                            if path:
                                filename = os.path.basename(path)
                        if filename:
                            file_counts[filename] += 1

                if not file_counts:
                    QMessageBox.warning(
                        page, "提示",
                        f"没有找到关键词'{keyword}'的文件分布数据\n请检查数据格式",
                        QMessageBox.Ok
                    )
                    return

                # 显示饼图
                chart = DynamicPieChart(keyword, csv_data, page, page.global_data["file_path"])
                chart.exec_()

        except Exception as e:
            QMessageBox.critical(
                page, "错误",
                f"生成图表时出错:\n{str(e)}",
                QMessageBox.Ok
            )
    # ---------- 信号连接 ----------
    btn_import.clicked.connect(_import_csv)
    btn_visualize.clicked.connect(_generate_chart)
    btn_visualize.setObjectName("生成可视化图表")  # 设置对象名称以便查找

    return page

def create_user_management_page(db_manager):
    """创建用户管理页面"""
    page = QWidget()
    page.setStyleSheet("""
        QWidget {
            background-color: #f8f9fa;
            font-family: 'SimHei';
        }
        QTableWidget {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            gridline-color: #eee;
        }
        QHeaderView::section {
            background-color: #3498db;
            color: white;
            padding: 8px;
            border: none;
        }
        QPushButton {
            padding: 6px 12px;
            border-radius: 4px;
            min-width: 80px;
        }
        QLineEdit {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    """)

    layout = QVBoxLayout(page)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(15)

    # 工具栏
    toolbar = QWidget()
    toolbar_layout = QHBoxLayout(toolbar)

    btn_add = QPushButton("添加用户")
    btn_edit = QPushButton("编辑用户")
    btn_delete = QPushButton("删除用户")
    btn_reset = QPushButton("重置密码")



    # 设置按钮样式
    for btn, color in [
        (btn_add, "#27ae60"),
        (btn_edit, "#f39c12"),
        (btn_delete, "#e74c3c"),
        (btn_reset, "#3498db")
    ]:
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
            }}
            QPushButton:hover {{
                background-color: {color}99;
            }}
        """)

    search_box = QLineEdit()
    search_box.setPlaceholderText("搜索用户名...")
    search_box.setClearButtonEnabled(True)

    toolbar_layout.addWidget(btn_add)
    toolbar_layout.addWidget(btn_edit)
    toolbar_layout.addWidget(btn_delete)
    toolbar_layout.addWidget(btn_reset)
    toolbar_layout.addStretch()
    toolbar_layout.addWidget(search_box)

    # 用户表格
    # 用户表格
    user_table = QTableWidget()
    user_table.setColumnCount(4)  # 从5列改为4列，移除操作列
    user_table.setHorizontalHeaderLabels(["ID", "用户名", "创建时间", "上次时间"])  # 移除"操作"表头
    user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    user_table.verticalHeader().setVisible(False)
    user_table.setSelectionBehavior(QTableWidget.SelectRows)
    user_table.setEditTriggers(QTableWidget.NoEditTriggers)

    # 刷新表格数据（移除操作按钮列的代码）
    def refresh_table(keyword: str = ""):
        try:
            if keyword:
                users = db_manager.search_users(keyword)
            else:
                users = db_manager.get_all_users()

            user_table.setRowCount(0)

            for row, user in enumerate(users):
                user_table.insertRow(row)

                # ID列
                user_table.setItem(row, 0, QTableWidgetItem(str(user["id"])))

                # 用户名列
                user_table.setItem(row, 1, QTableWidgetItem(user["username"]))

                # 创建时间列
                created_at = user["created_at"] if "created_at" in user.keys() else "N/A"
                user_table.setItem(row, 2, QTableWidgetItem(created_at))

                # 更新时间列
                updated_at = user["updated_at"] if "updated_at" in user.keys() else "N/A"
                user_table.setItem(row, 3, QTableWidgetItem(updated_at))

                # 移除操作按钮列的所有代码（原第4列）
                # 以下代码全部删除：
                # btn_widget = QWidget()
                # btn_layout = QHBoxLayout(btn_widget)
                # ...（按钮创建和添加逻辑）
                # user_table.setCellWidget(row, 4, btn_widget)

        except Exception as e:
            QMessageBox.critical(page, "错误", f"加载用户数据失败: {str(e)}")
    # 添加用户对话框
    def show_add_user_dialog():
        dialog = QDialog(page)
        dialog.setWindowTitle("添加用户")
        dialog.setFixedSize(300, 200)

        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        username_edit = QLineEdit()
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.Password)
        confirm_edit = QLineEdit()
        confirm_edit.setEchoMode(QLineEdit.Password)

        form.addRow("用户名:", username_edit)
        form.addRow("密码:", password_edit)
        form.addRow("确认密码:", confirm_edit)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)

        layout.addLayout(form)
        layout.addWidget(btn_box)

        if dialog.exec_() == QDialog.Accepted:
            username = username_edit.text().strip()
            password = password_edit.text().strip()
            confirm = confirm_edit.text().strip()

            if not username or not password:
                QMessageBox.warning(page, "警告", "用户名和密码不能为空")
                return

            if password != confirm:
                QMessageBox.warning(page, "警告", "两次输入的密码不一致")
                return

            success, message = db_manager.add_user(username, password)
            if success:
                QMessageBox.information(page, "成功", message)
                refresh_table()
            else:
                QMessageBox.warning(page, "警告", message)

    # 编辑用户对话框
    def edit_user():
        selected = user_table.selectedItems()
        if not selected:
            QMessageBox.warning(page, "警告", "请先选择要编辑的用户")
            return

        user_id = int(user_table.item(selected[0].row(), 0).text())
        user = db_manager.get_user_by_id(user_id)
        if not user:
            QMessageBox.warning(page, "警告", "用户不存在")
            return

        dialog = QDialog(page)
        dialog.setWindowTitle("编辑用户")
        dialog.setFixedSize(300, 200)

        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        username_edit = QLineEdit(user["username"])
        password_edit = QLineEdit()
        password_edit.setPlaceholderText("留空则不修改密码")
        password_edit.setEchoMode(QLineEdit.Password)

        form.addRow("用户名:", username_edit)
        form.addRow("新密码:", password_edit)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)

        layout.addLayout(form)
        layout.addWidget(btn_box)

        if dialog.exec_() == QDialog.Accepted:
            new_username = username_edit.text().strip()
            new_password = password_edit.text().strip()

            if not new_username:
                QMessageBox.warning(page, "警告", "用户名不能为空")
                return

            success, message = db_manager.update_user(
                user_id,
                new_username,
                new_password if new_password else None
            )

            if success:
                QMessageBox.information(page, "成功", message)
                refresh_table()
            else:
                QMessageBox.warning(page, "警告", message)

    # 删除用户
    def delete_user():
        selected = user_table.selectedItems()
        if not selected:
            QMessageBox.warning(page, "警告", "请先选择要删除的用户")
            return

        user_id = int(user_table.item(selected[0].row(), 0).text())

        reply = QMessageBox.question(
            page, "确认删除",
            "确定要删除这个用户吗?此操作不可恢复!",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success, message = db_manager.delete_user(user_id)
            if success:
                QMessageBox.information(page, "成功", message)
                refresh_table()
                # 删除后自动禁用按钮
                btn_delete.setEnabled(False)
                btn_edit.setEnabled(False)
                btn_reset.setEnabled(False)
            else:
                QMessageBox.warning(page, "警告", message)

    # 重置密码
    def reset_password():
        selected = user_table.selectedItems()
        if not selected:
            QMessageBox.warning(page, "警告", "请先选择要重置密码的用户")
            return

        user_id = int(user_table.item(selected[0].row(), 0).text())

        dialog = QDialog(page)
        dialog.setWindowTitle("重置密码")
        dialog.setFixedSize(300, 150)

        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.Password)
        confirm_edit = QLineEdit()
        confirm_edit.setEchoMode(QLineEdit.Password)

        form.addRow("新密码:", password_edit)
        form.addRow("确认密码:", confirm_edit)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)

        layout.addLayout(form)
        layout.addWidget(btn_box)

        if dialog.exec_() == QDialog.Accepted:
            password = password_edit.text().strip()
            confirm = confirm_edit.text().strip()

            if not password:
                QMessageBox.warning(page, "警告", "密码不能为空")
                return

            if password != confirm:
                QMessageBox.warning(page, "警告", "两次输入的密码不一致")
                return

            success, message = db_manager.reset_password(user_id, password)
            if success:
                QMessageBox.information(page, "成功", message)
                refresh_table()
            else:
                QMessageBox.warning(page, "警告", message)

    # 连接信号
    btn_add.clicked.connect(show_add_user_dialog)
    btn_edit.clicked.connect(edit_user)
    btn_delete.clicked.connect(delete_user)
    btn_reset.clicked.connect(reset_password)
    search_box.textChanged.connect(lambda: refresh_table(search_box.text()))

    # 初始加载数据
    refresh_table()

    # 添加到布局
    layout.addWidget(toolbar)
    layout.addWidget(user_table)

    return page


def create_help_center_page():
    page = QWidget()
    page.setStyleSheet("background-color: #f8f9fa;"
                       "  font-family: 'SimHei';")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(20)  # 增大整体间距

    # 帮助中心标题
    title = QLabel("帮助中心")
    title.setStyleSheet("""
        font-size: 24px;
        color: #2c3e50;
        font-weight: bold;
    """)
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    # 帮助内容区域
    help_tabs = QTabWidget()
    help_tabs.setStyleSheet("""
        QTabWidget::pane { 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            margin-top: 10px;  /* 选项卡与内容间距 */
        }
        QTabBar::tab { 
            padding: 10px 20px; 
            background: #ecf0f1; 
            margin-right: 5px; 
        }
        QTabBar::tab:selected { background: white; }
    """)

    # 使用指南
    guide = QWidget()
    guide_layout = QVBoxLayout(guide)
    guide_layout.setSpacing(15)  # 组间间距

    topics = [
        ("系统介绍", "这里是系统的基本功能介绍..."),
        ("快速入门", "如何快速开始使用本系统..."),
        ("数据源管理", "如何添加和管理数据源..."),
        ("检索技巧", "高级检索功能的使用方法..."),
        ("规则配置", "如何配置和使用规则...")
    ]

    for topic, content in topics:
        group = QGroupBox(topic)
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                color: #3498db;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-bottom: 10px;  /* 组框底部间距 */
                padding: 10px;  /* 组框内边距 */
            }
        """)
        group_layout = QVBoxLayout(group)
        label = QLabel(content)
        label.setWordWrap(True)
        group_layout.addWidget(label)
        guide_layout.addWidget(group)

    guide_layout.addStretch(1)  # 底部弹性空间
    help_tabs.addTab(guide, "使用指南")

    # 常见问题
    faq = QWidget()
    faq_layout = QVBoxLayout(faq)
    faq_layout.setSpacing(15)

    questions = [
        ("无法连接数据源?", "请检查权限设置,确保你的文件权限有读写权限"),
        ("检索结果不准确?", "尝试调整检索算法参数..."),
        ("规则不生效?", "检查规则语法和优先级..."),
        ("系统运行缓慢?", "可以考虑优化数据源和检索条件...")
    ]

    for q, a in questions:
        group = QGroupBox(q)
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                color: #e74c3c;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        group_layout = QVBoxLayout(group)
        label = QLabel(a)
        label.setWordWrap(True)
        group_layout.addWidget(label)
        faq_layout.addWidget(group)

    faq_layout.addStretch(1)
    help_tabs.addTab(faq, "常见问题")

    # 联系我们
    contact = QWidget()
    contact_layout = QFormLayout(contact)
    contact_layout.setVerticalSpacing(10)  # 表单行间距
    contact_layout.setContentsMargins(15, 15, 15, 15)  # 表单内边距

    # 增加标签宽度避免文字挤压
    contact_layout.setLabelAlignment(Qt.AlignRight)
    contact_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

    contact_layout.addRow("联系电话:", QLabel("13594809504"))
    contact_layout.addRow("QQ邮箱:", QLabel("3234083715@qq.com"))


    # 设置固定高度避免内容挤压
    contact.setMinimumHeight(200)
    help_tabs.addTab(contact, "联系方式")

    layout.addWidget(help_tabs, 1)
    page.setMinimumSize(800, 600)  # 设置窗口最小尺寸

    return page


# evaluation_page.py
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
                             QLabel, QLineEdit, QPushButton, QProgressBar, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
                             QDialog, QDoubleSpinBox)
from PyQt5.QtCore import Qt
import matplotlib

matplotlib.use('Qt5Agg')  # 确保使用Qt后端
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams['axes.unicode_minus'] = False


class VisualizationWindow(QDialog):
    """可视化结果窗口"""

    def __init__(self, metrics, detail_results, parent=None):
        super().__init__(parent)
        self.setWindowTitle("评估指标可视化")
        self.setMinimumSize(800, 600)
        self.metrics = metrics
        self.detail_results = detail_results

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("检索性能评估可视化")
        title.setStyleSheet("font-size: 20px; color: #2c3e50; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 图表区域
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # 按钮区域
        btn_layout = QHBoxLayout()

        # 精确率-召回率-F1值图表按钮
        prf_btn = QPushButton("显示PRF指标")
        prf_btn.clicked.connect(self.show_prf_metrics)

        # 误检率分布按钮
        error_btn = QPushButton("显示误检率")
        error_btn.clicked.connect(self.show_error_rate)

        # 返回按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)

        btn_layout.addWidget(prf_btn)
        btn_layout.addWidget(error_btn)
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # 初始显示PRF指标
        self.show_prf_metrics()

    def show_prf_metrics(self):
        """显示精确率、召回率和F1值图表"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        labels = ['精确率', '召回率', 'F1值']
        values = [
            self.metrics["precision"],
            self.metrics["recall"],
            self.metrics["f1"]
        ]
        colors = ['#3498db', '#27ae60', '#e74c3c']

        ax.bar(labels, values, color=colors, alpha=0.7)
        ax.set_title('核心评估指标对比')
        ax.set_ylabel('指标值')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # 添加数值标签
        for i, v in enumerate(values):
            ax.text(i, v + 0.05, f'{v:.2f}', ha='center', fontweight='bold')

        self.canvas.draw()

    def show_error_rate(self):
        """显示误检率相关图表"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # 计算每个查询的误检率
        error_rates = []
        for detail in self.detail_results:
            retrieved = detail["retrieved"]
            correct = detail["correct"]
            if retrieved > 0:
                error_rate = (retrieved - correct) / retrieved
                error_rates.append(error_rate)

        if not error_rates:
            ax.text(0.5, 0.5, "没有可用的误检率数据", ha='center', va='center', fontsize=12)
            self.canvas.draw()
            return

        # 绘制误检率分布
        ax.plot(range(1, len(error_rates) + 1), error_rates, 'o-', color='#9b59b6', alpha=0.7)
        ax.set_title('各查询误检率')
        ax.set_xlabel('查询ID')
        ax.set_ylabel('误检率')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # 计算并显示平均误检率
        avg_error = sum(error_rates) / len(error_rates)
        ax.text(0.02, 0.95, f'平均误检率: {avg_error:.2f}',
                transform=ax.transAxes, bbox=dict(facecolor='white', alpha=0.8))

        self.canvas.draw()

def create_evaluation_page():
    """创建评估页面"""
    page = QWidget()
    page.setStyleSheet("""
        QWidget {
            font-family: 'SimHei';
            background-color: #f8f9fa;
        }
        QGroupBox {
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover { background-color: #2980b9; }
        QTableWidget {
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        QHeaderView::section {
            background-color: #f0f0f0;
            padding: 4px;
        }
    """)

    layout = QVBoxLayout(page)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(15)

    # 标题栏
    title = QLabel("检索性能评估")
    title.setStyleSheet("font-size: 24px; color: #2c3e50; font-weight: bold;")
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    # 评估控制区
    control_group = QGroupBox("评估设置")
    control_layout = QGridLayout(control_group)

    # 真实样本集选择
    ground_truth_label = QLabel("真实样本集:")
    ground_truth_path = QLineEdit()
    ground_truth_path.setReadOnly(True)
    ground_truth_btn = QPushButton("浏览...")

    # 预测样本集选择
    predicted_label = QLabel("预测样本集:")
    predicted_path = QLineEdit()
    predicted_path.setReadOnly(True)
    predicted_btn = QPushButton("浏览...")

    # 置信度阈值
    threshold_label = QLabel("置信度阈值:")
    threshold_input = QDoubleSpinBox()
    threshold_input.setRange(0, 1)
    threshold_input.setSingleStep(0.1)
    threshold_input.setValue(0.5)

    # 评估按钮
    eval_btn = QPushButton("开始评估")
    eval_btn.setStyleSheet("""
        QPushButton {
            background-color: #27ae60;
            font-weight: bold;
            padding: 8px 20px;
        }
        QPushButton:hover { background-color: #219653; }
    """)

    # 进度条
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)

    # 布局控制区
    control_layout.addWidget(ground_truth_label, 0, 0)
    control_layout.addWidget(ground_truth_path, 0, 1)
    control_layout.addWidget(ground_truth_btn, 0, 2)
    control_layout.addWidget(predicted_label, 1, 0)
    control_layout.addWidget(predicted_path, 1, 1)
    control_layout.addWidget(predicted_btn, 1, 2)
    control_layout.addWidget(threshold_label, 2, 0)
    control_layout.addWidget(threshold_input, 2, 1)
    control_layout.addWidget(progress_bar, 3, 0, 1, 3)
    control_layout.addWidget(eval_btn, 4, 0, 1, 3)

    layout.addWidget(control_group)

    # 评估指标结果区
    metrics_group = QGroupBox("评估指标结果")
    metrics_layout = QGridLayout(metrics_group)

    # 精确率
    precision_label = QLabel("精确率:")
    precision_value = QLabel("0.00")
    precision_value.setStyleSheet("font-size: 18px; color: #3498db; font-weight: bold;")

    # 召回率
    recall_label = QLabel("召回率:")
    recall_value = QLabel("0.00")
    recall_value.setStyleSheet("font-size: 18px; color: #27ae60; font-weight: bold;")

    # F1值
    f1_label = QLabel("F1值:")
    f1_value = QLabel("0.00")
    f1_value.setStyleSheet("font-size: 18px; color: #e74c3c; font-weight: bold;")

    # 误检率
    error_label = QLabel("误检率:")
    error_value = QLabel("0.00")
    error_value.setStyleSheet("font-size: 18px; color: #9b59b6; font-weight: bold;")

    # 布局指标区
    metrics_layout.addWidget(precision_label, 0, 0)
    metrics_layout.addWidget(precision_value, 0, 1)
    metrics_layout.addWidget(recall_label, 1, 0)
    metrics_layout.addWidget(recall_value, 1, 1)
    metrics_layout.addWidget(f1_label, 2, 0)
    metrics_layout.addWidget(f1_value, 2, 1)
    metrics_layout.addWidget(error_label, 3, 0)
    metrics_layout.addWidget(error_value, 3, 1)

    layout.addWidget(metrics_group)

    # 详细结果表格
    detail_group = QGroupBox("详细评估结果")
    detail_layout = QVBoxLayout(detail_group)

    detail_table = QTableWidget()
    detail_table.setColumnCount(5)  # 从6列减少到5列
    detail_table.setHorizontalHeaderLabels(
        ["查询ID", "关键词", "相关文档数", "检索结果数", "正确结果数"])  # 移除"响应时间(ms)"
    detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    detail_table.setEditTriggers(QTableWidget.NoEditTriggers)

    detail_layout.addWidget(detail_table)
    layout.addWidget(detail_group)

    # 可视化图表区（仅保留容器，实际图表在新窗口中显示）
    vis_group = QGroupBox("评估指标可视化")
    vis_layout = QVBoxLayout(vis_group)

    vis_info = QLabel("点击'生成可视化图表'按钮查看详细可视化结果")
    vis_info.setAlignment(Qt.AlignCenter)
    vis_info.setStyleSheet("color: #7f8c8d; font-style: italic;")
    vis_layout.addWidget(vis_info)

    layout.addWidget(vis_group)

    # 结果导出区
    export_group = QGroupBox("结果导出")
    export_layout = QHBoxLayout(export_group)

    export_btn = QPushButton("导出评估报告")
    export_btn.setIcon(QIcon.fromTheme("document-save"))

    # 新增可视化按钮
    visualize_btn = QPushButton("生成可视化图表")
    visualize_btn.setIcon(QIcon.fromTheme("view-statistics"))
    visualize_btn.setEnabled(False)  # 初始禁用，直到评估完成

    export_layout.addWidget(export_btn)
    export_layout.addWidget(visualize_btn)
    export_layout.addStretch()

    layout.addWidget(export_group)

    # 存储评估数据
    page.eval_data = {
        "ground_truth_path": "",
        "predicted_path": "",
        "threshold": 0.5,
        "metrics": [],
        "detail_results": [],
        "calculated_metrics": None  # 存储计算好的指标，用于可视化
    }

    # 浏览真实样本集文件
    def browse_ground_truth():
        path, _ = QFileDialog.getOpenFileName(
            page, "选择真实样本集文件", "", "CSV Files (*.csv)"
        )
        if path:
            ground_truth_path.setText(path)
            page.eval_data["ground_truth_path"] = path

    ground_truth_btn.clicked.connect(browse_ground_truth)

    # 浏览预测样本集文件
    def browse_predicted():
        path, _ = QFileDialog.getOpenFileName(
            page, "选择预测样本集文件", "", "CSV Files (*.csv)"
        )
        if path:
            predicted_path.setText(path)
            page.eval_data["predicted_path"] = path

    predicted_btn.clicked.connect(browse_predicted)

    # 开始评估
    def start_evaluation():
        ground_truth_path_val = page.eval_data["ground_truth_path"]
        predicted_path_val = page.eval_data["predicted_path"]
        threshold = threshold_input.value()

        if not ground_truth_path_val or not predicted_path_val:
            QMessageBox.warning(page, "警告", "请先选择真实样本集和预测样本集文件")
            return

        # 禁用按钮，防止重复点击
        eval_btn.setEnabled(False)
        eval_btn.setText("评估中...")
        visualize_btn.setEnabled(False)  # 评估过程中禁用可视化按钮
        progress_bar.setValue(0)

        # 创建并启动工作线程
        global eval_worker
        eval_worker = EvaluationWorker(ground_truth_path_val, predicted_path_val, threshold)

        # 连接信号
        eval_worker.progress_updated.connect(lambda p, msg: [
            progress_bar.setValue(p),
            QApplication.processEvents()
        ])
        eval_worker.metrics_calculated.connect(show_metrics_and_table)
        eval_worker.error_occurred.connect(show_evaluation_error)
        eval_worker.finished.connect(evaluation_finished)

        eval_worker.start()

    def show_metrics_and_table(metrics):
        """显示核心指标结果和表格数据"""
        # 不再计算平均响应时间

        precision_value.setText(f"{metrics['precision']:.2f}")
        recall_value.setText(f"{metrics['recall']:.2f}")
        f1_value.setText(f"{metrics['f1']:.2f}")
        error_value.setText(f"{metrics['error_rate']:.2f}")

        # 存储计算好的指标用于可视化
        page.eval_data["calculated_metrics"] = metrics

        # 显示详细结果表格
        show_detail_results(metrics["detail"])

    def show_detail_results(results):
        """显示详细结果表格"""
        detail_table.setRowCount(len(results))
        for row, detail in enumerate(results):
            detail_table.setItem(row, 0, QTableWidgetItem(str(detail["query_id"])))
            detail_table.setItem(row, 1, QTableWidgetItem(detail["keyword"]))
            detail_table.setItem(row, 2, QTableWidgetItem(str(detail["relevant"])))
            detail_table.setItem(row, 3, QTableWidgetItem(str(detail["retrieved"])))
            detail_table.setItem(row, 4, QTableWidgetItem(str(detail["correct"])))
        page.eval_data["detail_results"] = results

    def show_evaluation_error(message):
        """显示评估错误"""
        QMessageBox.critical(page, "评估错误", message)

    def evaluation_finished():
        """评估完成后的清理工作"""
        eval_btn.setEnabled(True)
        eval_btn.setText("开始评估")
        visualize_btn.setEnabled(True)  # 评估完成后启用可视化按钮
        QMessageBox.information(page, "评估完成", "性能评估已完成，可点击'生成可视化图表'查看结果")

    # 生成可视化图表（修改为打开新窗口）
    def visualize_metrics():
        metrics = page.eval_data.get("calculated_metrics")
        detail_results = page.eval_data.get("detail_results", [])
        if not metrics:
            QMessageBox.warning(page, "警告", "请先完成评估并生成指标数据")
            return

        # 打开可视化窗口
        vis_window = VisualizationWindow(metrics, detail_results, page)
        vis_window.exec_()

    eval_btn.clicked.connect(start_evaluation)
    visualize_btn.clicked.connect(visualize_metrics)  # 连接可视化按钮

    # 导出评估报告
    def export_report():
        metrics = page.eval_data.get("calculated_metrics")
        if not metrics:
            QMessageBox.warning(page, "警告", "请先完成评估")
            return

        path, _ = QFileDialog.getSaveFileName(
            page, "导出评估报告", "", "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        if not path:
            return

        try:
            with open(path, 'w', encoding='utf-8', newline='') as f:
                # 写入评估设置
                f.write("评估设置\n")
                f.write(f"真实样本集,{page.eval_data['ground_truth_path']}\n")
                f.write(f"预测样本集,{page.eval_data['predicted_path']}\n")
                f.write(f"置信度阈值,{page.eval_data['threshold']}\n\n")

                # 写入指标结果
                f.write("评估指标,值\n")
                f.write(f"精确率,{metrics['precision']:.4f}\n")
                f.write(f"召回率,{metrics['recall']:.4f}\n")
                f.write(f"F1值,{metrics['f1']:.4f}\n")
                f.write(f"误检率,{metrics['error_rate']:.4f}\n\n")  # 移除响应时间行

                # 写入详细结果
                f.write("查询ID,关键词,相关文档数,检索结果数,正确结果数\n")  # 移除响应时间列
                for detail in page.eval_data["detail_results"]:
                    f.write(f"{detail['query_id']},{detail['keyword']},{detail['relevant']},")
                    f.write(f"{detail['retrieved']},{detail['correct']}\n")  # 移除时间数据

            QMessageBox.information(page, "导出成功", f"评估报告已导出到: {path}")
        except Exception as e:
            QMessageBox.critical(page, "导出失败", f"导出报告时出错: {str(e)}")

    export_btn.clicked.connect(export_report)

    return page
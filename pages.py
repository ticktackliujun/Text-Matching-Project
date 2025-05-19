from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QLineEdit, QPushButton, QFileDialog, QGroupBox, QTextEdit,
                             QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSplitter, QListWidget, QListWidgetItem,
                             QTabWidget, QFormLayout, QCheckBox, QSpinBox, QDoubleSpinBox, QProgressBar)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QDialogButtonBox,
    QMessageBox, QHeaderView
)
from worker_thread import IndexWorker
import os
from PyQt5.QtCore import Qt


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
    elif page_title == "规则模块":
        return create_rule_page()
    elif page_title == "可视化模块":
        return create_visualization_page()
    elif page_title == "用户管理":
        return create_user_management_page(db_manager)  # 传递db_manager
    elif page_title == "帮助中心":
        return create_help_center_page()

    return page


def create_data_source_page():
    page = QWidget()
    page.setStyleSheet("background-color: #f8f9fa;")
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

    # 进度条
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setStyleSheet("QProgressBar { border-radius: 4px; }")

    # 布局设置
    function_layout.addWidget(dir_label, 0, 0)
    function_layout.addWidget(dir_path, 0, 1)
    function_layout.addWidget(browse_btn, 0, 2)
    function_layout.addWidget(filter_label, 1, 0)
    function_layout.addWidget(filter_types, 1, 1)
    function_layout.addWidget(index_btn, 1, 2)
    function_layout.addWidget(status_label, 2, 0, 1, 2)
    function_layout.addWidget(progress_bar, 2, 2)

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

    # 功能实现
    def browse_directory():
        directory = QFileDialog.getExistingDirectory(page, "选择目录")
        if directory:
            dir_path.setText(directory)

    browse_btn.clicked.connect(browse_directory)

    def update_status(message):
        status_label.setText(message)

    def update_progress(progress):
        progress_bar.setValue(progress)

    def start_indexing():
        global index_worker
        directory = dir_path.text()
        if not directory:
            QMessageBox.warning(page, "警告", "请先选择目录")
            return

        index_btn.setEnabled(False)
        index_btn.setText("索引中...")
        progress_bar.setValue(0)

        filter_text = filter_types.text().strip()
        extensions = [ext.strip().lower() for ext in filter_text.split(',')] if filter_text else []

        # 创建并启动线程（关键：使用导入的IndexWorker类）
        index_worker = IndexWorker(directory, extensions)
        index_worker.progress_updated.connect(update_status)
        index_worker.file_found.connect(lambda path: print(f"Found file: {path}"))  # 可选：实时显示文件
        index_worker.indexing_finished.connect(on_indexing_finished)
        index_worker.start()

    def on_file_found(file_path):
        # 这里可以添加文件找到的处理逻辑，比如实时更新列表
        pass

    def on_indexing_finished(files):
        # 清空文件列表
        file_list.clear()

        # 添加文件到列表
        from PyQt5.QtCore import QFileInfo, QDateTime

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

        # 重新启用索引按钮
        index_btn.setEnabled(True)
        index_btn.setText("开始索引")

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

    return page


def create_search_page():
    page = QWidget()
    page.setStyleSheet("background-color: #f8f9fa;")
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

    # 算法参数
    param_group = QGroupBox("算法参数")
    param_layout = QFormLayout(param_group)
    param_layout.addRow("相似度阈值:", QDoubleSpinBox())
    param_layout.addRow("最大结果数:", QSpinBox())
    param_layout.addRow("启用模糊匹配:", QCheckBox())

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

    # 结果展示区
    result_tabs = QTabWidget()
    result_tabs.setStyleSheet("""
        QTabWidget::pane { border: 1px solid #ddd; border-radius: 4px; }
        QTabBar::tab { padding: 8px 15px; background: #ecf0f1; }
        QTabBar::tab:selected { background: white; }
    """)

    # 表格视图
    table_view = QTableWidget()
    table_view.setColumnCount(5)
    table_view.setHorizontalHeaderLabels(["文档ID", "标题", "相关度", "摘要", "操作"])
    table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    table_view.verticalHeader().setVisible(False)
    table_view.setAlternatingRowColors(True)

    # 图表视图
    chart_view = QWidget()
    chart_layout = QVBoxLayout(chart_view)
    chart_placeholder = QLabel("检索结果可视化图表将显示在这里")
    chart_placeholder.setAlignment(Qt.AlignCenter)
    chart_placeholder.setStyleSheet("color: #95a5a6; font-size: 16px;")
    chart_layout.addWidget(chart_placeholder)

    result_tabs.addTab(table_view, "表格视图")
    result_tabs.addTab(chart_view, "图表视图")
    layout.addWidget(result_tabs, 1)

    # 状态栏
    status_bar = QWidget()
    status_layout = QHBoxLayout(status_bar)
    status_layout.addWidget(QLabel("共找到 0 条结果"))
    status_layout.addStretch()
    status_layout.addWidget(QPushButton("导出结果"))

    layout.addWidget(status_bar)

    return page


def create_rule_page():
    page = QWidget()
    page.setStyleSheet("background-color: #f8f9fa;")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(15)

    # 规则管理工具栏
    toolbar = QWidget()
    toolbar_layout = QHBoxLayout(toolbar)

    rule_types = QComboBox()
    rule_types.addItems(["关键词规则", "正则表达式", "逻辑规则", "业务规则"])
    rule_types.setStyleSheet("padding: 8px; border-radius: 4px;")

    btn_new = QPushButton("新建规则")
    btn_new.setIcon(QIcon.fromTheme("document-new"))
    btn_save = QPushButton("保存规则")
    btn_save.setIcon(QIcon.fromTheme("document-save"))
    btn_test = QPushButton("测试规则")
    btn_test.setIcon(QIcon.fromTheme("system-run"))

    for btn in [btn_new, btn_save, btn_test]:
        btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #3498db;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)

    toolbar_layout.addWidget(rule_types)
    toolbar_layout.addWidget(btn_new)
    toolbar_layout.addWidget(btn_save)
    toolbar_layout.addWidget(btn_test)
    toolbar_layout.addStretch()
    layout.addWidget(toolbar)

    # 规则编辑区
    editor_splitter = QSplitter(Qt.Horizontal)

    # 规则列表
    rule_list = QListWidget()
    rule_list.setStyleSheet("""
        QListWidget {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        QListWidget::item {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
    """)
    rule_list.setFixedWidth(250)

    # 添加示例规则
    rules = ["敏感词过滤", "日期格式验证", "产品分类规则", "优先级标记"]
    for rule in rules:
        item = QListWidgetItem(rule)
        rule_list.addItem(item)

    # 规则编辑器
    editor_tabs = QTabWidget()

    # 规则内容编辑器
    content_editor = QWidget()
    content_layout = QVBoxLayout(content_editor)

    rule_name = QLineEdit()
    rule_name.setPlaceholderText("输入规则名称...")

    rule_editor = QTextEdit()
    rule_editor.setStyleSheet("""
        QTextEdit {
            font-family: Consolas;
            font-size: 12px;
            background-color: white;
            border: 1px solid #ddd;
        }
    """)
    rule_editor.setPlaceholderText("在这里编写规则内容...")

    content_layout.addWidget(rule_name)
    content_layout.addWidget(rule_editor)

    # 规则测试区
    test_area = QWidget()
    test_layout = QVBoxLayout(test_area)

    test_input = QTextEdit()
    test_input.setPlaceholderText("输入测试文本...")
    test_output = QTextEdit()
    test_output.setReadOnly(True)
    test_output.setPlaceholderText("测试结果将显示在这里...")

    test_layout.addWidget(QLabel("测试输入:"))
    test_layout.addWidget(test_input)
    test_layout.addWidget(QLabel("测试输出:"))
    test_layout.addWidget(test_output)

    editor_tabs.addTab(content_editor, "规则编辑")
    editor_tabs.addTab(test_area, "规则测试")

    editor_splitter.addWidget(rule_list)
    editor_splitter.addWidget(editor_tabs)
    layout.addWidget(editor_splitter, 1)

    return page


def create_visualization_page():
    page = QWidget()
    page.setStyleSheet("background-color: #f8f9fa;")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(15)

    # 可视化控制区
    control_panel = QWidget()
    control_layout = QHBoxLayout(control_panel)

    # 图表类型选择
    chart_combo = QComboBox()
    chart_combo.addItems(["柱状图", "折线图", "饼图", "散点图", "热力图", "词云"])
    chart_combo.setStyleSheet("padding: 8px; border-radius: 4px;")

    # 数据维度选择
    dim_combo = QComboBox()
    dim_combo.addItems(["时间分布", "类别分布", "关键词频率", "相关性分析", "情感分析"])

    # 图表样式
    style_combo = QComboBox()
    style_combo.addItems(["默认样式", "科技风格", "商务风格", "简约风格"])

    # 操作按钮
    btn_refresh = QPushButton("刷新图表")
    btn_export = QPushButton("导出图表")
    btn_settings = QPushButton("高级设置")

    for btn in [btn_refresh, btn_export, btn_settings]:
        btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #3498db;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)

    control_layout.addWidget(QLabel("图表类型:"))
    control_layout.addWidget(chart_combo)
    control_layout.addWidget(QLabel("分析维度:"))
    control_layout.addWidget(dim_combo)
    control_layout.addWidget(QLabel("图表样式:"))
    control_layout.addWidget(style_combo)
    control_layout.addStretch()
    control_layout.addWidget(btn_refresh)
    control_layout.addWidget(btn_export)
    control_layout.addWidget(btn_settings)
    layout.addWidget(control_panel)

    # 可视化展示区
    viz_area = QSplitter(Qt.Horizontal)

    # 数据筛选面板
    filter_panel = QWidget()
    filter_panel.setStyleSheet("background-color: white; border-radius: 4px;")
    filter_panel.setFixedWidth(250)
    filter_layout = QVBoxLayout(filter_panel)

    # 时间范围筛选
    time_group = QGroupBox("时间范围")
    time_layout = QVBoxLayout(time_group)
    time_layout.addWidget(QCheckBox("最近7天"))
    time_layout.addWidget(QCheckBox("最近30天"))
    time_layout.addWidget(QCheckBox("自定义范围"))
    filter_layout.addWidget(time_group)

    # 分类筛选
    category_group = QGroupBox("文档分类")
    category_layout = QVBoxLayout(category_group)
    categories = ["技术文档", "产品说明", "用户反馈", "市场分析"]
    for cat in categories:
        category_layout.addWidget(QCheckBox(cat))
    filter_layout.addWidget(category_group)

    # 关键词筛选
    keyword_group = QGroupBox("关键词过滤")
    keyword_layout = QVBoxLayout(keyword_group)
    keyword_edit = QLineEdit()
    keyword_edit.setPlaceholderText("输入关键词...")
    keyword_layout.addWidget(keyword_edit)
    filter_layout.addWidget(keyword_group)

    filter_layout.addStretch()
    viz_area.addWidget(filter_panel)

    # 图表展示区
    chart_container = QWidget()
    chart_layout = QVBoxLayout(chart_container)

    chart_tabs = QTabWidget()

    # 主图表
    main_chart = QWidget()
    main_chart_layout = QVBoxLayout(main_chart)
    main_chart_placeholder = QLabel("主图表区域")
    main_chart_placeholder.setAlignment(Qt.AlignCenter)
    main_chart_placeholder.setStyleSheet("""
        font-size: 18px;
        color: #95a5a6;
        background-color: white;
        border-radius: 4px;
        padding: 100px;
    """)
    main_chart_layout.addWidget(main_chart_placeholder)

    # 辅助图表
    sub_chart = QWidget()
    sub_chart_layout = QVBoxLayout(sub_chart)
    sub_chart_placeholder = QLabel("辅助图表区域")
    sub_chart_placeholder.setAlignment(Qt.AlignCenter)
    sub_chart_layout.addWidget(sub_chart_placeholder)

    chart_tabs.addTab(main_chart, "主图表")
    chart_tabs.addTab(sub_chart, "辅助图表")
    chart_layout.addWidget(chart_tabs)

    # 数据表格
    data_table = QTableWidget(10, 5)
    data_table.setStyleSheet("background-color: white;")
    data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    chart_layout.addWidget(data_table)

    viz_area.addWidget(chart_container)
    layout.addWidget(viz_area, 1)

    return page


def create_user_management_page(db_manager):
    """创建用户管理页面"""
    page = QWidget()
    page.setStyleSheet("""
        QWidget {
            background-color: #f8f9fa;
            font-family: 'Microsoft YaHei';
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
    page.setStyleSheet("background-color: #f8f9fa;")
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
    contact_layout.addRow("开发者:", QLabel("人工智能2班-202258334093-刘俊豪"))

    # 设置固定高度避免内容挤压
    contact.setMinimumHeight(200)
    help_tabs.addTab(contact, "联系方式")

    layout.addWidget(help_tabs, 1)
    page.setMinimumSize(800, 600)  # 设置窗口最小尺寸

    return page




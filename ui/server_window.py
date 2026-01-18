"""
Server Dashboard UI
PyQt6 implementation of the server management interface.
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QListWidget, QLabel, QPushButton, 
                             QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFormLayout, QLineEdit, QGroupBox, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.theme import Theme

class ServerMainWindow(QMainWindow):
    """Server Dashboard Window"""
    
    # Signals for server control
    stop_server_requested = pyqtSignal()
    start_server_requested = pyqtSignal(int)  # port
    api_config_changed = pyqtSignal(str, str, str)  # key, base, model
    disconnect_user_requested = pyqtSignal(str) # user_id
    refresh_stats_requested = pyqtSignal()
    test_ai_requested = pyqtSignal(str, str, str) # key, base, model
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PetChat 服务端管理")
        self.resize(1000, 700)
        
        self.active_connections = {}
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI components"""
        self.setStyleSheet(Theme.get_stylesheet())
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        self.status_label = QLabel("服务器状态: 已停止")
        self.status_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {Theme.ERROR};")
        header_layout.addWidget(self.status_label)
        
        header_layout.addStretch()
        
        # Global Server Control in Header
        self.port_input = QLineEdit("8888")
        self.port_input.setPlaceholderText("端口")
        self.port_input.setFixedWidth(60)
        self.port_input.setToolTip("服务器端口")
        header_layout.addWidget(QLabel("端口:"))
        header_layout.addWidget(self.port_input)
        
        self.start_btn = QPushButton("启动服务器")
        self.start_btn.clicked.connect(self._on_start_stop_clicked)
        self.start_btn.setCheckable(True)
        self.start_btn.setStyleSheet(f"background-color: {Theme.SUCCESS}; color: white; border-radius: 4px; padding: 6px 16px;")
        header_layout.addWidget(self.start_btn)
        
        layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Overview Tab
        self.overview_tab = QWidget()
        self._init_overview_tab()
        self.tabs.addTab(self.overview_tab, "概览")
        
        # Connections Tab
        self.connections_tab = QWidget()
        self._init_connections_tab()
        self.tabs.addTab(self.connections_tab, "连接管理")
        
        # AI Config Tab
        self.ai_tab = QWidget()
        self._init_ai_tab()
        self.tabs.addTab(self.ai_tab, "AI 配置 & 统计")
        
        # Logs Tab
        self.logs_tab = QWidget()
        self._init_logs_tab()
        self.tabs.addTab(self.logs_tab, "系统日志")

    def _init_overview_tab(self):
        layout = QVBoxLayout(self.overview_tab)
        
        # Stats Cards
        stats_layout = QHBoxLayout()
        
        self.online_count_card = self._create_stat_card("在线用户", "0")
        stats_layout.addWidget(self.online_count_card)
        
        self.message_count_card = self._create_stat_card("消息转发", "0")
        stats_layout.addWidget(self.message_count_card)
        
        self.ai_req_card = self._create_stat_card("AI 请求数", "0")
        stats_layout.addWidget(self.ai_req_card)
        
        layout.addLayout(stats_layout)
        layout.addStretch()
        
        # Refresh Button
        refresh_btn = QPushButton("刷新数据")
        refresh_btn.setStyleSheet(f"background-color: {Theme.SECONDARY}; color: white; margin-bottom: 20px;")
        refresh_btn.clicked.connect(lambda: self.refresh_stats_requested.emit())
        layout.addWidget(refresh_btn)

    def _create_stat_card(self, title, value):
        card = QGroupBox()
        layout = QVBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 12px;")
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 24px; font-weight: bold;")
        val_lbl.setObjectName("value_label") # For easy finding later
        layout.addWidget(title_lbl)
        layout.addWidget(val_lbl)
        card.setLayout(layout)
        return card
        
    def _init_connections_tab(self):
        layout = QVBoxLayout(self.connections_tab)
        
        self.connections_table = QTableWidget()
        self.connections_table.setColumnCount(4)
        self.connections_table.setHorizontalHeaderLabels(["用户 ID", "昵称", "IP 地址", "操作"])
        self.connections_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.connections_table)
        
    def _init_ai_tab(self):
        layout = QVBoxLayout(self.ai_tab)
        
        # Config
        config_group = QGroupBox("OpenAI / Local LLM 配置")
        form_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("LM Studio 可留空，OpenAI 填 sk-...")
        form_layout.addRow("API Key:", self.api_key_input)
        
        self.api_base_input = QLineEdit()
        self.api_base_input.setPlaceholderText("https://api.openai.com/v1 或 http://localhost:1234/v1")
        form_layout.addRow("Base URL:", self.api_base_input)
        
        # Add Model Name input
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("gpt-4o-mini 或 qwen2.5-7b-instruct")
        form_layout.addRow("模型名称:", self.model_input)
        
        apply_btn = QPushButton("应用配置")
        apply_btn.clicked.connect(self._on_apply_config)
        
        # Test Connection Button
        self.test_ai_btn = QPushButton("测试连接")
        self.test_ai_btn.clicked.connect(self._on_test_ai_connection)
        self.test_ai_btn.setStyleSheet(f"background-color: {Theme.BG_BORDER}; color: {Theme.TEXT_PRIMARY};")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(self.test_ai_btn)
        
        # Feedback Label
        self.ai_msg_label = QLabel("")
        self.ai_msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ai_msg_label.setWordWrap(True)
        self.ai_msg_label.setStyleSheet("font-size: 13px; margin-top: 10px;")
        
        config_group.setLayout(form_layout)
        config_group.layout().addRow("", btn_layout)
        config_group.layout().addRow(self.ai_msg_label)
        layout.addWidget(config_group)
        
        # Token Stats
        stats_group = QGroupBox("Token 使用统计 (估算)")
        stats_layout = QVBoxLayout()
        self.token_table = QTableWidget()
        self.token_table.setColumnCount(2)
        self.token_table.setHorizontalHeaderLabels(["会话 ID", "Token 使用量"])
        self.token_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        stats_layout.addWidget(self.token_table)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
    def _init_logs_tab(self):
        layout = QVBoxLayout(self.logs_tab)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")
        layout.addWidget(self.log_area)
        
    def log_message(self, message: str):
        """Add message to log area"""
        self.log_area.append(message)
        # Scroll to bottom
        sb = self.log_area.verticalScrollBar()
        sb.setValue(sb.maximum())
        
    def update_server_status(self, running: bool):
        if running:
            self.status_label.setText("服务器状态: 运行中")
            self.status_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {Theme.SUCCESS};")
            self.start_btn.setText("停止服务器")
            self.start_btn.setStyleSheet(f"background-color: {Theme.ERROR}; color: white; border-radius: 4px; padding: 6px 16px;")
            self.start_btn.setChecked(True)
            self.port_input.setEnabled(False)
        else:
            self.status_label.setText("服务器状态: 已停止")
            self.status_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {Theme.ERROR};")
            self.start_btn.setText("启动服务器")
            self.start_btn.setStyleSheet(f"background-color: {Theme.SUCCESS}; color: white; border-radius: 4px; padding: 6px 16px;")
            self.start_btn.setChecked(False)
            self.port_input.setEnabled(True)

    def _on_start_stop_clicked(self):
        # Button is checkable, so check state reflects desired state
        if self.start_btn.isChecked():
            try:
                port = int(self.port_input.text())
                self.start_server_requested.emit(port)
            except ValueError:
                self.log_message("无效的端口号")
                self.start_btn.setChecked(False)
        else:
            self.stop_server_requested.emit()
            
    def _on_test_ai_connection(self):
        """Emit test connection with current input values"""
        self.ai_msg_label.setText("正在测试连接... (超时时间 5s)")
        self.ai_msg_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        self.test_ai_btn.setEnabled(False)
        
        key = self.api_key_input.text().strip()
        base = self.api_base_input.text().strip()
        model = self.model_input.text().strip()
        self.test_ai_requested.emit(key, base, model)

    def _on_apply_config(self):
        key = self.api_key_input.text().strip()
        base = self.api_base_input.text().strip()
        model = self.model_input.text().strip()
        self.api_config_changed.emit(key, base, model)
        # Show immediate feedback
        self.ai_msg_label.setText("配置已应用 (请点击测试连接验证)")
        self.ai_msg_label.setStyleSheet(f"color: {Theme.SUCCESS}; font-weight: bold;")

    def show_ai_result(self, message: str, success: bool):
        """Display result in AI tab"""
        self.test_ai_btn.setEnabled(True)
        color = Theme.SUCCESS if success else Theme.ERROR
        self.ai_msg_label.setText(message)
        self.ai_msg_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
    def add_connection(self, user_id, user_name, address):
        """Add user to connections table"""
        row = self.connections_table.rowCount()
        self.connections_table.insertRow(row)
        
        self.connections_table.setItem(row, 0, QTableWidgetItem(user_id))
        self.connections_table.setItem(row, 1, QTableWidgetItem(user_name))
        
        addr_str = f"{address[0]}:{address[1]}"
        self.connections_table.setItem(row, 2, QTableWidgetItem(addr_str))
        
        disconnect_btn = QPushButton("断开连接")
        disconnect_btn.setStyleSheet("background-color: #DC3545; color: white; padding: 2px;")
        disconnect_btn.clicked.connect(lambda: self.disconnect_user_requested.emit(user_id))
        self.connections_table.setCellWidget(row, 3, disconnect_btn)
        
        # Update online count
        self._update_stat_card_value(self.online_count_card, str(self.connections_table.rowCount()))

    def remove_connection(self, user_id):
        """Remove user from connections table"""
        for i in range(self.connections_table.rowCount()):
            if self.connections_table.item(i, 0).text() == user_id:
                self.connections_table.removeRow(i)
                break
        # Update online count
        self._update_stat_card_value(self.online_count_card, str(self.connections_table.rowCount()))

    def update_stats(self, msg_count=None, ai_req_count=None):
        """Update statistic counters"""
        if msg_count is not None:
            self._update_stat_card_value(self.message_count_card, str(msg_count))
        if ai_req_count is not None:
            self._update_stat_card_value(self.ai_req_card, str(ai_req_count))

    def update_token_stats(self, usage_dict):
        """Update token usage table"""
        self.token_table.setRowCount(0)
        for cid, tokens in usage_dict.items():
            row = self.token_table.rowCount()
            self.token_table.insertRow(row)
            self.token_table.setItem(row, 0, QTableWidgetItem(cid))
            self.token_table.setItem(row, 1, QTableWidgetItem(str(tokens)))

    def _update_stat_card_value(self, card, value):
        label = card.findChild(QLabel, "value_label")
        if label:
            label.setText(value)

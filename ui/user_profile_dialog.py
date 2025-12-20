from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from ui.theme import Theme


class UserProfileDialog(QDialog):
    def __init__(self, current_name: str = "", current_avatar: str = "", parent=None):
        super().__init__(parent)
        self._avatar_path = current_avatar
        self._init_ui(current_name, current_avatar)

    def _init_ui(self, current_name: str, current_avatar: str):
        self.setWindowTitle("设置用户信息")
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout()
        layout.setSpacing(Theme.SPACING_MD)

        title = QLabel("欢迎使用 pet-chat")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"font-size: {Theme.FONT_SIZE_XL}px; font-weight: 600; color: {Theme.TEXT_PRIMARY};"
        )
        layout.addWidget(title)

        hint = QLabel("请先完成用户信息设置。用户名将展示给对方和在会话列表中使用。")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: {Theme.FONT_SIZE_SM}px;")
        layout.addWidget(hint)

        name_label = QLabel("用户名（2-20个字符，支持中英文）")
        name_label.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: {Theme.FONT_SIZE_MD}px;")
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入用户名")
        self.name_input.setText(current_name)
        layout.addWidget(self.name_input)

        avatar_label = QLabel("头像")
        avatar_label.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: {Theme.FONT_SIZE_MD}px;")
        layout.addWidget(avatar_label)

        avatar_layout = QHBoxLayout()

        self.avatar_combo = QComboBox()
        self.avatar_combo.addItem("默认头像", "default")
        self.avatar_combo.addItem("宠物头像A", "pet_a")
        self.avatar_combo.addItem("宠物头像B", "pet_b")
        avatar_layout.addWidget(self.avatar_combo)

        self.avatar_path_label = QLabel("未选择本地图片")
        self.avatar_path_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: {Theme.FONT_SIZE_SM}px;")
        avatar_layout.addWidget(self.avatar_path_label)

        choose_btn = QPushButton("选择图片")
        choose_btn.clicked.connect(self._choose_avatar)
        avatar_layout.addWidget(choose_btn)

        layout.addLayout(avatar_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("退出")
        ok_btn = QPushButton("确定")
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self._on_ok)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _choose_avatar(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择头像图片", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self._avatar_path = file_path
            self.avatar_path_label.setText(file_path)

    def _on_ok(self):
        name = self.name_input.text().strip()
        length = len(name)
        if length < 2 or length > 20:
            QMessageBox.warning(self, "无效用户名", "用户名长度需在2到20个字符之间。")
            return
        self.accept()

    def user_name(self) -> str:
        return self.name_input.text().strip()

    def avatar(self) -> str:
        if self._avatar_path:
            return self._avatar_path
        data = self.avatar_combo.currentData()
        return data or ""


"""Memory viewer widget for displaying and managing extracted memories"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QTextEdit, QMessageBox,
                             QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Dict
from ui.theme import Theme


class MemoryViewer(QWidget):
    """Widget for viewing and managing memories"""
    
    clear_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.memories: List[Dict] = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        title_label = QLabel("🧠 对话记忆")
        title_label.setStyleSheet(
            f"font-weight: bold; font-size: 15px; color: {Theme.TEXT_PRIMARY};"
        )
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        clear_btn = QPushButton("清空记忆")
        clear_btn.setStyleSheet(
            f"QPushButton {{ background-color: {Theme.ERROR}; color: {Theme.PRIMARY_TEXT};"
            f" border: none; border-radius: {Theme.RADIUS_SM}px; padding: 5px 15px; font-size: 11px; }}"
        )
        clear_btn.clicked.connect(self._on_clear_requested)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            f"QScrollArea {{ border: 1px solid {Theme.BG_BORDER}; border-radius: {Theme.RADIUS_MD}px;"
            f" background-color: {Theme.BG_MUTED}; }}"
        )
        
        self.memory_container = QWidget()
        self.memory_layout = QVBoxLayout()
        self.memory_container.setLayout(self.memory_layout)
        scroll_area.setWidget(self.memory_container)
        
        layout.addWidget(scroll_area)
        
        self.empty_label = QLabel("暂无记忆\n对话中的关键信息将自动提取并显示在这里")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            f"color: {Theme.TEXT_SECONDARY}; padding: 20px;"
        )
        self.memory_layout.addWidget(self.empty_label)
        self.memory_layout.addStretch()
        
        self.setLayout(layout)
        self.setStyleSheet(
            f"QWidget {{ background-color: {Theme.BG_MAIN}; padding: 10px; }}"
        )
    
    def update_memories(self, memories: List[Dict]):
        """Update displayed memories"""
        self.memories = memories
        self._refresh_display()
    
    def _refresh_display(self):
        """Refresh memory display"""
        # Clear existing memory cards
        while self.memory_layout.count():
            item = self.memory_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.memories:
            self.empty_label = QLabel("暂无记忆\n对话中的关键信息将自动提取并显示在这里")
            self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.empty_label.setStyleSheet(
                f"color: {Theme.TEXT_SECONDARY}; padding: 20px;"
            )
            self.memory_layout.addWidget(self.empty_label)
        else:
            # Hide empty label if exists
            if hasattr(self, 'empty_label') and self.empty_label:
                self.empty_label.hide()
            
            # Add memory cards
            for memory in self.memories:
                card = self._create_memory_card(memory)
                self.memory_layout.addWidget(card)
        
        self.memory_layout.addStretch()
    
    def _create_memory_card(self, memory: Dict) -> QWidget:
        """Create a memory card widget"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(
            f"QFrame {{ background-color: {Theme.BG_MUTED}; border: 1px solid {Theme.BG_BORDER};"
            f" border-radius: {Theme.RADIUS_MD}px; padding: 10px; margin: 5px 0px; }}"
        )
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        category = memory.get('category', 'unknown')
        category_colors = {
            'event': Theme.PRIMARY,
            'agreement': Theme.SUCCESS,
            'topic': Theme.ACCENT,
            'unknown': Theme.TEXT_DISABLED
        }
        color = category_colors.get(category, '#95a5a6')
        
        category_label = QLabel(f"📌 {category}")
        category_label.setStyleSheet(
            f"color: {color}; font-weight: bold; font-size: 11px; padding: 2px 8px;"
            f" background-color: {color}33; border-radius: 3px;"
        )
        layout.addWidget(category_label)
        
        content_text = QTextEdit()
        content_text.setPlainText(memory.get('content', ''))
        content_text.setReadOnly(True)
        content_text.setMaximumHeight(80)
        content_text.setStyleSheet(
            f"QTextEdit {{ border: none; background-color: transparent; font-size: 14px;"
            f" color: {Theme.TEXT_PRIMARY}; }}"
        )
        layout.addWidget(content_text)
        
        # Timestamp
        if 'created_at' in memory:
            timestamp_label = QLabel(f"记录时间: {memory['created_at'][:19]}")
            timestamp_label.setStyleSheet(
                f"color: {Theme.TEXT_SECONDARY}; font-size: 10px;"
            )
            layout.addWidget(timestamp_label)
        
        card.setLayout(layout)
        return card
    
    def _on_clear_requested(self):
        """Handle clear button click"""
        if not self.memories:
            return
        
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有记忆吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_requested.emit()


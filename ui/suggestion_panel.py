"""Suggestion panel for displaying AI-generated suggestions"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QScrollArea, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Optional, Dict
from ui.theme import Theme, ThemeManager


class SuggestionPanel(QWidget):
    """Panel for displaying AI suggestions"""
    
    suggestion_adopted = pyqtSignal(str)  # Emitted when user adopts a suggestion
    
    def __init__(self, parent=None):    
        super().__init__(parent)
        self.current_suggestion: Optional[Dict] = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        title_label = QLabel("💡 AI 建议")
        title_label.setProperty("role", "panel_title")
        layout.addWidget(title_label)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setProperty("role", "panel_scroll")
        # Disable static contents to prevent ghosting/trailing artifacts
        scroll_area.viewport().setAttribute(Qt.WidgetAttribute.WA_StaticContents, False)
        
        self.suggestion_container = QWidget()
        self.suggestion_container.setObjectName("suggestion_container")
        # NOTE: Removed WA_TranslucentBackground - was causing ghosting/smearing artifacts
        # when dragging widgets over this area. A solid background is needed for proper repaint.
        self.suggestion_layout = QVBoxLayout()
        self.suggestion_container.setLayout(self.suggestion_layout)
        scroll_area.setWidget(self.suggestion_container)
        
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
        self.setObjectName("suggestion_panel")
        
    def _apply_shadow(self, widget: QWidget):
        """Apply shadow effect to a widget based on current theme"""
        ThemeClass = ThemeManager.get_theme_class()
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(4)
        shadow.setOffset(0, 2)
        r, g, b, a = ThemeClass.SUGGESTION_SHADOW_COLOR
        shadow.setColor(QColor(r, g, b, a))
        widget.setGraphicsEffect(shadow)

    def update_theme(self):
        """Update theme-dependent styles like shadows"""
        # Iterate over all cards in layout
        for i in range(self.suggestion_layout.count()):
            item = self.suggestion_layout.itemAt(i)
            if item.widget() and item.widget().property("role") == "card":
                self._apply_shadow(item.widget())
    
    def show_suggestion(self, suggestion: Dict):
        """
        Display a new suggestion
        
        Args:
            suggestion: Dict with 'title', 'content', and optionally 'type'
        """
        self.current_suggestion = suggestion
        
        # Clear existing suggestions
        self._clear_suggestions()
        
        card = QWidget()
        card.setProperty("role", "card")
        self._apply_shadow(card)
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(8)
        
        title_label = QLabel(suggestion.get('title', '建议'))
        title_label.setProperty("role", "card_title")
        card_layout.addWidget(title_label)
        
        content_text = QTextEdit()
        content_text.setPlainText(suggestion.get('content', ''))
        content_text.setReadOnly(True)
        content_text.setMaximumHeight(150)
        content_text.setProperty("role", "card_content")
        card_layout.addWidget(content_text)
        
        adopt_btn = QPushButton("采用建议")
        adopt_btn.setProperty("role", "action_button")
        adopt_btn.clicked.connect(lambda: self._on_adopt(suggestion.get('content', '')))
        card_layout.addWidget(adopt_btn)
        
        card.setLayout(card_layout)
        
        self.suggestion_layout.addWidget(card)
        self.suggestion_layout.addStretch()
    
    def show_loading(self):
        """Show loading indicator while waiting for AI response"""
        self._clear_suggestions()
        
        loading_card = QWidget()
        loading_card.setProperty("role", "card")
        self._apply_shadow(loading_card)
        
        loading_layout = QVBoxLayout()
        loading_layout.setSpacing(8)
        
        loading_label = QLabel("🤔 AI 正在思考中...")
        loading_label.setProperty("role", "loading_text")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_layout.addWidget(loading_label)
        
        loading_card.setLayout(loading_layout)
        
        self.suggestion_layout.addWidget(loading_card)
        self.suggestion_layout.addStretch()
    
    def _clear_suggestions(self):
        """Clear all suggestion cards"""
        while self.suggestion_layout.count():
            item = self.suggestion_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def clear(self):
        """Clear all suggestions"""
        self.current_suggestion = None
        self._clear_suggestions()
    
    def _on_adopt(self, content: str):
        """Handle adopt button click"""
        self.suggestion_adopted.emit(content)
        # Optionally hide after adopting
        # self.clear()

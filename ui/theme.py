"""
UI Theme definitions complying with WCAG 2.1 AA and Modern UI standards.
"""
from PyQt6.QtGui import QColor


class Theme:
    """Application Theme Colors and Metrics"""

    PRIMARY = "#0a84ff"
    PRIMARY_HOVER = "#1b9aee"
    PRIMARY_TEXT = "#f9fafb"

    SECONDARY = "#4b5563"
    ACCENT = "#22c1c3"

    BG_MAIN = "#020617"
    BG_ELEVATED = "#020617"
    BG_SURFACE = "#020617"
    BG_MUTED = "#111827"
    BG_BORDER = "#1f2937"
    BG_HOVER = "#020617"
    BG_SELECTED = "#111827"

    TEXT_PRIMARY = "#e5e7eb"
    TEXT_SECONDARY = "#9ca3af"
    TEXT_DISABLED = "#6b7280"

    SUCCESS = "#22c55e"
    WARNING = "#fbbf24"
    ERROR = "#f97373"

    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    SPACING_XL = 32

    RADIUS_SM = 6
    RADIUS_MD = 10
    RADIUS_LG = 16

    FONT_SIZE_SM = 12
    FONT_SIZE_MD = 14
    FONT_SIZE_LG = 16
    FONT_SIZE_XL = 20

    @staticmethod
    def get_stylesheet():
        return f"""
            QWidget {{
                color: {Theme.TEXT_PRIMARY};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                background-color: {Theme.BG_MAIN};
            }}

            QMainWindow {{
                background-color: {Theme.BG_MAIN};
            }}

            QDialog {{
                background-color: {Theme.BG_MAIN};
            }}

            QMenuBar {{
                background-color: {Theme.BG_MAIN};
                color: {Theme.TEXT_PRIMARY};
                border: none;
            }}
            QMenuBar::item {{
                padding: 6px 14px;
                background: transparent;
            }}
            QMenuBar::item:selected {{
                background-color: {Theme.BG_MUTED};
            }}

            QMenu {{
                background-color: {Theme.BG_MUTED};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BG_BORDER};
                padding: 6px 0;
            }}
            QMenu::item {{
                padding: 6px 18px;
            }}
            QMenu::item:selected {{
                background-color: {Theme.PRIMARY};
            }}
            QMenu::separator {{
                height: 1px;
                margin: 4px 12px;
                background: {Theme.BG_BORDER};
            }}

            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_TEXT};
                border: none;
                border-radius: {Theme.RADIUS_MD}px;
                padding: {Theme.SPACING_SM}px {Theme.SPACING_MD}px;
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {Theme.BG_BORDER};
                color: {Theme.TEXT_DISABLED};
            }}

            QLineEdit, QTextEdit {{
                background-color: {Theme.BG_MUTED};
                border: 1px solid {Theme.BG_BORDER};
                border-radius: {Theme.RADIUS_MD}px;
                padding: {Theme.SPACING_SM}px;
                font-size: {Theme.FONT_SIZE_MD}px;
                color: {Theme.TEXT_PRIMARY};
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {Theme.PRIMARY};
            }}
            QLineEdit::placeholder, QTextEdit::placeholder {{
                color: {Theme.TEXT_SECONDARY};
            }}

            QTabWidget::pane {{
                border: 1px solid {Theme.BG_BORDER};
                border-radius: {Theme.RADIUS_MD}px;
                background: {Theme.BG_MUTED};
            }}
            QTabBar::tab {{
                background: {Theme.BG_MAIN};
                color: {Theme.TEXT_SECONDARY};
                padding: 6px 14px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {Theme.BG_MUTED};
                color: {Theme.TEXT_PRIMARY};
            }}

            QListWidget {{
                background-color: {Theme.BG_MAIN};
                border: none;
            }}

            QScrollBar:vertical {{
                border: none;
                background: {Theme.BG_MAIN};
                width: 10px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.BG_BORDER};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.TEXT_DISABLED};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
            }}
        """

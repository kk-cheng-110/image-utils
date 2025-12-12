from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

class BaseFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Override this method to setup UI components"""
        pass

    def apply_styles(self):
        """Override this method to apply specific styles"""
        pass

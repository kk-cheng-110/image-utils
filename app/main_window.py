import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QStackedWidget, QLabel, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

# Import frames (we will create these next)
# from app.image_to_tif.image_to_tif_frame import ImageToTifFrame
# from app.excel_to_img.excel_to_img_frame import ExcelToImgFrame

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ImageUtils")
        
        # Set window size
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * (2/3))
        height = int(screen.height() * (2/3))
        self.resize(width, height)
        self.center()

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar (Left)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # App Title in Sidebar
        title_label = QLabel("Image\nUtils")
        title_label.setObjectName("appTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFixedHeight(80)
        sidebar_layout.addWidget(title_label)

        # Navigation List
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("navList")
        self.nav_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.nav_list.currentRowChanged.connect(self.switch_page)
        sidebar_layout.addWidget(self.nav_list)
        
        # Version info or bottom spacer
        version_label = QLabel("v1.0.0")
        version_label.setObjectName("versionLabel")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_label)

        main_layout.addWidget(self.sidebar)

        # Content Area (Right)
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("contentArea")
        main_layout.addWidget(self.content_area)

        # Apply Styles
        self.apply_styles()

    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def add_page(self, widget, name, icon_name=None):
        """Add a page to the application"""
        self.content_area.addWidget(widget)
        item = QListWidgetItem(name)
        item.setSizeHint(QSize(0, 50))
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # if icon_name:
        #     item.setIcon(QIcon(icon_name))
        self.nav_list.addItem(item)

    def switch_page(self, index):
        self.content_area.setCurrentIndex(index)

    def apply_styles(self):
        style_sheet = """
        QMainWindow {
            background-color: #f5f6fa;
        }
        QWidget#sidebar {
            background-color: #ffffff;
            border-right: 1px solid #e0e0e0;
        }
        QLabel#appTitle {
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            padding: 10px;
            background-color: #ffffff;
            border-bottom: 1px solid #f0f0f0;
        }
        QLabel#versionLabel {
            color: #999999;
            padding: 10px;
            font-size: 10px;
        }
        QListWidget#navList {
            border: none;
            background-color: transparent;
            outline: none;
        }
        QListWidget#navList::item {
            padding-left: 20px;
            color: #555555;
            border-left: 4px solid transparent;
        }
        QListWidget#navList::item:selected {
            background-color: #fff3e6; /* Light orange background */
            color: #ff8e3b; /* Theme Color */
            border-left: 4px solid #ff8e3b;
            font-weight: bold;
        }
        QListWidget#navList::item:hover {
            background-color: #f8f9fa;
        }
        QStackedWidget#contentArea {
            background-color: #f5f6fa;
        }
        
        /* General Widget Styles */
        QLabel {
            color: #333333;
            font-size: 13px;
        }
        QLineEdit, QComboBox {
            padding: 8px;
            border: 1px solid #dddddd;
            border-radius: 4px;
            background-color: #ffffff;
            selection-background-color: #ff8e3b;
            min-height: 20px;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 1px solid #ff8e3b;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 0px;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        /* Simple arrow using border trick since we don't have icon assets */
        QComboBox::down-arrow {
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #666666;
            margin-right: 8px;
        }
        QComboBox::down-arrow:on { /* shift the arrow when popup is open */
            top: 1px;
            left: 1px;
        }
        QPushButton {
            background-color: #ff8e3b;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #e67e2b;
        }
        QPushButton:pressed {
            background-color: #cc6f20;
        }
        QPushButton:disabled {
            background-color: #cccccc;
        }
        QTreeWidget {
            border: 1px solid #dddddd;
            border-radius: 4px;
            background-color: #ffffff;
        }
        QHeaderView::section {
            background-color: #f0f0f0;
            padding: 4px;
            border: none;
            border-bottom: 1px solid #dddddd;
        }
        """
        self.setStyleSheet(style_sheet)

def run_app():
    app = QApplication(sys.argv)
    
    # Set default font
    font = QFont("Segoe UI", 10)
    if sys.platform == "darwin":
        font = QFont("Helvetica Neue", 12) # macOS font
    app.setFont(font)
    
    window = MainWindow()
    
    # Import and add pages here to avoid circular imports during class definition
    from app.image_to_tif.image_to_tif_frame import ImageToTifFrame
    from app.excel_to_img.excel_to_img_frame import ExcelToImgFrame
    
    window.add_page(ImageToTifFrame(), "影像转 TIF")
    window.add_page(ExcelToImgFrame(), "Excel 转图片")
    
    # Select first page
    if window.nav_list.count() > 0:
        window.nav_list.setCurrentRow(0)
        
    window.show()
    sys.exit(app.exec())

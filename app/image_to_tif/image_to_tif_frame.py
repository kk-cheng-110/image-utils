import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView, 
                             QComboBox, QFileDialog, QMessageBox, QSplitter, QFrame,
                             QAbstractItemView, QDialog, QFormLayout, QDialogButtonBox,
                             QProgressDialog, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QAction, QDragEnterEvent, QDropEvent
from PIL import Image

from app.base_frame import BaseFrame
from core.image_to_tif import image_to_tif

class ImageToTifFrame(BaseFrame):
    COMPRESSION_OPTIONS = {
        "raw": "Raw (无压缩) - 速度快，文件大",
        "lzw": "LZW (无损) - 适用于线条图、文本",
        "jpeg": "JPEG (有损) - 适用于照片，可调质量",
        "deflate": "Deflate (无损) - 通用压缩，效果好",
        "packbits": "PackBits (无损) - 适用于重复数据",
        "tiff_adobe_deflate": "Adobe Deflate (无损) - 兼容性更好的Deflate",
        "ccittfax4": "CCITT Fax4 (无损) - 适用于黑白图像"
    }

    def __init__(self, parent=None):
        self.image_paths = []
        super().__init__(parent)

    def setup_ui(self):
        # Top Area: Directory Selection
        top_layout = QHBoxLayout()
        
        self.path_entry = QLineEdit()
        self.path_entry.setPlaceholderText("请选择影像目录...")
        self.path_entry.setReadOnly(True)
        top_layout.addWidget(self.path_entry)
        
        self.select_btn = QPushButton("选择影像目录")
        self.select_btn.clicked.connect(self.select_images)
        top_layout.addWidget(self.select_btn)
        
        self.layout.addLayout(top_layout)

        # Middle Area: Splitter with List and Preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Image List
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.addWidget(QLabel("影像列表 (支持拖拽排序)"))
        
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["序号", "文件名"])
        self.tree_widget.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tree_widget.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setAcceptDrops(True)
        self.tree_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.tree_widget.itemSelectionChanged.connect(self.on_selection_changed)
        
        list_layout.addWidget(self.tree_widget)
        splitter.addWidget(list_container)
        
        # Right: Preview
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.addWidget(QLabel("影像预览"))
        
        self.preview_label = QLabel("暂无预览")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #ffffff; border: 1px solid #dddddd; border-radius: 4px;")
        self.preview_label.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        )
        self.preview_label.setMinimumSize(300, 300)
        preview_layout.addWidget(self.preview_label)
        
        splitter.addWidget(preview_container)
        splitter.setStretchFactor(0, 1) # List gets 1 part
        splitter.setStretchFactor(1, 2) # Preview gets 2 parts (approx 2/3)
        
        self.layout.addWidget(splitter)

        # Bottom Area: Compression and Save
        bottom_layout = QHBoxLayout()
        
        bottom_layout.addWidget(QLabel("压缩方式:"))
        self.compression_combo = QComboBox()
        for key, desc in self.COMPRESSION_OPTIONS.items():
            self.compression_combo.addItem(desc, key)
        # Default to JPEG as in original code
        index = self.compression_combo.findData("jpeg")
        if index >= 0:
            self.compression_combo.setCurrentIndex(index)
            
        bottom_layout.addWidget(self.compression_combo)
        bottom_layout.addStretch()
        
        self.save_btn = QPushButton("合并为 TIFF")
        self.save_btn.clicked.connect(self.save_tif)
        bottom_layout.addWidget(self.save_btn)
        
        self.layout.addLayout(bottom_layout)

    def select_images(self):
        directory = QFileDialog.getExistingDirectory(self, "选择目录")
        if not directory:
            return

        self.path_entry.setText(directory)
        try:
            self.image_paths = image_to_tif.load_images(directory)
            if not self.image_paths:
                QMessageBox.warning(self, "无影像文件", "该目录下没有影像文件")
            else:
                self.update_tree_view()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def update_tree_view(self):
        self.tree_widget.clear()
        for i, path in enumerate(self.image_paths, 1):
            filename = os.path.basename(path)
            item = QTreeWidgetItem([str(i), filename])
            item.setData(0, Qt.ItemDataRole.UserRole, path) # Store full path
            self.tree_widget.addTopLevelItem(item)

    def on_selection_changed(self):
        selected_items = self.tree_widget.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        path = item.data(0, Qt.ItemDataRole.UserRole)
        
        # Preview image
        try:
            # We can use QPixmap directly or PIL
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                # Scale to fit label
                scaled_pixmap = pixmap.scaled(self.preview_label.size(), 
                                              Qt.AspectRatioMode.KeepAspectRatio, 
                                              Qt.TransformationMode.SmoothTransformation)
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_label.setText("")
            else:
                self.preview_label.setText("无法加载预览")
        except Exception as e:
            self.preview_label.setText(f"预览错误: {e}")

    def resizeEvent(self, event):
        # Update preview when resized
        super().resizeEvent(event)
        self.on_selection_changed()

    def get_ordered_image_paths(self):
        paths = []
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            # Update sequence number visibly as well
            item.setText(0, str(i + 1))
            path = item.data(0, Qt.ItemDataRole.UserRole)
            if path:
                paths.append(path)
        return paths

    def save_tif(self):
        # Get paths from tree to respect drag-and-drop order
        current_paths = self.get_ordered_image_paths()
        
        if not current_paths:
            QMessageBox.warning(self, "警告", "请先选择图片文件")
            return
            
        self.image_paths = current_paths # Update member variable

        compression_key = self.compression_combo.currentData()
        
        # Show param dialog
        dialog = CompressionParamDialog(compression_key, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            params = dialog.get_params()
            self.do_save_tif(compression_key, **params)

    def do_save_tif(self, compression_key, dpi, jpeg_quality):
        default_filename = ""
        directory = self.path_entry.text()
        if directory:
            default_filename = os.path.join(directory, os.path.basename(directory) + ".tif")

        filepath, _ = QFileDialog.getSaveFileName(self, "保存 TIFF", default_filename, "TIFF Files (*.tif)")
        if not filepath:
            return

        # Create progress dialog
        progress = QProgressDialog("正在处理...", "取消", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()

        # Run in thread to avoid freezing UI
        self.thread = SaveThread(self.image_paths, filepath, compression_key, dpi, jpeg_quality)
        self.thread.progress_updated.connect(progress.setValue)
        self.thread.status_updated.connect(progress.setLabelText)
        self.thread.finished_signal.connect(lambda msg: self.on_save_finished(msg, progress))
        self.thread.error_signal.connect(lambda msg: self.on_save_error(msg, progress))
        self.thread.start()

    def on_save_finished(self, msg, progress_dialog):
        progress_dialog.setValue(100)
        progress_dialog.close()
        QMessageBox.information(self, "成功", msg)

    def on_save_error(self, msg, progress_dialog):
        progress_dialog.close()
        QMessageBox.critical(self, "错误", msg)


class CompressionParamDialog(QDialog):
    def __init__(self, compression_key, parent=None):
        super().__init__(parent)
        self.compression_key = compression_key
        self.setWindowTitle("参数设置")
        self.setFixedSize(300, 150)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.dpi_input = QLineEdit("200")
        layout.addRow("DPI:", self.dpi_input)
        
        self.jpeg_quality_input = None
        if self.compression_key == "jpeg":
            self.jpeg_quality_input = QLineEdit("75")
            layout.addRow("JPEG 质量 (1-100):", self.jpeg_quality_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def accept(self):
        try:
            dpi = int(self.dpi_input.text())
            if dpi <= 0:
                raise ValueError("DPI 必须为正整数")
            
            if self.jpeg_quality_input:
                quality = int(self.jpeg_quality_input.text())
                if not (1 <= quality <= 100):
                    raise ValueError("JPEG 质量必须在 1-100 之间")
        except ValueError as e:
            QMessageBox.warning(self, "参数错误", str(e))
            return
            
        super().accept()

    def get_params(self):
        params = {"dpi": int(self.dpi_input.text()), "jpeg_quality": None}
        if self.jpeg_quality_input:
            params["jpeg_quality"] = int(self.jpeg_quality_input.text())
        return params

class SaveThread(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, image_paths, filepath, compression, dpi, jpeg_quality):
        super().__init__()
        self.image_paths = image_paths
        self.filepath = filepath
        self.compression = compression
        self.dpi = dpi
        self.jpeg_quality = jpeg_quality

    def run(self):
        try:
            def callback(value, msg):
                self.progress_updated.emit(value)
                self.status_updated.emit(msg)
            
            image_to_tif.merge_images_to_tif(
                self.image_paths, 
                self.filepath, 
                compression=self.compression, 
                dpi=self.dpi,
                jpeg_quality=self.jpeg_quality, 
                progress_callback=callback
            )
            self.finished_signal.emit("TIF 文件已保存成功！")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error_signal.emit(f"保存失败: {str(e)}")

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QFileDialog, QMessageBox, QFormLayout,
                             QProgressDialog, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from app.base_frame import BaseFrame
from core.excel_to_img import excel_to_img

class ExcelToImgFrame(BaseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

    def setup_ui(self):
        # We use a Form Layout for better alignment
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # 1. Excel File
        file_layout = QHBoxLayout()
        self.excel_path_input = QLineEdit()
        self.excel_path_input.setPlaceholderText("请选择 Excel 文件 (.xlsx, .xls)")
        self.excel_path_input.setReadOnly(True)
        file_layout.addWidget(self.excel_path_input)
        
        self.select_excel_btn = QPushButton("选择 Excel")
        self.select_excel_btn.clicked.connect(self.select_excel)
        file_layout.addWidget(self.select_excel_btn)
        
        form_layout.addRow("Excel 文件:", file_layout)
        
        # 2. Sheet Selection
        self.sheet_combo = QComboBox()
        self.sheet_combo.currentIndexChanged.connect(self.on_sheet_selected)
        form_layout.addRow("选择 Sheet:", self.sheet_combo)
        
        # 3. Naming Field (Mandatory)
        naming_layout = QHBoxLayout()
        self.naming_combo = QComboBox()
        naming_layout.addWidget(self.naming_combo)
        form_layout.addRow("命名字段:", naming_layout)

        # 4. Grouping Checkbox
        self.group_checkbox = QCheckBox("是否分组")
        self.group_checkbox.setChecked(False) # Default No
        form_layout.addRow("", self.group_checkbox)
        
        # 5. Shared Directory
        share_layout = QHBoxLayout()
        self.share_dir_input = QLineEdit()
        self.share_dir_input.setPlaceholderText("请选择共享目录 (可选)")
        share_layout.addWidget(self.share_dir_input)
        
        self.select_share_btn = QPushButton("选择目录")
        self.select_share_btn.clicked.connect(self.select_share_dir)
        share_layout.addWidget(self.select_share_btn)
        
        form_layout.addRow("共享目录:", share_layout)
        
        self.layout.addLayout(form_layout)
        
        self.layout.addStretch()
        
        # 5. Generate Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.generate_btn = QPushButton("生成图片")
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.setMinimumWidth(150)
        self.generate_btn.clicked.connect(self.generate_images)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addStretch()
        
        self.layout.addLayout(btn_layout)
        self.layout.addStretch()

    def select_excel(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "选择 Excel 文件", "", "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if not filepath:
            return
            
        self.excel_path_input.setText(filepath)
        
        # Load Sheets
        try:
            sheets = excel_to_img.get_excel_sheets(filepath)
            self.sheet_combo.clear()
            self.sheet_combo.addItems(sheets)
            if sheets:
                self.sheet_combo.setCurrentIndex(0)
                # self.on_sheet_selected() # Triggered automatically by currentIndexChanged? Maybe not if 0->0
                # Force trigger if index is 0
                if self.sheet_combo.currentIndex() == 0:
                    self.on_sheet_selected()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取 Excel 文件失败:\n{str(e)}")

    def on_sheet_selected(self):
        excel_path = self.excel_path_input.text()
        sheet_name = self.sheet_combo.currentText()
        
        if not excel_path or not sheet_name:
            return
            
        try:
            columns = excel_to_img.get_sheet_columns(excel_path, sheet_name)
            self.naming_combo.clear()
            self.naming_combo.addItems(columns)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取 Sheet 列名失败:\n{str(e)}")

    def select_share_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择共享目录")
        if directory:
            self.share_dir_input.setText(directory)

    def generate_images(self):
        excel_path = self.excel_path_input.text()
        sheet_name = self.sheet_combo.currentText()
        
        if not excel_path:
            QMessageBox.warning(self, "警告", "请先选择 Excel 文件")
            return
        
        if not sheet_name:
            QMessageBox.warning(self, "警告", "请选择一个 Sheet")
            return
            
        output_dir = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if not output_dir:
            return
            
        naming_field = self.naming_combo.currentText()
        if not naming_field:
            QMessageBox.warning(self, "警告", "请选择命名字段")
            return

        is_grouped = self.group_checkbox.isChecked()
        group_field = naming_field if is_grouped else None
            
        share_dir = self.share_dir_input.text()
        if not share_dir:
            share_dir = None
            
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("生成中...")
        
        # Create indeterminate progress dialog
        self.progress = QProgressDialog("正在生成图片，请稍候...", "取消", 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.setCancelButton(None) # Disable cancel for now as backend might not support it
        self.progress.show()
        
        self.thread = GenerateThread(excel_path, sheet_name, output_dir, naming_field, is_grouped, share_dir)
        self.thread.finished_signal.connect(self.on_finished)
        self.thread.error_signal.connect(self.on_error)
        self.thread.start()

    def on_finished(self):
        self.progress.close()
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("生成图片")
        QMessageBox.information(self, "成功", "图片生成完成！")

    def on_error(self, msg):
        self.progress.close()
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("生成图片")
        QMessageBox.critical(self, "错误", f"生成图片失败:\n{msg}")

class GenerateThread(QThread):
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    
    def __init__(self, excel_path, sheet_name, output_dir, naming_field, is_grouped, share_dir):
        super().__init__()
        self.excel_path = excel_path
        self.sheet_name = sheet_name
        self.output_dir = output_dir
        self.naming_field = naming_field
        self.is_grouped = is_grouped
        self.share_dir = share_dir
        
    def run(self):
        try:
            excel_to_img.generate_images(
                excel_path=self.excel_path,
                sheet_name=self.sheet_name,
                output_dir=self.output_dir,
                naming_field=self.naming_field,
                is_grouped=self.is_grouped,
                share_dir=self.share_dir
            )
            self.finished_signal.emit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error_signal.emit(str(e))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
题库管理面板
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QFileDialog, QMessageBox,
    QGroupBox
)
from PyQt6.QtCore import pyqtSignal


class BankPanel(QWidget):
    """题库管理面板"""

    # 信号
    bank_changed = pyqtSignal(str)  # 当前题库变化
    bank_loaded = pyqtSignal(str, int)  # 题库加载完成 (名称, 题目数)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """初始化界面"""
        group = QGroupBox("题库管理")
        layout = QVBoxLayout(group)

        # 题库选择行
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("当前题库:"))

        self._bank_combo = QComboBox()
        self._bank_combo.setMinimumWidth(200)
        self._bank_combo.addItem("-- 请导入题库 --")
        self._bank_combo.currentTextChanged.connect(self._on_bank_changed)
        select_layout.addWidget(self._bank_combo, 1)

        layout.addLayout(select_layout)

        # 题库信息
        self._info_label = QLabel("题目数量: 0")
        layout.addWidget(self._info_label)

        # 按钮行
        btn_layout = QHBoxLayout()

        self._import_btn = QPushButton("导入题库")
        self._import_btn.clicked.connect(self._on_import_clicked)
        btn_layout.addWidget(self._import_btn)

        self._remove_btn = QPushButton("移除题库")
        self._remove_btn.clicked.connect(self._on_remove_clicked)
        self._remove_btn.setEnabled(False)
        btn_layout.addWidget(self._remove_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)

    def _on_import_clicked(self):
        """导入题库按钮点击"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择题库文件", "",
            "Markdown 文件 (*.md);;所有文件 (*.*)"
        )
        if file_path:
            self.import_requested.emit(file_path)

    def _on_remove_clicked(self):
        """移除题库按钮点击"""
        current = self._bank_combo.currentText()
        if current and current != "-- 请导入题库 --":
            reply = QMessageBox.question(
                self, "确认", f"确定要移除题库 '{current}' 吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.remove_requested.emit(current)

    def _on_bank_changed(self, bank_name: str):
        """题库选择变化"""
        if bank_name and bank_name != "-- 请导入题库 --":
            self._remove_btn.setEnabled(True)
            self.bank_changed.emit(bank_name)
        else:
            self._remove_btn.setEnabled(False)

    # 信号
    import_requested = pyqtSignal(str)
    remove_requested = pyqtSignal(str)

    def add_bank(self, name: str, count: int):
        """添加题库到下拉列表"""
        # 移除默认项
        idx = self._bank_combo.findText("-- 请导入题库 --")
        if idx >= 0:
            self._bank_combo.removeItem(idx)

        # 检查是否已存在
        existing_idx = self._bank_combo.findText(name)
        if existing_idx >= 0:
            self._bank_combo.removeItem(existing_idx)

        self._bank_combo.addItem(name)
        self._bank_combo.setCurrentText(name)
        self.update_info(count)

    def remove_bank(self, name: str):
        """从下拉列表移除题库"""
        idx = self._bank_combo.findText(name)
        if idx >= 0:
            self._bank_combo.removeItem(idx)

        if self._bank_combo.count() == 0:
            self._bank_combo.addItem("-- 请导入题库 --")
            self.update_info(0)

    def update_info(self, total: int, available: int = None):
        """更新题库信息显示"""
        if available is not None:
            self._info_label.setText(f"题目数量: {total} | 剩余可抽: {available}")
        else:
            self._info_label.setText(f"题目数量: {total}")

    def get_current_bank(self) -> str:
        """获取当前选中的题库"""
        current = self._bank_combo.currentText()
        if current == "-- 请导入题库 --":
            return ""
        return current

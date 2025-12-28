#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
名单管理面板
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import pyqtSignal


class RosterPanel(QWidget):
    """名单管理面板"""

    # 信号
    import_requested = pyqtSignal(str)  # 导入名单请求
    clear_requested = pyqtSignal()  # 清空名单请求

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """初始化界面"""
        group = QGroupBox("名单管理")
        layout = QVBoxLayout(group)

        # 名单信息
        self._name_label = QLabel("当前名单: 未导入")
        layout.addWidget(self._name_label)

        self._info_label = QLabel("人数: 0 | 剩余: 0")
        layout.addWidget(self._info_label)

        # 按钮行
        btn_layout = QHBoxLayout()

        self._import_btn = QPushButton("导入名单")
        self._import_btn.clicked.connect(self._on_import_clicked)
        btn_layout.addWidget(self._import_btn)

        self._clear_btn = QPushButton("清空名单")
        self._clear_btn.clicked.connect(self._on_clear_clicked)
        self._clear_btn.setEnabled(False)
        btn_layout.addWidget(self._clear_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)

    def _on_import_clicked(self):
        """导入名单按钮点击"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择名单文件", "",
            "文本文件 (*.txt);;Markdown 文件 (*.md);;所有文件 (*.*)"
        )
        if file_path:
            self.import_requested.emit(file_path)

    def _on_clear_clicked(self):
        """清空名单按钮点击"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空名单吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_requested.emit()

    def update_roster(self, name: str, total: int, available: int):
        """更新名单显示

        Args:
            name: 名单名称
            total: 总人数
            available: 剩余可抽人数
        """
        self._name_label.setText(f"当前名单: {name}")
        self._info_label.setText(f"人数: {total} | 剩余: {available}")
        self._clear_btn.setEnabled(True)

    def clear_display(self):
        """清空显示"""
        self._name_label.setText("当前名单: 未导入")
        self._info_label.setText("人数: 0 | 剩余: 0")
        self._clear_btn.setEnabled(False)

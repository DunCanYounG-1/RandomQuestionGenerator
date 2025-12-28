#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
抽题操作面板
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QCheckBox, QGroupBox
)
from PyQt6.QtCore import pyqtSignal, Qt


class DrawPanel(QWidget):
    """抽题操作面板"""

    # 信号
    draw_requested = pyqtSignal(int, bool)  # 抽题请求 (数量, 是否去重)
    reset_requested = pyqtSignal()  # 重置题池请求

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """初始化界面"""
        group = QGroupBox("抽题设置")
        layout = QVBoxLayout(group)

        # 抽取数量
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("抽取数量:"))

        self._count_spin = QSpinBox()
        self._count_spin.setRange(1, 100)
        self._count_spin.setValue(1)
        self._count_spin.setMinimumWidth(80)
        count_layout.addWidget(self._count_spin)

        count_layout.addStretch()
        layout.addLayout(count_layout)

        # 去重开关
        self._no_repeat_check = QCheckBox("启用去重（已抽过的不再抽取）")
        self._no_repeat_check.setChecked(True)
        layout.addWidget(self._no_repeat_check)

        # 抽题按钮
        self._draw_btn = QPushButton("开 始 抽 题")
        self._draw_btn.setMinimumHeight(50)
        self._draw_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self._draw_btn.clicked.connect(self._on_draw_clicked)
        layout.addWidget(self._draw_btn)

        # 重置按钮
        self._reset_btn = QPushButton("重置题池")
        self._reset_btn.clicked.connect(self._on_reset_clicked)
        layout.addWidget(self._reset_btn)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)

    def _on_draw_clicked(self):
        """抽题按钮点击"""
        count = self._count_spin.value()
        no_repeat = self._no_repeat_check.isChecked()
        self.draw_requested.emit(count, no_repeat)

    def _on_reset_clicked(self):
        """重置按钮点击"""
        self.reset_requested.emit()

    def set_enabled(self, enabled: bool):
        """设置控件可用状态"""
        self._draw_btn.setEnabled(enabled)
        self._count_spin.setEnabled(enabled)
        self._no_repeat_check.setEnabled(enabled)
        self._reset_btn.setEnabled(enabled)

    def set_max_count(self, max_count: int):
        """设置最大抽取数量"""
        self._count_spin.setMaximum(max(1, max_count))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
结果展示面板
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class DrawResult:
    """抽取结果"""
    question_title: str
    question_content: str
    question_id: str
    bank_name: str
    person_name: str = ""


class ResultPanel(QWidget):
    """结果展示面板"""

    # 导出信号
    export_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._results: List[DrawResult] = []
        self._current_index = 0
        self._init_ui()

    def _init_ui(self):
        """初始化界面"""
        group = QGroupBox("抽取结果")
        layout = QVBoxLayout(group)

        # 人员显示（可选）
        self._person_label = QLabel("")
        self._person_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1976D2;
                padding: 10px;
                background-color: #E3F2FD;
                border-radius: 5px;
            }
        """)
        self._person_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._person_label.setVisible(False)
        layout.addWidget(self._person_label)

        # 题目标题
        self._title_label = QLabel("等待抽题...")
        self._title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
            }
        """)
        self._title_label.setWordWrap(True)
        layout.addWidget(self._title_label)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # 题目内容
        content_label = QLabel("题目要求:")
        layout.addWidget(content_label)

        self._content_text = QTextEdit()
        self._content_text.setReadOnly(True)
        self._content_text.setMinimumHeight(120)
        self._content_text.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                padding: 10px;
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self._content_text, 1)

        # 导航按钮（多题时显示）
        nav_layout = QHBoxLayout()

        self._prev_btn = QPushButton("上一个")
        self._prev_btn.clicked.connect(self._show_prev)
        self._prev_btn.setVisible(False)
        nav_layout.addWidget(self._prev_btn)

        self._nav_label = QLabel("")
        self._nav_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self._nav_label, 1)

        self._next_btn = QPushButton("下一个")
        self._next_btn.clicked.connect(self._show_next)
        self._next_btn.setVisible(False)
        nav_layout.addWidget(self._next_btn)

        # 导出按钮
        self._export_btn = QPushButton("导出结果")
        self._export_btn.clicked.connect(self._on_export_clicked)
        self._export_btn.setEnabled(False)
        nav_layout.addWidget(self._export_btn)

        layout.addLayout(nav_layout)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)

    def show_results(self, results: List[DrawResult]):
        """显示抽取结果（替换模式）"""
        self._results = results
        self._current_index = 0

        if not results:
            self._title_label.setText("没有可抽取的题目")
            self._content_text.clear()
            self._person_label.setVisible(False)
            self._hide_nav()
            return

        # 显示导航（多个结果时）
        if len(results) > 1:
            self._show_nav()
        else:
            self._hide_nav()

        self._show_current()

    def append_results(self, results: List[DrawResult]):
        """追加抽取结果（累积模式）"""
        if not results:
            return

        self._results.extend(results)
        # 跳转到最新追加的第一个结果
        self._current_index = len(self._results) - len(results)

        # 显示导航（多个结果时）
        if len(self._results) > 1:
            self._show_nav()
        else:
            self._hide_nav()

        self._show_current()

    def set_export_enabled(self, enabled: bool):
        """设置导出按钮启用状态"""
        self._export_btn.setEnabled(enabled)

    def _show_current(self):
        """显示当前结果"""
        if not self._results:
            return

        result = self._results[self._current_index]

        # 显示人员（如果有）
        if result.person_name:
            self._person_label.setText(f"抽中: {result.person_name}")
            self._person_label.setVisible(True)
        else:
            self._person_label.setVisible(False)

        # 显示题目
        self._title_label.setText(result.question_title)
        self._content_text.setText(result.question_content or "（无详细要求）")

        # 更新导航
        self._nav_label.setText(f"{self._current_index + 1} / {len(self._results)}")
        self._prev_btn.setEnabled(self._current_index > 0)
        self._next_btn.setEnabled(self._current_index < len(self._results) - 1)

    def _show_prev(self):
        """显示上一个"""
        if self._current_index > 0:
            self._current_index -= 1
            self._show_current()

    def _show_next(self):
        """显示下一个"""
        if self._current_index < len(self._results) - 1:
            self._current_index += 1
            self._show_current()

    def _show_nav(self):
        """显示导航"""
        self._prev_btn.setVisible(True)
        self._next_btn.setVisible(True)
        self._nav_label.setVisible(True)

    def _hide_nav(self):
        """隐藏导航"""
        self._prev_btn.setVisible(False)
        self._next_btn.setVisible(False)
        self._nav_label.setVisible(False)

    def clear(self):
        """清空显示"""
        self._results = []
        self._current_index = 0
        self._title_label.setText("等待抽题...")
        self._content_text.clear()
        self._person_label.setVisible(False)
        self._hide_nav()
        self._export_btn.setEnabled(False)

    def _on_export_clicked(self):
        """导出按钮点击"""
        if self._results:
            self.export_requested.emit()

    def get_results(self) -> List[DrawResult]:
        """获取当前结果列表"""
        return self._results

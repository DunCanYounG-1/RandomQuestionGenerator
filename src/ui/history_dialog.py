#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
历史记录对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from typing import List
from src.storage.database import Database, DrawRecord
from src.storage.exporter import Exporter


class HistoryDialog(QDialog):
    """历史记录对话框"""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._db = db
        self._records: List[DrawRecord] = []
        self._init_ui()
        self._load_history()

    def _init_ui(self):
        """初始化界面"""
        self.setWindowTitle("抽题历史")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout(self)

        # 信息标签
        self._info_label = QLabel("共 0 条记录")
        layout.addWidget(self._info_label)

        # 历史表格
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["序号", "人员", "题目标题", "题库", "抽取时间"])
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.doubleClicked.connect(self._on_item_double_clicked)

        # 设置列宽
        self._table.setColumnWidth(0, 50)
        self._table.setColumnWidth(1, 80)
        self._table.setColumnWidth(3, 100)
        self._table.setColumnWidth(4, 150)

        layout.addWidget(self._table)

        # 按钮行
        btn_layout = QHBoxLayout()

        self._export_txt_btn = QPushButton("导出 TXT")
        self._export_txt_btn.clicked.connect(self._export_txt)
        btn_layout.addWidget(self._export_txt_btn)

        self._export_excel_btn = QPushButton("导出 Excel")
        self._export_excel_btn.clicked.connect(self._export_excel)
        btn_layout.addWidget(self._export_excel_btn)

        btn_layout.addStretch()

        self._clear_btn = QPushButton("清空历史")
        self._clear_btn.clicked.connect(self._clear_history)
        btn_layout.addWidget(self._clear_btn)

        self._close_btn = QPushButton("关闭")
        self._close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self._close_btn)

        layout.addLayout(btn_layout)

    def _load_history(self):
        """加载历史记录"""
        self._records = self._db.get_history(limit=500)
        self._info_label.setText(f"共 {len(self._records)} 条记录")

        self._table.setRowCount(len(self._records))
        for row, record in enumerate(self._records):
            self._table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self._table.setItem(row, 1, QTableWidgetItem(record.person_name or "-"))
            self._table.setItem(row, 2, QTableWidgetItem(record.question_title))
            self._table.setItem(row, 3, QTableWidgetItem(record.bank_name))
            self._table.setItem(row, 4, QTableWidgetItem(
                record.draw_time.strftime("%Y-%m-%d %H:%M:%S")))

    def _on_item_double_clicked(self, index):
        """双击查看详情"""
        row = index.row()
        if 0 <= row < len(self._records):
            record = self._records[row]
            person_info = f"抽中人员: {record.person_name}\n" if record.person_name else ""
            QMessageBox.information(
                self, "题目详情",
                f"{person_info}"
                f"题目: {record.question_title}\n\n"
                f"题库: {record.bank_name}\n"
                f"抽取时间: {record.draw_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"题目要求:\n{record.question_content or '（无）'}"
            )

    def _export_txt(self):
        """导出为 TXT"""
        if not self._records:
            QMessageBox.warning(self, "提示", "没有记录可导出")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出 TXT", "抽题记录.txt",
            "文本文件 (*.txt)"
        )
        if file_path:
            if Exporter.export_to_txt(self._records, file_path):
                QMessageBox.information(self, "成功", f"已导出到: {file_path}")
            else:
                QMessageBox.warning(self, "失败", "导出失败")

    def _export_excel(self):
        """导出为 Excel"""
        if not self._records:
            QMessageBox.warning(self, "提示", "没有记录可导出")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出 Excel", "抽题记录.xlsx",
            "Excel 文件 (*.xlsx)"
        )
        if file_path:
            if Exporter.export_to_excel(self._records, file_path):
                QMessageBox.information(self, "成功", f"已导出到: {file_path}")
            else:
                QMessageBox.warning(self, "失败", "导出失败，请确保已安装 openpyxl")

    def _clear_history(self):
        """清空历史"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有历史记录吗？\n此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._db.clear_history()
            self._load_history()
            QMessageBox.information(self, "成功", "历史记录已清空")

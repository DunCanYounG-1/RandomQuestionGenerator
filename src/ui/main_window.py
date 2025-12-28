#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
随机抽题机 - 主窗口
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QCheckBox, QFileDialog, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.core.bank import QuestionBank
from src.core.drawer import DrawEngine
from src.core.roster import RosterManager
from src.storage.database import Database
from src.storage.exporter import Exporter

from .bank_panel import BankPanel
from .draw_panel import DrawPanel
from .result_panel import ResultPanel, DrawResult
from .roster_panel import RosterPanel
from .history_dialog import HistoryDialog


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("随机抽题机")
        self.setMinimumSize(900, 650)

        # 初始化核心组件
        self._bank = QuestionBank()
        self._drawer = DrawEngine(self._bank)
        self._roster = RosterManager()
        self._db = Database()

        self._init_ui()
        self._connect_signals()
        # 每次启动时清除之前导入的题库和名单
        self._db.clear_all_bank_info()
        self._db.clear_roster_info()
        self._db.clear_drawn_questions()
        self._db.clear_drawn_persons()

    def _init_ui(self):
        """初始化界面"""
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 上部布局：题库管理 + 名单管理
        top_layout = QHBoxLayout()

        # 题库管理面板
        self._bank_panel = BankPanel()
        top_layout.addWidget(self._bank_panel, 1)

        # 名单管理面板
        self._roster_panel = RosterPanel()
        top_layout.addWidget(self._roster_panel, 1)

        main_layout.addLayout(top_layout)

        # 中部布局：抽题设置
        mid_layout = QHBoxLayout()

        # 抽题操作面板
        self._draw_panel = DrawPanel()
        self._draw_panel.set_enabled(False)
        mid_layout.addWidget(self._draw_panel, 1)

        # 抽人开关
        option_widget = QWidget()
        option_layout = QVBoxLayout(option_widget)
        option_layout.setContentsMargins(10, 10, 10, 10)

        self._draw_person_check = QCheckBox("同时抽取人员")
        self._draw_person_check.setChecked(False)
        self._draw_person_check.setEnabled(False)
        option_layout.addWidget(self._draw_person_check)

        self._person_no_repeat_check = QCheckBox("人员去重")
        self._person_no_repeat_check.setChecked(True)
        self._person_no_repeat_check.setEnabled(False)
        option_layout.addWidget(self._person_no_repeat_check)

        self._reset_person_btn = QPushButton("重置人员")
        self._reset_person_btn.clicked.connect(self._reset_persons)
        self._reset_person_btn.setEnabled(False)
        option_layout.addWidget(self._reset_person_btn)

        option_layout.addStretch()
        mid_layout.addWidget(option_widget)

        main_layout.addLayout(mid_layout)

        # 结果展示面板
        self._result_panel = ResultPanel()
        main_layout.addWidget(self._result_panel, 1)

        # 底部按钮
        bottom_layout = QHBoxLayout()

        # 作者水印
        author_label = QLabel("By duncany")
        author_label.setStyleSheet("color: #888888;")
        author_font = QFont()
        author_font.setPointSize(9)
        author_label.setFont(author_font)
        bottom_layout.addWidget(author_label)

        bottom_layout.addStretch()

        self._history_btn = QPushButton("查看历史")
        self._history_btn.clicked.connect(self._show_history)
        bottom_layout.addWidget(self._history_btn)

        main_layout.addLayout(bottom_layout)

    def _connect_signals(self):
        """连接信号"""
        # 题库面板信号
        self._bank_panel.import_requested.connect(self._import_bank)
        self._bank_panel.remove_requested.connect(self._remove_bank)
        self._bank_panel.bank_changed.connect(self._on_bank_changed)

        # 名单面板信号
        self._roster_panel.import_requested.connect(self._import_roster)
        self._roster_panel.clear_requested.connect(self._clear_roster)

        # 抽题面板信号
        self._draw_panel.draw_requested.connect(self._do_draw)
        self._draw_panel.reset_requested.connect(self._reset_pool)

        # 结果面板信号
        self._result_panel.export_requested.connect(self._export_results)

    def _load_saved_data(self):
        """加载保存的数据"""
        # 加载题库
        banks_info = self._db.get_bank_info()
        for info in banks_info:
            try:
                bank_name = self._bank.load_bank(info["file_path"])
                count = self._bank.get_question_count(bank_name)
                self._bank_panel.add_bank(bank_name, count)
            except Exception:
                self._db.remove_bank_info(info["name"])

        # 加载名单
        roster_info = self._db.get_roster_info()
        if roster_info:
            try:
                count = self._roster.load_roster(roster_info["file_path"])
                self._update_roster_status()
            except Exception:
                self._db.clear_roster_info()

    def _import_bank(self, file_path: str):
        """导入题库"""
        try:
            bank_name = self._bank.load_bank(file_path)
            count = self._bank.get_question_count(bank_name)

            self._db.save_bank_info(bank_name, file_path, count)
            self._bank_panel.add_bank(bank_name, count)
            self._update_status()
            self._draw_panel.set_enabled(True)

            QMessageBox.information(
                self, "成功", f"已导入题库: {bank_name}\n共 {count} 道题目"
            )
        except Exception as e:
            QMessageBox.warning(self, "导入失败", str(e))

    def _remove_bank(self, bank_name: str):
        """移除题库"""
        self._bank.remove_bank(bank_name)
        self._db.remove_bank_info(bank_name)
        self._bank_panel.remove_bank(bank_name)
        self._update_status()

        if not self._bank.get_bank_names():
            self._draw_panel.set_enabled(False)
            self._result_panel.clear()

    def _on_bank_changed(self, bank_name: str):
        """题库切换"""
        self._update_status()

    def _import_roster(self, file_path: str):
        """导入名单"""
        try:
            count = self._roster.load_roster(file_path)
            self._db.save_roster_info(
                self._roster.get_roster_name(),
                file_path,
                count
            )
            self._update_roster_status()

            QMessageBox.information(
                self, "成功", f"已导入名单: {self._roster.get_roster_name()}\n共 {count} 人"
            )
        except Exception as e:
            QMessageBox.warning(self, "导入失败", str(e))

    def _clear_roster(self):
        """清空名单"""
        self._roster.clear()
        self._db.clear_roster_info()
        self._db.clear_drawn_persons()
        self._roster_panel.clear_display()
        self._draw_person_check.setEnabled(False)
        self._draw_person_check.setChecked(False)
        self._person_no_repeat_check.setEnabled(False)
        self._reset_person_btn.setEnabled(False)
        # 清空结果面板
        self._result_panel.clear()

    def _update_roster_status(self):
        """更新名单状态"""
        if self._roster.is_loaded():
            total = self._roster.get_count()
            available = self._roster.get_available_count(True)
            self._roster_panel.update_roster(
                self._roster.get_roster_name(),
                total,
                available
            )
            self._draw_person_check.setEnabled(True)
            self._person_no_repeat_check.setEnabled(True)
            self._reset_person_btn.setEnabled(True)

    def _update_status(self):
        """更新状态显示"""
        bank_name = self._bank_panel.get_current_bank()
        if bank_name:
            total = self._bank.get_question_count(bank_name)
            available = self._bank.get_available_count(bank_name, True)
            self._bank_panel.update_info(total, available)
            self._draw_panel.set_max_count(available)

    def _do_draw(self, count: int, no_repeat: bool):
        """执行抽题"""
        bank_name = self._bank_panel.get_current_bank()
        if not bank_name:
            QMessageBox.warning(self, "提示", "请先选择题库")
            return

        # 是否同时抽人
        draw_person = self._draw_person_check.isChecked() and self._roster.is_loaded()
        person_no_repeat = self._person_no_repeat_check.isChecked()

        # 检查人员是否已抽完
        if draw_person and person_no_repeat:
            available_persons = self._roster.get_available_count(True)
            if available_persons == 0:
                QMessageBox.warning(self, "提示", "名单已全部抽完！\n请重置人员或关闭人员去重")
                return
            if available_persons < count:
                QMessageBox.warning(self, "提示", f"剩余人员不足！\n当前仅剩 {available_persons} 人可抽取")
                return

        questions = self._drawer.draw(count, bank_name, no_repeat)

        if not questions:
            QMessageBox.information(self, "提示", "没有可抽取的题目了\n请重置题池或关闭去重")
            return

        results = []
        for q in questions:
            person_name = ""
            if draw_person:
                person = self._roster.draw_one(person_no_repeat)
                if person:
                    person_name = person.name
                    if person_no_repeat:
                        self._db.add_drawn_person(person_name)

            results.append(DrawResult(
                question_title=q.title,
                question_content=q.content,
                question_id=q.id,
                bank_name=q.bank_name,
                person_name=person_name
            ))

            # 保存历史
            self._db.add_history(q.id, q.title, q.content, q.bank_name, person_name)
            if no_repeat:
                self._db.add_drawn_question(q.id, q.bank_name)

        # 显示结果（累积模式）
        self._result_panel.append_results(results)

        # 更新状态
        self._update_status()
        if draw_person:
            self._update_roster_status()
            # 检查名单是否已抽完
            remaining = self._roster.get_available_count(True)
            if remaining == 0:
                # 启用导出按钮
                self._result_panel.set_export_enabled(True)
                QMessageBox.information(self, "提示", "名单已全部抽完！可以导出结果了")

    def _reset_pool(self):
        """重置题池"""
        bank_name = self._bank_panel.get_current_bank()
        reply = QMessageBox.question(
            self, "确认",
            "确定要重置题池吗？\n这将清除当前题库的已抽取记录。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._drawer.reset(bank_name)
            self._db.clear_drawn_questions(bank_name)
            self._update_status()
            QMessageBox.information(self, "成功", "题池已重置")

    def _reset_persons(self):
        """重置人员"""
        reply = QMessageBox.question(
            self, "确认",
            "确定要重置人员名单吗？\n这将清除已抽取的人员记录和当前抽题结果。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._roster.reset()
            self._db.clear_drawn_persons()
            self._update_roster_status()
            # 清空结果面板
            self._result_panel.clear()
            QMessageBox.information(self, "成功", "人员名单已重置")

    def _show_history(self):
        """显示历史记录"""
        dialog = HistoryDialog(self._db, self)
        dialog.exec()

    def _export_results(self):
        """导出当前抽题结果"""
        results = self._result_panel.get_results()
        if not results:
            QMessageBox.information(self, "提示", "没有可导出的结果")
            return

        # 选择文件类型和路径
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "导出抽题结果",
            "",
            "Excel 文件 (*.xlsx);;文本文件 (*.txt)"
        )

        if not file_path:
            return

        # 根据选择的类型导出
        if selected_filter == "Excel 文件 (*.xlsx)":
            if not file_path.endswith(".xlsx"):
                file_path += ".xlsx"
            success = Exporter.export_results_to_excel(results, file_path)
        else:
            if not file_path.endswith(".txt"):
                file_path += ".txt"
            success = Exporter.export_results_to_txt(results, file_path)

        if success:
            QMessageBox.information(self, "成功", f"已导出到:\n{file_path}")
        else:
            QMessageBox.warning(self, "失败", "导出失败，请重试")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
题库管理器
"""

from typing import Dict, List, Optional, Set
from .question import Question
from .parser import MDParser


class QuestionBank:
    """题库管理器

    管理多个题库文件，支持题目的加载、查询和去重标记
    """

    def __init__(self):
        # 题库: {题库名称: [Question列表]}
        self._banks: Dict[str, List[Question]] = {}
        # 题库文件路径: {题库名称: 文件路径}
        self._bank_paths: Dict[str, str] = {}
        # 已抽取的题目ID集合（用于去重）
        self._drawn_ids: Set[str] = set()

    def load_bank(self, file_path: str) -> str:
        """加载题库文件

        Args:
            file_path: MD 文件路径

        Returns:
            题库名称
        """
        questions = MDParser.parse_file(file_path)
        bank_name = questions[0].bank_name if questions else ""

        if not bank_name:
            import os
            bank_name = os.path.splitext(os.path.basename(file_path))[0]

        # 如果题库已存在，先移除
        if bank_name in self._banks:
            self.remove_bank(bank_name)

        self._banks[bank_name] = questions
        self._bank_paths[bank_name] = file_path

        return bank_name

    def remove_bank(self, bank_name: str) -> bool:
        """移除题库

        Args:
            bank_name: 题库名称

        Returns:
            是否成功移除
        """
        if bank_name in self._banks:
            # 移除该题库中已抽取的题目记录
            bank_question_ids = {q.id for q in self._banks[bank_name]}
            self._drawn_ids -= bank_question_ids

            del self._banks[bank_name]
            del self._bank_paths[bank_name]
            return True
        return False

    def get_bank_names(self) -> List[str]:
        """获取所有题库名称"""
        return list(self._banks.keys())

    def get_bank_path(self, bank_name: str) -> Optional[str]:
        """获取题库文件路径"""
        return self._bank_paths.get(bank_name)

    def get_questions(self, bank_name: Optional[str] = None) -> List[Question]:
        """获取题目列表

        Args:
            bank_name: 题库名称，为 None 时返回所有题库的题目

        Returns:
            题目列表
        """
        if bank_name:
            return self._banks.get(bank_name, [])

        # 返回所有题库的题目
        all_questions = []
        for questions in self._banks.values():
            all_questions.extend(questions)
        return all_questions

    def get_available_questions(self, bank_name: Optional[str] = None,
                                 exclude_drawn: bool = True) -> List[Question]:
        """获取可抽取的题目列表

        Args:
            bank_name: 题库名称，为 None 时从所有题库获取
            exclude_drawn: 是否排除已抽取的题目

        Returns:
            可抽取的题目列表
        """
        questions = self.get_questions(bank_name)

        if exclude_drawn:
            questions = [q for q in questions if q.id not in self._drawn_ids]

        return questions

    def get_question_count(self, bank_name: Optional[str] = None) -> int:
        """获取题目总数"""
        return len(self.get_questions(bank_name))

    def get_available_count(self, bank_name: Optional[str] = None,
                            exclude_drawn: bool = True) -> int:
        """获取可抽取题目数量"""
        return len(self.get_available_questions(bank_name, exclude_drawn))

    def mark_drawn(self, question_ids: List[str]):
        """标记题目为已抽取

        Args:
            question_ids: 题目ID列表
        """
        self._drawn_ids.update(question_ids)

    def is_drawn(self, question_id: str) -> bool:
        """检查题目是否已抽取"""
        return question_id in self._drawn_ids

    def reset_drawn(self, bank_name: Optional[str] = None):
        """重置已抽取记录

        Args:
            bank_name: 题库名称，为 None 时重置所有
        """
        if bank_name:
            bank_question_ids = {q.id for q in self._banks.get(bank_name, [])}
            self._drawn_ids -= bank_question_ids
        else:
            self._drawn_ids.clear()

    def get_drawn_ids(self) -> Set[str]:
        """获取已抽取的题目ID集合"""
        return self._drawn_ids.copy()

    def set_drawn_ids(self, drawn_ids: Set[str]):
        """设置已抽取的题目ID集合（用于恢复状态）"""
        self._drawn_ids = set(drawn_ids)

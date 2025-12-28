#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
抽题引擎
"""

import random
from typing import List, Optional
from .question import Question
from .bank import QuestionBank


class DrawEngine:
    """抽题引擎

    提供随机抽题功能，支持去重和批量抽取
    """

    def __init__(self, bank: QuestionBank):
        """初始化抽题引擎

        Args:
            bank: 题库管理器实例
        """
        self._bank = bank

    def draw(self, count: int = 1,
             bank_name: Optional[str] = None,
             no_repeat: bool = True) -> List[Question]:
        """随机抽取题目

        Args:
            count: 抽取数量
            bank_name: 指定题库名称，为 None 时从所有题库抽取
            no_repeat: 是否启用去重（不抽取已抽过的题目）

        Returns:
            抽取的题目列表
        """
        available = self._bank.get_available_questions(bank_name, no_repeat)

        if not available:
            return []

        # 限制抽取数量不超过可用题目数
        count = min(count, len(available))

        # 随机抽取
        drawn = random.sample(available, count)

        # 如果启用去重，标记为已抽取
        if no_repeat:
            self._bank.mark_drawn([q.id for q in drawn])

        return drawn

    def draw_one(self, bank_name: Optional[str] = None,
                 no_repeat: bool = True) -> Optional[Question]:
        """抽取单个题目

        Args:
            bank_name: 指定题库名称
            no_repeat: 是否启用去重

        Returns:
            抽取的题目，如果没有可用题目则返回 None
        """
        result = self.draw(1, bank_name, no_repeat)
        return result[0] if result else None

    def get_available_count(self, bank_name: Optional[str] = None,
                            no_repeat: bool = True) -> int:
        """获取可抽取题目数量

        Args:
            bank_name: 指定题库名称
            no_repeat: 是否排除已抽取的题目

        Returns:
            可抽取题目数量
        """
        return self._bank.get_available_count(bank_name, no_repeat)

    def reset(self, bank_name: Optional[str] = None):
        """重置题池（清除已抽取记录）

        Args:
            bank_name: 指定题库名称，为 None 时重置所有
        """
        self._bank.reset_drawn(bank_name)

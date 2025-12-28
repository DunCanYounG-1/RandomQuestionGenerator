#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
名单管理器
"""

import os
import random
from typing import List, Set, Optional
from dataclasses import dataclass


@dataclass
class Person:
    """人员数据类"""
    name: str

    def __str__(self) -> str:
        return self.name


class RosterManager:
    """名单管理器

    管理人员名单，支持随机抽取
    """

    def __init__(self):
        self._persons: List[Person] = []
        self._roster_name: str = ""
        self._roster_path: str = ""
        self._drawn_names: Set[str] = set()

    def load_roster(self, file_path: str) -> int:
        """加载名单文件

        支持格式：每行一个名字，支持 .txt 和 .md 文件

        Args:
            file_path: 名单文件路径

        Returns:
            加载的人数
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        self._persons = []
        for line in content.split("\n"):
            name = line.strip()
            # 跳过空行和注释行
            if name and not name.startswith("#"):
                self._persons.append(Person(name=name))

        self._roster_name = os.path.splitext(os.path.basename(file_path))[0]
        self._roster_path = file_path
        self._drawn_names.clear()

        return len(self._persons)

    def get_roster_name(self) -> str:
        """获取名单名称"""
        return self._roster_name

    def get_roster_path(self) -> str:
        """获取名单文件路径"""
        return self._roster_path

    def get_persons(self) -> List[Person]:
        """获取所有人员"""
        return self._persons.copy()

    def get_available_persons(self, exclude_drawn: bool = True) -> List[Person]:
        """获取可抽取的人员

        Args:
            exclude_drawn: 是否排除已抽取的人员

        Returns:
            可抽取的人员列表
        """
        if exclude_drawn:
            return [p for p in self._persons if p.name not in self._drawn_names]
        return self._persons.copy()

    def get_count(self) -> int:
        """获取总人数"""
        return len(self._persons)

    def get_available_count(self, exclude_drawn: bool = True) -> int:
        """获取可抽取人数"""
        return len(self.get_available_persons(exclude_drawn))

    def draw(self, count: int = 1, no_repeat: bool = True) -> List[Person]:
        """随机抽取人员

        Args:
            count: 抽取数量
            no_repeat: 是否启用去重

        Returns:
            抽取的人员列表
        """
        available = self.get_available_persons(no_repeat)

        if not available:
            return []

        count = min(count, len(available))
        drawn = random.sample(available, count)

        if no_repeat:
            for p in drawn:
                self._drawn_names.add(p.name)

        return drawn

    def draw_one(self, no_repeat: bool = True) -> Optional[Person]:
        """抽取单个人员"""
        result = self.draw(1, no_repeat)
        return result[0] if result else None

    def reset(self):
        """重置已抽取记录"""
        self._drawn_names.clear()

    def clear(self):
        """清空名单"""
        self._persons = []
        self._roster_name = ""
        self._roster_path = ""
        self._drawn_names.clear()

    def is_loaded(self) -> bool:
        """是否已加载名单"""
        return len(self._persons) > 0

    def get_drawn_names(self) -> Set[str]:
        """获取已抽取的名字集合"""
        return self._drawn_names.copy()

    def set_drawn_names(self, names: Set[str]):
        """设置已抽取的名字集合"""
        self._drawn_names = set(names)

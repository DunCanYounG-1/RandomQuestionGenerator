#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
题目数据模型
"""

import uuid
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Question:
    """题目数据类"""
    title: str                          # 题目标题（第一行）
    content: str                        # 题目要求（后续行）
    bank_name: str = ""                 # 所属题库名称
    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 唯一标识

    def __str__(self) -> str:
        return f"{self.title}\n{self.content}" if self.content else self.title

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "bank_name": self.bank_name
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        """从字典创建"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data["title"],
            content=data.get("content", ""),
            bank_name=data.get("bank_name", "")
        )

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MD 文件解析器
"""

import os
from typing import List
from .question import Question


class MDParser:
    """Markdown 文件解析器

    解析规则:
    - 空行分隔不同题目
    - 每道题的第一行为标题
    - 后续行为题目要求/内容
    """

    @staticmethod
    def parse_file(file_path: str) -> List[Question]:
        """解析 MD 文件

        Args:
            file_path: MD 文件路径

        Returns:
            题目列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        bank_name = os.path.splitext(os.path.basename(file_path))[0]
        return MDParser.parse_content(content, bank_name)

    @staticmethod
    def parse_content(content: str, bank_name: str = "") -> List[Question]:
        """解析 MD 内容

        Args:
            content: MD 文本内容
            bank_name: 题库名称

        Returns:
            题目列表
        """
        questions = []

        # 按空行分割题目块
        blocks = MDParser._split_blocks(content)

        for block in blocks:
            question = MDParser._parse_block(block, bank_name)
            if question:
                questions.append(question)

        return questions

    @staticmethod
    def _split_blocks(content: str) -> List[str]:
        """按空行分割内容为题目块"""
        # 统一换行符
        content = content.replace("\r\n", "\n").replace("\r", "\n")

        # 按连续空行分割
        blocks = []
        current_block = []

        for line in content.split("\n"):
            if line.strip():
                current_block.append(line)
            elif current_block:
                blocks.append("\n".join(current_block))
                current_block = []

        # 处理最后一个块
        if current_block:
            blocks.append("\n".join(current_block))

        return blocks

    @staticmethod
    def _parse_block(block: str, bank_name: str) -> Question | None:
        """解析单个题目块

        Args:
            block: 题目块文本
            bank_name: 题库名称

        Returns:
            Question 对象或 None
        """
        lines = block.strip().split("\n")

        if not lines:
            return None

        # 第一行为标题
        title = lines[0].strip()

        # 移除 Markdown 标题符号 (如 # ## ### 等)
        if title.startswith("#"):
            title = title.lstrip("#").strip()

        if not title:
            return None

        # 后续行为内容
        content = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        return Question(
            title=title,
            content=content,
            bank_name=bank_name
        )

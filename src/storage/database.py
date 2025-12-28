#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库操作模块
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Set, Optional
from dataclasses import dataclass


@dataclass
class DrawRecord:
    """抽题记录"""
    id: int
    question_id: str
    question_title: str
    question_content: str
    bank_name: str
    draw_time: datetime
    person_name: str = ""  # 抽到的人员名字

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "question_id": self.question_id,
            "question_title": self.question_title,
            "question_content": self.question_content,
            "bank_name": self.bank_name,
            "person_name": self.person_name,
            "draw_time": self.draw_time.strftime("%Y-%m-%d %H:%M:%S")
        }


class Database:
    """数据库操作类"""

    def __init__(self, db_path: str = None):
        """初始化数据库

        Args:
            db_path: 数据库文件路径，默认为程序目录下的 data/history.db
        """
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "history.db")

        self._db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()

            # 抽题历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS draw_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id TEXT NOT NULL,
                    question_title TEXT NOT NULL,
                    question_content TEXT,
                    bank_name TEXT NOT NULL,
                    person_name TEXT DEFAULT '',
                    draw_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 检查并添加 person_name 列（兼容旧数据库）
            cursor.execute("PRAGMA table_info(draw_history)")
            columns = [col[1] for col in cursor.fetchall()]
            if "person_name" not in columns:
                cursor.execute("ALTER TABLE draw_history ADD COLUMN person_name TEXT DEFAULT ''")

            # 已抽题目表（去重用）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS drawn_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id TEXT UNIQUE NOT NULL,
                    bank_name TEXT NOT NULL
                )
            """)

            # 已抽人员表（去重用）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS drawn_persons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_name TEXT UNIQUE NOT NULL
                )
            """)

            # 题库记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS question_banks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    file_path TEXT NOT NULL,
                    question_count INTEGER DEFAULT 0,
                    import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 名单记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roster_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    file_path TEXT NOT NULL,
                    person_count INTEGER DEFAULT 0,
                    import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    # ========== 抽题历史操作 ==========

    def add_history(self, question_id: str, question_title: str,
                    question_content: str, bank_name: str,
                    person_name: str = "") -> int:
        """添加抽题记录

        Returns:
            记录ID
        """
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO draw_history
                (question_id, question_title, question_content, bank_name, person_name)
                VALUES (?, ?, ?, ?, ?)
            """, (question_id, question_title, question_content, bank_name, person_name))
            conn.commit()
            return cursor.lastrowid

    def get_history(self, limit: int = 100, offset: int = 0) -> List[DrawRecord]:
        """获取抽题历史

        Args:
            limit: 返回记录数量
            offset: 偏移量

        Returns:
            抽题记录列表
        """
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM draw_history
                ORDER BY draw_time DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

            records = []
            for row in cursor.fetchall():
                records.append(DrawRecord(
                    id=row["id"],
                    question_id=row["question_id"],
                    question_title=row["question_title"],
                    question_content=row["question_content"] or "",
                    bank_name=row["bank_name"],
                    person_name=row["person_name"] if "person_name" in row.keys() else "",
                    draw_time=datetime.strptime(row["draw_time"],
                                                "%Y-%m-%d %H:%M:%S")
                ))
            return records

    def get_history_count(self) -> int:
        """获取历史记录总数"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM draw_history")
            return cursor.fetchone()[0]

    def clear_history(self):
        """清空抽题历史"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM draw_history")
            conn.commit()

    # ========== 已抽题目操作（去重） ==========

    def add_drawn_question(self, question_id: str, bank_name: str):
        """记录已抽题目"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO drawn_questions (question_id, bank_name)
                VALUES (?, ?)
            """, (question_id, bank_name))
            conn.commit()

    def get_drawn_question_ids(self, bank_name: Optional[str] = None) -> Set[str]:
        """获取已抽题目ID集合"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            if bank_name:
                cursor.execute(
                    "SELECT question_id FROM drawn_questions WHERE bank_name = ?",
                    (bank_name,))
            else:
                cursor.execute("SELECT question_id FROM drawn_questions")
            return {row[0] for row in cursor.fetchall()}

    def clear_drawn_questions(self, bank_name: Optional[str] = None):
        """清空已抽题目记录"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            if bank_name:
                cursor.execute(
                    "DELETE FROM drawn_questions WHERE bank_name = ?",
                    (bank_name,))
            else:
                cursor.execute("DELETE FROM drawn_questions")
            conn.commit()

    # ========== 已抽人员操作（去重） ==========

    def add_drawn_person(self, person_name: str):
        """记录已抽人员"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO drawn_persons (person_name)
                VALUES (?)
            """, (person_name,))
            conn.commit()

    def get_drawn_person_names(self) -> Set[str]:
        """获取已抽人员名字集合"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT person_name FROM drawn_persons")
            return {row[0] for row in cursor.fetchall()}

    def clear_drawn_persons(self):
        """清空已抽人员记录"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM drawn_persons")
            conn.commit()

    # ========== 题库记录操作 ==========

    def save_bank_info(self, name: str, file_path: str, question_count: int):
        """保存题库信息"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO question_banks
                (name, file_path, question_count, import_time)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (name, file_path, question_count))
            conn.commit()

    def get_bank_info(self) -> List[Dict]:
        """获取所有题库信息"""
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM question_banks ORDER BY import_time DESC")
            return [dict(row) for row in cursor.fetchall()]

    def remove_bank_info(self, name: str):
        """移除题库信息"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM question_banks WHERE name = ?", (name,))
            conn.commit()

    def clear_all_bank_info(self):
        """清空所有题库信息"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM question_banks")
            conn.commit()

    # ========== 名单记录操作 ==========

    def save_roster_info(self, name: str, file_path: str, person_count: int):
        """保存名单信息"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO roster_info
                (name, file_path, person_count, import_time)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (name, file_path, person_count))
            conn.commit()

    def get_roster_info(self) -> Optional[Dict]:
        """获取名单信息"""
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM roster_info ORDER BY import_time DESC LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else None

    def clear_roster_info(self):
        """清空名单信息"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM roster_info")
            conn.commit()

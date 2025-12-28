#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
随机抽题机 - 程序入口
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.ui import MainWindow


def main():
    """程序主入口"""
    app = QApplication(sys.argv)
    app.setApplicationName("随机抽题机")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Python 源码语法高亮。

用 Qt 自带的 QSyntaxHighlighter 挂在编辑器的 QTextDocument 上，
不改控件本身、也不引入额外依赖（不需要 QScintilla）。
"""
import re

from PySide6 import QtCore, QtGui, QtWidgets


class PythonHighlighter(QtGui.QSyntaxHighlighter):
    """关键字 / 字符串 / 注释 / 数字 / 装饰器 / 函数名的基础高亮。"""

    KEYWORDS = (
        "and", "as", "assert", "async", "await", "break", "class", "continue",
        "def", "del", "elif", "else", "except", "finally", "for", "from",
        "global", "if", "import", "in", "is", "lambda", "nonlocal", "not",
        "or", "pass", "raise", "return", "try", "while", "with", "yield",
        "True", "False", "None",
    )

    def __init__(self, document):
        super(PythonHighlighter, self).__init__(document)

        fmt_keyword = QtGui.QTextCharFormat()
        fmt_keyword.setForeground(QtGui.QColor("#0000B0"))
        fmt_keyword.setFontWeight(QtGui.QFont.Bold)

        fmt_builtin = QtGui.QTextCharFormat()
        fmt_builtin.setForeground(QtGui.QColor("#795E26"))

        fmt_string = QtGui.QTextCharFormat()
        fmt_string.setForeground(QtGui.QColor("#067D17"))

        fmt_comment = QtGui.QTextCharFormat()
        fmt_comment.setForeground(QtGui.QColor("#7A7A7A"))
        fmt_comment.setFontItalic(True)

        fmt_number = QtGui.QTextCharFormat()
        fmt_number.setForeground(QtGui.QColor("#1750EB"))

        fmt_decorator = QtGui.QTextCharFormat()
        fmt_decorator.setForeground(QtGui.QColor("#9B2393"))

        fmt_func = QtGui.QTextCharFormat()
        fmt_func.setForeground(QtGui.QColor("#8250DF"))

        self._rules = []

        for word in self.KEYWORDS:
            self._rules.append((QtCore.QRegularExpression(r"\b%s\b" % word), fmt_keyword))

        # 数值：整数、小数、科学计数
        self._rules.append((QtCore.QRegularExpression(
            r"\b\d+(\.\d*)?([eE][+-]?\d+)?\b"), fmt_number))

        # 装饰器 @param / @activate
        self._rules.append((QtCore.QRegularExpression(r"@[A-Za-z_]\w*"), fmt_decorator))

        # 函数/类名
        self._rules.append((QtCore.QRegularExpression(
            r"\b(?:def|class)\s+([A-Za-z_]\w*)"), fmt_func))

        # 字符串（单/双引号，含转义；单行匹配，够用且不会跨行漏光）
        self._rules.append((QtCore.QRegularExpression(
            r"'(\\.|[^'\\])*'|\"(\\.|[^\"\\])*\""), fmt_string))

        # 注释 # ... 到行尾
        self._rules.append((QtCore.QRegularExpression(r"#[^\n]*"), fmt_comment))

    def highlightBlock(self, text):
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                # 有捕获组时只高亮组内（函数名），否则高亮整体
                if m.lastCapturedIndex() >= 1 and pattern.pattern().startswith(r"\b(?:def|class)"):
                    start, length = m.capturedStart(1), m.capturedLength(1)
                else:
                    start, length = m.capturedStart(0), m.capturedLength(0)
                if start >= 0 and length > 0:
                    self.setFormat(start, length, fmt)
        self.setCurrentBlockState(0)
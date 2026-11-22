# -*- coding: utf-8 -*-
"""AutoCAD Plant 3D 无人值守自动化测试入口快捷调用。"""
import os
import sys

# 路由至 autocad_runner 功能包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.autocad_runner.unattended_runner import main

if __name__ == "__main__":
    main()

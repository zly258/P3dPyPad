# -*- coding: utf-8 -*-
"""`python -m plant3d_occ` 入口：等价于 python plant3d_occ/main.py。

真实逻辑在 main.py 里，这里只做转发，保证两种启动方式行为一致。
"""

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from plant3d_occ.main import main

if __name__ == "__main__":
    main()

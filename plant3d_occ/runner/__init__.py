# -*- coding: utf-8 -*-
from .sandbox import run_script_in_sandbox, build_mock_environment, execute_script_source

inject_mock_environment = build_mock_environment

__all__ = [
    "run_script_in_sandbox",
    "build_mock_environment",
    "inject_mock_environment",
    "execute_script_source",
]

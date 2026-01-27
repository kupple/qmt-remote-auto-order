#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试platform模块是否可用
"""

import sys

def test_platform():
    """测试platform模块"""
    try:
        print("Testing platform module import...")
        import platform
        print("SUCCESS: platform imported")

        print("Testing platform functions...")
        version = platform.python_version()
        print("Python version: {}".format(version))

        system = platform.system()
        print("System: {}".format(system))

        return True

    except ImportError as e:
        print("IMPORT ERROR: {}".format(e))
        return False
    except Exception as e:
        print("OTHER ERROR: {}".format(e))
        return False

def main():
    print("Platform Module Test")
    print("Frozen: {}".format(getattr(sys, 'frozen', False)))
    print("-" * 40)

    success = test_platform()

    print("-" * 40)
    if success:
        print("RESULT: SUCCESS - platform module works")
    else:
        print("RESULT: FAILED - platform module failed")

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()

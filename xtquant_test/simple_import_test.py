#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简单的xtquant导入测试
"""

import sys
import os

def test_xtquant_import():
    """测试xtquant包导入"""
    try:
        print("Testing xtquant import...")

        # 添加路径到sys.path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
            print("Added to path: {}".format(parent_dir))

        print("Importing xtdata...")
        from pyapp.pkg.xtquant import xtdata
        print("SUCCESS: xtdata imported")

        print("Importing xtconstant...")
        from pyapp.pkg.xtquant import xtconstant
        print("SUCCESS: xtconstant imported")

        print("Testing xtdata version...")
        print("xtdata imported from: {}".format(xtdata.__file__ if hasattr(xtdata, '__file__') else 'unknown'))

        return True

    except ImportError as e:
        print("IMPORT ERROR: {}".format(e))
        return False
    except Exception as e:
        print("OTHER ERROR: {}".format(e))
        return False

def main():
    print("Simple xtquant Import Test")
    print("Python: {}".format(sys.version.split()[0]))
    print("Frozen: {}".format(getattr(sys, 'frozen', False)))
    print("Current dir: {}".format(os.getcwd()))
    print("Script dir: {}".format(os.path.dirname(os.path.abspath(__file__))))
    print("-" * 50)

    success = test_xtquant_import()

    print("-" * 50)
    if success:
        print("RESULT: SUCCESS - xtquant can be imported")
    else:
        print("RESULT: FAILED - xtquant import failed")

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()

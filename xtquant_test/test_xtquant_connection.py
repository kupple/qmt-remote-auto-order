#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试xtquant连接的程序
"""

import socket
import time
import sys

def test_basic_connection(host='127.0.0.1', port=58610):
    """测试基本的socket连接"""
    print("=== 基本Socket连接测试 ===")
    print("测试连接到 {}:{}".format(host, port))

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        start_time = time.time()
        result = sock.connect_ex((host, port))
        end_time = time.time()

        if result == 0:
            print("✅ Socket连接成功!")
            print("   响应时间: {:.3f}秒".format(end_time - start_time))
            sock.close()
            return True
        else:
            print("❌ Socket连接失败, 错误代码: {}".format(result))
            sock.close()
            return False

    except Exception as e:
        print("❌ Socket连接异常: {}".format(e))
        return False

def test_xtquant_import():
    """测试xtquant模块导入"""
    print("\n=== xtquant模块导入测试 ===")

    try:
        print("正在导入xtdata...")
        from pyapp.pkg.xtquant import xtdata
        print("✅ xtdata 导入成功")

        print("正在导入xtconn...")
        from pyapp.pkg.xtquant import xtconn
        print("✅ xtconn 导入成功")

        print("正在导入xtdatacenter...")
        from pyapp.pkg.xtquant import xtdatacenter
        print("✅ xtdatacenter 导入成功")

        return True

    except ImportError as e:
        print("❌ 模块导入失败: {}".format(e))
        return False
    except Exception as e:
        print("❌ 模块导入异常: {}".format(e))
        return False

def test_xtdata_connect():
    """测试xtdata连接"""
    print("\n=== xtdata连接测试 ===")

    try:
        from pyapp.pkg.xtquant import xtdata

        print("正在调用 xtdata.connect()...")
        client = xtdata.connect(ip='127.0.0.1', port=58610)
        print("✅ xtdata.connect() 成功")
        return True

    except Exception as e:
        print("❌ xtdata.connect() 失败: {}".format(e))
        return False

def test_xtdata_get_full_tick():
    """测试xtdata.get_full_tick"""
    print("\n=== xtdata.get_full_tick 测试 ===")

    try:
        from pyapp.pkg.xtquant import xtdata

        # 先尝试连接
        print("先连接xtdata...")
        client = xtdata.connect(ip='127.0.0.1', port=58610)

        # 测试获取数据
        print("调用 get_full_tick(['600031.SH'])...")
        result = xtdata.get_full_tick(['600031.SH'])
        print("✅ get_full_tick 成功, 返回数据条数: {}".format(len(result) if result else 0))
        return True

    except Exception as e:
        print("❌ get_full_tick 失败: {}".format(e))
        return False

def main():
    print("xtquant连接完整测试程序")
    print("Python版本: {}".format(sys.version))
    print("运行环境: {}".format('打包后' if getattr(sys, 'frozen', False) else '开发环境'))
    print("=" * 60)

    # 1. 基本连接测试
    socket_ok = test_basic_connection()

    # 2. 模块导入测试
    import_ok = test_xtquant_import()

    # 3. xtdata连接测试
    if import_ok:
        connect_ok = test_xtdata_connect()

        # 4. 数据获取测试
        if connect_ok:
            data_ok = test_xtdata_get_full_tick()
        else:
            print("\n=== 数据获取测试 ===")
            print("❌ 跳过数据获取测试 (连接失败)")
            data_ok = False
    else:
        connect_ok = False
        data_ok = False

    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print("  Socket连接: {}".format("✅" if socket_ok else "❌"))
    print("  模块导入: {}".format("✅" if import_ok else "❌"))
    print("  xtdata连接: {}".format("✅" if connect_ok else "❌"))
    print("  数据获取: {}".format("✅" if data_ok else "❌"))

    if socket_ok and not connect_ok:
        print("\n🔍 诊断: Socket能连接但xtdata不能,可能是:")
        print("   1. QMT服务版本不匹配")
        print("   2. 动态库版本不匹配")
        print("   3. PyInstaller打包问题")
    elif not socket_ok:
        print("\n🔍 诊断: 基本连接失败, 请检查:")
        print("   1. QMT是否启动")
        print("   2. 端口58610是否被监听")
        print("   3. 防火墙设置")

if __name__ == "__main__":
    main()

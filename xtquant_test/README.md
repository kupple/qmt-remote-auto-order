# xtquant连接问题诊断测试

## 📁 文件说明

```
xtquant_test/
├── simple_import_test.py       # ⭐ 简单导入测试 (推荐先用这个)
├── simple_import_test.spec     # 简单导入测试的spec文件
├── build_simple_test.bat       # 简单导入测试的打包脚本
├── rebuild_and_test.bat       # 🔄 一键重新打包和测试 (推荐)
├── test_platform.py           # 🔧 platform模块测试 (调试用)
├── test_platform.spec         # platform模块测试的spec文件
├── test_xtquant_connection.py  # 完整功能测试程序
├── test_xtquant_spec.py        # 完整测试的PyInstaller配置
├── run_test_standalone.py      # 独立Python测试脚本
└── README.md                   # 本说明文件
```

## 🎯 问题诊断

这个测试套件用于诊断为什么 `sync_position_action_by_task_id` 在开发环境中正常但打包后会报错：
```
无法连接xtquant服务，请检查QMT-投研版或QMT-极简版是否开启
```

## 🚀 快速开始

### 🎯 推荐方式：一键测试 (已修复标准库问题)
**双击运行 `rebuild_and_test.bat`** ⭐
- 自动清理旧文件
- 重新打包（包含所有修复）
- 自动运行测试
- 显示完整结果

### 手动测试步骤
**步骤1: 开发环境测试**
双击运行 `simple_import_test.py`
- 测试xtquant包导入
- 快速判断能否引用包
- 开发环境验证

**步骤2: 打包测试**
双击运行 `build_simple_test.bat`
- 打包简单导入测试
- 测试打包后能否正常工作

### 步骤2: 打包测试
**双击运行 `build_simple_test.bat`**
- 自动打包简单导入测试
- 测试打包后能否正常工作

### 步骤3: 完整功能测试
**双击运行 `run_test_standalone.py`** 或 `test_xtquant_connection.py`
- 测试完整的xtquant功能
- 检查QMT连接状态

### 打包测试

**双击运行 `build_simple_test.bat`**，它会：
- 检查PyInstaller是否安装
- 清理旧的build文件
- 使用PyInstaller打包测试程序
- 运行打包后的程序测试导入

## 📊 测试结果分析

### ✅ 全部通过
```
Socket连接: ✅
模块导入: ✅
xtdata连接: ✅
数据获取: ✅
```
**诊断**: xtquant配置正确，问题在应用的其他部分

### ❌ Socket连接失败
```
Socket连接: ❌
```
**诊断**: QMT未启动或防火墙阻止端口58610

**解决**:
```cmd
# 检查端口
netstat -ano | findstr :58610

# 添加防火墙规则
netsh advfirewall firewall add rule name="QMT Data Service" dir=in action=allow protocol=TCP localport=58610
```

### ❌ 模块导入失败
```
模块导入: ❌
```
**诊断**: PyInstaller没有正确包含xtquant模块

**解决**: 检查spec文件中的hiddenimports配置

### ❌ xtdata连接失败但Socket成功
```
Socket连接: ✅
xtdata连接: ❌
```
**诊断**: 这就是打包问题的核心！

**可能原因**:
1. 动态库(.pyd/.dll)版本不匹配
2. PyInstaller打包配置问题
3. xtquant库与Python版本不兼容

## 🔧 手动测试步骤

如果批处理文件不工作，可以手动执行：

```cmd
# 1. 检查QMT状态
netstat -ano | findstr :58610

# 2. 运行开发版本
python test_xtquant_connection.py

# 3. 打包程序
pyinstaller test_xtquant_spec.py

# 4. 运行打包版本
cd build_xtquant_test
test_xtquant_connection.exe
```

## 📋 诊断输出示例

### 正常情况
```
xtquant连接完整测试程序
Python版本: 3.9.12
运行环境: 开发环境
============================================================

=== 基本Socket连接测试 ===
测试连接到 127.0.0.1:58610
✅ Socket连接成功!
   响应时间: 0.001秒

=== xtquant模块导入测试 ===
✅ xtdata 导入成功
✅ xtconn 导入成功
✅ xtdatacenter 导入成功

=== xtdata连接测试 ===
✅ xtdata.connect() 成功

=== xtdata.get_full_tick 测试 ===
✅ get_full_tick 成功, 返回数据条数: 1
```

### 打包后问题
```
运行环境: 打包后
=== xtquant模块导入测试 ===
❌ 模块导入失败: No module named 'pyapp.pkg.xtquant'
```

## 🆘 常见问题

### Q: 提示"权限被拒绝"
A: 以管理员身份运行脚本

### Q: PyInstaller安装失败
A: 使用国内源安装：
```cmd
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyinstaller
```

### Q: Python命令不可用
A: 使用 `run_test_standalone.py`，它会自动检测环境

### Q: 打包后导入失败
A: 检查spec文件中的hiddenimports和datas配置

### Q: 遇到 "No module named 'platform'" 或其他标准库错误
A: 这是PyInstaller没有包含标准库模块的问题。spec文件已修复，重新打包：
```cmd
cd xtquant_test

# 重新打包简单测试
pyinstaller simple_import_test.spec

# 运行打包后的程序
cd build_simple_test
simple_import_test.exe
```

### Q: 如果仍有其他标准库模块错误
A: 在spec文件的hiddenimports中继续添加缺失的模块

### Q: 需要完整测试结果
A: 运行 `run_test_standalone.py` 获取详细诊断信息

### Q: 所有脚本都无法运行
A: 手动执行：
```cmd
cd xtquant_test
python test_xtquant_connection.py
```

## 📞 获取帮助

请运行测试并分享完整的输出信息，包括：
- 开发环境测试结果
- 打包环境测试结果
- 错误信息
- 系统信息

这样我们就能准确定位问题并提供解决方案！

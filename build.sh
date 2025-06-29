#!/bin/bash

# 清理数据库
python clean_db.py

# 打包程序
pyinstaller --clean --noconfirm --onefile --windowed main.py

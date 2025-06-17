#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

pyappDir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pyappDir)

from config.config import Config

appName = Config.appName    # 应用名称
appVersion = Config.appVersion    # 应用版本号

dmgName = f'{appName}-{appVersion}_macOS'


# 获取配置文件内容
def getJson():
    return """
filename = '""" + dmgName + """'
volume_name = '""" + dmgName + """.dmg'
format = 'UDBZ'
files = ['""" + pyappDir + """/../build/""" + appName + """.app', '""" + pyappDir + """/package/dmg/潘高的小站.webloc']
symlinks = {'Applications': '/Applications'}
icon_locations = {
    '""" + appName + """.app': (160, 120),
    'Applications': (430, 120),
    '潘高的小站.webloc': (450, 243)
}
window_rect = ((200, 200), (590, 416))
icon_size = 60
text_size = 12
badge_icon = '""" + pyappDir + """/icon/logo.icns'
background = '""" + pyappDir + """/package/dmg/bg.png'
"""


# 生成配置文件
jsonDir = os.path.dirname(__file__)
with open(os.path.join(jsonDir, 'dmg.py'), 'w+', encoding='utf-8') as f:
    f.write(getJson())

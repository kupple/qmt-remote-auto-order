# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE

# 存放最终打包成app的相对路径
buildPath = 'build_simple_test'

# 存放打包成app的中间文件的相对路径
cachePath = os.path.join(buildPath, 'cache')

# 添加动态库
binaries = [
    ('../pyapp/pkg/xtquant/libeay32.dll', './'),
    ('../pyapp/pkg/xtquant/log4cxx.dll', './'),
    ('../pyapp/pkg/xtquant/msvcp140.dll', './'),
    ('../pyapp/pkg/xtquant/vcruntime140.dll', './'),
    ('../pyapp/pkg/xtquant/ssleay32.dll', './'),
    ('../pyapp/pkg/xtquant/datacenter.cp39-win_amd64.pyd', './'),
    ('../pyapp/pkg/xtquant/xtpythonclient.cp39-win_amd64.pyd', './'),
]

# 添加数据文件
datas = [
    ('../pyapp/pkg', 'pyapp/pkg'),
]

# 隐藏导入
hiddenimports = [
    'pyapp.pkg.xtquant.xtdata',
    'pyapp.pkg.xtquant.xtconstant',
    # xtquant依赖的标准库模块
    'platform',
    'uuid',
    'os',
    'time',
    'traceback',
    'calendar',
    'datetime',
    'copy',
    're',
]

a = Analysis(
    ['simple_import_test.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='simple_import_test',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

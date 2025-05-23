
# -*- mode: python ; coding: utf-8 -*-

import os

import PyInstaller.config

# 存放最终打包成app的相对路径
buildPath = 'build'
PyInstaller.config.CONF['distpath'] = buildPath

# 存放打包成app的中间文件的相对路径
cachePath = os.path.join(buildPath, 'cache')
if not os.path.exists(cachePath):
    os.makedirs(cachePath)
PyInstaller.config.CONF['workpath'] = cachePath

# icon相对路径
icoPath = os.path.join('..', 'icon', 'logo.icns')

# 项目名称
appName = 'qmt_auto_order'

# 版本号
version = 'V0.0.1'


a = Analysis(['../../main.py'],
            pathex=[],
            binaries=[],
            datas=[('../../gui/dist', 'web'), ('../../static', 'static'), ('../../pyapp/icon', 'pyapp/icon')],
            hiddenimports=[],
            hookspath=[],
            hooksconfig={},
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            noarchive=False)
pyz = PYZ(a.pure, a.zipped_data)


exe = EXE(pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=appName,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        target_arch=None,  # x86_64, arm64, universal2
        codesign_identity=None,
        entitlements_file=None)
coll = COLLECT(exe,
                a.binaries,
                a.zipfiles,
                a.datas,
                strip=False,
                upx=True,
                upx_exclude=[],
                name=appName)
app = BUNDLE(coll,
            name=appName+'.app',
            icon=icoPath,
            version=version,
            bundle_identifier=None)


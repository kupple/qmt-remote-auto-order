import os
import sys
import win32com.client  # 需要安装pywin32库: pip install pywin32

def create_shortcut(exe_path):
    """为指定的exe文件在同级目录创建快捷方式"""
    try:
        # 创建的快捷方式名称
        exe_dir = os.path.dirname(exe_path)
        shortcut_name = f"autoxiadan.lnk"
        shortcut_path = os.path.join(exe_dir, shortcut_name)
        
        # 检查快捷方式是否已存在
        if os.path.exists(shortcut_path):
            print(f"快捷方式已存在：{shortcut_path}")
            return True

        # 检查文件是否存在
        if not os.path.exists(exe_path):
            print(f"错误：文件不存在 - {exe_path}")
            return False
        
        # 检查是否为exe文件
        if not exe_path.lower().endswith('.exe'):
            print(f"错误：不是有效的exe文件 - {exe_path}")
            return False
        
        # 创建快捷方式对象
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        
        # 设置快捷方式属性
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = exe_dir  # 设置工作目录为exe所在目录
        shortcut.Description = f"快捷方式：{os.path.basename(exe_path)}"
        
        # 保存快捷方式
        shortcut.Save()
        
        print(f"成功创建快捷方式：{shortcut_path}")
        return True
        
    except Exception as e:
        print(f"错误：创建快捷方式失败 - {e}")
        return False

if __name__ == "__main__":

    exe_path = r"D:\同花顺\同花顺\xiadan.exe"
    create_shortcut(exe_path)    
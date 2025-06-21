import win32gui
import win32con

def control_ths_window(show: bool):
    """
    控制同花顺交易软件窗口的显示或隐藏
    :param show: True 显示窗口，False 隐藏窗口
    """
    # 获取窗口句柄
    hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if hwnd:
        if show:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # 恢复窗口
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)  # 显示窗口
            win32gui.SetForegroundWindow(hwnd)  # 将窗口置于最前面
            # 设置窗口大小和位置
            win32gui.MoveWindow(hwnd, 0, 0, 1024, 768, True)  # 设置窗口为1024x768
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)  # 隐藏窗口
            print("窗口已隐藏")
    else:
        print("未找到窗口，请确认同花顺交易软件是否已打开")

if __name__ == "__main__":
    # 显示窗口
    control_ths_window(True)

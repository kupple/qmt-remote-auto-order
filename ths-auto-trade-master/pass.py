import win32gui
import win32con
import win32api
import time

def find_window_by_control_id(target_control_id):
    """通过 ControlID 查找包含特定控件的窗口"""
    result = []
    
    def enum_windows_callback(hwnd, param):
        # 跳过不可见窗口
        if not win32gui.IsWindowVisible(hwnd):
            return True
            
        # 检查窗口是否包含目标 ControlID
        has_control = False
        
        def enum_child_callback(child_hwnd, param):
            nonlocal has_control
            control_id = win32gui.GetDlgCtrlID(child_hwnd)
            if control_id == target_control_id:
                has_control = True
                # 记录找到的控件信息
                class_name = win32gui.GetClassName(child_hwnd)
                text = win32gui.GetWindowText(child_hwnd)
                param.append((hwnd, child_hwnd, class_name, text))
                return False  # 停止枚举子控件
            return True
            
        # 枚举当前窗口的所有子控件
        win32gui.EnumChildWindows(hwnd, enum_child_callback, param)
        
        if has_control:
            result.append(hwnd)
            
        return True
        
    # 枚举所有顶级窗口
    win32gui.EnumWindows(enum_windows_callback, [])
    
    return result[0] if result else 0

def get_window_info(hwnd):
    """获取窗口的基本信息"""
    if not hwnd:
        return {}
        
    title = win32gui.GetWindowText(hwnd)
    class_name = win32gui.GetClassName(hwnd)
    rect = win32gui.GetWindowRect(hwnd)
    
    return {
        "hwnd": hwnd,
        "title": title,
        "class_name": class_name,
        "position": (rect[0], rect[1]),
        "size": (rect[2] - rect[0], rect[3] - rect[1])
    }

def find_control_by_id(parent_hwnd, control_id):
    """在指定窗口中查找特定 ControlID 的控件"""
    result = None
    
    def enum_child_callback(child_hwnd, param):
        nonlocal result
        if win32gui.GetDlgCtrlID(child_hwnd) == control_id:
            result = child_hwnd
            return False  # 停止枚举
        return True
        
    win32gui.EnumChildWindows(parent_hwnd, enum_child_callback, None)
    return result

def send_key(key_code):
    """发送单个按键"""
    win32api.keybd_event(key_code, 0, 0, 0)  # 按下
    time.sleep(0.05)
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
    time.sleep(0.1)  # 给界面响应时间

def type_string(text):
    """模拟输入字符串"""
    for char in text:
        # 普通字符直接发送
        win32api.keybd_event(ord(char), 0, 0, 0)
        time.sleep(0.03)  # 添加微小延迟
        win32api.keybd_event(ord(char), 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)

def set_text_to_control(control_hwnd, text):
    """向控件发送文本"""
    if control_hwnd:
        win32gui.SendMessage(control_hwnd, win32con.WM_SETTEXT, 0, text)
        return True
    return False
if __name__ == "__main__":
    # 设置目标 ControlID
    MAIN_WINDOW_CONTROL_ID = 0x92E    # 主窗口的 ControlID
    INPUT_BOX_CONTROL_ID = 0x3E9      # 输入框的 ControlID
    PASSWORD_BOX_CONTROL_ID = 0x3F4   # 密码框的 ControlID
    
    # 查找主窗口
    main_hwnd = find_window_by_control_id(MAIN_WINDOW_CONTROL_ID)
    
    if main_hwnd:
        # 获取窗口信息
        info = get_window_info(main_hwnd)
        print(f"找到主窗口:")
        print(f"  句柄: {info['hwnd']}")
        print(f"  标题: {info['title']}")
        print(f"  类名: {info['class_name']}")
        
        # 激活窗口
        win32gui.SetForegroundWindow(main_hwnd)
        time.sleep(0.5)
        
        # 查找输入框
        input_box_hwnd = find_control_by_id(main_hwnd, INPUT_BOX_CONTROL_ID)
        
        if input_box_hwnd:
            print(f"找到输入框 (ControlID: 0x{INPUT_BOX_CONTROL_ID:X})")
            
            # 使用模拟键盘输入来确保输入框获得焦点
            # 先激活窗口
            win32gui.ShowWindow(main_hwnd, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(main_hwnd)
            time.sleep(0.2)
            # 使用Tab键切换到输入框
            win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)
            win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.2)
            
            # 清空输入框内容
            win32gui.SendMessage(input_box_hwnd, win32con.WM_SETTEXT, 0, "")
            time.sleep(0.1)  # 等待内容清空完成
            
            # 使用模拟键盘输入来确保输入框获得焦点
            win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            
            # 设置窗口为不可激活状态
            win32gui.SetWindowLong(main_hwnd, win32con.GWL_EXSTYLE,
                                  win32gui.GetWindowLong(main_hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_NOACTIVATE)
            win32gui.SendMessage(input_box_hwnd, win32con.WM_SETTEXT, 0, "")
            time.sleep(0.1)  # 等待内容清空完成
            
            # 确保输入框获得焦点
            # win32gui.SetFocus(input_box_hwnd)
            time.sleep(0.3)

            if set_text_to_control(input_box_hwnd, "121600012698"):
                print(f"成功向输入框输入文本: {INPUT_BOX_CONTROL_ID}")
            else:
                print("输入文本失败")  
            
            # 输入内容
            # type_string("121600012698")
            # print("输入框内容已填充")
            
            # 使用Tab键切换到密码框
            print("按Tab键切换到密码框")
            send_key(win32con.VK_TAB)
            
            # 输入密码
            print("开始输入密码")
            type_string("520803")
            print("密码输入完成")
            
            time.sleep(0.3)

        else:
            print(f"未找到输入框 (ControlID: 0x{INPUT_BOX_CONTROL_ID:X})")
    else:
        print(f"未找到主窗口 (ControlID: 0x{MAIN_WINDOW_CONTROL_ID:X})")
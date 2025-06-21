import win32gui
import win32con
import win32api
import ctypes
import time
import win32ui

# 定义一些常用的 Windows 消息常量
WM_GETTEXT = 0x000D
WM_GETTEXTA = 0x000D  # ANSI 版本
WM_GETTEXTW = 0x000C  # Unicode 版本
WM_USER = 0x0400
WM_PAINT = 0x000F  # 绘制消息
WM_GETTEXTLENGTH = 0x000E  # 获取文本长度

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

def start_ths_auto():
    # 设置目标 ControlID
    MAIN_WINDOW_CONTROL_ID = 0x92E    # 主窗口的 ControlID
    INPUT_BOX_CONTROL_ID = 0x3E9      # 输入框的 ControlID
    PASSWORD_BOX_CONTROL_ID = 0x3F4   # 密码框的 ControlID
    BUTTON_CONTROL_ID = 0x3EE
    # 查找主窗口
    main_hwnd = find_window_by_control_id(MAIN_WINDOW_CONTROL_ID)

    if main_hwnd:
        # 获取窗口信息
        info = get_window_info(main_hwnd)
        # 激活窗口
        win32gui.SetForegroundWindow(main_hwnd)
        time.sleep(0.5)
        
        # 查找输入框
        input_box_hwnd = find_control_by_id(main_hwnd, INPUT_BOX_CONTROL_ID)
        
        if input_box_hwnd:
            print(f"找到输入框 (ControlID: 0x{INPUT_BOX_CONTROL_ID:X})")
            
            # 确保输入框获得焦点
            win32gui.SendMessage(input_box_hwnd, win32con.WM_SETFOCUS, 0, 0)
            time.sleep(0.1)
            
            # 使用 SendMessage 获取输入框内容
            text_length = win32gui.SendMessage(input_box_hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            print(text_length)
            if text_length > 0:
                import ctypes
                buffer = ctypes.create_unicode_buffer(text_length + 1)
                win32gui.SendMessage(input_box_hwnd, win32con.WM_GETTEXT, text_length + 1, buffer)
                text = buffer.value
                print(f"输入框内容: {text}")
                
                # 如果输入框有内容则发送 Tab 键
                if text.strip():
                    type_string("520803")
                    button_hwnd = find_control_by_id(main_hwnd, BUTTON_CONTROL_ID)
                    if button_hwnd:
                        print(f"找到按钮 (ControlID: 0x{BUTTON_CONTROL_ID:X})")
                        # 使用 PostMessage 替代 SendMessage
                        win32gui.PostMessage(button_hwnd, win32con.WM_LBUTTONDOWN, 0, 0)
                        time.sleep(0.1)
                        win32gui.PostMessage(button_hwnd, win32con.WM_LBUTTONUP, 0, 0)
                        time.sleep(1)  # 等待按钮点击后的响应
                        
                        # 使用 FindWindow 查找 PhonTipWnd 组件
                        phon_tip_hwnd = win32gui.FindWindow("PhonTipWnd", None)
                        if phon_tip_hwnd:
                            print(f"找到 PhonTipWnd 组件")
                            # 获取组件的详细信息
                            print(f"PhonTipWnd 句柄: {phon_tip_hwnd}")
                            print(f"PhonTipWnd 类名: {win32gui.GetClassName(phon_tip_hwnd)}")
                            print(f"PhonTipWnd 标题: {win32gui.GetWindowText(phon_tip_hwnd)}")
                            
                            # 获取组件的位置和大小
                            rect = win32gui.GetWindowRect(phon_tip_hwnd)
                            print(f"PhonTipWnd 位置: ({rect[0]}, {rect[1]})")
                            print(f"PhonTipWnd 大小: ({rect[2]-rect[0]}, {rect[3]-rect[1]})")
                            
                            # 尝试多种方式获取组件内容
                            print("尝试获取 PhonTipWnd 内容:")
                            
                            # 方法1: 使用 win32ui 获取窗口对象
                            try:
                                window = win32ui.CreateWindowFromHandle(phon_tip_hwnd)
                                text = window.GetWindowText()
                                print(f"win32ui 窗口文本: {text}")
                            except Exception as e:
                                print(f"win32ui 获取失败: {e}")
                            
                            # 方法2: 尝试获取窗口的客户区域
                            rect = win32gui.GetClientRect(phon_tip_hwnd)
                            print(f"客户区域: ({rect[0]}, {rect[1]}, {rect[2]}, {rect[3]})")
                            
                            # 方法3: 尝试发送 WM_PAINT 消息
                            win32gui.SendMessage(phon_tip_hwnd, WM_PAINT, 0, 0)
                            
                            # 方法4: 尝试获取窗口的 DC (设备上下文)
                            try:
                                hdc = win32gui.GetWindowDC(phon_tip_hwnd)
                                print(f"获取到 DC: {hdc}")
                            except Exception as e:
                                print(f"获取 DC 失败: {e}")
                            
                            # 方法5: 尝试获取窗口的子窗口
                            print("尝试获取子窗口:")
                            def print_child_info(hwnd, param):
                                class_name = win32gui.GetClassName(hwnd)
                                text = win32gui.GetWindowText(hwnd)
                                rect = win32gui.GetWindowRect(hwnd)
                                print(f"  子窗口 - 类名: {class_name} 标题: {text} 位置: {rect}")
                                return True
                            
                            win32gui.EnumChildWindows(phon_tip_hwnd, print_child_info, None)
                            
                            # 方法6: 尝试获取窗口的属性
                            style = win32gui.GetWindowLong(phon_tip_hwnd, win32con.GWL_STYLE)
                            print(f"窗口样式: {style:08X}")
                            ex_style = win32gui.GetWindowLong(phon_tip_hwnd, win32con.GWL_EXSTYLE)
                            print(f"扩展样式: {ex_style:08X}")
                            
                            # 方法7: 尝试获取窗口的父窗口
                            parent = win32gui.GetParent(phon_tip_hwnd)
                            print(f"父窗口句柄: {parent}")
                            if parent:
                                print(f"父窗口类名: {win32gui.GetClassName(parent)}")
                                print(f"父窗口标题: {win32gui.GetWindowText(parent)}")
                            
                            # 获取组件的位置和大小
                            rect = win32gui.GetWindowRect(phon_tip_hwnd)
                            x1, y1, x2, y2 = rect
                            width = x2 - x1
                            height = y2 - y1
                            print(width)
                            print(height)
                            # 计算右下角点击位置（留出一点边距）
                            click_x = x2 - 50  # 距离右边10像素
                            click_y = y2 - 40  # 距离下边10像素
                            
                            print(f"准备在 ({click_x}, {click_y}) 点击右下角")
                            
                            # 使用 mouse_event 模拟鼠标点击
                            import win32api
                            
                            # 确保主窗口获得焦点
                            win32gui.SetForegroundWindow(main_hwnd)
                            time.sleep(0.1)
                            
                            # 移动鼠标到目标位置
                            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE,
                                                int(click_x * 65535 / win32api.GetSystemMetrics(0)),
                                                int(click_y * 65535 / win32api.GetSystemMetrics(1)))
                            time.sleep(0.1)
                            
                            # 左键按下
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                            time.sleep(0.1)
                            
                            # 左键松开
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                            print("已点击")
                            
                            # 等待点击生效
                            time.sleep(0.5)
                            
                            # 等待一段时间让点击生效
                            time.sleep(0.5)
                        else:
                            print("未找到 PhonTipWnd 组件")
                        time.sleep(0.5)
        

                    
                else:
                    # 如果输入框为空，直接发送 DELETE 键
                    win32gui.SendMessage(input_box_hwnd, win32con.WM_SETFOCUS, 0, 0)
                    time.sleep(0.1)
                    win32api.keybd_event(win32con.VK_DELETE, 0, 0, 0)  # 按下 DELETE 键
                    time.sleep(0.1)
                    win32api.keybd_event(win32con.VK_DELETE, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放 DELETE 键
                    time.sleep(0.1)
            else:
                print("输入框为空")
                # 如果输入框为空，直接发送 DELETE 键
                win32gui.SendMessage(input_box_hwnd, win32con.WM_SETFOCUS, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_DELETE, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_DELETE, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)
            
            # 如果输入框有内容才发送 DELETE 键
            if text.strip():
                # 确保输入框获得焦点
                win32gui.SendMessage(input_box_hwnd, win32con.WM_SETFOCUS, 0, 0)
                time.sleep(0.1)
                # 发送 DELETE 键
                win32api.keybd_event(win32con.VK_DELETE, 0, 0, 0)  # 按下 DELETE 键
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_DELETE, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放 DELETE 键
                time.sleep(0.1)

            # 确保输入框获得焦点
            win32gui.SendMessage(input_box_hwnd, win32con.WM_SETFOCUS, 0, 0)
            time.sleep(0.1)
            # 发送 DELETE 键
            win32api.keybd_event(win32con.VK_DELETE, 0, 0, 0)  # 按下 DELETE 键
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_DELETE, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放 DELETE 键
            time.sleep(0.1)
            
        else:
            print(f"未找到输入框 (ControlID: 0x{INPUT_BOX_CONTROL_ID:X})")
    else:
        print(f"未找到主窗口 (ControlID: 0x{MAIN_WINDOW_CONTROL_ID:X})")
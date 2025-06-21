import win32gui
import win32con
import win32api

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

def set_text_to_control(control_hwnd, text):
    """向控件发送文本"""
    if control_hwnd:
        win32gui.SendMessage(control_hwnd, win32con.WM_SETTEXT, 0, text)
        return True
    return False

if __name__ == "__main__":
    # 设置目标 ControlID
    MAIN_WINDOW_CONTROL_ID = 0x92E  # 主窗口标识控件的 ControlID
    INPUT_BOX_ACC_CONTROL_ID = 0x3E9    # 输入框的 ControlID
    INPUT_BOX_PWD_CONTROL_ID = 0x3F4    # 输入框的 ControlID
    
    # 查找主窗口
    main_hwnd = find_window_by_control_id(MAIN_WINDOW_CONTROL_ID)
    
    if main_hwnd:
        # 获取窗口信息
        info = get_window_info(main_hwnd)
        print(f"找到主窗口:")
        print(f"  句柄: {info['hwnd']}")
        print(f"  标题: {info['title']}")
        print(f"  类名: {info['class_name']}")
        
        # # 查找输入框控件
        # input_box_accout_hwnd = find_control_by_id(main_hwnd, INPUT_BOX_ACC_CONTROL_ID)
        
        # if input_box_accout_hwnd:
        #     control_class = win32gui.GetClassName(input_box_accout_hwnd)
        #     print(f"找到输入框控件 (类名: {control_class})")
            
        #     # 向输入框发送文本
        #     text_to_input = "121600012698"  # 请替换为你要输入的文本
        #     if set_text_to_control(input_box_accout_hwnd, text_to_input):
        #         print(f"成功向输入框输入文本: {text_to_input}")
        #     else:
        #         print("输入文本失败")

        # 查找输入框控件
        input_box_pwd_hwnd = find_control_by_id(main_hwnd, INPUT_BOX_PWD_CONTROL_ID)
        print(input_box_pwd_hwnd)
        if input_box_pwd_hwnd:
            control_class = win32gui.GetClassName(input_box_pwd_hwnd)
            print(f"找到输入框控件 (类名: {control_class})")
            
            # 向输入框发送文本
            text_to_input = "12312zc"  # 请替换为你要输入的文本
            if set_text_to_control(input_box_pwd_hwnd, text_to_input):
                print(f"成功向输入框输入文本: {text_to_input}")
            else:
                print("输入文本失败")            
        else:
            print(f"未找到 ControlID 为 0x{INPUT_BOX_PWD_CONTROL_ID:X} 的输入框")
    else:
        print(f"未找到主窗口 (ControlID: 0x{MAIN_WINDOW_CONTROL_ID:X})")
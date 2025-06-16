import tkinter as tk
from tkinter import ttk
import platform
import random
import time
from threading import Timer

class ResizableFloatingWindow:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # 无边框窗口
        self.root.attributes('-topmost', True)  # 窗口置顶
        
        # 检测操作系统
        self.is_macos = platform.system() == "Darwin"
        
        # 窗口最小尺寸
        self.min_width = 300
        self.min_height = 200
        
        # 边框宽度（用于拉伸）
        self.border_width = 8  # 统一使用中等宽度，提升跨平台体验
        
        # 用于 macOS 的调整因子
        self.macos_adjustment = 1.5 if self.is_macos else 1.0
        
        # 获取屏幕尺寸
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        
        # 设置窗口初始位置和大小
        self.root.geometry(f'400x300+{self.screen_width//2-200}+{self.screen_height//2-150}')
        
        # 创建标题栏和内容区域
        self.create_widgets()
        
        # 吸附阈值（像素）
        self.snap_threshold = 50
        
        # 拖动相关变量
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        
        # 拉伸相关变量
        self.resizing = False
        self.resize_direction = None  # 'n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw'
        self.original_width = 0
        self.original_height = 0
        self.original_x = 0
        self.original_y = 0
        
        # 边缘吸附相关变量
        self.edge_docked = False
        self.dock_position = None  # 'top', 'bottom', 'left', 'right'
        self.dock_timer = None
        self.dock_timer_duration = 3.0
        
        # 绑定鼠标事件
        self.bind_events()
    
    def create_widgets(self):
        # 标题栏
        self.title_bar = tk.Frame(self.root, bg='#2a2a2a', height=30)
        self.title_bar.pack(fill=tk.X)
        
        # 标题
        self.title_label = tk.Label(self.title_bar, text="可拉伸消息列表", 
                                   bg='#2a2a2a', fg='white', font=('SimHei', 10))
        self.title_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 添加消息按钮
        self.add_button = tk.Button(self.title_bar, text="+", bg='#3a3a3a', fg='white',
                                    width=2, height=0, command=self.on_add_message,
                                    relief=tk.FLAT, font=('SimHei', 10))
        self.add_button.pack(side=tk.RIGHT, padx=2, pady=5)
        
        # 关闭按钮
        self.close_button = tk.Button(self.title_bar, text="×", bg='#2a2a2a', fg='white',
                                     width=2, height=0, command=self.root.quit,
                                     relief=tk.FLAT, font=('SimHei', 10))
        self.close_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 创建内容框架（黑色背景）
        self.content_frame = tk.Frame(self.root, bg='black', bd=0, highlightthickness=0)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建 Canvas（黑色背景）
        self.canvas = tk.Canvas(self.content_frame, bg='black', bd=0, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建垂直滚动条
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置 Canvas 的滚动
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 创建消息框架（黑色背景）
        self.message_frame = tk.Frame(self.canvas, bg='black')
        self.message_window = self.canvas.create_window((0, 0), window=self.message_frame, anchor=tk.NW)
        
        # 绑定事件
        self.message_frame.bind("<Configure>", self.on_message_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # 绑定鼠标滚轮事件
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)  # Windows 和 macOS
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)    # Linux 向上滚动
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)    # Linux 向下滚动
        
        # 初始提示信息
        self.add_message("消息列表将显示在这里...")
    
    def on_message_frame_configure(self, event):
        # 更新 Canvas 的滚动区域
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        # 当 Canvas 大小改变时，调整内部窗口宽度
        width = event.width
        self.canvas.itemconfig(self.message_window, width=width)
    
    def bind_events(self):
        # 鼠标事件绑定
        self.root.bind('<Button-1>', self.on_drag_start)
        self.root.bind('<B1-Motion>', self.on_drag_motion)
        self.root.bind('<ButtonRelease-1>', self.on_drag_stop)
        self.root.bind('<Motion>', self.on_mouse_move)
        self.root.bind('<Enter>', self.on_mouse_enter)
        self.root.bind('<Leave>', self.on_mouse_leave)
        
        # 滚轮事件
        self.root.bind('<MouseWheel>', self.on_mousewheel)
        
    
    def on_drag_start(self, event):
        self.dragging = True
        # 获取鼠标相对于窗口的位置
        self.offset_x = event.x
        self.offset_y = event.y
        
        # 获取窗口当前的位置
        self.window_x = self.root.winfo_x()
        self.window_y = self.root.winfo_y()
        
        # 获取鼠标相对于屏幕的位置
        self.screen_x = self.root.winfo_pointerx()
        self.screen_y = self.root.winfo_pointery()
        
        # 计算偏移量
        self.offset_x = self.screen_x - self.window_x - event.x
        self.offset_y = self.screen_y - self.window_y - event.y
    
    def on_drag_motion(self, event):
        if self.dragging:
            # 获取鼠标当前相对于屏幕的位置
            screen_x = self.root.winfo_pointerx()
            screen_y = self.root.winfo_pointery()
            
            # 计算新位置
            x = screen_x - self.offset_x
            y = screen_y - self.offset_y
            
            # 限制窗口位置，防止拖出屏幕
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            
            x = max(0, min(x, screen_width - window_width))
            y = max(0, min(y, screen_height - window_height))
            
            # 更新窗口位置
            self.root.geometry(f'+{x}+{y}')
    
    def on_drag_stop(self, event):
        self.dragging = False
        self._apply_snap()
    
    def on_drag_stop(self, event):
        self.dragging = False
        self._apply_snap()
    
    def on_mouse_move(self, event):
        # 重置光标
        self.root.config(cursor="arrow")  # 使用通用的箭头光标
    
        self.dock_timer.start()

    def dock_window(self):
        if not self.edge_docked:
            x, y = self.root.winfo_x(), self.root.winfo_y()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            if self.dock_position == 'left':
                self.root.geometry(f'20x{height}+0+{y}')
            elif self.dock_position == 'right':
                self.root.geometry(f'20x{height}+{self.screen_width - 20}+{y}')
            elif self.dock_position == 'top':
                self.root.geometry(f'{width}x20+{x}+0')
            elif self.dock_position == 'bottom':
                self.root.geometry(f'{width}x20+{x}+{self.screen_height - 20}')
            
            self.edge_docked = True

    def undock_window(self):
        if self.edge_docked:
            x, y = self.root.winfo_x(), self.root.winfo_y()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # 恢复原始大小
            if self.dock_position == 'left':
                self.root.geometry(f'400x{height}+0+{y}')
            elif self.dock_position == 'right':
                self.root.geometry(f'400x{height}+{self.screen_width - 400}+{y}')
            elif self.dock_position == 'top':
                self.root.geometry(f'{width}x300+{x}+0')
            elif self.dock_position == 'bottom':
                self.root.geometry(f'{width}x300+{x}+{self.screen_height - 300}')
            
            self.edge_docked = False

    def on_mouse_enter(self, event):
        if self.edge_docked:
            self.undock_window()
        if self.dock_timer:
            self.dock_timer.cancel()

    def on_mouse_leave(self, event):
        if not self.edge_docked:
            self.start_dock_timer()

    # 鼠标滚轮事件处理
    def on_mousewheel(self, event):
        """处理鼠标滚轮事件，使整个内容区域都能滚动"""
        # 检查鼠标是否在内容区域内（包括Canvas和滚动条）
        x, y = self.root.winfo_pointerxy()
        content_x = self.content_frame.winfo_rootx()
        content_y = self.content_frame.winfo_rooty()
        content_width = self.content_frame.winfo_width()
        content_height = self.content_frame.winfo_height()
        
        if (content_x <= x <= content_x + content_width and 
            content_y <= y <= content_y + content_height):
            # 根据不同操作系统处理滚轮事件
            if self.is_macos:
                # macOS 使用 event.delta 直接滚动
                self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
            else:
                # Windows/Linux 使用 Button-4/5 事件
                if event.num == 4:
                    self.canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.canvas.yview_scroll(1, "units")
    
    # 添加消息按钮回调
    def on_add_message(self):
        """按钮点击回调：添加随机消息"""
        messages = [
            "这是一条新消息",
            "点击按钮添加的消息",
            "消息列表正在增长",
            "试试调整窗口大小",
            "这个窗口可以随意拖动",
            "边框可以拉伸改变尺寸",
            "边缘吸附功能很实用",
            "自定义按钮很简单",
            "Python Tkinter 很强大",
            "保持黑色主题很美观"
        ]
        self.add_message(random.choice(messages))
    
    # 向列表添加消息
    def add_message(self, message):
        """向消息列表添加一条新消息"""
        # 获取当前窗口宽度，减去边距
        width = self.root.winfo_width() - 20
        
        # 创建消息标签（白色文本，黑色背景）
        msg_label = tk.Label(self.message_frame, text=f"- {message}", 
                            bg='black', fg='white',
                            font=('SimHei', 10), justify=tk.LEFT, wraplength=width)
        msg_label.pack(anchor=tk.W, padx=5, pady=3)
        
        # 滚动到底部
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

if __name__ == "__main__":
    root = tk.Tk()
    
    # 设置 macOS 系统字体支持
    if platform.system() == "Darwin":
        default_font = ('Heiti TC', 10)
        root.option_add("*Font", default_font)
    
    app = ResizableFloatingWindow(root)
    
    # 示例：添加一些测试消息
    app.add_message("欢迎使用可拉伸的黑色主题消息列表!")
    app.add_message("现在可以通过拖动边缘来调整窗口大小")
    app.add_message("将鼠标移动到窗口边缘，光标会变成调整大小的样式")
    
    root.mainloop()
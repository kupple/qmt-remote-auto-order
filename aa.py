import tkinter as tk
from tkinter import ttk
import platform
import random

class ResizableFloatingWindow:
  def __init__(self, root):
    self.root = root
    self.root.overrideredirect(True) # 无边框窗口
    self.root.attributes('-topmost', True) # 窗口置顶
    
    # 检测操作系统
    self.is_macos = platform.system() == "Darwin"
    
    # 窗口最小尺寸
    self.min_width = 300
    self.min_height = 200
    
    # 边框宽度（用于拉伸）
    self.border_width = 8 # 统一使用中等宽度，提升跨平台体验
    
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
    self.resize_direction = None # 'n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw'
    self.original_width = 0
    self.original_height = 0
    self.original_x = 0
    self.original_y = 0
    
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
    
    # 添加消息按钮（新增）
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
    # 绑定标题栏的鼠标事件（拖动窗口）
    self.title_bar.bind("<Button-1>", self.on_drag_start)
    self.title_bar.bind("<B1-Motion>", self.on_drag_motion)
    self.title_bar.bind("<ButtonRelease-1>", self.on_drag_stop)
    
    # 让标签也能响应拖动
    self.title_label.bind("<Button-1>", self.on_drag_start)
    self.title_label.bind("<B1-Motion>", self.on_drag_motion)
    self.title_label.bind("<ButtonRelease-1>", self.on_drag_stop)
    
    # 绑定窗口边缘的鼠标事件（调整大小）
    self.root.bind("<Motion>", self.on_mouse_move)
    self.root.bind("<Button-1>", self.on_resize_start)
    self.root.bind("<B1-Motion>", self.on_resize_motion)
    self.root.bind("<ButtonRelease-1>", self.on_resize_stop)
  
  def on_drag_start(self, event):
    self.dragging = True
    self.offset_x = event.x
    self.offset_y = event.y
  
  def on_drag_motion(self, event):
    if self.dragging and not self.resizing:
      # 计算新位置
      x = self.root.winfo_pointerx() - self.offset_x
      y = self.root.winfo_pointery() - self.offset_y
      
      # 更新窗口位置
      self.root.geometry(f'+{x}+{y}')
  
  def on_drag_stop(self, event):
    self.dragging = False
    self._apply_snap()
  
  def on_mouse_move(self, event):
    # 检测鼠标是否在窗口边缘，设置相应的光标样式
    x, y = event.x, event.y
    width = self.root.winfo_width()
    height = self.root.winfo_height()
    
    # 调整后的边框宽度（macOS 上更灵敏）
    adjusted_border = int(self.border_width * self.macos_adjustment)
    
    # 重置光标
    self.root.config(cursor="")
    
    # 检测边缘区域
    if y < adjusted_border:
      if x < adjusted_border:
        self.root.config(cursor="nwse_resize") # 左上角
        self.resize_direction = "nw"
      elif x > width - adjusted_border:
        self.root.config(cursor="nesw_resize") # 右上角
        self.resize_direction = "ne"
      else:
        self.root.config(cursor="ns_resize")  # 上边缘
        self.resize_direction = "n"
    elif y > height - adjusted_border:
      if x < adjusted_border:
        self.root.config(cursor="nesw_resize") # 左下角
        self.resize_direction = "sw"
      elif x > width - adjusted_border:
        self.root.config(cursor="nwse_resize") # 右下角
        self.resize_direction = "se"
      else:
        self.root.config(cursor="ns_resize")  # 下边缘
        self.resize_direction = "s"
    elif x < adjusted_border:
      self.root.config(cursor="ew_resize")  # 左边缘
      self.resize_direction = "w"
    elif x > width - adjusted_border:
      self.root.config(cursor="ew_resize")  # 右边缘
      self.resize_direction = "e"
    else:
      self.resize_direction = None
  
  def on_resize_start(self, event):
    if self.resize_direction:
      self.resizing = True
      self.original_width = self.root.winfo_width()
      self.original_height = self.root.winfo_height()
      self.original_x = self.root.winfo_x()
      self.original_y = self.root.winfo_y()
      self.start_x = event.x
      self.start_y = event.y
  
  def on_resize_motion(self, event):
    if self.resizing:
      dx = event.x - self.start_x
      dy = event.y - self.start_y
      width = self.original_width
      height = self.original_height
      x = self.original_x
      y = self.original_y
      
      # 根据方向调整大小
      if self.resize_direction in ["n", "nw", "ne"]:
        height -= dy
        y += dy
        dy = 0 # 防止重复计算
      if self.resize_direction in ["s", "sw", "se"]:
        height += dy
      if self.resize_direction in ["w", "nw", "sw"]:
        width -= dx
        x += dx
        dx = 0 # 防止重复计算
      if self.resize_direction in ["e", "ne", "se"]:
        width += dx
      
      # 确保不小于最小尺寸
      width = max(width, self.min_width)
      height = max(height, self.min_height)
      
      # 更新窗口大小和位置
      self.root.geometry(f"{width}x{height}+{x}+{y}")
  
  def on_resize_stop(self, event):
    if self.resizing:
      self.resizing = False
      self._apply_snap()
  
  def _apply_snap(self):
    # 获取当前窗口位置和大小
    x = self.root.winfo_x()
    y = self.root.winfo_y()
    width = self.root.winfo_width()
    height = self.root.winfo_height()
    
    # 边缘吸附逻辑
    if x < self.snap_threshold: # 左边缘
      x = 0
    elif x > self.screen_width - width - self.snap_threshold: # 右边缘
      x = self.screen_width - width
    
    if y < self.snap_threshold: # 上边缘
      y = 0
    elif y > self.screen_height - height - self.snap_threshold: # 下边缘
      y = self.screen_height - height
    
    # 更新窗口位置（吸附后）
    self.root.geometry(f'+{x}+{y}')
  
  # 新增方法：添加消息按钮回调
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
  
  # 新增方法：向列表添加消息
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

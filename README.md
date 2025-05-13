# QMT Remote Auto Order

> ⚠️ **重要提示**：该项目目前仍在开发中，可能存在不稳定的功能和未解决的问题。请勿在生产环境中使用，仅用于开发和测试目的。

一个基于Python和WebView的远程自动下单系统，支持实时通信和自动化交易操作。

## 功能特性

- 基于WebView的现代化用户界面
- 实时WebSocket通信
- 支持CEF模式运行
- 自动化的交易操作
- 可配置的开发和生产环境
- 完整的日志记录系统

## 系统要求

- Python 3.x
- Node.js (用于前端开发)
- pnpm (包管理器)

## 安装说明

1. 克隆项目到本地：
```bash
git clone [项目地址]
cd qmt-remote-auto-order
```

2. 安装Python依赖：
```bash
pip install pywebview flask flask-socketio
```

3. 安装前端依赖：
```bash
pnpm install
```

## 使用方法

### 开发环境运行

1. 启动前端开发服务器：
```bash
pnpm run dev
```

2. 启动Python应用：
```bash
python main.py
```

### 生产环境运行

直接运行Python应用：
```bash
python main.py
```

### CEF模式运行

如果需要使用CEF模式运行：
```bash
python main.py --cef
```

## 项目结构

```
qmt-remote-auto-order/
├── src/              # 前端源代码
├── src_py/           # Python源代码
├── api/              # API接口
├── static/           # 静态资源
├── dist/             # 构建输出目录
├── main.py           # 主程序入口
├── server.py         # WebSocket服务器
└── package.json      # 项目配置文件
```

## 日志

系统日志保存在 `log.txt` 文件中，记录了详细的运行信息和错误追踪。

## 许可证

本项目采用 [LICENSE](LICENSE) 文件中的许可证。

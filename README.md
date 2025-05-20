# 注意
```
 该项目正在开发中
```
# QMT Remote Auto Order

![Logo](gui/src/assets/images/logo.png)

## 项目简介

QMT Remote Auto Order 是一个自动化交易系统，用于远程管理和执行交易订单。

## 功能特点

- 远程订单管理
- 自动化交易执行
- 实时监控和报告
- 用户友好的界面

## 技术栈

- 后端：Python
- 前端：Node.js
- 数据库：SQLite

## 安装说明

1. 克隆仓库
```bash
git clone [repository-url]
```

2. 安装依赖
```bash
# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd gui
pnpm install
```

3. 运行应用
```bash
# 启动后端服务
python main.py

# 启动前端服务
cd gui
pnpm dev
```

## 使用说明

1. 启动应用后，通过浏览器访问 `http://localhost:3000`
2. 登录系统
3. 开始使用自动化交易功能

## 项目结构

```
├── api/            # API 接口
├── gui/            # 前端界面
├── pyapp/          # Python 应用
├── static/         # 静态资源
└── main.py         # 主程序入口
```

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

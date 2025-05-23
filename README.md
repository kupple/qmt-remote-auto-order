<div align="center">
  <img src="resources/logo.png" width="200" height="200" alt="Logo"/>
  <div>&nbsp;</div>
  <b><font size="5">qmt远程自动下单程序</font></b>
</div>

## 项目简介

基于pywebview开发的一款能在回测平台(暂时支持聚宽)发送下单信号，收到信号后在qmt进行本地下单。使用本程序旨在简化自动下单流程，免去代码，让用户友好操作。

## 功能特点


- 用户友好的界面
- 自动打新打债逆回购功能
- 一键转换代码功能 复制->粘贴 完成代码的转换
- token验证确保信号安全
- 支持多策略运行
- 查看受理订单
- 支持自建服务器搭建/私有服务器
- 后端使用go高性能服务作为支持
- 后端有重发机制确保发出信号安全


## 技术栈
- python 3.9+
- pywebview 6.0+
- nodejs 22+
- vue 3.0+
- element-plus 2.3+
  
## 下载

## 开发说明

1. 克隆仓库
```   
    请自行安装nodejs >= 20.0 python >= 3.8
```
   
2. 克隆仓库

```bash
git clone https://github.com/kupple/qmt-remote-auto-order
```

3. 初始化/运行/打包

```bash
# 安装依赖
npm run init

# 运行开发模型
npm run start

# 打包应用
npm run build

```

## ToDo
- 接入更多平台如掘金量化，SuperMind
- 接入easytrader
- 按金额比例数量下单
  
## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

<img src="resources/WechatIMG.jpg" width="300"  alt="Logo"/>
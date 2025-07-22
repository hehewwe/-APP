# 智能诈骗信息识别 APP

一款基于 `uni-app` 和 `Flask` 开发的移动应用，旨在帮助用户识别潜在的诈骗信息，保护个人财产安全。

## 核心功能

- **智能文本分析**: 用户可以手动输入可疑文本，应用将通过后端服务进行分析，返回诈骗类别和详细说明。
- **用户认证系统**: 应用包含完整的用户登录、退出及会话管理功能，保障核心功能（如文本分析）的授权访问。
- **丰富的诈骗分类**: 后端内置了十余种常见的诈骗类型关键词，能够对文本进行较为精确的分类。
- **动态UI展示**: 前端能够根据后端返回的分析结果，动态展示不同的风险提示样式。
- **模块化设置**: 提供登录管理、版本检查、隐私政策查阅等功能。

## 技术栈

- **前端**:
  - `uni-app`: 一个使用 Vue.js 开发所有前端应用的框架。
  - `Vue.js`: 渐进式 JavaScript 框架。
- **后端**:
  - `Python`: 主要编程语言。
  - `Flask`: 轻量级的 Web 应用框架。
  - `Flask-CORS`: 用于处理跨域请求。

## 如何运行

### 1. 运行后端服务（只有登录和诈骗信息智能识别功能需要）

后端服务位于 `FLASK` 目录下。

```bash
# 1. 进入后端目录
cd FLASK

# 2. (建议) 创建并激活虚拟环境
#    Windows:
python -m venv venv
venv\Scripts\activate
# 3. 安装依赖
pip install Flask Flask-CORS requests

# 4. 启动服务
python myflask2.py
```

### 2. 运行前端应用

1.  使用 **HBuilderX** 打开项目根目录。（有提示需要安装的插件安装一下）
2.  **修改IP地址**: 在utils\config.js文件里找到const BASE_URL = 'http://真实局域网地址：5000'例如（‘http://132.145.11.21:5000’）
3.  通过 HBuilderX 的 **运行** 菜单，将应用运行到模拟器或真机进行测试。
真实局域网地址：
先打开电脑的cmd，输入ipconfig，找到无线局域网适配器 WLAN下的 IPv4 地址 ：xxx.xxx.xx.xx例如（132.145.11.21）
## 项目结构

```
/
|-- FLASK/                # 后端 Flask 应用
|   |-- myflask2.py       # 主要的后端服务文件
|   `-- ...
|-- pages/                # uni-app 前端页面
|   |-- home/             # 主页
|   |-- fraud-detection/  # 诈骗信息智能识别页
|   |-- settings/         # 设置页
|   |   `-- login.vue     # 登录页
|   `-- ...
|-- utils/                # 前端工具模块 (例如: alert-manager.js)
|-- static/               # 静态资源 (例如: 图片)
|-- .gitignore            # Git 忽略配置文件
|-- App.vue               # 应用全局配置
|-- main.js               # Vue 初始化脚本
|-- manifest.json         # 应用配置文件
|-- pages.json            # 页面路由配置
`-- README.md             # 项目说明文件
``` 

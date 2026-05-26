# Telegram Media NAS

现代化 Telegram 媒体下载与管理系统，采用前后端分离架构。

## 功能特性

- 🚀 **实时下载进度** - WebSocket 实时推送下载进度
- 📁 **文件管理** - 浏览、搜索、筛选已下载的文件
- 💬 **多聊天支持** - 同时订阅多个频道/群组
- 🔍 **智能过滤** - 按时间、媒体类型、文件格式过滤
- 🐳 **Docker 部署** - 一键部署，适合 NAS 环境
- 🎨 **现代化 UI** - 基于 Vue 3 + Element Plus

## 技术栈

### 后端
- FastAPI - 异步 Web 框架
- Pyrogram - Telegram MTProto API
- PostgreSQL - 数据库
- Redis - 缓存与任务队列
- WebSocket - 实时通信

### 前端
- Vue 3 - 前端框架
- TypeScript - 类型安全
- Element Plus - UI 组件库
- Vite - 构建工具

## 快速开始

### 1. 获取 Telegram API 凭证

1. 访问 [https://my.telegram.org/apps](https://my.telegram.org/apps)
2. 登录你的 Telegram 账号
3. 创建一个新应用获取 `api_id` 和 `api_hash`

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 Telegram API 凭证：

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number
```

### 3. 使用 Docker Compose 启动

```bash
docker-compose up -d
```

服务将在以下端口启动：
- 后端 API: http://localhost:8000
- 前端界面: http://localhost:3000
- API 文档: http://localhost:8000/docs

### 4. 登录 Telegram

首次启动时，应用会要求你输入 Telegram 验证码。

## 开发模式

### 后端开发

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看 Swagger API 文档。

## 项目结构

```
telegram-media-nas/
├── backend/              # 后端代码
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # 业务逻辑
│   │   ├── tasks/       # 异步任务
│   │   └── websocket/   # WebSocket 处理
│   └── requirements.txt
├── frontend/            # 前端代码
│   └── src/
│       ├── api/        # API 调用
│       ├── components/ # 组件
│       ├── views/      # 页面
│       └── stores/     # 状态管理
└── docker-compose.yml
```

## 许可证

MIT License

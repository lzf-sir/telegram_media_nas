# Telegram Media NAS

现代化 Telegram 媒体下载与管理系统，采用前后端分离架构，专为 NAS 环境设计。

## 功能特性

### 核心功能
- 🚀 **批量下载** - 从 Telegram 聊天/频道批量下载媒体文件
- 📁 **文件管理** - 浏览、搜索、预览、筛选已下载的文件
- 🔍 **MD5 去重** - 自动计算文件哈希，跳过重复文件
- 💬 **多聊天支持** - 同时订阅多个频道/群组
- 📡 **实时监听** - 监听聊天新消息，自动下载或转发
- 🔄 **消息转发** - 将消息自动转发到其他聊天
- 🤖 **Bot 命令** - 通过 Telegram Bot 远程控制下载

### 实时监控
- 📊 **实时进度** - WebSocket 推送下载进度，含速度和 ETA
- 🩺 **系统健康** - Dashboard 显示磁盘、队列、账号状态
- 🔔 **任务通知** - 任务完成/失败实时通知

### 高级功能
- 🧩 **智能过滤** - 按媒体类型、文件格式、大小等多维度过滤
- ⭐ **聊天收藏** - 收藏常用聊天 ID，创建任务时一键选择
- 🖼️ **缩略图预览** - 图片文件缩略图列表 + 大图弹窗预览
- 👥 **多账号管理** - 多 Telegram 账号隔离与负载均衡
- 🎯 **断点续传** - 任务暂停/恢复，重启后自动恢复
- 🎨 **现代化 UI** - Vue 3 + Element Plus 玻璃态设计

## 技术栈

### 后端
- **FastAPI** - 异步 Web 框架
- **Pyrogram** - Telegram MTProto API 客户端
- **SQLite** (aiosqlite) - 轻量文件数据库，零配置
- **Redis** - 缓存与消息队列
- **WebSocket** - 实时双向通信

### 前端
- **Vue 3** + Composition API
- **TypeScript** - 类型安全
- **Element Plus** - 组件库
- **Pinia** - 状态管理
- **Vite** - 构建工具

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
- 后端 API: http://localhost:8741
- 前端界面: http://localhost:6742
- API 文档: http://localhost:8741/docs

### 4. 首次初始化

1. 访问前端界面 `http://localhost:6742`
2. 创建管理员账号
3. 在「系统设置」中配置 Telegram API 凭证
4. 在「账号管理」中添加并激活 Telegram 账号
5. 开始创建下载任务

## 开发模式

### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

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

启动后端服务后，访问 http://localhost:8741/docs 查看 Swagger API 文档。

### 主要 API 端点

| 路径 | 说明 |
|------|------|
| `/api/v1/auth` | 认证（登录/注册/初始化） |
| `/api/v1/tasks` | 下载任务管理 |
| `/api/v1/files` | 文件管理（含预览、缩略图） |
| `/api/v1/chats` | 聊天订阅 |
| `/api/v1/settings` | 系统设置（支持动态更新） |
| `/api/v1/accounts` | 账号管理 |
| `/api/v1/forwards` | 转发任务 |
| `/api/v1/listens` | 实时监听 |
| `/api/v1/favorites` | 聊天收藏 |
| `/api/v1/system` | 系统健康检查 |
| `/api/v1/logs` | 操作日志 |
| `/ws/task/{id}` | WebSocket 任务进度 |
| `/ws/notifications` | WebSocket 全局通知 |

## 项目结构

```
telegram-media-nas/
├── backend/                  # 后端代码
│   ├── app/
│   │   ├── api/v1/          # API 路由（14 个模块）
│   │   │   ├── auth.py      # 认证
│   │   │   ├── tasks.py     # 任务管理
│   │   │   ├── files.py     # 文件管理（含预览/缩略图）
│   │   │   ├── accounts.py  # 账号管理
│   │   │   ├── settings.py  # 设置管理（支持动态持久化）
│   │   │   ├── chats.py     # 聊天管理
│   │   │   ├── forwards.py  # 转发规则
│   │   │   ├── listens.py   # 监听规则
│   │   │   ├── logs.py      # 日志查询
│   │   │   ├── system.py    # 系统健康
│   │   │   └── favorites.py # 聊天收藏
│   │   ├── core/            # 核心模块
│   │   │   ├── config.py    # 配置管理
│   │   │   ├── telegram.py  # Telegram 客户端
│   │   │   ├── bot.py       # Bot 管理器
│   │   │   ├── security.py  # 认证安全
│   │   │   └── rate_limit.py # 速率限制
│   │   ├── models/          # 数据模型（12 个）
│   │   ├── services/        # 业务逻辑层
│   │   │   ├── task_service.py
│   │   │   ├── account_service.py
│   │   │   ├── listen_service.py
│   │   │   ├── forward_service.py
│   │   │   └── settings_service.py
│   │   ├── tasks/           # 异步任务
│   │   │   └── download.py  # 下载 + MD5 去重 + 速度追踪
│   │   └── websocket/       # WebSocket 管理
│   │       └── manager.py   # 连接池 + 心跳 + 广播
│   ├── data/                # SQLite 数据库
│   ├── downloads/           # 下载文件存储
│   ├── temp/                # 临时文件
│   └── sessions/            # Telegram 会话
├── frontend/                # 前端代码
│   └── src/
│       ├── api/             # API 调用封装（11 个模块）
│       ├── components/      # 可复用组件
│       │   ├── TaskCard.vue       # 任务卡片（含速度/ETA）
│       │   ├── TaskList.vue       # 任务列表
│       │   ├── CreateTaskDialog.vue # 创建任务（含收藏选择）
│       │   ├── CreateForwardDialog.vue
│       │   ├── AddAccountDialog.vue
│       │   ├── AddListenDialog.vue
│       │   └── ThemeToggle.vue
│       ├── views/           # 页面视图（11 个）
│       │   ├── Dashboard.vue      # 仪表板（KPI + 健康 + 收藏）
│       │   ├── Tasks.vue          # 任务管理
│       │   ├── Files.vue          # 文件管理（缩略图 + 预览）
│       │   ├── Settings.vue       # 系统设置
│       │   ├── Accounts.vue       # 账号管理
│       │   ├── Chats.vue          # 聊天订阅
│       │   ├── Forwards.vue       # 转发任务
│       │   ├── Listens.vue        # 实时监听
│       │   ├── Logs.vue           # 操作日志
│       │   ├── Login.vue          # 登录
│       │   └── InitSetup.vue      # 初始化
│       ├── stores/          # Pinia 状态管理
│       ├── composables/     # 组合式函数
│       │   ├── useWebSocket.ts    # WebSocket（心跳+重连）
│       │   └── useTheme.ts
│       ├── router/          # 路由配置
│       ├── types/           # TypeScript 类型
│       └── utils/           # 工具函数
├── docker-compose.yml       # Docker Compose 编排
├── CLAUDE.md                # 项目开发规则
└── FUNCTIONALITY.md         # 功能详细文档
```

## 许可证

MIT License

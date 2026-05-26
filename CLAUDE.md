# Telegram Media NAS - Claude Code 项目规则

## 项目概述

现代化 Telegram 媒体下载与管理系统，采用前后端分离架构。

- **后端**: FastAPI + Pyrogram + SQLite + Redis
- **前端**: Vue 3 + TypeScript + Element Plus
- **部署**: Docker Compose
- **特性**: MD5 去重，自动跳过重复文件

## 代码规范

### 通用规则

1. **注释语言**: 所有注释必须使用中文
2. **编码风格**: 遵循项目现有代码风格
3. **提交信息**: 使用清晰的中文提交信息
4. **命名约定**:
   - Python: snake_case
   - TypeScript/Vue: camelCase
   - 组件名: PascalCase

### 后端规范 (Python/FastAPI)

- 使用异步函数 (`async def`) 处理数据库和 API 操作
- 使用 Pydantic 进行数据验证
- 使用 SQLAlchemy ORM 进行数据库操作
- 业务逻辑放在 `services/` 目录下
- API 路由放在 `api/v1/` 目录下
- 数据模型放在 `models/` 目录下
- 使用 loguru 记录日志
- **数据库**: 使用 SQLite，无需额外配置数据库服务
- **去重策略**: 每个文件下载前计算 MD5 并检查数据库，已存在则跳过

```python
# 服务层示例
class TaskService:
    """任务服务 - 管理下载任务的业务逻辑"""

    async def create_task(self, db: AsyncSession, task_data: TaskCreate) -> DownloadTask:
        """创建新的下载任务"""
        # 实现逻辑
        pass
```

### 前端规范 (Vue 3 + TypeScript)

- 使用 Composition API (`<script setup>`)
- 使用 TypeScript 类型定义
- API 调用封装在 `api/` 目录
- 状态管理使用 Pinia (`stores/` 目录)
- 组件放在 `components/` 目录
- 页面放在 `views/` 目录

```typescript
// API 定义示例
export interface Task {
  id: number
  chat_id: string
  status: string
  // ...
}

export const tasksApi = {
  create: (data: TaskCreate) => api.post('/tasks/', data),
}
```

## 目录结构

```
telegram-media-nas/
├── backend/                     # 后端代码
│   ├── app/
│   │   ├── api/v1/             # API 路由
│   │   │   ├── auth.py         # 认证相关
│   │   │   ├── tasks.py        # 任务管理
│   │   │   ├── files.py        # 文件管理
│   │   │   ├── chats.py        # 聊天管理
│   │   │   ├── accounts.py     # 账号管理
│   │   │   ├── forwards.py     # 转发规则
│   │   │   ├── listens.py      # 监听规则
│   │   │   ├── logs.py         # 日志查询
│   │   │   └── settings.py     # 设置管理
│   │   ├── core/               # 核心模块
│   │   │   ├── config.py       # 配置管理
│   │   │   └── telegram.py     # Telegram 客户端
│   │   ├── models/             # 数据库模型
│   │   │   └── file.py         # 包含 md5_hash 字段
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # 业务逻辑服务
│   │   ├── tasks/              # 异步任务
│   │   │   └── download.py     # 实现 MD5 去重逻辑
│   │   └── websocket/          # WebSocket 处理
│   ├── data/                   # SQLite 数据库目录
│   └── requirements.txt
├── frontend/                    # 前端代码
│   └── src/
│       ├── api/                # API 调用封装
│       ├── components/         # Vue 组件
│       ├── views/              # 页面视图
│       ├── stores/             # Pinia 状态管理
│       ├── router/             # 路由配置
│       ├── composables/        # 组合式函数
│       └── utils/              # 工具函数
└── docker-compose.yml          # Docker 编排配置（不含 PostgreSQL）
```

## 开发工作流

### 启动开发环境

**后端**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端**:
```bash
cd frontend
npm install
npm run dev
```

### 添加新功能

1. **后端 API**:
   - 在 `backend/app/models/` 创建数据模型
   - 在 `backend/app/schemas/` 创建请求/响应 schema
   - 在 `backend/app/services/` 创建业务逻辑
   - 在 `backend/app/api/v1/` 创建路由

2. **前端页面**:
   - 在 `frontend/src/api/` 创建 API 调用
   - 在 `frontend/src/views/` 创建页面组件
   - 在 `frontend/src/router/routes.ts` 添加路由

### 数据库

- 使用 SQLite 文件数据库，无需额外服务
- 数据库文件位于 `backend/data/telegram_media_nas.db`
- 首次启动时自动创建表结构
- 修改模型后删除数据库文件即可重建

## 文件下载与去重机制

### MD5 去重流程

1. 文件下载到临时目录 (`TEMP_PATH`)
2. 计算文件 MD5 哈希值
3. 查询数据库检查是否已存在该 MD5
4. 如果存在：删除临时文件，跳过下载
5. 如果不存在：移动到目标位置，保存记录

### 相关代码

- `backend/app/tasks/download.py`: 实现下载和 MD5 去重逻辑
- `backend/app/models/file.py`: 包含 `md5_hash` 字段（唯一索引）

```python
# MD5 计算函数
def calculate_md5(file_path: str) -> str:
    """计算文件的 MD5 哈希值"""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()
```

## 测试规范

- 后端测试使用 pytest
- 前端测试使用 Vitest
- 测试文件与源码文件同名，添加 `.test` 后缀

## 环境变量

项目使用 `.env` 文件配置环境变量，参考 `.env.example`:

```env
# Telegram 配置
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number

# 数据库（SQLite，自动管理）
# DATABASE_URL=sqlite+aiosqlite:///./data/telegram_media_nas.db

# Redis
REDIS_URL=redis://redis:6379/0

# 下载路径
DOWNLOAD_PATH=./downloads
TEMP_PATH=./temp
SESSION_PATH=./sessions
```

## WebSocket 通信

- 前端通过 WebSocket 接收实时下载进度
- 进度更新通过 `app/websocket/manager.py` 广播
- 前端使用 `composables/useWebSocket.ts` 处理连接

## 重要注意事项

1. **Telegram 限制**: 注意 Telegram API 的请求频率限制
2. **文件去重**: 所有文件通过 MD5 去重，避免重复下载
3. **会话管理**: Telegram 会话文件存储在 `sessions/` 目录
4. **并发控制**: 通过 `MAX_CONCURRENT_DOWNLOADS` 控制并发下载数
5. **SQLite**: 单写数据库，适合中小规模部署

## Docker 部署

生产环境使用 Docker Compose 部署：
```bash
docker-compose up -d
```

服务包含:
- `backend`: FastAPI 应用
- `frontend`: Nginx 服务的前端静态文件
- `redis`: Redis 缓存和消息队列
- 数据库: SQLite（内置，无需额外容器）


# Telegram Media NAS - 功能文档

## 目录

1. [系统概述](#系统概述)
2. [核心功能](#核心功能)
3. [交互流程](#交互流程)
4. [配置说明](#配置说明)
5. [部署指南](#部署指南)
6. [注意事项](#注意事项)

---

## 系统概述

Telegram Media NAS 是一个现代化的 Telegram 媒体下载与管理系统，采用前后端分离架构设计。

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + Pyrogram + SQLite + Redis |
| 前端 | Vue 3 + TypeScript + Element Plus |
| 部署 | Docker Compose |

### 核心特性

- **MD5 去重**：自动计算文件哈希值，跳过重复文件
- **多账号管理**：支持同时管理多个 Telegram 账号
- **实时进度**：WebSocket 实时推送下载进度
- **灵活过滤**：支持按媒体类型、文件格式、大小等多维度过滤
- **监听订阅**：实时监听聊天/频道新消息自动下载

---

## 核心功能

### 1. 下载任务管理

#### 功能描述

从 Telegram 聊天、频道或群组批量下载媒体文件。

#### 支持的媒体类型

| 类型 | 说明 | 支持格式 |
|------|------|----------|
| audio | 音频文件 | mp3, flac, aac, ogg, wav, m4a, wma, opus, ape |
| video | 视频文件 | mp4, avi, mkv, mov, wmv, flv, webm, m4v, ts, rmvb |
| photo | 图片文件 | jpg, jpeg, png, gif, webp, bmp, tiff, svg, ico |
| document | 文档文件 | pdf, doc, docx, xls, xlsx, ppt, pptx, txt, zip, rar, 7z 等 |
| voice | 语音消息 | ogg, opus, wav |
| animation | 动画文件 | gif, webm, mp4 |

#### 任务配置选项

- **媒体类型过滤**：选择要下载的媒体类型
- **文件格式过滤**：
  - 排除格式：指定不下载的文件扩展名
  - 包含格式：仅下载指定扩展名的文件（优先级高于排除）
- **文件大小限制**：设置最小/最大文件大小
- **数量限制**：限制最大下载数量，0 表示无限制
- **起始偏移**：从指定消息 ID 开始下载

#### 任务状态

```
pending   → 等待执行
running   → 执行中
paused    → 已暂停
completed → 已完成
failed    → 失败
cancelled → 已取消
```

---

### 2. 转发任务

#### 功能描述

将一个聊天/频道的消息转发到另一个聊天/频道。

#### 配置选项

| 选项 | 说明 |
|------|------|
| source_chat_id | 源聊天 ID |
| destination_chat_id | 目标聊天 ID |
| forward_with_caption | 是否转发时保留文字说明 |
| copy_media | 以复制模式转发（隐藏原始来源） |
| media_types | 要转发的媒体类型过滤 |

---

### 3. 实时监听订阅

#### 功能描述

实时监听指定聊天/频道的新消息，自动下载或转发符合条件的媒体。

#### 工作模式

1. **监听模式**：连接 Telegram，持续接收新消息
2. **过滤处理**：根据配置过滤符合条件的消息
3. **自动操作**：下载或转发符合条件的媒体

#### 配置选项

| 配置项 | 说明 |
|--------|------|
| chat_id | 要监听的聊天/频道 ID |
| media_types | 监听的媒体类型 |
| file_formats | 文件格式过滤规则 |
| min_file_size / max_file_size | 文件大小限制 |
| auto_forward | 是否自动转发 |
| forward_to_chat_id | 转发目标聊天 ID |

#### 订阅状态

```
active  → 活跃监听中
paused  → 已暂停
stopped → 已停止
error   → 发生错误
```

---

### 4. 多账号管理

#### 功能描述

管理多个 Telegram 账号，实现账号隔离和负载均衡。

#### 账号配置

| 配置项 | 说明 |
|--------|------|
| phone | 手机号码 |
| api_id / api_hash | Telegram API 凭证 |
| device_model | 设备型号（用于指纹隔离） |
| proxy | 每账号独立代理配置 |

#### 账号状态

```
active   → 活跃可用
inactive → 未激活
banned   → 已被封禁
error    → 错误状态
```

---

### 5. Telegram Bot 交互

#### Bot 命令

| 命令 | 功能 | 使用场景 |
|------|------|----------|
| /start | 初始化 Bot | 首次使用 |
| /download | 下载当前聊天媒体 | 在任意聊天中使用 |
| /status | 查看任务状态 | 查询下载进度 |
| /cancel | 取消当前任务 | 中止正在进行的任务 |
| /help | 帮助文档 | 查看命令说明 |

#### 转发消息处理

Bot 支持处理转发的消息，自动识别原始来源并下载对应媒体。

---

### 6. 文件管理

#### 文件去重机制（MD5）

```
1. 文件下载到临时目录 (TEMP_PATH)
2. 计算文件 MD5 哈希值
3. 查询数据库检查是否已存在该 MD5
4. 如果存在：删除临时文件，跳过下载
5. 如果不存在：移动到目标位置，保存记录
```

#### 文件存储结构

```
downloads/
├── [聊天标题]/
│   └── [年_月]/
│       ├── audio/
│       ├── video/
│       ├── photo/
│       └── document/
```

---

### 7. 高级过滤规则

#### 过滤条件

支持多种操作符进行条件组合：

| 操作符 | 说明 | 示例 |
|--------|------|------|
| equals | 等于 | file_size equals 1024000 |
| not_equals | 不等于 | media_type not_equals audio |
| contains | 包含 | caption contains "关键字" |
| not_contains | 不包含 | file_name not_contains ".tmp" |
| greater_than | 大于 | file_size greater_than 1048576 |
| less_than | 小于 | file_size less_than 104857600 |
| between | 在范围内 | file_size between 1048576,104857600 |
| in | 在列表中 | extension in ".mp4,.mkv,.avi" |
| regex | 正则匹配 | file_name regex "^\d{8}" |

#### 逻辑组合

- **AND**：所有条件都满足
- **OR**：任一条件满足

---

## 交互流程

### 下载任务流程

```
┌─────────────┐
│  用户操作   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ 选择聊天/频道   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ 配置过滤规则   │
│ - 媒体类型      │
│ - 文件格式      │
│ - 大小限制      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ 创建下载任务   │
│ status=pending  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ 获取聊天历史   │
│ 遍历消息列表   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ 逐个处理消息   │
└──────┬──────────┘
       │
       ▼
  ┌──────────────────┐
  │ 是否有媒体？      │
  └────┬─────────┬───┘
       │         │
      No        Yes
       │         │
       │         ▼
       │  ┌─────────────────┐
       │  │ 格式过滤检查    │
       │  └────┬────────────┘
       │       │
       │  ┌────┴─────┐
       │  │ 通过？    │
       │  └──┬───┬───┘
       │    │   │
       │   No  Yes
       │    │   │
       │    │   ▼
       │    │  ┌─────────────────┐
       │    │  │ 下载到临时目录  │
       │    │  └────┬────────────┘
       │    │       │
       │    │       ▼
       │    │  ┌─────────────────┐
       │    │  │ 计算 MD5        │
       │    │  └────┬────────────┘
       │    │       │
       │    │       ▼
       │    │  ┌─────────────────┐
       │    │  │ MD5 已存在？     │
       │    │  └────┬──────┬─────┘
       │    │       │      │
       │    │      Yes    No
       │    │       │      │
       │    │       │      ▼
       │    │       │  ┌─────────────────┐
       │    │       │  │ 保存文件        │
       │    │       │  │ 记录到数据库    │
       │    │       │  └────┬────────────┘
       │    │       │       │
       │    └───────┴───────┘
       │
       ▼
┌─────────────────┐
│ 更新任务进度   │
│ WebSocket 推送 │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ 任务完成       │
│ status=completed│
└─────────────────┘
```

### 监听订阅流程

```
┌─────────────┐
│ 创建订阅   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ 连接 Telegram  │
│ 启动监听       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ 等待新消息     │
│ status=active  │
└──────┬──────────┘
       │
       ▼ (收到新消息)
┌─────────────────┐
│ 过滤检查       │
└──────┬──────────┘
       │
  ┌────┴─────┐
  │ 符合？    │
  └──┬───┬───┘
     │   │
    No  Yes
     │   │
     │   ▼
     │  ┌─────────────────┐
     │  │ 自动下载/转发   │
     │  └────┬────────────┘
     │       │
     └───────┴───────
       │
       ▼
┌─────────────────┐
│ 更新统计       │
│ 继续监听       │
└─────────────────┘
```

---

## 配置说明

### 环境变量配置

创建 `.env` 文件（参考 `.env.example`）：

```env
# Telegram 配置
TELEGRAM_API_ID=your_api_id              # 从 my.telegram.org 获取
TELEGRAM_API_HASH=your_api_hash          # 从 my.telegram.org 获取
TELEGRAM_PHONE=your_phone_number         # 手机号（国际格式）

# Telegram Bot（可选）
TELEGRAM_BOT_TOKEN=your_bot_token        # 从 @BotFather 获取

# 数据库（SQLite，自动管理）
DATABASE_URL=sqlite+aiosqlite:///./data/telegram_media_nas.db

# Redis
REDIS_URL=redis://redis:6379/0

# 下载路径
DOWNLOAD_PATH=./downloads                # 下载文件保存位置
TEMP_PATH=./temp                         # 临时文件目录
SESSION_PATH=./sessions                  # Telegram 会话目录
```

### 系统设置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| MAX_CONCURRENT_DOWNLOADS | 5 | 最大并发下载数 |
| DOWNLOAD_TIMEOUT | 300 | 下载超时时间（秒） |
| MAX_RETRIES | 3 | 失败重试次数 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 10080 | JWT 有效期（7天） |

### 获取 Telegram API 凭证

1. 访问 [https://my.telegram.org](https://my.telegram.org)
2. 登录你的 Telegram 账号
3. 进入 "API development tools"
4. 创建一个新应用
5. 记录 `api_id` 和 `api_hash`

### 创建 Telegram Bot（可选）

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置 Bot 名称和用户名
4. 记录返回的 Bot Token

---

## 部署指南

### 开发环境启动

**后端：**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

### Docker 部署

1. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入配置
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **查看服务状态**
   ```bash
   docker-compose ps
   ```

4. **查看日志**
   ```bash
   docker-compose logs -f backend
   ```

### 服务端口

| 服务 | 端口 |
|------|------|
| Frontend | 3000 |
| Backend API | 8000 |
| Redis | 6379 |

### 数据持久化

系统使用 Docker Volume 持久化以下数据：

- `redis_data`：Redis 数据
- `downloads_data`：下载的文件
- `sqlite_data`：SQLite 数据库
- `sessions_data`：Telegram 会话文件

---

## 注意事项

### Telegram API 限制

1. **请求频率限制**
   - 避免短时间内大量请求
   - 使用多账号分散请求
   - 系统内置限流控制

2. **文件大小限制**
   - Telegram 单文件最大 2GB
   - 建议设置合理的文件大小过滤

3. **账号安全**
   - 不要频繁登录/登出
   - 使用设备指纹隔离
   - 必要时配置代理

### 文件去重

- MD5 计算需要读取完整文件，大文件耗时较长
- 重复文件会被自动跳过，节省存储空间
- MD5 数据库字段有唯一索引，查询高效

### SQLite 数据库

- 适合中小规模部署（单机、低并发）
- 数据库文件位于 `backend/data/telegram_media_nas.db`
- 修改模型后删除数据库文件即可重建
- 不支持多写并发，但读取是并发的

### 并发控制

- 通过 `MAX_CONCURRENT_DOWNLOADS` 控制并发下载数
- 过高并发可能导致账号被限制
- 建议值：3-5

### 代理配置

每个账号可独立配置代理，避免账号关联：

```
proxy_type: socks5 或 http
proxy_host: 代理服务器地址
proxy_port: 代理端口
proxy_username: 代理用户名（可选）
proxy_password: 代理密码（可选）
```

### 会话管理

- 会话文件存储在 `sessions/` 目录
- 首次登录需要验证码
- 会话过期后需要重新登录
- 建议定期备份会话文件

### 系统资源

- **内存**：建议至少 2GB
- **磁盘**：根据下载文件量确定
- **网络**：下载速度取决于网络带宽

### 安全建议

1. 不要将 `.env` 文件提交到版本控制
2. 生产环境修改 `SECRET_KEY`
3. 使用反向代理（Nginx）部署前端
4. 限制数据库文件的访问权限
5. 定期备份重要数据

### 故障排除

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| 无法连接 Telegram | 网络问题/代理配置 | 检查网络连接，配置代理 |
| 下载失败 | 频率限制/文件过大 | 降低并发，增加超时时间 |
| 数据库错误 | 文件权限/磁盘满 | 检查文件权限，清理磁盘 |
| Bot 无响应 | Token 错误/Bot 被封 | 检查 Token，重新创建 Bot |

---

## 附录

### 媒体类型映射表

| Telegram 类型 | Pyrogram 属性 | 说明 |
|---------------|---------------|------|
| audio | message.audio | 音频文件 |
| document | message.document | 通用文档 |
| photo | message.photo | 图片 |
| video | message.video | 视频 |
| voice | message.voice | 语音消息 |
| video_note | message.video_note | 圆形视频 |
| animation | message.animation | GIF 动画 |

### 数据库模型关系

```
TelegramAccount (账号)
    ├── DownloadTask (下载任务)
    │   └── DownloadedFile (下载文件)
    ├── ForwardTask (转发任务)
    └── ListenSubscription (监听订阅)

FilterGroup (过滤规则组)
    └── FilterCondition (过滤条件)

ActivityLog (操作日志)
```

### API 端点概览

| 端点 | 方法 | 功能 |
|------|------|------|
| /api/v1/auth/login | POST | 用户登录 |
| /api/v1/tasks | POST/GET | 创建/查询下载任务 |
| /api/v1/tasks/{id}/pause | POST | 暂停任务 |
| /api/v1/tasks/{id}/cancel | POST | 取消任务 |
| /api/v1/files | GET | 查询下载文件 |
| /api/v1/chats | GET | 获取聊天列表 |
| /api/v1/accounts | POST/GET | 添加/查询账号 |
| /api/v1/forwards | POST/GET | 创建/查询转发任务 |
| /api/v1/listens | POST/GET | 创建/查询监听订阅 |
| /api/v1/logs | GET | 查询操作日志 |
| /ws | WebSocket | 实时进度推送 |

---

*文档版本：1.0.0*
*更新日期：2026-05-26*

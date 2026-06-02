# ============================================================
# 飞牛 NAS 部署指南
# ============================================================

## 前提条件

1. 飞牛 NAS 已安装 Docker 和 Docker Compose
2. 已获取 Telegram API 凭证（https://my.telegram.org/apps）

## 部署步骤

### 1. 上传项目到飞牛 NAS

将整个项目目录上传到飞牛 NAS，例如：
```
/vol1/docker/telegram-media-nas/
```

### 2. 配置环境变量

```bash
cd /vol1/docker/telegram-media-nas
cp .env.feiniu.example .env
```

编辑 `.env` 文件，填入你的实际配置：
- `TELEGRAM_API_ID` / `TELEGRAM_API_HASH` / `TELEGRAM_PHONE`：必填
- `SECRET_KEY`：修改为随机字符串
- `FRONTEND_ORIGINS`：改为飞牛 NAS 的实际 IP 地址

### 3. 创建数据目录

```bash
mkdir -p nas-data/{data,downloads,sessions,temp}
```

### 4. （可选）修改存储路径

如果需要将下载文件存储到其他卷（如大容量存储池），编辑 `docker-compose.feiniu.yml`，将 `./nas-data/downloads` 改为实际路径：

```yaml
volumes:
  - /vol2/media/telegram-downloads:/app/downloads
```

### 5. 启动服务

```bash
docker-compose -f docker-compose.feiniu.yml up -d
```

### 6. 首次登录 Telegram

启动后查看后端日志，按提示输入 Telegram 验证码：

```bash
docker logs -f tg_nas_backend
```

### 7. 访问系统

- 前端界面：`http://<飞牛IP>:13500`
- API 文档：`http://<飞牛IP>:18500/docs`

## 常用命令

```bash
# 查看服务状态
docker-compose -f docker-compose.feiniu.yml ps

# 查看后端日志
docker logs -f tg_nas_backend

# 重启服务
docker-compose -f docker-compose.feiniu.yml restart

# 停止服务
docker-compose -f docker-compose.feiniu.yml down

# 更新后重新构建并启动
docker-compose -f docker-compose.feiniu.yml up -d --build
```

## 目录结构（飞牛 NAS 上）

```
telegram-media-nas/
├── docker-compose.feiniu.yml   # 飞牛专用部署配置
├── .env                         # 环境变量（需自行创建）
├── .env.feiniu.example          # 环境变量模板
├── backend/                     # 后端源码
├── frontend/                    # 前端源码
└── nas-data/                    # 持久化数据目录
    ├── data/                    # SQLite 数据库
    ├── downloads/               # 下载的媒体文件
    ├── sessions/                # Telegram 登录会话
    └── temp/                    # 临时文件
```

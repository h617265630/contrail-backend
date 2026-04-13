# Learnpathly Backend

> FastAPI 后端 API 服务

## 技术栈

- **FastAPI** — Python Web 框架
- **SQLAlchemy** — ORM
- **PostgreSQL** — 数据库 (Supabase)
- **Pydantic** — 数据验证
- **JWT** — 身份认证
- **Uvicorn** — ASGI 服务器

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 填入数据库连接和 API 密钥
```

### 3. 启动服务
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. 访问 API 文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 环境变量

### 数据库
```
DATABASE_URL=postgresql://user:password@host:port/database
```

### API 密钥 (可选)
```
GITHUB_TOKEN=ghp_xxx
TAVILY_API_KEY=tvly-xxx
YOUTUBE_API_KEY=xxx
```

### 应用配置
```
SQL_ECHO=false          # 是否打印 SQL
APP_DEBUG=false         # 调试模式
```

## 目录结构

```
backend/
├── app/
│   ├── api/               # API 路由 (新版)
│   │   ├── ai_path/      # AI 路径生成
│   │   ├── category/      # 分类管理
│   │   ├── learning_path/ # 学习路径
│   │   ├── path_item_note/# 路径节点笔记
│   │   ├── progress/      # 学习进度
│   │   ├── subscription/  # 订阅管理
│   │   ├── trending/      # 热门资源
│   │   ├── webhooks/      # Webhook 处理
│   │   └── admin/         # 管理功能
│   ├── core/              # 核心配置
│   │   ├── config.py      # 应用配置
│   │   ├── deps.py        # 依赖注入
│   │   └── security.py    # 安全工具
│   ├── curd/              # CRUD 操作
│   │   ├── resources/     # 资源 CRUD
│   │   └── ...
│   ├── models/            # SQLAlchemy 模型
│   │   ├── resource.py    # 资源模型
│   │   ├── learning_path.py # 学习路径模型
│   │   ├── path_item.py   # 路径节点模型
│   │   ├── progress.py    # 进度模型
│   │   ├── category.py    # 分类模型
│   │   ├── user.py        # 用户模型
│   │   ├── subscription.py # 订阅模型
│   │   ├── user_image.py  # 用户图片模型
│   │   ├── user_file.py   # 用户文件模型
│   │   ├── webhook_event.py # Webhook 事件模型
│   │   └── rbac/          # RBAC 模型
│   │       ├── role.py
│   │       ├── permission.py
│   │       ├── user_role.py
│   │       ├── role_permission.py
│   │       └── associations.py
│   ├── routers/           # FastAPI 路由 (旧版)
│   │   ├── auth.py        # 认证
│   │   ├── reader.py      # 阅读模式
│   │   ├── resources/     # 资源
│   │   ├── rbac/          # RBAC
│   │   ├── user_image.py  # 用户图片
│   │   ├── user_file.py   # 用户文件
│   │   └── ...
│   ├── schemas/           # Pydantic 模型
│   │   ├── auth.py
│   │   ├── resource.py
│   │   ├── learning_path.py
│   │   └── ...
│   ├── db/
│   │   └── database.py    # 数据库连接
│   └── main.py            # 应用入口
├── supabase/              # Supabase 配置
├── alembic/               # 数据库迁移
├── tests/                 # 测试文件
├── static/                # 静态文件
├── requirements.txt
├── .env.example
└── .gitignore
```

## API 路由

### 认证 `/auth`
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/auth/register` | 用户注册 |
| POST | `/auth/login` | 用户登录 |
| POST | `/auth/logout` | 用户登出 |
| GET | `/auth/me` | 获取当前用户 |

### 资源 `/resources`
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/resources` | 列表资源 |
| GET | `/resources/{id}` | 资源详情 |
| POST | `/resources/extract` | 从 URL 提取资源信息 |
| GET | `/resources/search` | 搜索 GitHub/YouTube |
| POST | `/resources/me` | 创建资源 |
| GET | `/resources/me` | 我的资源列表 |
| PATCH | `/resources/me/{id}` | 更新我的资源 |
| DELETE | `/resources/me/{id}` | 删除我的资源 |

### 学习路径 `/learning-paths`
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/learning-paths` | 列表路径 |
| GET | `/learning-paths/{id}` | 路径详情 |
| POST | `/learning-paths` | 创建路径 |
| PUT | `/learning-paths/{id}` | 更新路径 |
| DELETE | `/learning-paths/{id}` | 删除路径 |
| GET | `/learning-paths/{id}/items` | 获取路径节点 |
| POST | `/learning-paths/{id}/items` | 添加路径节点 |
| PUT | `/learning-paths/{id}/items/{item_id}` | 更新路径节点 |
| DELETE | `/learning-paths/{id}/items/{item_id}` | 删除路径节点 |

### AI 路径 `/ai-path`
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/ai-path/generate` | 生成 AI 学习路径 |

### 分类 `/categories`
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/categories` | 列表分类 |
| GET | `/categories/{id}` | 分类详情 |
| GET | `/categories/{id}/tree` | 分类树 |

### 进度 `/progress`
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/progress` | 我的进度 |
| POST | `/progress` | 更新进度 |
| GET | `/progress/stats` | 进度统计 |

### 订阅 `/subscriptions`
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/subscriptions` | 我的订阅 |
| POST | `/subscriptions` | 创建订阅 |
| DELETE | `/subscriptions/{id}` | 取消订阅 |

### 阅读模式 `/reader`
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/reader/extract` | 提取网页内容 |

### Webhooks `/webhooks`
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/webhooks/stripe` | Stripe Webhook |

### RBAC
- `/roles` — 角色管理
- `/permissions` — 权限管理
- `/user-roles` — 用户角色
- `/role-permissions` — 角色权限

### 管理 `/admin`
- `/admin/users` — 用户管理
- `/admin/resources` — 资源管理
- `/admin/learning-paths` — 路径管理
- `/admin/analytics` — 数据分析

## 数据库模型

### 核心表
- `users` — 用户
- `categories` — 分类 (树形)
- `resources` — 资源
- `learning_paths` — 学习路径
- `path_items` — 路径节点
- `progress` — 学习进度
- `learning_path_comments` — 路径评论

### 关联表
- `user_resource` — 用户资源收藏
- `user_learning_paths` — 用户路径收藏
- `user_follows` — 用户关注

### 资源扩展
- `videos` — 视频信息
- `articles` — 文章信息
- `docs` — 文档信息

### RBAC
- `roles` — 角色
- `permissions` — 权限
- `role_permissions` — 角色权限
- `user_roles` — 用户角色

### 其他
- `subscriptions` — 订阅
- `user_images` — 用户图片
- `user_files` — 用户文件
- `webhook_events` — Webhook 事件

详细 Schema: [../database_schema.md](../database_schema.md)

## 开发

### 添加新模型
1. 在 `models/` 创建模型文件
2. 在 `schemas/` 创建 Pydantic 模型
3. 在 `curd/` 创建 CRUD 操作
4. 在 `routers/` 创建路由
5. 在 `main.py` 注册路由

### 数据库迁移
```bash
# 生成迁移
alembic revision --autogenerate -m "add xxx"

# 执行迁移
alembic upgrade head
```

### 运行测试
```bash
pytest tests/
```

## License

MIT

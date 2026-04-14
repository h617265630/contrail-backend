# Backend Memory — FastAPI

## 目录结构

```
backend/
├── app/
│   ├── api/           # 业务 API 模块（ai_path 等）
│   ├── routers/       # 标准 REST 路由
│   ├── models/        # SQLAlchemy ORM 模型
│   ├── schemas/       # Pydantic 请求/响应 schema
│   ├── curd/          # 数据库操作层（非 CRUD 拼写）
│   ├── core/          # 配置、依赖注入
│   └── db/            # 数据库连接
├── alembic/           # 数据库迁移
└── scripts/
```

## 认证 & 依赖注入（app/core/deps.py）

| 依赖 | 说明 |
|------|------|
| `get_db_dep()` | yield DB session，所有路由通用 |
| `get_current_user()` | JWT 必须认证，返回 User，401 |
| `get_current_user_optional()` | JWT 可选认证，未登录返回 None |
| `get_current_active_user()` | 在 get_current_user 基础上校验 is_active |
| `PermissionChecker(["perm"])` | 检查用户拥有所有指定权限，superuser 跳过 |
| `RoleChecker(["role"])` | 检查用户拥有任一指定角色，superuser 跳过 |

JWT：`SECRET_KEY` + `ALGORITHM` 来自 `settings`，token 从 `Authorization: Bearer` 获取

## 路由分层

- `app/routers/` — 标准资源路由（resources、learning_path 等）
- `app/api/` — 复杂业务模块（ai_path，含 service 层）

## AI Path 模块（app/api/ai_path/）

| 文件 | 说明 |
|------|------|
| `router.py` | FastAPI 路由定义 |
| `service.py` | 调用 ai_path LangGraph 流水线 |
| `prompts.py` | 节点 explanation / tutorial 模板 |

### 端点
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/ai-path/generate` | 运行完整流水线生成学习路径 |
| POST | `/ai-path/search-resources` | Web（Tavily）+ GitHub 并发搜索 |
| GET  | `/ai-path/cached-results/{topic}` | 读缓存，不消耗外部 API |

### search-resources 请求体
```json
{ "query": "string", "exclude_urls": ["url1", "url2"] }
```
`exclude_urls` 用于 Shuffle，传入已展示 URL，后端在搜索阶段就排除（已修复）

## 数据库 CURD 层

- 命名：`XxxCURD`，静态方法，接收 `db: Session` 作为第一参数
- 缓存表：`resource_summary_cache`，按 `(url, topic)` 唯一，避免重复 LLM 摘要
  - CURD：`app/curd/resource_summary_cache_curd.py`
  - 方法：`get(db, url, topic)`、`upsert(...)`、`get_multi_by_topic(db, topic, limit)`

## 迁移规范

- 文件命名：`YYYYMMDD_NNNN_描述.py`
- 运行：`alembic upgrade head`

## 已知修复

### [2026-04-14] exclude_urls 未传入流水线导致搜索重复
- `service.py` `search_resources_pipeline` 的 `initial` state 现已包含 `exclude_urls`
- 缓存层遇到被排除的 URL 会直接跳过

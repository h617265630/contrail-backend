# 用户管理 FastAPI 项目

## 项目简介

本项目基于 **FastAPI** + **SQLAlchemy/SQLModel** + **PostgreSQL** 构建，提供用户注册、登录、获取当前用户等基础认证能力。密码使用 `passlib` 的 `bcrypt` 算法进行加密，登录后返回 JWT Token，并通过依赖注入的方式实现鉴权。

主要模块：
- `app/routers/user.py`：用户注册、登录、当前用户、列表、详情等 API 路由。
- `app/curd/user.py`：封装用户相关的数据库操作。
- `app/models/User.py`：定义用户 ORM 模型。
- `app/auth.py`：密码哈希、Token 生成与校验工具函数。
- `app/deps.py`：通用依赖，例如获取数据库 Session、解析当前用户。
- `app/con_db/database.py`：数据库连接、Session 工厂与 `Base` 定义。

## 环境准备

1. 安装 **Python 3.11**。
2. 准备可访问的 PostgreSQL 数据库，确保账号密码与数据库名称正确。
3. 推荐使用虚拟环境隔离依赖（例：`python -m venv .venv`）。
4. 使用anaconda 创建虚拟环境，python 版本3.11
5. 本地安装 postgres 数据库

## 依赖安装

克隆该项目到本地文件夹
git clone https://github.com/h617265630/stepbystep

在本地安装pgsql , 并且新建数据库。db文件夹里的database 根据本地pgsql的数据库名修改连接的数据库。

在该文件的 step目录下执行： 根据自己的虚拟环境。
```powershell
Set-Location 'C:\Users\Administrator\Videos\stepbystep\step'
python -m venv .venv
.\.venv\Scripts\Activate
pip install --upgrade pip
pip install -r requirements.txt
```

若需要开发依赖（如测试、迁移），`requirements.txt` 已包含 `pytest`、`alembic`、`httpx` 等可选组件。

## 环境变量

建议使用 `.env` 文件集中管理敏感配置，可参考：

```
SECRET_KEY=请替换为强随机字符串
DATABASE_URL=postgresql://postgres:密码@localhost/db
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

在应用入口（如 `app/main.py`）调用 `python-dotenv` 的 `load_dotenv()`，即可在运行时加载环境变量。

## 运行项目

1. 自动创建数据表：应用启动时会执行 `Base.metadata.create_all(bind=engine)`。
2. 启动开发服务器（默认端口 8000）：

```powershell
Set-Location 'C:\Users\Administrator\Videos\stepbystep\step'
cd 到 step 目录下
uvicorn app.main:app --reload --port 8000 --log-level debug
```


3. 打开接口文档：访问 `http://127.0.0.1:8000/docs`。

## 常用接口示例

- **注册用户**：`POST /users/register`
- **登录获取 Token**：`POST /users/login`
- **获取当前用户**：`GET /users/me`
- **获取用户列表**：`GET /users/`

示例（PowerShell 调用注册接口）：

```powershell
$body = @{ username='demo'; email='demo@example.com'; password='P@ssw0rd!' } | ConvertTo-Json
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/users/register' -Method Post -Body $body -ContentType 'application/json'
```

## 测试与验证（可选）

若安装了 `pytest`，可在 `tests/` 目录添加测试，然后执行：

```powershell
pytest
```

手动验证密码哈希是否存储在数据库中：

```powershell
psql -h localhost -U postgres -d db -c "SELECT username, password FROM users LIMIT 5;"
```

## 常见问题排查

1. **500 Internal Server Error**：检查服务器终端日志，确认是否为重复注册（可能触发数据库唯一约束）或环境变量未配置。
2. **导入失败**：确保 `step` 及子目录包含 `__init__.py`，并在项目根运行 uvicorn。
3. **依赖报错**：执行 `pip install -r requirements.txt --force-reinstall` 以刷新依赖。

## 下一步建议

- 在 `create_user` 中捕获 `sqlalchemy.exc.IntegrityError`，提升错误提示。
- 将 SECRET_KEY / DATABASE_URL 等敏感信息完全迁移到环境变量。
- 引入 Alembic 管理数据库迁移，便于团队协作。
- 编写集成测试并在 CI 中执行，防止回归。

---

如需进一步扩展（邮件验证、刷新 Token、Docker 部署等），可在现有结构上逐步迭代。祝开发顺利！

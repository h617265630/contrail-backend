from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from pathlib import Path
from app.api.learning_path.router import router as learning_path_router
from app.api.progress.router import router as progress_router
from app.api.category.router import router as category_router
from app.api.admin.router import router as admin_router
from app.routers import reader
from app.routers import user_image
from app.routers import user_file
from app.api.trending.router import router as trending_router
from app.api.ai_path.router import router as ai_path_router
from app.routers.rbac import role, user, permission, user_role, role_permission
from app.core.config import settings


from app.db.database import engine, Base

# Ensure rbac model modules (including association classes) are imported so
# SQLAlchemy can resolve relationships that reference mapped classes/tables.
import app.models.rbac.associations
import app.models.rbac.user
import app.models.rbac.role
import app.models.rbac.permission

# 确保关联/中间表与关系类被加载，避免字符串解析失败
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import SessionLocal
from app.core.initial_data import init_default_data
from app.routers.resources import product, resource
from app.api.subscription.router import router as subscription_router
from app.api.webhooks.router import router as webhooks_router

# Ensure generic resource models are imported before create_all
import app.models.user_resource
import app.models.resources.video
import app.models.resources.doc
import app.models.resources.article
import app.models.resource
import app.models.learning_path
import app.models.path_item
import app.models.category
import app.models.progress
import app.models.user_image
import app.models.user_file
import app.models.subscription
import app.models.webhook_event

Base.metadata.create_all(bind=engine)

"""
Custom FastAPI app with local Swagger UI assets to avoid CDN timeouts.
"""
app = FastAPI(
    title="User Management API",
    debug=settings.APP_DEBUG,
    docs_url=None,
    redoc_url=None,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    # When allow_credentials=True, browsers reject Access-Control-Allow-Origin='*'.
    # Explicitly allow the Vite dev origins to prevent axios 'Network Error' caused by CORS.
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}


# Serve local static files (e.g., Swagger UI assets) from backend/static.
# Use an absolute path so the app can be started from any working directory.
_STATIC_DIR = (Path(__file__).resolve().parents[1] / "static").as_posix()
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


# Custom /docs using local swagger-ui assets
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="API Docs",
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
    )


app.include_router(user.router)
app.include_router(learning_path_router)
app.include_router(progress_router)
app.include_router(category_router)
app.include_router(reader.router)
app.include_router(product.router)
app.include_router(resource.router)
app.include_router(role.router)
app.include_router(permission.router)
app.include_router(user_role.router)
app.include_router(role_permission.router)
app.include_router(user_image.router)
app.include_router(user_file.router)
app.include_router(subscription_router)
app.include_router(webhooks_router)
app.include_router(trending_router)
app.include_router(ai_path_router)
app.include_router(admin_router)


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据"""
    # 防止同一进程内重复初始化（如被多次触发）
    if getattr(app.state, "initialized", False):
        return
    app.state.initialized = True

    # 使用上下文管理自动关闭会话
    with SessionLocal() as db:
        init_default_data(db)

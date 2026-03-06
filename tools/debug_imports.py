"""
检查所有导入是否正常
运行方式：python debug_imports.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("检查项目导入...")
print("=" * 60)

errors = []

# 检查 1: database 模块
print("\n1. 检查 app.con_db.database...")
try:
    from app.con_db.database import Base, engine, get_db
    print("   ✅ app.con_db.database 导入成功")
    print(f"   - Base: {Base}")
    print(f"   - engine: {engine}")
    print(f"   - get_db: {get_db}")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    errors.append(("app.con_db.database", str(e)))

# 检查 2: models
print("\n2. 检查 app.models.User...")
try:
    from app.models.User import User
    print("   ✅ app.models.User 导入成功")
    print(f"   - User 表名: {User.__tablename__}")
    print(f"   - User 列: {User.__table__.columns.keys()}")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    errors.append(("app.models.User", str(e)))

# 检查 3: schemas
print("\n3. 检查 app.schemas.user...")
try:
    from app.schemas.user import UserCreate, UserOut
    print("   ✅ app.schemas.user 导入成功")
    print(f"   - UserCreate 字段: {UserCreate.model_fields.keys()}")
    print(f"   - UserOut 字段: {UserOut.model_fields.keys()}")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    errors.append(("app.schemas.user", str(e)))

# 检查 4: auth
print("\n4. 检查 app.auth...")
try:
    from app.auth import hash_password, verify_password
    print("   ✅ app.auth 导入成功")
    # 测试密码哈希
    test_hash = hash_password("test123")
    is_valid = verify_password("test123", test_hash)
    print(f"   - 密码哈希测试: {'✅ 通过' if is_valid else '❌ 失败'}")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    errors.append(("app.auth", str(e)))

# 检查 5: curd
print("\n5. 检查 app.curd.user...")
try:
    from app.curd.user import create_user, get_user_by_username
    print("   ✅ app.curd.user 导入成功")
    print(f"   - create_user: {create_user}")
    print(f"   - get_user_by_username: {get_user_by_username}")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    errors.append(("app.curd.user", str(e)))

# 检查 6: deps
print("\n6. 检查 app.deps...")
try:
    from app.deps import get_db_dep, get_current_user
    print("   ✅ app.deps 导入成功")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    errors.append(("app.deps", str(e)))

# 检查 7: routers
print("\n7. 检查 app.routers.user...")
try:
    from app.routers.user import router
    print("   ✅ app.routers.user 导入成功")
    print(f"   - 路由前缀: {router.prefix}")
    print(f"   - 路由数量: {len(router.routes)}")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    errors.append(("app.routers.user", str(e)))

# 检查 8: main app
print("\n8. 检查 app.main...")
try:
    from app.main import app
    print("   ✅ app.main 导入成功")
    print(f"   - 应用标题: {app.title}")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    errors.append(("app.main", str(e)))

# 汇总结果
print("\n" + "=" * 60)
if errors:
    print(f"❌ 发现 {len(errors)} 个导入错误:")
    for module, error in errors:
        print(f"\n模块: {module}")
        print(f"错误: {error}")
else:
    print("✅ 所有导入检查通过！")
    print("\n下一步:")
    print("1. 启动服务器: uvicorn app.main:app --reload")
    print("2. 运行测试: python test_register.py")
print("=" * 60)

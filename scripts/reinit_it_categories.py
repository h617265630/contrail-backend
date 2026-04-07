#!/usr/bin/env python3
"""
重新设置IT技术相关的分类体系
将数据库中的分类统一为IT方向

运行: cd backend && python -m scripts.reinit_it_categories
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.db.database import SessionLocal


# 新的IT分类体系
NEW_IT_CATEGORIES = [
    {"name": "AI / Machine Learning", "code": "ai_ml", "description": "LLM, NLP, CV, AI应用开发"},
    {"name": "Frontend", "code": "frontend", "description": "React, Vue, CSS, TypeScript, 移动端H5"},
    {"name": "Backend", "code": "backend", "description": "Node.js, Python后端, Go, Java, 微服务"},
    {"name": "DevOps / Cloud", "code": "devops_cloud", "description": "Docker, K8s, CI/CD, AWS/GCP, Linux"},
    {"name": "Database", "code": "database", "description": "SQL, NoSQL, Redis, PostgreSQL, 数据建模"},
    {"name": "Mobile", "code": "mobile", "description": "iOS, Android, Flutter, React Native"},
    {"name": "Data / Analytics", "code": "data_analytics", "description": "Python数据分析, Pandas, BI, 大数据"},
    {"name": "Security", "code": "security", "description": "Web安全, 网络安全, 渗透测试, CTF"},
    {"name": "Product / Design", "code": "product_design", "description": "产品设计, UX, Figma, 项目管理"},
    {"name": "CS Fundamentals", "code": "cs_fundamentals", "description": "算法, 系统设计, 操作系统, 网络, 面试"},
    {"name": "Other", "code": "other", "description": "其他IT相关资源"},
]

# 旧分类到新分类的映射
CATEGORY_MAPPING = {
    "ai": "ai_ml", "machine_learning": "ai_ml", "deep_learning": "ai_ml",
    "nlp": "ai_ml", "computer_vision": "ai_ml", "llm": "ai_ml",
    "gpt": "ai_ml", "chatgpt": "ai_ml", "genai": "ai_ml", "generative_ai": "ai_ml",
    "frontend": "frontend", "react": "frontend", "vue": "frontend", "css": "frontend",
    "javascript": "frontend", "typescript": "frontend", "tailwind": "frontend",
    "html": "frontend", "web_development": "frontend", "ui": "frontend",
    "backend": "backend", "nodejs": "backend", "node.js": "backend", "python": "backend",
    "java": "backend", "golang": "backend", "go": "backend", "php": "backend",
    "django": "backend", "flask": "backend", "spring": "backend", "spring_boot": "backend",
    "api": "backend", "restful": "backend", "graphql": "backend", "microservices": "backend",
    "devops": "devops_cloud", "docker": "devops_cloud", "kubernetes": "devops_cloud",
    "k8s": "devops_cloud", "cicd": "devops_cloud", "ci_cd": "devops_cloud",
    "aws": "devops_cloud", "gcp": "devops_cloud", "azure": "devops_cloud",
    "cloud": "devops_cloud", "linux": "devops_cloud", "shell": "devops_cloud",
    "bash": "devops_cloud", "infrastructure": "devops_cloud",
    "database": "database", "sql": "database", "nosql": "database",
    "postgresql": "database", "postgres": "database", "mysql": "database",
    "mongodb": "database", "redis": "database", "data_modeling": "database",
    "mobile": "mobile", "ios": "mobile", "android": "mobile", "flutter": "mobile",
    "react_native": "mobile", "swift": "mobile", "kotlin": "mobile",
    "xcode": "mobile", "android_studio": "mobile", "app_development": "mobile",
    "data_science": "data_analytics", "data_analysis": "data_analytics",
    "pandas": "data_analytics", "numpy": "data_analytics", "jupyter": "data_analytics",
    "notebook": "data_analytics", "bi": "data_analytics", "business_intelligence": "data_analytics",
    "big_data": "data_analytics", "hadoop": "data_analytics", "spark": "data_analytics",
    "ml": "data_analytics", "data_engineering": "data_analytics",
    "security": "security", "cybersecurity": "security", "web_security": "security",
    "penetration_testing": "security", "pen_test": "security", "ctf": "security",
    "owasp": "security", "ethical_hacking": "security", "infosec": "security",
    "product_design": "product_design", "design": "product_design", "ux": "product_design",
    "ui_design": "product_design", "figma": "product_design", "sketch": "product_design",
    "product_management": "product_design", "pm": "product_design", "agile": "product_design",
    "scrum": "product_design", "product_manager": "product_design",
    "cs_fundamentals": "cs_fundamentals", "algorithms": "cs_fundamentals",
    "data_structures": "cs_fundamentals", "system_design": "cs_fundamentals",
    "coding_interview": "cs_fundamentals", "interview": "cs_fundamentals",
    "leetcode": "cs_fundamentals", "algorithms_and_data_structures": "cs_fundamentals",
    "operating_system": "cs_fundamentals", "os": "cs_fundamentals",
    "computer_networks": "cs_fundamentals", "networking": "cs_fundamentals",
    "distributed_systems": "cs_fundamentals", "object_oriented": "cs_fundamentals", "oop": "cs_fundamentals",
    "handmade": "other", "crafts": "other", "diy": "other",
    "other": "other",
}


def create_new_categories(db):
    """创建新的IT分类"""
    print("\n📁 创建新的IT分类...")

    created = 0
    for cat_data in NEW_IT_CATEGORIES:
        # 检查是否已存在
        existing = db.execute(
            text("SELECT id FROM categories WHERE code = :code"),
            {"code": cat_data["code"]}
        ).fetchone()

        if not existing:
            db.execute(
                text("""INSERT INTO categories (name, code, description, level, is_leaf, is_system, owner_user_id, created_at)
                   VALUES (:name, :code, :description, 0, true, true, NULL, NOW())"""),
                {"name": cat_data["name"], "code": cat_data["code"], "description": cat_data.get("description")}
            )
            created += 1
            print(f"  ✅ 创建: {cat_data['name']} ({cat_data['code']})")
        else:
            # 更新现有分类名称
            db.execute(
                text("UPDATE categories SET name = :name, description = :description WHERE code = :code"),
                {"name": cat_data["name"], "description": cat_data.get("description"), "code": cat_data["code"]}
            )
            print(f"  🔄 更新: {cat_data['code']} -> {cat_data['name']}")

    db.commit()
    print(f"\n共创建了 {created} 个新分类")


def get_category_id_by_code(db, code: str) -> int:
    """根据code获取分类ID"""
    result = db.execute(
        text("SELECT id FROM categories WHERE code = :code"),
        {"code": code}
    ).fetchone()
    return result[0] if result else None


def migrate_resources(db):
    """迁移资源到新分类"""
    print("\n📦 迁移资源分类...")

    new_category_codes = [c["code"] for c in NEW_IT_CATEGORIES]
    placeholders = ','.join([f':code{i}' for i in range(len(new_category_codes))])
    params = {f"code{i}": code for i, code in enumerate(new_category_codes)}

    # 获取所有需要迁移的资源
    result = db.execute(
        text(f"""
            SELECT r.id, r.category_id, c.code as old_code
            FROM resources r
            LEFT JOIN categories c ON r.category_id = c.id
            WHERE c.code NOT IN ({placeholders}) OR c.code IS NULL
        """),
        params
    )

    resources_to_migrate = result.fetchall()
    migrated_count = 0
    other_id = get_category_id_by_code(db, "other")

    for row in resources_to_migrate:
        resource_id, old_cat_id, old_code = row
        new_code = CATEGORY_MAPPING.get(old_code, "other") if old_code else "other"
        new_cat_id = get_category_id_by_code(db, new_code)

        if new_cat_id and new_cat_id != old_cat_id:
            db.execute(
                text("UPDATE resources SET category_id = :new_cat_id WHERE id = :resource_id"),
                {"new_cat_id": new_cat_id, "resource_id": resource_id}
            )
            migrated_count += 1
        elif other_id and old_cat_id:
            db.execute(
                text("UPDATE resources SET category_id = :other_id WHERE id = :resource_id"),
                {"other_id": other_id, "resource_id": resource_id}
            )
            migrated_count += 1

    db.commit()
    print(f"  ✅ 迁移了 {migrated_count} 个资源")


def migrate_learning_paths(db):
    """迁移学习路径到新分类"""
    print("\n📚 迁移学习路径分类...")

    new_category_codes = [c["code"] for c in NEW_IT_CATEGORIES]
    placeholders = ','.join([f':code{i}' for i in range(len(new_category_codes))])
    params = {f"code{i}": code for i, code in enumerate(new_category_codes)}

    result = db.execute(
        text(f"""
            SELECT lp.id, lp.category_id, c.code as old_code
            FROM learning_paths lp
            LEFT JOIN categories c ON lp.category_id = c.id
            WHERE c.code NOT IN ({placeholders}) OR c.code IS NULL
        """),
        params
    )

    paths_to_migrate = result.fetchall()
    migrated_count = 0
    other_id = get_category_id_by_code(db, "other")

    for row in paths_to_migrate:
        path_id, old_cat_id, old_code = row
        new_code = CATEGORY_MAPPING.get(old_code, "other") if old_code else "other"
        new_cat_id = get_category_id_by_code(db, new_code)

        if new_cat_id and new_cat_id != old_cat_id:
            db.execute(
                text("UPDATE learning_paths SET category_id = :new_cat_id WHERE id = :path_id"),
                {"new_cat_id": new_cat_id, "path_id": path_id}
            )
            migrated_count += 1
        elif other_id and old_cat_id:
            db.execute(
                text("UPDATE learning_paths SET category_id = :other_id WHERE id = :path_id"),
                {"other_id": other_id, "path_id": path_id}
            )
            migrated_count += 1

    db.commit()
    print(f"  ✅ 迁移了 {migrated_count} 个学习路径")


def delete_non_it_categories(db):
    """删除非IT分类（如果没有被使用）"""
    print("\n🗑️  检查并删除未使用的非IT分类...")

    new_category_codes = [c["code"] for c in NEW_IT_CATEGORIES]
    placeholders = ','.join([f':code{i}' for i in range(len(new_category_codes))])
    params = {f"code{i}": code for i, code in enumerate(new_category_codes)}

    result = db.execute(
        text(f"""
            SELECT c.id, c.name, c.code
            FROM categories c
            WHERE c.code NOT IN ({placeholders})
        """),
        params
    )

    non_it_cats = result.fetchall()
    deleted = 0

    for cat_id, cat_name, cat_code in non_it_cats:
        # 检查是否被资源使用
        resource_count = db.execute(
            text("SELECT COUNT(*) FROM resources WHERE category_id = :cat_id"),
            {"cat_id": cat_id}
        ).fetchone()[0]

        # 检查是否被学习路径使用
        path_count = db.execute(
            text("SELECT COUNT(*) FROM learning_paths WHERE category_id = :cat_id"),
            {"cat_id": cat_id}
        ).fetchone()[0]

        if resource_count == 0 and path_count == 0:
            # 先将子分类的 parent_id 设为 NULL
            db.execute(text("UPDATE categories SET parent_id = NULL WHERE parent_id = :cat_id"), {"cat_id": cat_id})
            db.execute(text("DELETE FROM categories WHERE id = :cat_id"), {"cat_id": cat_id})
            deleted += 1
            print(f"  🗑️  删除空分类: {cat_name} ({cat_code})")
        else:
            print(f"  ⏭️  跳过 (已被使用): {cat_name} ({cat_code}) - {resource_count} resources, {path_count} paths")

    db.commit()
    print(f"\n共删除了 {deleted} 个空分类")


def print_summary(db):
    """打印分类统计"""
    print("\n" + "=" * 70)
    print("📊 最终分类状态")
    print("=" * 70)

    for cat_data in NEW_IT_CATEGORIES:
        cat_id = get_category_id_by_code(db, cat_data["code"])
        if cat_id:
            resource_count = db.execute(
                text("SELECT COUNT(*) FROM resources WHERE category_id = :cat_id"),
                {"cat_id": cat_id}
            ).fetchone()[0]
            path_count = db.execute(
                text("SELECT COUNT(*) FROM learning_paths WHERE category_id = :cat_id"),
                {"cat_id": cat_id}
            ).fetchone()[0]
            print(f"  {cat_data['name']:25s} | resources: {resource_count:3d} | paths: {path_count:2d}")

    total_resources = db.execute(text("SELECT COUNT(*) FROM resources")).fetchone()[0]
    total_paths = db.execute(text("SELECT COUNT(*) FROM learning_paths")).fetchone()[0]
    print("-" * 70)
    print(f"  {'总计':25s} | resources: {total_resources:3d} | paths: {total_paths:3d}")
    print("=" * 70)


def main():
    print("=" * 70)
    print("🔄 开始重新设置IT分类体系")
    print("=" * 70)

    db = SessionLocal()
    try:
        # 1. 创建新分类
        create_new_categories(db)

        # 2. 迁移现有资源
        migrate_resources(db)

        # 3. 迁移学习路径
        migrate_learning_paths(db)

        # 4. 删除未使用的非IT分类
        delete_non_it_categories(db)

        # 5. 打印统计
        print_summary(db)

        print("\n✅ 分类重新设置完成！")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
手动初始化分类数据的脚本
用于确保数据库中有默认分类数据
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.db.database import SessionLocal
from app.core.initial_data import init_default_categories

# 导入所有模型以确保 SQLAlchemy 能正确解析关系
import app.models.rbac.associations
import app.models.rbac.user
import app.models.rbac.role
import app.models.rbac.permission
import app.models.user_resource
import app.models.user_learning_path
import app.models.user_video
import app.models.resources.video
import app.models.resources.doc
import app.models.resources.article
import app.models.resources.clip
import app.models.resources.product
import app.models.resources.link
import app.models.resource
import app.models.learning_path
import app.models.learning_path_comment
import app.models.path_item
import app.models.path_progress
import app.models.category
import app.models.progress
import app.models.relations
import app.models.video_category
import app.models.watch_history

def main():
    print("=" * 60)
    print("开始初始化分类数据...")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        init_default_categories(db)
        print("\n" + "=" * 60)
        print("✅ 分类数据初始化完成！")
        print("=" * 60)
        
        # 验证：列出所有分类
        from app.models.category import Category
        categories = db.query(Category).all()
        print(f"\n当前数据库中共有 {len(categories)} 个分类：")
        for cat in categories:
            owner_info = f"(owner_user_id={cat.owner_user_id})" if cat.owner_user_id else "(系统分类)"
            print(f"  - ID={cat.id}, code={cat.code}, name={cat.name}, is_system={cat.is_system} {owner_info}")
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()

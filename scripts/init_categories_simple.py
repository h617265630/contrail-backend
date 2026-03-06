#!/usr/bin/env python3
"""
使用原始 SQL 直接初始化分类数据，避免 ORM 模型依赖问题
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from sqlalchemy import create_engine, text

def main():
    print("=" * 60)
    print("开始初始化分类数据...")
    print("=" * 60)
    
    # 直接使用配置中的数据库 URL
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # 插入默认分类（使用 ON CONFLICT DO NOTHING 避免重复）
            insert_sql = text("""
                INSERT INTO categories (name, code, level, is_leaf, is_system, owner_user_id, description)
                VALUES 
                    ('AI', 'ai', 0, true, true, NULL, 'AI related resources'),
                    ('Design', 'design', 0, true, true, NULL, 'Design related resources'),
                    ('UI', 'ui', 0, true, true, NULL, 'UI design related resources'),
                    ('Frontend', 'frontend', 0, true, true, NULL, 'Frontend development related resources'),
                    ('Backend', 'backend', 0, true, true, NULL, 'Backend development related resources'),
                    ('Handmade', 'handmade', 0, true, true, NULL, 'Handmade / craft related resources'),
                    ('Other', 'other', 0, true, true, NULL, 'Other resources')
                ON CONFLICT (code) DO NOTHING
            """)
            
            result = conn.execute(insert_sql)
            conn.commit()
            
            print(f"✅ 插入操作完成（受影响行数：{result.rowcount}）")
            
            # 查询并显示所有分类
            select_sql = text("SELECT id, name, code, is_system, owner_user_id FROM categories ORDER BY id")
            categories = conn.execute(select_sql).fetchall()
            
            print("\n" + "=" * 60)
            print(f"当前数据库中共有 {len(categories)} 个分类：")
            print("=" * 60)
            for cat in categories:
                owner_info = f"(owner_user_id={cat.owner_user_id})" if cat.owner_user_id else "(系统分类)"
                print(f"  - ID={cat.id}, code={cat.code:12s}, name={cat.name:8s}, is_system={cat.is_system} {owner_info}")
            
            print("\n" + "=" * 60)
            print("🎉 分类数据初始化完成！")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

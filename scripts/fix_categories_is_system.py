#!/usr/bin/env python3
"""
修复分类的 is_system 字段，将系统默认分类设置为 is_system=True
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from sqlalchemy import create_engine, text

def main():
    print("=" * 60)
    print("修复分类的 is_system 字段")
    print("=" * 60)
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # 将所有默认分类的 is_system 设置为 True
            update_sql = text("""
                UPDATE categories 
                SET is_system = TRUE 
                WHERE code IN ('ai', 'design', 'ui', 'frontend', 'backend', 'handmade', 'other')
                  AND owner_user_id IS NULL
            """)
            
            result = conn.execute(update_sql)
            conn.commit()
            
            print(f"✅ 更新完成（受影响行数：{result.rowcount}）")
            
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
            print("🎉 修复完成！")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

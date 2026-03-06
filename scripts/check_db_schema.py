#!/usr/bin/env python3
"""
检查数据库表结构
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from sqlalchemy import create_engine, text

def main():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # 检查 resources 表结构
        print("=" * 60)
        print("resources 表结构:")
        print("=" * 60)
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'resources'
            ORDER BY ordinal_position
        """))
        for row in result:
            print(f"  {row[0]:30s} {row[1]}")
        
        # 检查用户资源关联表
        print("\n" + "=" * 60)
        print("查找用户资源关联表:")
        print("=" * 60)
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%user%resource%'
        """))
        tables = result.fetchall()
        if tables:
            for t in tables:
                print(f"  找到表: {t[0]}")
                result2 = conn.execute(text(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{t[0]}'
                    ORDER BY ordinal_position
                """))
                for row in result2:
                    print(f"    - {row[0]:30s} {row[1]}")
        else:
            print("  未找到用户资源关联表")

if __name__ == "__main__":
    main()

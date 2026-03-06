#!/usr/bin/env python3
"""
使用 SQL 直接插入测试资源，避免 ORM 关系问题
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from sqlalchemy import create_engine, text

def main():
    print("=" * 60)
    print("开始添加测试资源（使用 SQL）")
    print("=" * 60)
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # 获取 admin 用户 ID
            result = conn.execute(text("SELECT id FROM users WHERE username = 'admin' LIMIT 1"))
            user_row = result.fetchone()
            if not user_row:
                print("❌ 未找到 admin 用户")
                sys.exit(1)
            user_id = user_row[0]
            print(f"✅ 找到用户 admin (ID={user_id})")
            
            # 获取 AI 分类 ID
            result = conn.execute(text("SELECT id FROM categories WHERE code = 'ai' LIMIT 1"))
            cat_row = result.fetchone()
            if not cat_row:
                print("❌ 未找到 AI 分类")
                sys.exit(1)
            category_id = cat_row[0]
            print(f"✅ 找到分类 AI (ID={category_id})")
            
            # 测试资源列表
            test_resources = [
                {
                    "name": "Bilibili 视频",
                    "resource_type": "video",
                    "platform": "bilibili",
                    "title": "【测试】Bilibili 视频资源",
                    "summary": "这是一个来自 Bilibili 的测试视频资源",
                    "source_url": "https://www.bilibili.com/video/BV1GJ411x7h7",
                    "thumbnail": "https://i0.hdslb.com/bfs/archive/test.jpg",
                },
                {
                    "name": "小红书视频",
                    "resource_type": "video",
                    "platform": "xiaohongshu",
                    "title": "【测试】小红书视频资源",
                    "summary": "这是一个来自小红书的测试视频资源",
                    "source_url": "https://www.xiaohongshu.com/explore/65a1b2c3d4e5f6g7h8i9j0k1",
                    "thumbnail": "https://sns-img-qc.xhscdn.com/test.jpg",
                },
                {
                    "name": "Medium 文章",
                    "resource_type": "article",
                    "platform": "medium",
                    "title": "【测试】Understanding Machine Learning Basics",
                    "summary": "A comprehensive guide to machine learning fundamentals",
                    "source_url": "https://medium.com/@example/understanding-machine-learning-basics-123abc",
                    "thumbnail": "https://miro.medium.com/max/test.jpg",
                },
                {
                    "name": "GitHub 文档",
                    "resource_type": "document",
                    "platform": "github",
                    "title": "【测试】OpenAI GPT-3 Repository",
                    "summary": "Official repository for GPT-3 documentation and examples",
                    "source_url": "https://github.com/openai/gpt-3",
                    "thumbnail": "https://opengraph.githubassets.com/test.png",
                },
                {
                    "name": "Medium 文章 2",
                    "resource_type": "article",
                    "platform": "medium",
                    "title": "【测试】Deep Learning Explained",
                    "summary": "An in-depth explanation of deep learning concepts and applications",
                    "source_url": "https://medium.com/@techwriter/deep-learning-explained-456def",
                    "thumbnail": "https://miro.medium.com/max/test2.jpg",
                },
            ]
            
            print("\n" + "=" * 60)
            print("开始插入资源...")
            print("=" * 60)
            
            added_count = 0
            
            for idx, res in enumerate(test_resources, 1):
                print(f"\n[{idx}/{len(test_resources)}] 添加 {res['name']}...")
                print(f"  类型: {res['resource_type']}")
                print(f"  平台: {res['platform']}")
                
                try:
                    # 插入 resource
                    insert_resource = text("""
                        INSERT INTO resources (
                            resource_type, platform, title, summary, source_url, 
                            thumbnail, category_id, difficulty, tags, raw_meta, 
                            is_system_public, created_at
                        ) VALUES (
                            :resource_type, :platform, :title, :summary, :source_url,
                            :thumbnail, :category_id, NULL, '{}', '{}',
                            FALSE, NOW()
                        ) RETURNING id
                    """)
                    
                    result = conn.execute(insert_resource, {
                        "resource_type": res["resource_type"],
                        "platform": res["platform"],
                        "title": res["title"],
                        "summary": res["summary"],
                        "source_url": res["source_url"],
                        "thumbnail": res["thumbnail"],
                        "category_id": category_id,
                    })
                    resource_id = result.fetchone()[0]
                    
                    # 根据类型插入对应的子表
                    if res["resource_type"] == "video":
                        conn.execute(text("""
                            INSERT INTO videos (resource_id, duration, channel, video_id)
                            VALUES (:resource_id, NULL, NULL, NULL)
                        """), {"resource_id": resource_id})
                    elif res["resource_type"] == "document":
                        conn.execute(text("""
                            INSERT INTO docs (resource_id, doc_type, version)
                            VALUES (:resource_id, NULL, NULL)
                        """), {"resource_id": resource_id})
                    elif res["resource_type"] == "article":
                        conn.execute(text("""
                            INSERT INTO articles (resource_id, publisher, published_at)
                            VALUES (:resource_id, NULL, NULL)
                        """), {"resource_id": resource_id})
                    
                    # 关联到用户
                    conn.execute(text("""
                        INSERT INTO user_resource (user_id, resource_id, is_public)
                        VALUES (:user_id, :resource_id, FALSE)
                    """), {"user_id": user_id, "resource_id": resource_id})
                    
                    conn.commit()
                    
                    print(f"  ✅ 成功添加！(ID={resource_id})")
                    added_count += 1
                    
                except Exception as e:
                    print(f"  ⚠️  添加失败: {e}")
                    conn.rollback()
                    continue
            
            print("\n" + "=" * 60)
            print(f"✅ 成功添加 {added_count}/{len(test_resources)} 条资源")
            print("=" * 60)
            
            # 验证：查询所有资源
            print("\n验证：查询所有测试资源...")
            result = conn.execute(text("""
                SELECT r.id, r.resource_type, r.platform, r.title
                FROM resources r
                JOIN user_resource ur ON ur.resource_id = r.id
                WHERE ur.user_id = :user_id
                ORDER BY r.id DESC
                LIMIT 10
            """), {"user_id": user_id})
            
            resources = result.fetchall()
            print(f"\n当前用户共有 {len(resources)} 条资源：")
            for res in resources:
                print(f"  - [{res[1]:8s}] {res[2]:12s} | {res[3]}")
            
            print("\n" + "=" * 60)
            print("🎉 测试资源添加完成！")
            print("=" * 60)
            print("\n提示：现在可以在前端 http://localhost:5173/my-resources 查看这些资源")
            
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

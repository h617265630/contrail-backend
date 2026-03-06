#!/usr/bin/env python3
"""
添加测试资源到数据库
- Bilibili video
- 小红书 video
- Medium article
- GitHub document
- Medium article (另一条)
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

# 导入所有必要的模型
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

from app.db.database import SessionLocal
from app.curd.resources.resource_curd import ResourceCURD
from app.models.category import Category
from app.models.rbac.user import User

def main():
    print("=" * 60)
    print("开始添加测试资源")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 获取 admin 用户
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("❌ 未找到 admin 用户，请先创建")
            sys.exit(1)
        
        print(f"✅ 找到用户: {admin.username} (ID={admin.id})")
        
        # 获取默认分类（AI）
        ai_category = db.query(Category).filter(Category.code == "ai").first()
        if not ai_category:
            print("❌ 未找到 AI 分类")
            sys.exit(1)
        
        print(f"✅ 找到分类: {ai_category.name} (ID={ai_category.id})")
        
        # 测试资源列表
        test_resources = [
            {
                "name": "Bilibili 视频",
                "url": "https://www.bilibili.com/video/BV1GJ411x7h7",
                "type": "video"
            },
            {
                "name": "小红书视频",
                "url": "https://www.xiaohongshu.com/explore/65a1b2c3d4e5f6g7h8i9j0k1",
                "type": "video"
            },
            {
                "name": "Medium 文章",
                "url": "https://medium.com/@example/understanding-machine-learning-basics-123abc",
                "type": "article"
            },
            {
                "name": "GitHub 文档",
                "url": "https://github.com/openai/gpt-3",
                "type": "document"
            },
            {
                "name": "Medium 文章 2",
                "url": "https://medium.com/@techwriter/deep-learning-explained-456def",
                "type": "article"
            },
        ]
        
        print("\n" + "=" * 60)
        print("开始添加资源...")
        print("=" * 60)
        
        added_resources = []
        
        for idx, res_info in enumerate(test_resources, 1):
            print(f"\n[{idx}/{len(test_resources)}] 添加 {res_info['name']}...")
            print(f"  URL: {res_info['url']}")
            print(f"  类型: {res_info['type']}")
            
            try:
                resource = ResourceCURD.create_from_url(
                    db,
                    user_id=admin.id,
                    url=res_info['url'],
                    category_id=ai_category.id,
                    is_system_public=False
                )
                db.commit()
                
                print(f"  ✅ 成功添加！")
                print(f"     - ID: {resource.id}")
                print(f"     - 标题: {resource.title}")
                print(f"     - 平台: {resource.platform}")
                print(f"     - 资源类型: {resource.resource_type}")
                
                added_resources.append(resource)
                
            except Exception as e:
                print(f"  ⚠️  添加失败: {e}")
                db.rollback()
                continue
        
        print("\n" + "=" * 60)
        print(f"✅ 成功添加 {len(added_resources)} 条资源")
        print("=" * 60)
        
        # 显示摘要
        print("\n资源摘要:")
        for res in added_resources:
            print(f"  - [{res.resource_type:8s}] {res.platform:12s} | {res.title[:50]}")
        
        print("\n" + "=" * 60)
        print("🎉 测试资源添加完成！")
        print("=" * 60)
        print("\n提示：现在可以在前端 http://localhost:5173/my-resources 查看这些资源")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()

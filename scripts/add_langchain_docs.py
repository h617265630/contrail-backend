#!/usr/bin/env python3
"""
添加 LangChain 文档资源到数据库
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from sqlalchemy import create_engine, text

def main():
    print("=" * 60)
    print("添加 LangChain 文档资源")
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
            
            # LangChain 文档资源列表
            langchain_docs = [
                {
                    "title": "LangChain Introduction",
                    "summary": "LangChain is a framework for developing applications powered by language models. Learn the basics and core concepts.",
                    "source_url": "https://python.langchain.com/docs/introduction",
                    "thumbnail": "https://python.langchain.com/img/brand/wordmark.png",
                },
                {
                    "title": "LangChain Quick Start",
                    "summary": "Get started with LangChain quickly. Build your first LLM application in minutes.",
                    "source_url": "https://python.langchain.com/docs/tutorials/llm_chain",
                    "thumbnail": "https://python.langchain.com/img/brand/wordmark.png",
                },
                {
                    "title": "LangChain Chains",
                    "summary": "Learn about Chains - the core building blocks of LangChain for combining multiple components.",
                    "source_url": "https://python.langchain.com/docs/modules/chains",
                    "thumbnail": "https://python.langchain.com/img/brand/wordmark.png",
                },
                {
                    "title": "LangChain Agents",
                    "summary": "Understand Agents - autonomous systems that use LLMs to decide which actions to take.",
                    "source_url": "https://python.langchain.com/docs/modules/agents",
                    "thumbnail": "https://python.langchain.com/img/brand/wordmark.png",
                },
                {
                    "title": "LangChain Memory",
                    "summary": "Learn how to add memory to your LangChain applications to maintain conversation context.",
                    "source_url": "https://python.langchain.com/docs/modules/memory",
                    "thumbnail": "https://python.langchain.com/img/brand/wordmark.png",
                },
                {
                    "title": "LangChain RAG Tutorial",
                    "summary": "Build a Retrieval-Augmented Generation (RAG) application with LangChain.",
                    "source_url": "https://python.langchain.com/docs/tutorials/rag",
                    "thumbnail": "https://python.langchain.com/img/brand/wordmark.png",
                },
            ]
            
            print("\n" + "=" * 60)
            print("开始插入 LangChain 文档资源...")
            print("=" * 60)
            
            added_count = 0
            
            for idx, doc in enumerate(langchain_docs, 1):
                print(f"\n[{idx}/{len(langchain_docs)}] 添加 {doc['title']}...")
                
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
                        "resource_type": "document",
                        "platform": "langchain",
                        "title": doc["title"],
                        "summary": doc["summary"],
                        "source_url": doc["source_url"],
                        "thumbnail": doc["thumbnail"],
                        "category_id": category_id,
                    })
                    resource_id = result.fetchone()[0]
                    
                    # 插入 docs 表
                    conn.execute(text("""
                        INSERT INTO docs (resource_id, doc_type, version)
                        VALUES (:resource_id, 'documentation', NULL)
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
            print(f"✅ 成功添加 {added_count}/{len(langchain_docs)} 个 LangChain 文档资源")
            print("=" * 60)
            
            # 验证：查询所有 LangChain 资源
            print("\n验证：查询所有 LangChain 文档资源...")
            result = conn.execute(text("""
                SELECT r.id, r.title, r.platform
                FROM resources r
                JOIN user_resource ur ON ur.resource_id = r.id
                WHERE ur.user_id = :user_id AND r.platform = 'langchain'
                ORDER BY r.id DESC
            """), {"user_id": user_id})
            
            resources = result.fetchall()
            print(f"\n当前用户共有 {len(resources)} 个 LangChain 文档资源：")
            for res in resources:
                print(f"  - ID={res[0]}, {res[1]}")
            
            print("\n" + "=" * 60)
            print("🎉 LangChain 文档资源添加完成！")
            print("=" * 60)
            print("\n提示：现在可以在前端 http://localhost:5173/my-resources 查看这些文档")
            
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

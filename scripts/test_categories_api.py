#!/usr/bin/env python3
"""
测试分类 API 是否正常返回数据
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

import requests
from app.core.config import settings

def main():
    print("=" * 60)
    print("测试分类 API")
    print("=" * 60)
    
    # 首先登录获取 token
    login_url = "http://localhost:8000/users/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("\n1. 尝试登录获取 token...")
    try:
        # OAuth2PasswordRequestForm 需要 form-data 格式
        login_response = requests.post(login_url, data=login_data)
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"✅ 登录成功，获取到 token: {token[:20]}...")
        else:
            print(f"❌ 登录失败: {login_response.status_code} - {login_response.text}")
            print("\n提示：请确保数据库中有 admin 用户（密码：admin123）")
            print("或者修改脚本使用你自己的用户名和密码")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        sys.exit(1)
    
    # 测试分类 API
    categories_url = "http://localhost:8000/categories/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n2. 请求分类列表...")
    try:
        response = requests.get(categories_url, headers=headers)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ 成功获取分类列表，共 {len(categories)} 个分类：")
            print("=" * 60)
            for cat in categories:
                print(f"  - ID={cat['id']}, code={cat['code']:12s}, name={cat['name']:8s}, is_system={cat.get('is_system', False)}")
            print("=" * 60)
            print("\n🎉 分类 API 工作正常！")
            print("\n前端应该能够正常获取并展示这些分类。")
        else:
            print(f"❌ 获取分类失败: {response.status_code} - {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

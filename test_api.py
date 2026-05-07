"""快速 API 测试脚本"""
import urllib.request
import urllib.error
import json

BASE = "http://localhost:8001"

def test_root():
    try:
        req = urllib.request.Request(BASE + "/")
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode())
        print("✅ 根路由:", data)
    except Exception as e:
        print("❌ 根路由失败:", e)

def test_health():
    try:
        req = urllib.request.Request(BASE + "/health")
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode())
        print("✅ 健康检查:", data)
    except Exception as e:
        print("❌ 健康检查失败:", e)

def test_register():
    try:
        body = json.dumps({
            "username": "admin",
            "password": "admin123",
            "real_name": "管理员",
            "email": "admin@test.com",
            "department": "技术部",
            "position": "管理员"
        }).encode("utf-8")
        req = urllib.request.Request(
            BASE + "/api/auth/register",
            data=body,
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode())
        print("✅ 注册:", data)
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print("❌ 注册失败:", e.code, err)
    except Exception as e:
        print("❌ 注册失败:", e)

def test_login():
    try:
        body = json.dumps({
            "username": "admin",
            "password": "admin123"
        }).encode("utf-8")
        req = urllib.request.Request(
            BASE + "/api/auth/login",
            data=body,
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode())
        print("✅ 登录:", data)
        return data.get("data", {}).get("access_token")
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print("❌ 登录失败:", e.code, err)
    except Exception as e:
        print("❌ 登录失败:", e)

def test_me(token):
    try:
        req = urllib.request.Request(
            BASE + "/api/auth/me",
            headers={"Authorization": "Bearer " + token}
        )
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode())
        print("✅ 用户信息:", data)
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print("❌ 获取用户信息失败:", e.code, err)
    except Exception as e:
        print("❌ 获取用户信息失败:", e)

def test_openapi():
    try:
        req = urllib.request.Request(BASE + "/openapi.json")
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode())
        paths = list(data.get("paths", {}).keys())
        print("✅ API 路由 (%d 条):" % len(paths))
        for p in sorted(paths):
            print("   ", p)
    except Exception as e:
        print("❌ OpenAPI 失败:", e)

if __name__ == "__main__":
    print("=" * 50)
    print("智能会议助手 API 测试")
    print("=" * 50)
    
    test_root()
    test_health()
    test_openapi()
    test_register()
    token = test_login()
    if token:
        test_me(token)
    
    print("\n" + "=" * 50)
    print("测试完成")

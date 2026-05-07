"""测试 DeepSeek AI 接口集成"""
import urllib.request
import json
import sys

BASE = "http://localhost:8001"

# 1. 登录
login_data = json.dumps({"username": "admin", "password": "123456"}).encode()
req = urllib.request.Request(f"{BASE}/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read().decode())
    token = result["access_token"]
    print(f"[OK] 登录成功，token: {token[:20]}...")
except Exception as e:
    print(f"[FAIL] 登录失败: {e}")
    sys.exit(1)

# 2. 调用 AI 问答
qa_data = json.dumps({"question": "你好，请简单自我介绍"}).encode()
req2 = urllib.request.Request(
    f"{BASE}/api/ai/qa",
    data=qa_data,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    },
)
try:
    resp2 = urllib.request.urlopen(req2, timeout=120)
    result2 = json.loads(resp2.read().decode("utf-8"))
    print(f"\n[AI 问答结果]")
    print(f"code: {result2.get('code')}")
    answer = result2.get("data", {}).get("answer", "")
    print(f"answer: {answer[:500]}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"[FAIL] AI 问答失败: HTTP {e.code}")
    print(f"响应: {body[:500]}")
except Exception as e:
    print(f"[FAIL] AI 问答异常: {e}")

# 3. 直接测试 DeepSeek API 连通性
print("\n--- 直接测试 DeepSeek API ---")
ds_data = json.dumps({
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "hello"}],
    "max_tokens": 50,
    "stream": False,
}).encode()
ds_req = urllib.request.Request(
    "https://api.deepseek.com/v1/chat/completions",
    data=ds_data,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-8a15df628a69470db74cc62bb22ed074",
    },
)
try:
    ds_resp = urllib.request.urlopen(ds_req, timeout=30)
    ds_result = json.loads(ds_resp.read().decode("utf-8"))
    content = ds_result["choices"][0]["message"]["content"]
    print(f"[OK] DeepSeek 直连成功: {content[:200]}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"[FAIL] DeepSeek HTTP {e.code}: {body[:300]}")
except Exception as e:
    print(f"[FAIL] DeepSeek 连接失败: {type(e).__name__}: {e}")

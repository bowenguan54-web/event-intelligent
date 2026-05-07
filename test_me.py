"""快速测试 /api/auth/me"""
import urllib.request
import json

BASE = "http://localhost:8001"

# 先登录拿 token
body = json.dumps({"username": "admin", "password": "admin123"}).encode("utf-8")
req = urllib.request.Request(BASE + "/api/auth/login", data=body, headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode())
token = data.get("access_token")
print("Token:", token[:30] + "...")

# 测试 /me
req = urllib.request.Request(BASE + "/api/auth/me", headers={"Authorization": "Bearer " + token})
resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode())
print("用户信息:", json.dumps(data, ensure_ascii=False, indent=2))

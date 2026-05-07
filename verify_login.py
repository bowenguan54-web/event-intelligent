import urllib.request, json
body = json.dumps({"username": "admin", "password": "123456"}).encode()
req = urllib.request.Request("http://localhost:8001/api/auth/login", data=body, headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req)
d = json.loads(resp.read().decode())
print("Login OK:", d["user"]["username"], d["user"]["real_name"])

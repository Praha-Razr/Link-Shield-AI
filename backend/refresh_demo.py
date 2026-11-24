import urllib.request
import json

clear_req = urllib.request.Request(
    "http://127.0.0.1:8000/api/demo/clear",
    data=json.dumps({"confirm": True}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(clear_req) as resp:
    print("Clear response:", resp.read().decode())

load_req = urllib.request.Request(
    "http://127.0.0.1:8000/api/demo/load",
    data=b"{}",
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(load_req) as resp:
    print("Load response:", resp.read().decode())

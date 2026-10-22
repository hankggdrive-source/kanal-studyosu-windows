#!/usr/bin/env python3
"""Testler için sahte `claude` komutu. Davranış ortam değişkenlerinden:
SAHTE_KAYIT: her çağrının argümanları ve stdin'i bu dosyaya JSON satırı olarak eklenir.
SAHTE_CEVAPLAR: JSON liste dosyası; her çağrıda sıradaki metin verilir (SAHTE_SAYAC dosyası sayar).
SAHTE_SENARYO: normal | sinir | giris | bayrak | yavas"""
import json
import os
import sys
import time

argv = sys.argv[1:]
if argv[:1] == ["--version"]:
    print("2.1.300 (Claude Code)")
    sys.exit(0)
if argv[:2] == ["auth", "status"]:
    print(json.dumps({"loggedIn": True, "authMethod": os.environ.get("SAHTE_AUTH", "claude.ai")}))
    sys.exit(0)
girdi = sys.stdin.read()
with open(os.environ["SAHTE_KAYIT"], "a", encoding="utf-8") as f:
    f.write(json.dumps({"argv": argv, "stdin": girdi, "api_key": os.environ.get("ANTHROPIC_API_KEY"),
                        "cwd": os.getcwd()}, ensure_ascii=False) + "\n")
senaryo = os.environ.get("SAHTE_SENARYO", "normal")
if senaryo == "bayrak" and "--effort" in argv:
    sys.stderr.write("error: unknown option '--effort'\n")
    sys.exit(1)
if senaryo == "yavas":
    time.sleep(30)
sayac = os.environ["SAHTE_SAYAC"]
n = int(open(sayac).read()) if os.path.exists(sayac) else 0
open(sayac, "w").write(str(n + 1))
cevaplar = json.load(open(os.environ["SAHTE_CEVAPLAR"], encoding="utf-8"))
metin = cevaplar[min(n, len(cevaplar) - 1)]
oturum = argv[argv.index("--resume") + 1] if "--resume" in argv else f"oturum-{n + 1}"
model = argv[argv.index("--model") + 1]
cikti = [{"type": "system", "subtype": "init", "session_id": oturum},
         {"type": "stream_event", "event": {"type": "content_block_delta", "delta": {"type": "text_delta", "text": metin}}}]
if senaryo == "sinir":
    cikti.append({"type": "result", "subtype": "success", "is_error": True,
                  "result": "You've hit your limit · resets 5pm (Europe/Istanbul)", "session_id": oturum})
elif senaryo == "giris":
    cikti.append({"type": "result", "subtype": "success", "is_error": True,
                  "result": "Invalid API key · Please run /login", "session_id": oturum})
else:
    cikti += [{"type": "assistant", "message": {"content": [{"type": "text", "text": metin}]}},
              {"type": "result", "subtype": "success", "is_error": False, "result": metin, "session_id": oturum,
               "total_cost_usd": 0.42, "modelUsage": {model: {}},
               "usage": {"input_tokens": 1200, "output_tokens": 800, "cache_read_input_tokens": 300,
                         "cache_creation_input_tokens": 0, "server_tool_use": {"web_search_requests": 2}}}]
for o in cikti:
    print(json.dumps(o, ensure_ascii=False), flush=True)

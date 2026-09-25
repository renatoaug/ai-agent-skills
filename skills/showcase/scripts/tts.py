import json, subprocess, os, sys, hashlib
S = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(f"{S}/narration.json"))
voice = os.environ.get("TTS_VOICE", cfg["voice"]); rate = os.environ.get("TTS_RATE", cfg["rate"])
only = set(sys.argv[1:])
for b in cfg["beats"]:
    if only and b["id"] not in only: continue
    h = hashlib.md5((voice+rate+b["text"]).encode()).hexdigest()[:8]
    out = f"{S}/clips/{b['id']}.mp3"; stamp = f"{S}/clips/{b['id']}.hash"
    if os.path.exists(stamp) and open(stamp).read() == h and not only: continue
    subprocess.run([f"{S}/.venv/bin/edge-tts", "--voice", voice, f"--rate={rate}", "--text", b["text"], "--write-media", out], check=True, capture_output=True)
    open(stamp, "w").write(h); print("gen", b["id"])

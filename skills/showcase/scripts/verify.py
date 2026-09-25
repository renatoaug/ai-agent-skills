import json, os, sys, re, subprocess, unicodedata, difflib, mlx_whisper
S = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(f"{S}/narration.json"))
only = set(sys.argv[1:])
norm = lambda t: re.sub(r"[^a-z0-9 ]", " ", unicodedata.normalize("NFD", t.lower()).encode("ascii","ignore").decode()).split()
words = {}
for b in cfg["beats"]:
    if only and b["id"] not in only: continue
    f = f"{S}/clips/{b['id']}.mp3"
    r = mlx_whisper.transcribe(f, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language=cfg.get("lang", "pt"), word_timestamps=True)
    ws = [{"w": w["word"].strip(), "s": round(w["start"],2), "e": round(w["end"],2)} for s in r["segments"] for w in s["words"]]
    words[b["id"]] = ws
    a, t = norm(b["text"]), norm(r["text"])
    ratio = difflib.SequenceMatcher(None, a, t).ratio()
    gaps = [round(ws[i+1]["s"]-ws[i]["e"],2) for i in range(len(ws)-1)]
    mg = max(gaps) if gaps else 0
    flag = "OK " if ratio > .9 and mg < .9 else "CHK"
    print(flag, b["id"], f"{ratio:.2f}", f"gap={mg}", "|", r["text"].strip() if flag=="CHK" else "")
old = json.load(open(f"{S}/words.json")) if os.path.exists(f"{S}/words.json") else {}
old.update(words); json.dump(old, open(f"{S}/words.json","w"), ensure_ascii=False, indent=0)

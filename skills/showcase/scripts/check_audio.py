# Transcribe the assembled video and diff it against the whole script. Usage: .venv/bin/python check_audio.py out/v1.mp4
import json, re, unicodedata, difflib, subprocess, sys, os, mlx_whisper
S = os.path.dirname(os.path.abspath(__file__)); mp4 = sys.argv[1]; wav = mp4 + ".wav"
subprocess.run(["ffmpeg","-loglevel","error","-y","-i",mp4,"-vn","-ac","1","-ar","16000",wav], check=True)
norm = lambda t: re.sub(r"[^a-z0-9 ]", " ", unicodedata.normalize("NFD", t.lower()).encode("ascii","ignore").decode()).split()
lang = json.load(open(f"{S}/narration.json")).get("lang", "pt")
script = norm(" ".join(b["text"] for b in json.load(open(f"{S}/narration.json"))["beats"]))
got = norm(mlx_whisper.transcribe(wav, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language=lang)["text"])
sm = difflib.SequenceMatcher(None, script, got, autojunk=False)
print("ratio", round(sm.ratio(), 3))
print("missing runs (>=3 words):", [" ".join(script[a:b]) for t, a, b, c, d in sm.get_opcodes() if t in ("delete","replace") and b - a >= 3])

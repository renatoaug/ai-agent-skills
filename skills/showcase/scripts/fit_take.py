# Speed up marked wait windows (w+ .. w-) so each beat fits its narration; writes <take>.mp4 in place (orig kept as _raw).
import json, subprocess, os, sys
S = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(f"{S}/durations.json")); PAD = 1.2
name = sys.argv[1]
raw = f"{S}/takes/{name}_raw.mp4"
if not os.path.exists(raw): os.rename(f"{S}/takes/{name}.mp4", raw)
log = json.load(open(f"{S}/takes/{name}.beats.json"))
beats = [x for x in log if not x["id"].startswith("#")]
end = [x["at"] for x in log if x["id"] == "#end"][0]
wins = []; st = None
for x in log:
    if x["id"] == "#w+": st = x["at"]
    if x["id"] == "#w-" and st is not None: wins.append((st, x["at"])); st = None
pieces = []  # (start, end, speed)
newlog = []; T = 0.0
for i, b in enumerate(beats):
    s0 = b["at"]; s1 = beats[i + 1]["at"] if i + 1 < len(beats) else end
    ws = [(max(a, s0), min(c, s1)) for a, c in wins if a < s1 and c > s0]
    W = sum(c - a for a, c in ws); L = s1 - s0; target = D[b["id"]] + PAD
    sp = 1.0
    if L > target and W > 0:
        need = max(target - (L - W), 0.35 * len(ws)); sp = min(max(W / need, 1.0), 16.0)
    newlog.append({"id": b["id"], "at": round(T, 3)})
    cur = s0
    for a, c in ws:
        if a > cur: pieces.append((cur, a, 1.0)); T += a - cur
        pieces.append((a, c, sp)); T += (c - a) / sp; cur = c
    if s1 > cur: pieces.append((cur, s1, 1.0)); T += s1 - cur
    print(b["id"], "len", round(L, 1), "target", round(target, 1), "speed", round(sp, 2))
newlog.append({"id": "#end", "at": round(T, 3)})
fl = []; ins = []
for i, (a, c, sp) in enumerate(pieces):
    fl.append(f"[0:v]trim={a:.3f}:{c:.3f},setpts=(PTS-STARTPTS)/{sp:.4f}[p{i}]")
fl.append("".join(f"[p{i}]" for i in range(len(pieces))) + f"concat=n={len(pieces)}:v=1:a=0,fps=30,format=yuv420p[v]")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-filter_complex", ";".join(fl), "-map", "[v]", "-c:v", "libx264", "-crf", "16", f"{S}/takes/{name}.mp4"], check=True)
json.dump(newlog, open(f"{S}/takes/{name}.beats.json", "w")); print(newlog)

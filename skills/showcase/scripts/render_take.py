# frames+timestamps -> CFR 30fps mp4 starting at the first beat; writes beats offsets json
import json, sys, subprocess, os
S = os.path.dirname(os.path.abspath(__file__))
for name in sys.argv[1:]:
    d = f"{S}/takes/{name}"; m = json.load(open(f"{d}/meta.json"))
    fr, log = m["frames"], m["log"]
    t0 = next(x["t"] for x in log if not x["id"].startswith("#")); tend = log[-1]["t"]
    lines = []
    # frame shown until next frame
    idx = max([i for i, t in enumerate(fr) if t <= t0] or [0])
    ts = [max(t, t0) for t in fr]
    for i in range(idx, len(fr)):
        nxt = ts[i+1] if i+1 < len(fr) else tend
        if nxt <= t0: continue
        du = min(nxt, tend) - ts[i]
        if du <= 0: continue
        lines.append(f"file '{d}/{i:06d}.jpg'\nduration {du:.4f}")
    lines.append(f"file '{d}/{len(fr)-1:06d}.jpg'")
    open(f"{d}/list.txt","w").write("\n".join(lines))
    subprocess.run(["ffmpeg","-loglevel","error","-y","-f","concat","-safe","0","-i",f"{d}/list.txt","-vf","fps=30,format=yuv420p","-c:v","libx264","-crf","16","-preset","medium",f"{S}/takes/{name}.mp4"],check=True)
    beats = [{"id": x["id"], "at": round(x["t"]-t0, 3)} for x in log]
    json.dump(beats, open(f"{S}/takes/{name}.beats.json","w"))
    print(name, beats)

# Cut each take to its beats, chain takes with xfade transitions, lay narration at word-accurate offsets.
# Scene order comes from narration.json: beats are grouped by their "take" in the order they appear.
# Optional narration.json keys: "transitions": {"<take>": "<xfade name>"}.
# Usage: python3 assemble.py out/v1.mp4
import json, subprocess, os, sys
S = os.path.dirname(os.path.abspath(__file__))
LEAD = 0.25; XF = 0.6
ROTATE = ["smoothleft", "circleopen", "fade", "smoothup", "zoomin"]
N = json.load(open(f"{S}/narration.json"))
SEQ = []
for b in N["beats"]:
    if SEQ and SEQ[-1][0] == b["take"]: SEQ[-1][1].append(b["id"])
    else: SEQ.append((b["take"], [b["id"]]))
TR = N.get("transitions", {})
SEQ = [(t, bs, None if i == 0 else TR.get(t, ROTATE[i % len(ROTATE)])) for i, (t, bs) in enumerate(SEQ)]
if SEQ: SEQ[-1] = (SEQ[-1][0], SEQ[-1][1], TR.get(SEQ[-1][0], "fadeblack"))
out = sys.argv[1]
dur = lambda f: float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
D = json.load(open(f"{S}/durations.json"))
segs = []  # (take, mp4, start, length, [(beat, offset)], transition, pad)
for take, beats, tr in SEQ:
    mp4 = f"{S}/takes/{take}.mp4"
    if not os.path.exists(mp4): print("skip (no take)", take); continue
    log = json.load(open(f"{S}/takes/{take}.beats.json"))
    at = {x["id"]: x["at"] for x in log}
    missing = [b for b in beats if b not in at]
    if missing: print("skip (beats not recorded)", take, missing); continue
    start = at[beats[0]]
    end = min(x["at"] for x in log if x["at"] > at[beats[-1]] and x["id"] in ("#end", "#nav"))
    end = min(end, dur(mp4))
    for i, bb in enumerate(beats[:-1]):
        if at[bb] + D[bb] + LEAD > at[beats[i + 1]]: print("WARN overlap", take, bb)
    pad = max(0.0, at[beats[-1]] + D[beats[-1]] + LEAD + 0.5 - end)  # freeze last frame if the line outlasts the take
    segs.append((take, mp4, start, end - start + pad, [(b, at[b] - start) for b in beats], tr, pad))
inputs, fl = [], []
for i, (take, mp4, st, ln, _, _, pad) in enumerate(segs):
    inputs += ["-ss", f"{st:.3f}", "-t", f"{ln - pad:.3f}", "-i", mp4]
    tp = f",tpad=stop_mode=clone:stop_duration={pad:.3f}" if pad > 0 else ""
    fl.append(f"[{i}:v]fps=30,settb=AVTB,setpts=PTS-STARTPTS{tp},format=yuv420p[v{i}]")
cur, t = "v0", segs[0][3]; starts = [0.0]
for i in range(1, len(segs)):
    off = t - XF; starts.append(off)
    fl.append(f"[{cur}][v{i}]xfade=transition={segs[i][5] or 'fade'}:duration={XF}:offset={off:.3f}[x{i}]")
    cur = f"x{i}"; t = off + segs[i][3]
total = t
fl.append(f"[{cur}]fade=t=in:st=0:d=0.6,fade=t=out:st={total-1.0:.3f}:d=1.0[vout]")
n = len(segs); ai = []
for k, (take, mp4, st, ln, beats, _, _) in enumerate(segs):
    for b, off in beats:
        idx = n + len(ai); inputs += ["-i", f"{S}/clips/{b}.mp3"]
        ms = int((starts[k] + off + LEAD) * 1000)
        ai.append(f"[{idx}:a]aresample=48000,adelay={ms}|{ms}[a{len(ai)}]")
fl += ai
fl.append("".join(f"[a{i}]" for i in range(len(ai))) + f"amix=inputs={len(ai)}:normalize=0,apad,atrim=0:{total:.3f},loudnorm=I=-16:TP=-1.5[aout]")
subprocess.run(["ffmpeg","-loglevel","error","-y",*inputs,"-filter_complex",";".join(fl),"-map","[vout]","-map","[aout]","-c:v","libx264","-crf","18","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",out], check=True)
tl = [{"take": s[0], "start": round(starts[i],2), "len": round(s[3],2), "beats": [(b, round(starts[i]+o+LEAD,2)) for b,o in s[4]]} for i,s in enumerate(segs)]
json.dump(tl, open(out + ".timeline.json","w"), indent=1)
print("total", round(total,2))

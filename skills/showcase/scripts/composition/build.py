"""Writes index.html, a HyperFrames composition, from video.json.

Every scene is one of a few kinds, each with its motion already worked out
(the vocabulary in references/motion.md). Timing comes from the narration
when there is one: a scene lasts as long as its beats' clips (clips/<id>.mp3,
made by tts.py) plus a pad; without narration, each scene's "dur" sets it.

    python3 build.py                 # video.json -> index.html
    python3 build.py --lang en       # pick the "en" side of every {"pt":..,"en":..} text
    python3 build.py --spec other.json

Media sizes are read with ffprobe, so a clip or a screenshot is always laid
out in its own aspect (HyperFrames letterboxes a <video> into a box of any
other shape, and only `render` shows it).
"""

import argparse
import html
import json
import os
import subprocess

HERE = os.getcwd()
W, H = 1920, 1080
FADE_IN, FADE_OUT = 0.6, 0.45  # a scene settles up into place; the last one leaves
PAD = 0.8  # breathing room after each narrated line
LEAD = 0.25  # the picture moves first, the voice follows

ap = argparse.ArgumentParser()
ap.add_argument('--spec', default='video.json')
ap.add_argument('--lang', default=None)
ap.add_argument('--out', default='index.html')
args = ap.parse_args()
spec = json.load(open(args.spec))
lang = args.lang or spec.get('lang', 'en')


def T(v):
    """A text: a string, or {"pt": ..., "en": ...}. May hold <b>, <em>, <br>."""
    if isinstance(v, dict):
        return v.get(lang) or next(iter(v.values()))
    return v or ''


_sizes = {}


def size(src):
    if src not in _sizes:
        out = subprocess.check_output(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', src]
        ).decode().strip().split('\n')[0]
        w, h = (int(x) for x in out.split(',')[:2])
        _sizes[src] = (w, h)
    return _sizes[src]


def fit(src, bw, bh):
    """The largest box of the media's aspect inside bw x bh."""
    w, h = size(src)
    s = min(bw / w, bh / h)
    return round(w * s), round(h * s)


def clip_len(beat):
    p = os.path.join(HERE, 'clips', f'{beat}.mp3')
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))


THEME = {**json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'theme.json'))), **spec.get('theme', {})}

# ---- timing ---------------------------------------------------------------

narration = {b['id']: b for b in spec.get('beats', [])}
scenes = spec['scenes']
t = 0.0
audio = []  # (beat id, start, dur)
for sc in scenes:
    sc['start'] = t
    beats = sc.get('beats', [])
    sc['beat_at'] = {}
    if beats:
        at = sc.get('lead_in', 0.6)
        for b in beats:
            d = clip_len(b)
            sc['beat_at'][b] = at
            audio.append((b, t + at + LEAD, d))
            at += d + PAD
        sc['dur'] = max(at, sc.get('dur', 0))
    t += sc['dur']
TOTAL = round(t, 2)


def when(sc, item, default):
    """When an item fires inside its scene: on its beat, at its "at", or the default."""
    if 'beat' in item and item['beat'] in sc['beat_at']:
        return sc['beat_at'][item['beat']]
    return item.get('at', default)


# ---- scenes ---------------------------------------------------------------

parts, js = [], []
vid = 0


def video(src, x, y, w, h, start, dur, cls='', extra=''):
    """A media element. Every <video> needs an id or it renders frozen, and both sides."""
    global vid
    vid += 1
    style = f'left:{x}px;top:{y}px;width:{w}px;height:{h}px;{extra}'
    if src.endswith(('.png', '.jpg', '.jpeg', '.webp')):
        return f'<img id="m{vid}" class="{cls}" src="{src}" alt="" style="position:absolute;{style}">', f'#m{vid}'
    return (
        f'<video id="m{vid}" class="{cls}" src="{src}" muted data-start="{start:.2f}" data-duration="{dur:.2f}" style="{style}"></video>',
        f'#m{vid}',
    )


def cap_html(sid, c, style):
    k = f'<div class="k"><i></i>{T(c.get("kicker"))}</div>' if c.get('kicker') else ''
    h = f'<div class="h" style="font-size:{c.get("size", 92)}px">{T(c.get("title"))}</div>' if c.get('title') else ''
    p = f'<div class="p">{T(c.get("text"))}</div>' if c.get('text') else ''
    return f'<div class="cap" id="{sid}c" style="{style}">{k}{h}{p}</div>'


for n, sc in enumerate(scenes):
    sid, s0, dur, kind = f's{n}', sc['start'], sc['dur'], sc['kind']
    body, at = [], lambda x: round(s0 + x, 2)
    glow = sc.get('glow', 'center')

    if kind == 'card':  # the opening and the outro: whole from its first frame when it opens the video
        media = ''
        if sc.get('media'):
            w, h = fit(sc['media'], 600, 300)
            m, mid = video(sc['media'], (W - w) // 2, 60 + (300 - h), w, h, s0, dur)
            media = m
        cmd = f'<div class="cmd-row" id="{sid}cmd"><span class="cmd"><s>$</s> {html.escape(sc["cmd"])}</span></div>' if sc.get('cmd') else ''
        foot = f'<div class="foot" id="{sid}u">{T(sc.get("foot"))}</div>' if sc.get('foot') else ''
        body.append(
            f'<div class="grid"></div><div class="glow" style="width:1000px;height:600px;left:460px;top:120px;opacity:.3"></div>'
            f'<div class="center" id="{sid}c"><div style="height:{340 if media else 0}px"></div>'
            f'<div class="h" style="font-size:140px">{T(sc["title"])}</div><div class="p" style="font-size:40px">{T(sc.get("text"))}</div>{cmd}{foot}</div>{media}'
        )
        if n > 0:  # an outro builds up; the opening is already there
            js.append(f"tl.fromTo('#{sid}c > *', {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.8, ease, stagger: 0.22 }}, {at(0.4)})")
            if media:
                js.append(f"tl.fromTo('{mid}', {{ scale: 0.3, opacity: 0, y: 100 }}, {{ scale: 1, opacity: 1, y: 0, duration: 1.0, ease: 'back.out(1.6)' }}, {at(0.2)})")

    elif kind == 'hook':  # a big number climbs, turns hot and shakes; the media lands beside it
        to = sc.get('to', 100)
        body.append(
            f'<div class="grid"></div><div class="glow" id="{sid}g" style="width:900px;height:700px;left:1000px;top:200px;background:var(--hot)"></div>'
            f'<div class="cap" style="left:130px;top:190px;width:1050px;gap:10px"><div class="k" id="{sid}k"><i></i>{T(sc.get("kicker"))}</div>'
            f'<div class="big" id="{sid}n">0{sc.get("unit", "%")}</div><div class="h" id="{sid}h" style="font-size:84px;margin-top:30px">{T(sc["title"])}</div>'
            f'<div class="p" id="{sid}p" style="margin-top:16px">{T(sc.get("text"))}</div></div>'
        )
        mid = None
        if sc.get('media'):
            w, h = fit(sc['media'], 640, 640)
            m, mid = video(sc['media'], 1220, 200, w, h, s0, dur)
            body.append(m)
        unit = sc.get('unit', '%')
        js += [
            f"tl.fromTo('#{sid}k', {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.6, ease }}, {at(0.2)})",
            f"tl.fromTo('#{sid}n', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {at(0.3)})",
            f"count('#{sid}n', {to}, '{unit}', {at(0.4)})",
            f"tl.to('#{sid}n', {{ color: '{THEME['hot']}', duration: 0.2 }}, {at(1.95)})",
            f"tl.fromTo('#{sid}n', {{ x: 0 }}, {{ x: 14, duration: 0.05, yoyo: true, repeat: 7, ease: 'none' }}, {at(2.0)})",
            f"tl.fromTo('#{sid}g', {{ scale: 0.4, opacity: 0 }}, {{ scale: 1, opacity: 0.22, duration: 1.2, ease }}, {at(1.9)})",
            f"tl.fromTo('#{sid}h', {{ y: 50, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.8, ease }}, {at(2.5)})",
            f"tl.fromTo('#{sid}p', {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.7, ease }}, {at(3.3)})",
        ]
        if mid:
            js.append(f"tl.fromTo('{mid}', {{ y: 120, opacity: 0, scale: 0.8 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.9, ease: 'back.out(1.4)' }}, {at(2.1)})")

    elif kind == 'feature':  # caption on one side, the media on the other, callouts that draw a line to it
        side = sc.get('side', 'right')
        box = sc.get('box', [760, 900])
        w, h = fit(sc['media'], *box)
        mx = W - 140 - w if side == 'right' else 140
        my = (H - h) // 2
        cx = 130 if side == 'right' else 140 + w + 90
        body.append(f'<div class="glow" style="width:900px;height:900px;left:{1000 if side == "right" else 20}px;top:90px;opacity:.2"></div>')
        body.append(cap_html(sid, sc, f'left:{cx}px;top:{sc.get("cap_top", 220)}px;width:{W - w - 360}px'))
        m, mid = video(sc['media'], mx, my, w, h, s0, dur)
        body.append(m)
        js.append(f"enterCap('#{sid}c', {at(0.2)})")
        js.append(f"tl.fromTo('{mid}', {{ x: {260 if side == 'right' else -260}, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.9, ease }}, {at(0.1)})")
        lines = []
        for i, c in enumerate(sc.get('callouts', [])):
            # target: [x, y] as fractions of the media; the line runs from the callout to it
            tx, ty = mx + c['target'][0] * w, my + c['target'][1] * h
            y = c.get('y', 560 + i * 120)
            body.append(f'<div class="callout {c.get("tone", "")}" id="{sid}k{i}" style="left:{cx}px;top:{y - 38}px">{T(c["text"])}</div>')
            lines.append(f'<path id="{sid}l{i}" d="M{cx + 170} {y} L{tx - 90:.0f} {y} L{tx - 10:.0f} {ty:.0f}"/>')
            t0 = when(sc, c, 2.5 + i * 1.2)
            js.append(f"pop('#{sid}k{i}', {at(t0)})")
            js.append(f"draw('#{sid}l{i}', {at(t0 + 0.3)})")
        if lines:
            body.append(f'<svg class="lines" width="{W}" height="{H}" style="position:absolute;left:0;top:0;z-index:9">{"".join(lines)}</svg>')

    elif kind == 'row':  # a centred caption, tiles that rise in, each lit in turn
        items = sc['items']
        gap = 60
        bw = (W - 200 - gap * (len(items) - 1)) / len(items)
        bh = sc.get('tile_h', 420)
        body.append('<div class="glow" style="width:1300px;height:500px;left:310px;top:400px;opacity:.15"></div>')
        body.append(cap_html(sid, sc, 'left:0;right:0;top:80px;align-items:center;text-align:center;gap:16px'))
        ids, labs = [], []
        for i, it in enumerate(items):
            w, h = fit(it['media'], bw, bh)
            x = 100 + i * (bw + gap) + (bw - w) / 2
            m, mid = video(it['media'], round(x), 340 + bh - h, w, h, s0, dur)
            body.append(m)
            ids.append(mid)
            lab = f'<b>{T(it.get("title"))}</b>' + (f'<span>{T(it.get("text"))}</span>' if it.get('text') else '')
            body.append(f'<div class="lab" id="{sid}l{i}" style="left:{100 + i * (bw + gap):.0f}px;width:{bw:.0f}px;top:{340 + bh + 30}px">{lab}</div>')
            labs.append(f'#{sid}l{i}')
        js.append(f"enterCap('#{sid}c', {at(0.2)})")
        js.append(f"rise({json.dumps(ids)}, {at(0.8)}, {0.3 if len(ids) < 4 else 0.22})")
        js.append(f"labels({json.dumps(labs)}, {at(1.6)})")
        step = sc.get('spot_every', min(1.4, (dur - 3.2) / max(len(ids), 1)))
        for i, (mid, it) in enumerate(zip(ids, items)):
            js.append(f"spot('{mid}', {at(when(sc, it, 2.6 + i * step))})")

    elif kind == 'lineup':  # each one lands big in the middle while the rest blurs, then glides into its slot
        items = sc['items']
        gap = 70
        bh = sc.get('tile_h', 560)
        widths = [fit(it['media'], 9999, bh)[0] for it in items]
        scale = min(1, (W - 160 - gap * (len(items) - 1)) / sum(widths))
        x = (W - (sum(widths) * scale + gap * (len(items) - 1))) / 2
        body.append('<div class="glow" style="width:1400px;height:500px;left:260px;top:480px;opacity:.13"></div>')
        body.append(cap_html(sid, sc, 'left:0;right:0;top:56px;align-items:center;text-align:center;gap:14px'))
        each = sc.get('each', 4.2)
        zooms = []
        for i, it in enumerate(items):
            w, h = fit(it['media'], widths[i] * scale, bh * scale)
            zooms.append(it.get('zoom', round(min(1.7, 600 / h), 2)))
            top = 860 - h
            m, _ = video(it['media'], 0, 0, w, h, s0, dur)
            body.append(f'<div class="slot" id="{sid}a{i}" style="left:{x:.0f}px;top:{top:.0f}px;width:{w}px;height:{h}px">{m}</div>')
            body.append(f'<div class="lab" id="{sid}al{i}" style="left:{x + w / 2 - 240:.0f}px;width:480px;top:880px"><b>{T(it.get("title"))}</b><span>{T(it.get("short", ""))}</span></div>')
            body.append(f'<div class="lab big-lab" id="{sid}b{i}" style="left:0;right:0;top:905px"><b>{T(it.get("title"))}</b><span>{T(it.get("text", ""))}</span></div>')
            x += w + gap
        js.append(f"enterCap('#{sid}c', {at(0.1)})")
        js.append(f"lineup('{sid}', {len(items)}, {at(1.2)}, {each}, {json.dumps(zooms)})")

    elif kind == 'shot':  # a screenshot in a frame, a slow push-in, highlight boxes that dim the rest
        w, h = fit(sc['media'], 1600, 880)
        x, y = (W - w) // 2, 34
        hls = ''
        for i, b in enumerate(sc.get('highlights', [])):
            # box: [x, y, w, h] in the screenshot's own pixels
            iw, ih = size(sc['media'])
            k = w / iw
            bx, by, bw2, bh2 = (v * k for v in b['box'])
            hls += f'<div class="hl" id="{sid}h{i}" style="left:{bx - 10:.0f}px;top:{by - 10:.0f}px;width:{bw2 + 20:.0f}px;height:{bh2 + 20:.0f}px"></div>'
            t0 = when(sc, b, 0.8 + i * 2)
            js.append(f"tl.fromTo('#{sid}h{i}', {{ opacity: 0, scale: 1.06 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: 'back.out(2)' }}, {at(t0)})")
            if 'until' in b:
                js.append(f"tl.to('#{sid}h{i}', {{ opacity: 0, duration: 0.3 }}, {at(b['until'])})")
        m, _ = video(sc['media'], 0, 0, w, h, s0, dur)
        body.append(f'<div class="frame" id="{sid}f" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{m}{hls}</div>')
        num = f'<span class="num">{sc["num"]:02d}</span>' if 'num' in sc else ''
        body.append(f'<div class="caption" id="{sid}cap">{num}<span>{T(sc.get("text"))}</span></div>')
        js.append(f"tl.fromTo('#{sid}f', {{ scale: 1 }}, {{ scale: 1.025, duration: {dur:.2f}, ease: 'none' }}, {at(0)})")
        js.append(f"tl.fromTo('#{sid}cap', {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.6, ease }}, {at(0.3)})")

    elif kind == 'scroll':  # a tall media in a window the camera slides down
        w, h = fit(sc['media'], 660, 99999)
        body.append('<div class="glow" style="width:800px;height:900px;left:1050px;top:100px;opacity:.18"></div>')
        body.append(cap_html(sid, sc, 'left:130px;top:290px;width:820px'))
        m, mid = video(sc['media'], 0, 0, w, h, s0, dur)
        body.append(f'<div class="cam" id="{sid}cam" style="left:1120px;top:40px;width:{w}px;height:1000px">{m}</div>')
        js.append(f"enterCap('#{sid}c', {at(0.2)})")
        js.append(f"tl.fromTo('#{sid}cam', {{ x: 200, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.8, ease }}, {at(0.1)})")
        js.append(f"tl.fromTo('{mid}', {{ y: 0 }}, {{ y: -{max(0, h - 1000)}, duration: {max(1.0, dur - 2.6):.2f}, ease: 'power1.inOut' }}, {at(1.3)})")

    elif kind == 'checklist':  # what to do next, one line at a time
        lis = ''.join(f'<li id="{sid}i{i}"><span class="ck">{T(k)}</span><span>{T(v)}</span></li>' for i, (k, v) in enumerate(sc['items']))
        body.append(f'<div class="grid"></div><div class="list" id="{sid}c"><div class="h" style="font-size:88px">{T(sc["title"])}</div><ol>{lis}</ol></div>')
        js.append(f"tl.fromTo('#{sid}c .h', {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.7, ease }}, {at(0.2)})")
        for i in range(len(sc['items'])):
            js.append(f"tl.fromTo('#{sid}i{i}', {{ x: -24, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.5, ease }}, {at(when(sc, sc['items'][i] if isinstance(sc['items'][i], dict) else {}, 0.9 + i * 0.6))})")

    else:
        raise SystemExit(f'unknown scene kind: {kind}')

    parts.append(f'<!-- {s0:.1f}-{s0 + dur:.1f} {kind} -->\n<div class="clip" id="{sid}" data-start="{s0:.2f}" data-duration="{dur:.2f}">\n  ' + '\n  '.join(body) + '\n</div>')
    # scene changes: the new one settles up into place, the old one fades out
    if n > 0:
        js.append(f"tl.fromTo('#{sid}', {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: {FADE_IN}, ease: 'power2.out' }}, {at(0)})")
    if n < len(scenes) - 1:
        js.append(f"tl.to('#{sid}', {{ opacity: 0, duration: {FADE_OUT}, ease: 'power1.in' }}, {at(dur - FADE_OUT)})")
    else:
        js.append(f"tl.to('#{sid} > *', {{ opacity: 0, duration: 1.2 }}, {at(dur - 1.6)})")

# ---- sound ------------------------------------------------------------------

sound = []
if spec.get('music'):
    vol = spec.get('music_volume', 0.25 if audio else 0.9)
    sound.append(f'<audio id="music" src="{spec["music"]}" data-start="0" data-duration="{TOTAL}" data-volume="{vol}"></audio>')
for b, start, d in audio:
    sound.append(f'<audio id="vo-{b}" src="clips/{b}.mp3" data-start="{start:.2f}" data-duration="{d:.2f}" data-volume="1"></audio>')

theme = THEME
tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')).read()
out = (
    tpl.replace('{{LANG}}', lang)
    .replace('{{TOTAL}}', str(TOTAL))
    .replace('{{VARS}}', ' '.join(f'--{k}:{v};' for k, v in theme.items()))
    .replace('{{SOUND}}', '\n  '.join(sound))
    .replace('{{SCENES}}', '\n\n'.join(parts))
    .replace('{{JS}}', '\n    '.join(js))
)
open(args.out, 'w').write(out)
print(f'{args.out}: {len(scenes)} scenes, {TOTAL}s, {len(audio)} narrated lines')
for sc in scenes:
    print(f'  {sc["start"]:6.2f}  {sc["dur"]:5.2f}s  {sc["kind"]}')

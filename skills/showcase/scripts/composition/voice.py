"""One narration clip per beat of video.json, into clips/<id>.mp3, with edge-tts.

Only changed lines are regenerated (text + voice + rate hash). build.py then
times every scene to its beats' clips.

    python3 voice.py            # every beat
    python3 voice.py b3 b4      # only these

video.json: "voice" (default en-US-AndrewNeural; pt-BR-AntonioNeural for
Portuguese), "rate" (default +10%), and "beats": [{"id": "b1", "text": ...}].
A cloned voice (ElevenLabs) writes the same clips/<id>.mp3 instead; see
references/narration.md.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

spec = json.load(open('video.json'))
lang = spec.get('lang', 'en')
voice = os.environ.get('TTS_VOICE', spec.get('voice', 'pt-BR-AntonioNeural' if lang == 'pt' else 'en-US-AndrewNeural'))
rate = os.environ.get('TTS_RATE', spec.get('rate', '+10%'))
only = set(sys.argv[1:])
os.makedirs('clips', exist_ok=True)
tts = ['edge-tts'] if shutil.which('edge-tts') else ['uvx', 'edge-tts']

for b in spec.get('beats', []):
    if only and b['id'] not in only:
        continue
    text = b['text'][lang] if isinstance(b['text'], dict) else b['text']
    h = hashlib.md5((voice + rate + text).encode()).hexdigest()[:8]
    out, stamp = f'clips/{b["id"]}.mp3', f'clips/{b["id"]}.hash'
    if not only and os.path.exists(stamp) and open(stamp).read() == h:
        continue
    for attempt in range(4):  # the service drops a request now and then
        r = subprocess.run([*tts, '--voice', voice, f'--rate={rate}', '--text', text, '--write-media', out], capture_output=True, text=True)
        if r.returncode == 0:
            break
        time.sleep(2 + attempt * 2)
    else:
        sys.exit(f'{b["id"]}: edge-tts failed: {r.stderr.strip()[-300:]}')
    open(stamp, 'w').write(h)
    print('gen', b['id'])

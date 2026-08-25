#!/usr/bin/env python3
"""no_loss_gate.py — content-preservation gate for site refactors.
Freeze: python3 scripts/no_loss_gate.py freeze <pages...>  (writes scripts/no-loss-freeze.json)
Verify: python3 scripts/no_loss_gate.py verify <pages...>  (fails if any frozen sentence is absent)
A sentence is any >40-char run ending in terminal punctuation, tags and scripts stripped."""
import re, json, sys, html as H, hashlib
def corpus(p):
    h = open(p).read()
    h = re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S)
    t = H.unescape(re.sub(r'\s+',' ', re.sub(r'<[^>]+>',' ',h))).strip()
    return t, set(s.strip() for s in re.split(r'(?<=[.!?])\s+', t) if len(s.strip())>40)
if sys.argv[1]=='freeze':
    fr={}
    for p in sys.argv[2:]:
        t,s=corpus(p); fr[p]={"chars":len(t),"sentences":sorted(s),"sha":hashlib.sha256(t.encode()).hexdigest()}
    json.dump(fr, open('scripts/no-loss-freeze.json','w'), ensure_ascii=False); print('frozen', len(fr))
else:
    fr=json.load(open('scripts/no-loss-freeze.json'))
    new=' '.join(corpus(p)[0] for p in sys.argv[2:])
    bad=sum(1 for r in fr.values() for s in r['sentences'] if s not in new)
    print('PASS' if bad==0 else f'FAIL {bad}'); sys.exit(1 if bad else 0)

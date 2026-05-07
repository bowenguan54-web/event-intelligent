#!/usr/bin/env python3
"""Check and fix remaining 3 in MeetingLive"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingLive.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

print(f'Remaining: {c.count(chr(0xfffd))}')

idx = 0
while True:
    pos = c.find(p, idx)
    if pos < 0: break
    ctx = c[max(0,pos-60):pos+60]
    # show with hex for key chars
    print(f'pos={pos}: {repr(ctx)}')
    print(f'  hex around: {ctx[max(0,pos-60-max(0,pos-60)):30].encode()!r}')
    idx = pos + 2

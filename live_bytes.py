#!/usr/bin/env python3
"""Dump raw bytes around remaining FFFD chars"""

path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingLive.vue'

with open(path, 'rb') as f:
    raw = f.read()

# Find EF BF BD (FFFD in UTF-8)
fffd = b'\xef\xbf\xbd'
idx = 0
count = 0
while count < 5:
    pos = raw.find(fffd, idx)
    if pos < 0: break
    ctx = raw[max(0,pos-30):pos+40]
    print(f'pos={pos} hex: {ctx.hex()}')
    try:
        print(f'  text: {ctx.decode("utf-8", errors="replace")!r}')
    except:
        pass
    count += 1
    idx = pos + 3

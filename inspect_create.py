#!/usr/bin/env python3
"""Inspect exact chars around L687"""
import sys
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

out = open('inspect_out.txt', 'w', encoding='utf-8')
# L683 and L687
for ln in [683, 687]:
    line = lines[ln-1]
    out.write(f'L{ln} hex around FFFD:\n')
    for i, ch in enumerate(line):
        if ord(ch) == 0xFFFD:
            snippet = line[max(0,i-5):i+8]
            hexs = ' '.join(f'{ord(c):04X}' for c in snippet)
            out.write(f'  pos {i}: {hexs}\n')
    out.write(f'  full: {repr(line)}\n')
out.close()
print('done')

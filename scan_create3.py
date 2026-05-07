#!/usr/bin/env python3
"""Show exact repr of remaining corrupted lines"""
import sys
p = '\ufffd'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

out = open('create3.txt', 'w', encoding='utf-8')
for i, line in enumerate(lines, 1):
    if p in line:
        out.write(f'L{i}: {repr(line)}\n')
out.close()
print('done', sum(l.count(chr(0xFFFD)) for l in lines), 'total')

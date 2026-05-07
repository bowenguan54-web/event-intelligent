#!/usr/bin/env python3
p = '\ufffd'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
import sys
out = open('create2.txt', 'w', encoding='utf-8')
for i, line in enumerate(lines, 1):
    if p in line:
        out.write(f'L{i}: {repr(line.rstrip())}\n')
out.close()
print('done')

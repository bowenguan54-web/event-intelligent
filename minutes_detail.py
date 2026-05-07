#!/usr/bin/env python3
"""Inspect remaining FFFD in MeetingMinutes.vue"""
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingMinutes.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

out = open('minutes_detail.txt', 'w', encoding='utf-8')
for i, line in enumerate(lines, 1):
    if '\ufffd' in line:
        out.write(f'\nL{i}:\n{repr(line)}\n')
        for j, ch in enumerate(line):
            if ord(ch) == 0xFFFD:
                snippet = line[max(0,j-8):j+10]
                hexs = ' '.join(f'{ord(c):04X}' for c in snippet)
                out.write(f'  pos{j}: {hexs}\n')
out.close()
print('done')

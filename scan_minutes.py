#!/usr/bin/env python3
"""Scan MeetingMinutes.vue for corruptions"""
p = '\ufffd'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingMinutes.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
out = open('minutes_scan.txt', 'w', encoding='utf-8')
count = 0
for i, line in enumerate(lines, 1):
    if p in line:
        count += 1
        out.write(f'L{i}: {repr(line)}\n')
out.close()
print(f'Total lines: {len(lines)}')
print(f'FFFD lines: {count}')
print(f'FFFD total: {sum(l.count(p) for l in lines)}')

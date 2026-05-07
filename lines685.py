#!/usr/bin/env python3
"""Show lines 685-690"""
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
out = open('lines685.txt', 'w', encoding='utf-8')
for i in range(684, 691):
    out.write(f'L{i+1}: {repr(lines[i])}\n')
out.close()
print('done')

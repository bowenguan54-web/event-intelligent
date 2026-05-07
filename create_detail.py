#!/usr/bin/env python3
"""Show hex around FFFD in specific lines"""
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

target_lines = [423, 524, 525, 526, 681, 683, 687, 699, 744, 827, 1083, 1398, 1431, 1575, 1579, 1619, 1714, 1757, 1934, 1986]
out = open('create_detail.txt', 'w', encoding='utf-8')
for ln in target_lines:
    line = lines[ln-1]
    out.write(f'\nL{ln}:\n{repr(line)}\n')
    # Find positions of FFFD
    for i, ch in enumerate(line):
        if ord(ch) == 0xFFFD:
            ctx = repr(line[max(0,i-10):i+5])
            out.write(f'  FFFD at pos {i}: {ctx}\n')
out.close()
print('done')

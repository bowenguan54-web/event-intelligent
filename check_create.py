#!/usr/bin/env python3
"""Check if file is now re-corrupted / garbled"""
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'

# read as binary and look for 0xEF 0xBF 0xBD (U+FFFD)
with open(path, 'rb') as f:
    data = f.read()

fffd_count = data.count(b'\xef\xbf\xbd')
print(f'FFFD bytes (U+FFFD): {fffd_count}')

# look for 0x3F after various byte sequences (the raw corruption pattern)
# Raw corruption: last byte of 3-byte sequence replaced with 0x3F
# 3-byte UTF-8 starts with 0xE0-0xEF
import re
# Pattern: E0-EF xx 3F
raw_corrupt = re.findall(b'[\xe0-\xef][\x80-\xbf]\x3f', data)
print(f'Raw 3-byte corruption (EX XX 3F): {len(raw_corrupt)}')

# Check first few lines
with open(path, encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')
print(f'FFFD count via string: {sum(l.count(chr(0xFFFD)) for l in lines)}')

# Show L191
print(f'L191: {repr(lines[190][:100])}')
print(f'L413: {repr(lines[412][:100])}')

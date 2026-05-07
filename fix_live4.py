#!/usr/bin/env python3
"""Final fix for last 3 MeetingLive corruptions using byte-aware approach"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingLive.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

print(f'Before: {c.count(chr(0xfffd))}')

# Fix 1: ellipsis '…' corruption  (E2 80 A6 + ' absorbed → \ufffd?)
# content: match[0].slice(0, 60) + '…' : match[0]
c = c.replace("slice(0, 60) + '" + p + " : match[0]",
              "slice(0, 60) + '…' : match[0]")

# Fix 2-3: // idle → 全新开始 (two occurrences, → = E2 86 92, 始 = E5 A7 8B)
# The → corruption: E2 86 3F (no absorption or space absorbed)
# The 始 corruption: E5 A7 3F + \n absorbed -> 4 spaces
c = c.replace('// idle ' + p + ' 全新开' + p + '    recordingStatus',
              '// idle → 全新开始\n    recordingStatus')
# In case there's still more (double replace for 2nd occurrence)
c = c.replace('// idle ' + p + ' 全新开' + p + '    recordingStatus',
              '// idle → 全新开始\n    recordingStatus')

after = c.count(chr(0xfffd))
print(f'After: {after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')

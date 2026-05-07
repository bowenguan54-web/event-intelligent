#!/usr/bin/env python3
"""Byte-level fix for remaining 2 'idle' corruptions in MeetingLive.vue"""

# The raw corruption in file:
# // idle [E2 86 3F] [5168=全][65B0=新][5F00=开][FFFD][?]    recordingStatus
# After all the write-backs, \ufffd? = EF BF BD 3F in the file

path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingLive.vue'

with open(path, 'rb') as f:
    raw = f.read()

# Pattern to find: "// idle " + (corrupted →) + " 全新开" + (corrupted 始) + "    recordingStatus"
# corrupted → = E2 86 3F OR EF BF BD 3F (FFFD?)
# 全 = E5 85 A8, 新 = E6 96 B0, 开 = E5 BC 80
#   wait: U+5168=全=E5 85 A8? Let me compute: 5168=0x5168
#   E5=11100101, 85=10000101, A8=10101000 -> (5<<12)|(5<<6)|40 = 20480+320+40=20840=0x5168 YES
# U+65B0=新: E6=11100110, 96=10010110, B0=10110000 -> (6<<12)|(0x16<<6)|0x30 = 24576+1408+48=26032=0x65B0 YES  
# U+5F00=开: E5=11100101, BC=10111100, 80=10000000 -> (5<<12)|(0x3C<<6)|0 = 20480+3840+0=24320=0x5F00 YES

import re

# The "→" arrow: U+2192 = E2 86 92. Corrupted: last byte 92→3F. After writeback: EF BF BD 3F
# The "始": U+59CB = E5 A7 8B. Corrupted: last byte 8B→3F. After writeback: EF BF BD 3F + absorbed \n
# Full pattern: "// idle " + EF_BF_BD_3F + " " + E5_85_A8 + E6_96_B0 + E5_BC_80 + EF_BF_BD_3F + "    recordingStatus"

idle_corrupt = (b'// idle ' + b'\xef\xbf\xbd\x3f' + b' ' + 
               b'\xe5\x85\xa8' + b'\xe6\x96\xb0' + b'\xe5\xbc\x80' + 
               b'\xef\xbf\xbd\x3f' + b'    recordingStatus')

# Replacement: "// idle → 全新开始\n    recordingStatus"
idle_fixed = (b'// idle ' + b'\xe2\x86\x92' +  # →
             b' ' + b'\xe5\x85\xa8' + b'\xe6\x96\xb0' + b'\xe5\xbc\x80' +  # 全新开
             b'\xe5\xa7\x8b' +  # 始
             b'\n' + b'    recordingStatus')

print(f'Pattern length: {len(idle_corrupt)}')
print(f'Found: {raw.count(idle_corrupt)} occurrences')

raw_fixed = raw.replace(idle_corrupt, idle_fixed)
print(f'After: {raw_fixed.count(idle_corrupt)} remaining occurrences')

with open(path, 'wb') as f:
    f.write(raw_fixed)

# Verify
with open(path, encoding='utf-8', errors='replace') as f:
    content = f.read()
print(f'FFFD count: {content.count(chr(0xfffd))}')
print('Done!')

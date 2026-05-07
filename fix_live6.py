#!/usr/bin/env python3
"""Byte-level fix for remaining 2 idle corruptions (using exact bytes from dump)"""

path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingLive.vue'

with open(path, 'rb') as f:
    raw = f.read()

print(f'File size: {len(raw)} bytes')
print(f'Line endings: {"CRLF" if b"\r\n" in raw else "LF"}')

# From byte dump: // idle [EF BF BD 3F][E5 85 A8][E6 96 B0][E5 BC 80][EF BF BD 3F][20202020]recordingStatus
# Full pattern: b'// idle \xef\xbf\xbd\x3f\xe5\x85\xa8\xe6\x96\xb0\xe5\xbc\x80\xef\xbf\xbd\x3f    recordingStatus'

old = b'// idle \xef\xbf\xbd\x3f\xe5\x85\xa8\xe6\x96\xb0\xe5\xbc\x80\xef\xbf\xbd\x3f    recordingStatus'
# Replace with: // idle → 全新开始\r\n    recordingStatus
# → = E2 86 92, 全 = E5 85 A8, 新 = E6 96 B0, 开 = E5 BC 80, 始 = E5 A7 8B
new = b'// idle \xe2\x86\x92 \xe5\x85\xa8\xe6\x96\xb0\xe5\xbc\x80\xe5\xa7\x8b\r\n    recordingStatus'

print(f'Occurrences of pattern: {raw.count(old)}')

raw_fixed = raw.replace(old, new)
print(f'After replacement: {raw_fixed.count(old)} remaining')

# Verify FFFD count
fffd_count = raw_fixed.count(b'\xef\xbf\xbd')
print(f'FFFD bytes: {fffd_count}')

with open(path, 'wb') as f:
    f.write(raw_fixed)
print('Done!')

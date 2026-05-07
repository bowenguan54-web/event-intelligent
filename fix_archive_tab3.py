#!/usr/bin/env python3
"""Final fix for last 3 corruptions"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingArchiveTab.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# [8] L818: ${s.speaker}：${s.text}  (single } not double)
c = c.replace('s.speaker}' + p + '{s.text}', "s.speaker}}：${s.text}")

# [9] L896: 加速执行方案' (description: not description=)
c = c.replace('加速执行方' + p + ', description:', "加速执行方案', description:")

# [10] L897: 时间协调' (description: not description=)
c = c.replace('施工时间协' + p + ', description:', "施工时间协调', description:")

after = c.count('\ufffd')
print(f'After: {after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

#!/usr/bin/env python3
"""Fix last 2 in MeetingMinutes.vue"""
p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingMinutes.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()
before = c.count('\ufffd')
print(f'Before: {before}')

# L901: 截断\ufffd?  const  (）absorbed \n)
c = c.replace('可能截断' + p + '  const chunks', '可能截断）\n  const chunks')

# L998: '拟稿签署成功\ufffd?)  ('  absorbed by 功)
c = c.replace("ElMessage.success('拟稿签署成功" + p + ")", "ElMessage.success('拟稿签署成功')")

after = c.count('\ufffd')
print(f'After: {after}')
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

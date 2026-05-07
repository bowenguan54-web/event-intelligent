#!/usr/bin/env python3
"""Third-pass fix for MeetingMinutes.vue - 29 remaining - exact patterns"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingMinutes.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# L25: 参考面板\ufffd?--> → 参考面板 -->
c = c.replace('参考面' + p + '-->', '参考面板 -->')

# L139: ref-section-title">\ufffd?关键要点  (the bullet/star emoji absorbed <)
c = c.replace('"ref-section-title">' + p + '关键要点<', '"ref-section-title">✨ 关键要点<')

# L998: 拟稿签署成功\ufffd?)
c = c.replace("'拟稿签署成" + p + ")", "'拟稿签署成功')")

# L885: Chrome \ufffd?Edge  (or absorbed <)
c = c.replace('Chrome ' + p + "Edge'", "Chrome 或 Edge'")

# L901: 截断\ufffd?  const chunks (newline absorbed)
c = c.replace('可能截' + p + '  const chunks', '可能截断）\n  const chunks')

# Template patterns - HTML inside strings  
# Pattern 1: XX\ufffd?/strong> where XX is end of Chinese word  
# From hex: 65F6 95F4 FFFD 003F 002F 0073 = 时间 FFFD ?/strong
# 8BAE 65F6 95F4 = 会议时间;  95F4 = 间
c = c.replace('时间' + p + '/strong>', '时间</strong>')
# 5730 70B9 = 地点; 70B9 = 点
c = c.replace('地点' + p + '/strong>', '地点</strong>')
# 53C2 4F1A 4EBA 5458 = 参会人员; 5458 = 员
c = c.replace('参会人员' + p + '/strong>', '参会人员</strong>')

# Pattern 2: 待填\ufffd?nbsp;  (写 absorbed &)
# 5F85 586B FFFD 003F 006E 0062 0073 0070 = 待填 FFFD ?nbsp
c = c.replace('待填' + p + 'nbsp;&nbsp;', '待填写&nbsp;&nbsp;')
c = c.replace('待填' + p + 'nbsp;', '待填写&nbsp;')

# Pattern 3: 待填\ufffd?/p> (写 absorbed <)
c = c.replace('待填' + p + '/p>', '待填写</p>')

# L702: specific patterns  
# strong>时间: 时 = 65F6 95F4; after FFFD: /strong> then 待填\ufffd?/p>  
# (these should be caught by the generic patterns above)

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

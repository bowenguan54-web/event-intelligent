#!/usr/bin/env python3
"""Follow-up fix for 13 remaining corruptions in MeetingArchiveTab.vue"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingArchiveTab.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# [0] L40: participants_count }}人</span>  (}} was broken in f-string before)
c = c.replace('participants_count }}' + p + '/span>', 'participants_count }}人</span>')

# [1] L91: }} — {{ fmtTime
c = c.replace('start_time) }} ' + p + '{{ fmtTime', 'start_time) }} — {{ fmtTime')

# [2] L166: {{ seg.speaker }}：</span>
c = c.replace('seg.speaker }}' + p + '/span>', 'seg.speaker }}：</span>')

# [3] L477: 稳定运行。' },
c = c.replace('系统稳定运行' + p + " },", "系统稳定运行。' },")

# [4] L490: 完成全面部署。' },
c = c.replace('完成全面部署' + p + ' },', "完成全面部署。' },")

# [5] L561: 会议记录关键点编辑\nconst
c = c.replace('会议记录关键点编' + p + 'const', '会议记录关键点编辑\nconst')

# [6] L641: 确认删除会议「${meetingTitle}」
c = c.replace('确认删除会议' + p + '{meetingTitle}', '确认删除会议「${meetingTitle}')

# [7] L815: .join('、')
c = c.replace(".join('" + p + ")}", ".join('、')}")

# [8] L818: ${s.speaker}：${s.text}
c = c.replace('s.speaker}}' + p + '{s.text}', 's.speaker}}：${s.text}')

# [9] L896: 信息化专项经费加速执行方案'
c = c.replace('加速执行方' + p + ', description=', "加速执行方案', description=")

# [10] L897: 会议室改造施工时间协调'
c = c.replace('施工时间协' + p + ', description=', "施工时间协调', description=")

# [11] L947: 已添加 ${toAdd.length}
c = c.replace('已添' + p + '${toAdd', '已添加 ${toAdd')

# [12] L1267 CSS comment: /* ─── 响应式 ─── */
c = c.replace('响应' + p + '─── */', '响应式 ─── */')

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print('Done!')

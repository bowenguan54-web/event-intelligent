#!/usr/bin/env python3
"""Fourth-pass fix for MeetingCreate.vue - 40 remaining"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# L423: & 签到表 -->
c = c.replace('& 签到' + p + ' ==================== --> -->', '& 签到表 ==================== -->')

# L524-526, L570-572, L631-633: button texts (single char absorbed + / before el-button)
# Only one char is missing per button - the char IS already consumed
# Pattern revealed: >上\ufffd?/  →  the button char is 上/下/删 then \ufffd? ate the < of </el-button>
c = c.replace('moveExpertRowUp(idx)">上' + p + '/el-button>', 'moveExpertRowUp(idx)">上</el-button>')
c = c.replace('moveExpertRowDown(idx)">下' + p + '/el-button>', 'moveExpertRowDown(idx)">下</el-button>')
c = c.replace('removeExpertRow(idx)">删' + p + '/el-button>', 'removeExpertRow(idx)">删</el-button>')
c = c.replace('moveOtherRowUp(idx)">上' + p + '/el-button>', 'moveOtherRowUp(idx)">上</el-button>')
c = c.replace('moveOtherRowDown(idx)">下' + p + '/el-button>', 'moveOtherRowDown(idx)">下</el-button>')
c = c.replace('removeOtherRow(idx)">删' + p + '/el-button>', 'removeOtherRow(idx)">删</el-button>')

# L681 & L699: 🤖\ufffd?</span>  
c = c.replace('"quick-icon">🤖' + p + '/span>自动', '"quick-icon">🤖</span>自动')
# L699: typing-dot •\ufffd?</span>
c = c.replace('"typing-dot">•' + p + '/span>', '"typing-dot">•</span>')

# L683: 详细议程\ufffd?
c = c.replace('总结的详细议' + p + '")', '总结的详细议程")')

# L687: 📝\ufffd?</span> 简洁议\ufffd?\n
c = c.replace('"quick-icon">📝' + p + '/span>简洁议' + p + '\n', '"quick-icon">📝</span>简洁议程\n')

# L744: ✅ 已生成</el-tag>
c = c.replace('style="margin-left:8px">✅ 已生' + p + '/el-tag>', 'style="margin-left:8px">✅ 已生成</el-tag>')

# L827: agendaContent ? '✅ 已生成' : '未生成'
c = c.replace("agendaContent ? '" + p + " 已生" + p + " : '未生" + p + " }}",
              "agendaContent ? '✅ 已生成' : '未生成' }}")

# L1083: 优先从 form.location
c = c.replace('  // 优先' + p + ' form.location', '  // 优先从 form.location')

# L1398: 在${extConflict.timeRange}
c = c.replace(' ' + p + ' ${extConflict.timeRange} 有', ' 在 ${extConflict.timeRange} 时间段有')

# L1431: 已选人员
c = c.replace('已选人' + p + ' ${u.real_name}', '已选人员 ${u.real_name}')
c = c.replace(' ' + p + ' ${info.timeRange} 有', ' 在 ${info.timeRange} 时间段有')

# L1571: Markdown语法等）。 - pattern: 法\ufffd?\ufffd?\ufffd?*等）\ufffd?
# Read the actual chars carefully from the file
c = c.replace('Markdown语法' + p + p + p + '*等）' + p, 'Markdown语法、##、*等）。')

# L1575: 格式：序号
c = c.replace('格式' + p + ' 序号', '格式：序号')

# L1579: 开场5分钟
c = c.replace('开' + p + ' 分钟、每个议程5-', '开场5分钟、每个议程5-')

# L1619: 会议名称：${form.title}
c = c.replace('会议名称' + p + ' {form.title}', '会议名称：${form.title}')

# L1714-1716: template agendas
# L1714: 纪律\ufffd?分钟  → 纪律（5分钟
c = c.replace('宣读会议纪律' + p + ' 分钟）', '宣读会议纪律（5分钟）')
# 讨论\ufffd?0分钟 → 讨论（30分钟
c = c.replace('专家提问与讨论' + p + '0分钟）', '专家提问与讨论（30分钟）')
# L1714: 散会 (should be fixed from prev pass, check)
# L1715: 发言\ufffd?0分钟 → 发言（10分钟
c = c.replace('一、主题发言' + p + '0分钟）', '一、主题发言（10分钟）')
c = c.replace('四、总结发言' + p + '0分钟）', '四、总结发言（10分钟）')
# L1716: 决策\ufffd?0分钟 → 决策（30分钟
c = c.replace('讨论与决策' + p + '0分钟）', '讨论与决策（30分钟）')
# 通过\ufffd?0分钟 → 通过（10分钟
c = c.replace('四、表决通过' + p + '0分钟）', '四、表决通过（10分钟）')
# 散\ufffd? at end of decision template
c = c.replace("\\n六、散" + p + "',\n", "\\n六、散会',\n")

# L1757: ${label}：</span>
c = c.replace('>${label}' + p + '</span>', '>${label}：</span>')

# L1934: 签到表</h3>
c = c.replace("|| '会议'} - 签到" + p + '</h3>', "|| '会议'} - 签到表</h3>")

# L1986: 签到表</title>
c = c.replace("|| '会议'} - 签到" + p + '</title>', "|| '会议'} - 签到表</title>")

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

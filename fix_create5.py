#!/usr/bin/env python3
"""Fifth-pass fix for MeetingCreate.vue - 31 remaining - exact patterns"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# L423: 签到\ufffd?=== → 签到表 ===
c = c.replace('& 签到' + p + '=', '& 签到表 =')

# L524-526, L570-572, L631-633: buttons — the pattern is "Up(idx)">X\ufffd?/el-button>"
# where X is the single button char (上/下/删)
# BUT the patterns already failed in prev passes. Let me check: the repr shows 'wUp(idx)">\\ufffd?/el'
# meaning the WHOLE button char is gone. So it was: idx)">上</el-button> but the 上 was corrupted to \ufffd?
# Actually: idx)">上\ufffd? means the last byte of character "上" absorbed the "<" making: idx)">上\ufffd?/el-button>
# So we have: original上 = E4 B8 8A, corrupted to "上\ufffd?" means the original char is FINE 
# and then \ufffd? ate the < of </el-button>
# Wait - repr shows 'wUp(idx)">\\ufffd?/el' - the CHAR BEFORE FFFD is NOT 上/下/删!
# It shows 'wUp(idx)">\\ufffd?' - 上 is GONE (was last byte of char that got corrupted to \ufffd?)
# So 上 = E4 B8 8A; corruption 3rd byte → 3F: E4 B8 3F → \ufffd? then absorbed the next <
# Pattern: >"\ufffd?/el-button>

c = c.replace('wUp(idx)">' + p + '/el-button>', 'wUp(idx)">上</el-button>')
c = c.replace('wDown(idx)">' + p + '/el-button>', 'wDown(idx)">下</el-button>')
c = c.replace('ExpertRow(idx)">' + p + '/el-button>', 'ExpertRow(idx)">删</el-button>')
c = c.replace('OtherRow(idx)">' + p + '/el-button>', 'OtherRow(idx)">删</el-button>')

# L681: quick-icon">🤖\ufffd?/span>  (🤖 U+1F916 = 4 bytes, last byte absorbed >)
# Actually 🤖 = F0 9F A4 96; after that the char U+25A0 or something... let's check repr:
# 'ick-icon">\\ufffd?/sp'  — so 🤖 is gone too? 
# repr shows: 'quick-icon">\ufffd?/span>' - so the icon emoji was corrupted
# 🤖 = F0 9F A4 96 = 4-byte char; if 4th byte replaced by 3F: F0 9F A4 3F → \ufffd? and consumed <
c = c.replace('"quick-icon">' + p + '/span>自动', '"quick-icon">🤖</span>自动')
c = c.replace('"quick-icon">' + p + '/span>简洁议' + p + '\n', '"quick-icon">📝</span>简洁议程\n')

# L683: 详细议\ufffd?)" → 详细议程)"
c = c.replace('总结的详细议' + p + '")', '总结的详细议程")')

# L699: typing-dot>\ufffd?/span>
c = c.replace('"typing-dot">' + p + '/span>', '"typing-dot">•</span>')

# L744: ✅ 已生\ufffd?/el-tag>  — TWO FFFD: margin-left:8px">\ufffd?已生\ufffd?/el
# first \ufffd? = the ✅ emoji (U+2705 = E2 9C 85, last byte 85→3F, absorbed >)
# second \ufffd? = 成 (E6 88 90 → E6 88 3F, absorbed <)
c = c.replace('margin-left:8px">' + p + '已生' + p + '/el-tag>', 'margin-left:8px">✅ 已生成</el-tag>')

# L827: agendaContent ? '\ufffd?已生\ufffd? : '未生\ufffd? }}
# Three FFFD:
# 1st: the ✅ in '✅ 已生成' → \ufffd? (absorbed ')
# 2nd: 成 in 已生成 → \ufffd? (absorbed ')  
# 3rd: 成 in 未生成 → \ufffd? (absorbed -)
c = c.replace("agendaContent ? '" + p + "已生" + p + " : '未生" + p + " }}",
              "agendaContent ? '✅ 已生成' : '未生成' }}")

# L1083: 优先\ufffd?form → 优先从 form
c = c.replace('// 优先' + p + 'form.location', '// 优先从 form.location')

# L1398: real_name} \ufffd?\${ext  →  real_name} 在 ${ext
c = c.replace('real_name} ' + p + '${extConflict', 'real_name} 在 ${extConflict')

# L1431: `已选人\ufffd?\${  →  `已选人员 ${
c = c.replace('`已选人' + p + '${u.real_name}', '`已选人员 ${u.real_name}')
c = c.replace('real_name} ' + p + '${info.', 'real_name} 在 ${info.')

# L1575: 格式\ufffd?序号 → 格式：序号
c = c.replace('格式' + p + '序号', '格式：序号')

# L1579: 开\ufffd?分钟 → 开场5分钟
c = c.replace('开' + p + '分钟、每个议程5-', '开场5分钟、每个议程5-')

# L1619: 名称\ufffd?{form → 名称：${form
c = c.replace('会议名称' + p + '{form.title}', '会议名称：${form.title}')

# L1714: 纪律\ufffd?分钟 → 纪律（5分钟
c = c.replace('宣读会议纪律' + p + '分钟）', '宣读会议纪律（5分钟）')

# L1757: ${label}\ufffd?/span> → ${label}：</span>
c = c.replace('>${label}' + p + '/span>', '>${label}：</span>')

# L1934 & L1986: 签到\ufffd?/h3> and /title>
c = c.replace("'会议'} - 签到" + p + '/h3>', "'会议'} - 签到表</h3>")
c = c.replace("'会议'} - 签到" + p + '/title>', "'会议'} - 签到表</title>")

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

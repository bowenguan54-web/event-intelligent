#!/usr/bin/env python3
"""Follow-up fix for remaining 17 corruptions in MeetingLive.vue"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingLive.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# '会议进行中' }} (absorption of ')
c = c.replace("title || '会议进行" + p + " }}", "title || '会议进行中' }}")
c = c.replace("title || '会议进行中' }}", "title || '会议进行中' }}")  # idempotent

# 敏感词 (newline absorbed)
c = c.replace('敏感' + p + '            </el-button>', '敏感词\n            </el-button>')

# 标注模式已开启/开启标注模式 (absorption of ')
c = c.replace("'标注模式已开" + p + " : '开启标注模" + p + " }}", "'标注模式已开启' : '开启标注模式' }}")

# 整行标注 / 局部标注 (two occurrences)
c = c.replace('，' + p + '<strong>', '，或<strong>')
c = c.replace('进行局部标' + p + '         ', '进行局部标注\n            ')  # restore \n

# 录音已暂停 (newline absorbed)
c = c.replace('录音已暂' + p + '                </template>', '录音已暂停\n                </template>')

# 尚未开始录音 (newline absorbed)
c = c.replace('尚未开始录' + p + '                </template>', '尚未开始录音\n                </template>')

# AI greeting 了解的
c = c.replace('有什么需要了解的' + p + ',', "有什么需要了解的？',")

# 记录问题确认
c = c.replace('记录问题"确' + p + ')', '记录问题"确认\')')

# 简单模拟 AI
c = c.replace('简单模' + p + 'AI', '简单模拟 AI')

# '...' string truncation
c = c.replace("+ '..." + p + " : match[0]", "+ '...' : match[0]")

# 不自动关闭 AI 弹窗（用户需点忽略或确认）
c = c.replace('用户需点忽略或确认' + p + '  }', '用户需点忽略或确认）\n  }')

# // idle → 全新开始 (two occurrences, → and 始 both corrupted)
c = c.replace('// idle ' + p + ' 全新开' + p + '    recordingStatus',
              '// idle → 全新开始\n    recordingStatus')

# 会议记录文件存在。']  (newline/quote absorbed)
c = c.replace('存在' + p + ']', "存在。']")

# CSS comment 工具栏 (space absorbed)
c = c.replace('工具' + p + '===== */', '工具栏 ===== */')

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

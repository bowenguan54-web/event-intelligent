#!/usr/bin/env python3
"""Second-pass fix for MeetingMinutes.vue - 50 remaining"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingMinutes.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# L25: 纪要编辑区 + 参考面板 -->  (newline absorbed)
c = c.replace('纪要编辑区 + 参考面' + p + '-->', '纪要编辑区 + 参考面板 -->')

# L43: <!-- 编辑工具栏：\ufffd?draft  (colon char absorbed)
c = c.replace('<!-- 编辑工具栏：' + p + 'draft', '<!-- 编辑工具栏：仅 draft')

# L119: ✅\ufffd?专家组长已完成签署</el-tag>
# The ✅ was corrupted eating the space
c = c.replace('"success" size="large">' + p + '专家组长已完成签' + p + '/el-tag>',
              '"success" size="large">✅ 专家组长已完成签署</el-tag>')

# L139: ✨\ufffd?关键要点</div>  
c = c.replace('"ref-section-title">' + p + '关键要' + p + '/div>',
              '"ref-section-title">✨ 关键要点</div>')

# Also single FFFD variants:
c = c.replace('"ref-section-title">' + p + ' 关键要点</div>',
              '"ref-section-title">✨ 关键要点</div>')
c = c.replace('"success" size="large">' + p + ' 专家组长已完成签' + p + '/el-tag>',
              '"success" size="large">✅ 专家组长已完成签署</el-tag>')

# L146: 生成\ufffd?{{ new Date  → 生成于 {{ new Date
c = c.replace('生成' + p + '{{ new Date', '生成于 {{ new Date')

# L200: \ufffd?<strong>  → 为 <strong>
c = c.replace('color:#606266">' + p + '<strong>{{ offlineSignTarget?.real_name }}<',
              'color:#606266">为 <strong>{{ offlineSignTarget?.real_name }}<')

# L283: // 会议状态\n  (newline absorbed)
c = c.replace('// 会议状' + p + "const meetingStatus", '// 会议状态\nconst meetingStatus')

# L578: // 编辑器\n  (newline absorbed)
c = c.replace('// 编辑' + p + 'const editorToolbarRef', '// 编辑器\nconst editorToolbarRef')

# L584: // 纪要状态\n
c = c.replace('// 纪要状' + p + "const minutesStatus", '// 纪要状态\nconst minutesStatus')

# L592: // 审签状态\n
c = c.replace('// 审签状' + p + 'const loadingStatus', '// 审签状态\nconst loadingStatus')

# L611: // 参考面板\n
c = c.replace('// 参考面' + p + 'const showRefPanel', '// 参考面板\nconst showRefPanel')

# L697: editorContainerRef template - remaining corruptions
# '纰要' → '纪要' (was that in the original? No, wait...)
# 时间：</strong>待填\ufffd?/p>  etc.
c = c.replace('<strong>时间：</strong>待填' + p + '/p>', '<strong>时间：</strong>待填写</p>')
c = c.replace('<strong>地点：</strong>待填' + p + '/p>', '<strong>地点：</strong>待填写</p>')
c = c.replace('<strong>参会人员：</strong>待填' + p + '/p>', '<strong>参会人员：</strong>待填写</p>')
c = c.replace('议题讨论记' + p + '/h2>', '议题讨论记录</h2>')
c = c.replace('请点击上' + p + '<b>AI', '请点击上方<b>AI')
c = c.replace('决策结' + p + '/h2>', '决策结论</h2>')
c = c.replace('纪要加载失败，请刷新页面' + p + '/p>', '纪要加载失败，请刷新页面。</p>')
c = c.replace("'纪要加载失败，请刷新页面。</p>'", "'<p>纪要加载失败，请刷新页面。</p>'")

# L700: // 载入纪要状态\n
c = c.replace('// 载入纪要状' + p + '    minutesStatus', '// 载入纪要状态\n    minutesStatus')

# L703: // 载入签名状态\n
c = c.replace('// 载入签名状' + p + '    const sigs', '// 载入签名状态\n    const sigs')

# L727: general template - remaining
# '会议时间：</strong>待填\ufffd?nbsp;'
c = c.replace('<strong>会议时间：</strong>待填' + p + 'nbsp;', '<strong>会议时间：</strong>待填写&nbsp;')
c = c.replace('<strong>会议地点：</strong>待填' + p + '/p>', '<strong>会议地点：</strong>待填写</p>')
c = c.replace('<strong>地点：</strong>待填' + p + 'nbsp;', '<strong>地点：</strong>待填写&nbsp;')
c = c.replace('待填写nbsp;', '待填写&nbsp;')
c = c.replace('待填写/p>', '待填写</p>')
c = c.replace('<td>待填' + p + '</td>', '<td>待填写</td>')
c = c.replace('<td>待填' + p + '/td>', '<td>待填写</td>')
# '2. \ufffd?/h3>'  → '2. 议项</h3>'
c = c.replace('<h3>2. ' + p + '/h3>', '<h3>2. 议项</h3>')

# L764: // 仅在已发布/审签中时轮询
c = c.replace('// 仅在已发' + p + '审签中时轮询', '// 仅在已发布/审签中时轮询')

# L878: Chrome 或 Edge
c = c.replace('Chrome ' + p + " Edge'", "Chrome 或 Edge'")

# L894: 截断）\n
c = c.replace('对长文本可能截' + p + '  const chunks', '对长文本可能截断）\n  const chunks')

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

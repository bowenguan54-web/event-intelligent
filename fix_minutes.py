#!/usr/bin/env python3
"""Comprehensive fix for MeetingMinutes.vue - 157 corruptions"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingMinutes.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# ── TEMPLATE ────────────────────────────────────────────────────────────

# L3: 状态横幅 -->
c = c.replace('<!-- 状态横' + p + '-->', '<!-- 状态横幅 -->')

# L6: 不可修改\ufffd? → 不可修改。
c = c.replace('如需修改请等待会议端驳回' + p, '如需修改请等待会议端驳回。')

# L9: 纪要审签中\ufffd? → 纪要审签中。
c = c.replace('等待会议端审签' + p, '等待会议端审签。')

# L12: 重新发布\ufffd? → 重新发布。
c = c.replace('请修改后重新发布' + p, '请修改后重新发布。')

# L16: 纪要签署流程已结束\ufffd? → 已结束。
c = c.replace('纪要签署流程已结束' + p, '纪要签署流程已结束。')

# L23: 审查 \ufffd? → 审查 →
c = c.replace('前往问题记录审查 ' + p, '前往问题记录审查 →')

# L25: 纪要编辑区 + 参考面板 -->
c = c.replace('纪要编辑区 + 参考面' + p + '-->', '纪要编辑区 + 参考面板 -->')

# L35: 收起参考资料 / 展开参考资料
c = c.replace("showRefPanel ? '收起参" + p + " : '展开参考资" + p, 
              "showRefPanel ? '收起参考资料' : '展开参考资料'")

# L43: draft / rejected 可操作 -->
c = c.replace('draft / rejected 可操' + p + '-->', 'draft / rejected 可操作 -->')

# L57: 办公会纪要</el-dropdown-item>
c = c.replace('办公会纪' + p + '/el-dropdown-item>', '办公会纪要</el-dropdown-item>')

# L109: 专家组长签署状态 -->
c = c.replace('专家组长签署状' + p + '-->', '专家组长签署状态 -->')

# L112: '已签署' : '待签署'
c = c.replace("draftSigned ? '已签" + p + " : '待签" + p, "draftSigned ? '已签署' : '待签署'")

# L119: ✅ 专家组长已完成签署</el-tag>
c = c.replace('"success" size="large">' + p + ' 专家组长已完成签' + p + '/el-tag>',
              '"success" size="large">✅ 专家组长已完成签署</el-tag>')

# L126: 右侧参考面板 -->
c = c.replace('<!-- 右侧参考面' + p + '-->', '<!-- 右侧参考面板 -->')

# L129: 📋 参考资料</span>
c = c.replace('"ref-panel-title">📋 参考资' + p + '/span>', '"ref-panel-title">📋 参考资料</span>')

# L139: ✨ 关键要点</div>
c = c.replace('"ref-section-title">' + p + ' 关键要' + p + '/div>', '"ref-section-title">✨ 关键要点</div>')

# L146: 生成于 {{ ... }}
c = c.replace('生成' + p + ' {{ new Date', '生成于 {{ new Date')

# L152: 暂无参考资料</p>
c = c.replace('暂无参考资' + p + '/p>', '暂无参考资料</p>')

# L153: 将自动显示在此处</p>
c = c.replace('将自动显示在此' + p + '/p>', '将自动显示在此处。</p>')

# L160: 签到管理（审签结束后）-->
c = c.replace('签到管理（审签结束后' + p + '-->', '签到管理（审签结束后） -->')

# L171: 重新签名）；对于无设备人员...代为签字。
c = c.replace('可直接点击"签到"代为签字' + p + '/p>', '可直接点击"签到"代为签字。</p>')

# L177: label="状态"
c = c.replace('label="状' + p + ' width="100"', 'label="状态" width="100"')

# L179: '已签到' : '未签到'
c = c.replace("row.checked_in ? '已签" + p + " : '未签" + p, "row.checked_in ? '已签到' : '未签到'")

# L198: 代签到弹框 -->
c = c.replace('<!-- 代签到弹' + p + '-->', '<!-- 代签到弹框 -->')

# L199: title="签到-${...}"
c = c.replace('`:签到' + p + '{offlineSignTarget', '`签到-${offlineSignTarget')

# L199 variant:
c = c.replace(':title="`签到' + p + '{offlineSignTarget?.real_name', ':title="`签到-${offlineSignTarget?.real_name')
c = c.replace('v-model="offlineSignVisible" :title="`签到' + p + '{offlineSignTarget',
              'v-model="offlineSignVisible" :title="`签到-${offlineSignTarget')

# L200: 在下方手写签名</p>
c = c.replace('在下方手写签' + p + '/p>', '在下方手写签名。</p>')

# L226: :title="`签到（放大）-${...}"
c = c.replace(':title="`签到（放大）' + p + '{offlineSignTarget', ':title="`签到（放大）-${offlineSignTarget')

# L248: 使用此签名</el-button>
c = c.replace('使用此签' + p + '/el-button>', '使用此签名</el-button>')

# L256: label="编辑人"
c = c.replace('label="编辑' + p + ' width="100"', 'label="编辑人" width="100"')

# ── JS SECTION ────────────────────────────────────────────────────────────

# L283: // 会议状态
c = c.replace('// 会议状' + p + '\n', '// 会议状态\n')

# L328: '退回失败'
c = c.replace("'退回失" + p + ")", "'退回失败')")

# L526: '确认结束本次会议？'
c = c.replace("'确认结束本次会议" + p + ",", "'确认结束本次会议？',")

# L538: '会议已结束'
c = c.replace("ElMessage.success('会议已结" + p + ")", "ElMessage.success('会议已结束')")

# L570: '纪要签署流程已完成'
c = c.replace("'已强制结束审签，纪要签署流程已完" + p + ")", "'已强制结束审签，纪要签署流程已完成')")

# L578: // 编辑器
c = c.replace('// 编辑' + p + '\n', '// 编辑器\n')

# L584: // 纪要状态
c = c.replace('// 纪要状' + p + '\n', '// 纪要状态\n')

# L588: status map values
c = c.replace("published: '已发" + p + ",", "published: '已发布',")
c = c.replace("rejected: '已驳" + p + ",", "rejected: '已驳回',")
c = c.replace("signed: '已签" + p + ",", "signed: '已签署',")
c = c.replace("reviewing: '审签" + p + ",", "reviewing: '审签中',")
c = c.replace("none: '未创" + p, "none: '未创建'")

# L592: // 审签状态
c = c.replace('// 审签状' + p + '\n', '// 审签状态\n')

# L593: sign_step='draft' 的记录 + sign_step='review' 的所有记录
c = c.replace("// sign_step='draft' 的记" + p, "// sign_step='draft' 的记录")
c = c.replace("// sign_step='review' 的所有记" + p, "// sign_step='review' 的所有记录")

# L611: // 参考面板
c = c.replace('// 参考面' + p + '\n', '// 参考面板\n')

# L647: // 发布/审签中状态自动轮询签署进度
c = c.replace('// 发布/审签中状态自动轮询签署进' + p, '// 发布/审签中状态自动轮询签署进度')

# L648: // 若已完成签署，加载签到管理数据
c = c.replace('// 若已完成签署，加载签到管理数' + p, '// 若已完成签署，加载签到管理数据')

# L697: HTML template content (multiple待填写)
c = c.replace("'时间：'</strong>待填" + p + "/p>", "'时间：'</strong>待填写</p>")
c = c.replace('<strong>时间：</strong>待填' + p + '/p>', '<strong>时间：</strong>待填写</p>')
c = c.replace('<strong>地点：</strong>待填' + p + '/p>', '<strong>地点：</strong>待填写</p>')
c = c.replace('<strong>参会人员：</strong>待填' + p + '/p>', '<strong>参会人员：</strong>待填写</p>')
c = c.replace('手动编写' + p + '/p>', '手动编写。</p>')
c = c.replace('<li>待填' + p + '/li>', '<li>待填写</li>')
c = c.replace('<p>待填' + p + '/p>', '<p>待填写</p>')
c = c.replace('待填' + p + '</p>', '待填写</p>')

# L700: // 载入纪要状态
c = c.replace('// 载入纪要状' + p + '\n', '// 载入纪要状态\n')

# L703: // 载入签名状态
c = c.replace('// 载入签名状' + p + '\n', '// 载入签名状态\n')

# L706: // 从后端取与会人数（可选，为了判断"全部已签"）
c = c.replace('// 从后端取与会人数（可选，为了判断"全部已签"' + p, '// 从后端取与会人数（可选，为了判断"全部已签"）')

# L709: // 控制编辑器只读
c = c.replace('// 控制编辑器只' + p, '// 控制编辑器只读')

# L719: '纪要加载失败，请刷新页面'
c = c.replace("'纪要加载失败，请刷新页面" + p + "</p>'", "'纪要加载失败，请刷新页面。</p>'")

# L727-730: HTML templates - all 待填写 and section titles
# These have many corruptions. Work through systematically.
# Common patterns in template strings:
c = c.replace("'会议概" + p + "/h2>", "'会议概况</h2>")
c = c.replace("'时间：</strong>待填' + p +", "'时间：</strong>待填写'")

# More specific patterns for L727+
templates = [
    ('会议概' + p + '/h2>', '会议概况</h2>'),
    ('会议内' + p + '/h2>', '会议内容</h2>'),
    ('会议决' + p + '/h2>', '会议决议</h2>'),
    ('待办事' + p + '/h2>', '待办事项</h2>'),
    ('时间：</strong>待填' + p, '时间：</strong>待填写'),
    ('地点：</strong>待填' + p, '地点：</strong>待填写'),
    ('参会人员：</strong>待填' + p, '参会人员：</strong>待填写'),
    ('主持人：</strong>待填' + p, '主持人：</strong>待填写'),
    ('记录人：</strong>待填' + p, '记录人：</strong>待填写'),
    ('责任' + p + '/th>', '责任人</th>'),
    ('<td>待填' + p + '</td>', '<td>待填写</td>'),
    ('<li>待填' + p + '</li>', '<li>待填写</li>'),
    ('<p>待填' + p + '</p>', '<p>待填写</p>'),
    ('<p>待填' + p + '/p>', '<p>待填写</p>'),
    # 评审会议
    ('评审项目概' + p + '/h2>', '评审项目概况</h2>'),
    ('主要审查意' + p + '/h2>', '主要审查意见</h2>'),
    ('尚列问题清' + p + '/h2>', '尚列问题清单</h2>'),
    ('专家评审结' + p + '/h2>', '专家评审结论</h2>'),
    ('评审愿' + p + '/h2>', '评审愿景</h2>'),
    ('评审会议纪' + p + '/h1>', '评审会议纪要</h1>'),
    # 专题研讨
    ('专题研讨会纪' + p + '/h1>', '专题研讨会纪要</h1>'),
    ('情况通报</h2>', '情况通报</h2>'),  # already OK
    ('主要讨论意' + p + '/h2>', '主要讨论意见</h2>'),
    ('支持意见</h3>', '支持意见</h3>'),  # already OK
    ('待商榷事' + p + '/h3>', '待商榷事项</h3>'),
    ('研讨结论与下一步工' + p + '/h2>', '研讨结论与下一步工作</h2>'),
    # 办公会
    ('办公会纪' + p + '/h1>', '办公会纪要</h1>'),
    ('基本信' + p + '/h2>', '基本信息</h2>'),
    ('据办事' + p + '/h2>', '议办事项</h2>'),
    ('其他事' + p + '/h2>', '其他事项</h2>'),
    ('散' + p + '/h2>', '散会</h2>'),
    ('决议</h3>', '决议</h3>'),  # already OK
    ('<strong>主议题：</strong>待填' + p, '<strong>主议题：</strong>待填写'),
    ('<strong>参会专家及代表：</strong>待填' + p, '<strong>参会专家及代表：</strong>待填写'),
    ('<strong>参会人：</strong>待填' + p, '<strong>参会人：</strong>待填写'),
    ('<strong>会议时间：</strong>待填' + p, '<strong>会议时间：</strong>待填写'),
    ('<strong>会议地点：</strong>待填' + p, '<strong>会议地点：</strong>待填写'),
    ('会议于待填写散会' + p + '/p>', '会议于待填写散会。</p>'),
]
for old, new in templates:
    c = c.replace(old, new)

# L740: 确认继续？
c = c.replace("确认继续" + p + ",", "确认继续？',")

# L764: // 仅在已发布/审签中时轮询
c = c.replace('// 仅在已发' + p + '/审签中时轮询（等待', '// 仅在已发布/审签中时轮询（等待')

# L778: 更新编辑器状态
c = c.replace('停止轮询并更新编辑器状' + p, '停止轮询并更新编辑器状态')

# L811: '纪要内容加载中'
c = c.replace("content.includes('纪要内容加载" + p + ")", "content.includes('纪要内容加载中')")

# L824: '纪要已发布，等待会议端审签'
c = c.replace("ElMessage.success('纪要已发布，等待会议端审" + p + ")", 
              "ElMessage.success('纪要已发布，等待会议端审签')")

# L825: // 初始化签名画板
c = c.replace('// 初始化签名画' + p, '// 初始化签名画板')

# L837: '纪要内容加载中..'
c = c.replace("content === '<p>纪要内容加载" + p + "..</p>'", "content === '<p>纪要内容加载中..</p>'")

# L842: // 否则润色全文
c = c.replace('否则润色全' + p, '否则润色全文')

# L866: 'AI 润色失败，请检查网络连接'
c = c.replace("'AI 润色失败，请检查网络连" + p + ")", "'AI 润色失败，请检查网络连接')")

# L878: 请使用 Chrome 或 Edge
c = c.replace("请使用 Chrome " + p + " Edge'", "请使用 Chrome 或 Edge'")

# L890: '纪要内容为空，无法播报'
c = c.replace("'纪要内容为空，无法播" + p + ")", "'纪要内容为空，无法播报')")

# L894: // 分段处理（SpeechSynthesis 对长文本可能截断）
c = c.replace('// 分段处理（SpeechSynthesis 对长文本可能截' + p, 
              '// 分段处理（SpeechSynthesis 对长文本可能截断）')

# L902-903: splitIdx
c = c.replace("remaining.lastIndexOf('" + p + ", maxLen)\n    if (splitIdx < 0) splitIdx = remaining.lastIndexOf('" + p,
              "remaining.lastIndexOf('。', maxLen)\n    if (splitIdx < 0) splitIdx = remaining.lastIndexOf('，'")
# Simpler approach:
c = c.replace("remaining.lastIndexOf('" + p + ", maxLen)", "remaining.lastIndexOf('。', maxLen)")

# L991: '拟稿签署成功'
c = c.replace("ElMessage.success('拟稿签署成" + p + ")", "ElMessage.success('拟稿签署成功')")

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

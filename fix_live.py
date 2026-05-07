#!/usr/bin/env python3
"""Comprehensive fix for MeetingLive.vue - 99 corruptions"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingLive.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# ── TEMPLATE SECTION ──────────────────────────────────────────────────────

# L3: 左栏：会议信息 + AI 问答 -->
c = c.replace('会议信' + p + '+ AI 问答', '会议信息 + AI 问答')

# L8: '会议进行中'
c = c.replace("'会议进行" + p + "'", "'会议进行中'")

# L21: '已签到' : '未签到'
c = c.replace("'已签" + p + " : '未签" + p + " }}", "'已签到' : '未签到' }}")

# L79: 中栏：实时转写 -->
c = c.replace('实时转' + p + '-->', '实时转写 -->')

# L90: 开始录音'
c = c.replace("开始录" + p + ")", "开始录音')")

# L106: 禁忌词警告 -->
c = c.replace('禁忌词警' + p + '-->', '禁忌词警告 -->')

# L109: 敏感词
c = c.replace('敏感' + p + '\n', '敏感词\n')

# L123: '已连接' : '未连接'
c = c.replace("'已连" + p + " : '未连" + p + " }}", "'已连接' : '未连接' }}")

# L128: 逐字输出模式） -->
c = c.replace('逐字输出模式' + p + '-->', '逐字输出模式） -->')

# L130: 可编辑、可标注） -->
c = c.replace('可编辑、可标注' + p + '-->', '可编辑、可标注） -->')

# L149: 局部标注高亮 -->
c = c.replace('局部标注高' + p + '-->', '局部标注高亮 -->')

# L162: 等待录音开始...
c = c.replace('等待录音开' + p + '..', '等待录音开始..')

# L166: 右栏：辅助工具 -->
c = c.replace('辅助工' + p + '-->', '辅助工具 -->')

# L200: 状态操作 -->
c = c.replace('态操' + p + '-->', '态操作 -->')

# L203: 更改状态</el-button>
c = c.replace('更改状' + p + '/el-button>', '更改状态</el-button>')

# L207-209: dropdown items (✓ prefix + 已解决/未解决)
c = c.replace('command="adopted">' + p + '采纳<', 'command="adopted">采纳<')
c = c.replace(p + '采纳 ' + p + '已解' + p + '/el-dropdown-item>',
              '采纳 已解决</el-dropdown-item>')
c = c.replace(p + '采纳 ' + p + '未解' + p,
              '采纳 未解决<')
# catch remaining in dropdown
c = c.replace('已解' + p + '/el-dropdown-item>', '已解决</el-dropdown-item>')
c = c.replace('未解' + p + '/el-dropdown-item>', '未解决</el-dropdown-item>')

# L224: 请输入回复内容..
c = c.replace('请输入回复内' + p + '..', '请输入回复内容..')

# L246: 标注模式开关 -->
c = c.replace('标注模式开' + p + '-->', '标注模式开关 -->')

# L250: '标注模式已开启' : '开启标注模式'
c = c.replace("'标注模式已开" + p + " : '开启标注模" + p + "'",
              "'标注模式已开启' : '开启标注模式'")

# L253: two corruptions in instruction text
c = c.replace('整行标注，' + p + '<strong>', '整行标注，或<strong>')
c = c.replace('进行局部标' + p + '\n', '进行局部标注\n')

# L257: 已标注条目列表 -->
c = c.replace('已标注条目列' + p + '-->', '已标注条目列表 -->')

# L278: 等待状态 -->
c = c.replace('等待状' + p + '-->', '等待状态 -->')

# L285: 已记录 {{ ... }} 条
c = c.replace('已记' + p + '{{ simulatedLines.length }} ' + p,
              '已记录 {{ simulatedLines.length }} 条')

# L287: 录音已暂停
c = c.replace('录音已暂' + p + '\n', '录音已暂停\n')

# L289: 尚未开始录音
c = c.replace('尚未开始录' + p + '\n', '尚未开始录音\n')

# L293: 可生成状态 -->
c = c.replace('可生成状' + p + '-->', '可生成状态 -->')

# L297: 共 {{ ... }} 条</span>
c = c.replace('simulatedLines.length }} ' + p + '/span>', 'simulatedLines.length }} 条</span>')

# L301: 生成 AI 摘要与要点
c = c.replace('生成 AI 摘要与要' + p, '生成 AI 摘要与要点')

# L308: ref-section-title with icon
c = c.replace('"ref-section-title" style="margin-top:16px">' + p + '关键要点',
              '"ref-section-title" style="margin-top:16px">📌关键要点')

# L332-333: 聚合 options
c = c.replace('按议题聚' + p + ' value=', '按议题聚合" value=')
c = c.replace('按发言人聚' + p + ' value=', '按发言人聚合" value=')

# L368: 敏感词日志弹窗 -->
c = c.replace('敏感词日志弹' + p + '-->', '敏感词日志弹窗 -->')

# L369: title="敏感词屏蔽日志"
c = c.replace('title="敏感词屏蔽日' + p + ' width=', 'title="敏感词屏蔽日志" width=')

# L372: label="发言人"
c = c.replace('label="发言' + p + ' width=', 'label="发言人" width=')

# L382: 请下载查看</div>
c = c.replace('请下载查' + p + '/div>', '请下载查看</div>')

# L385: 文字选中标注浮层工具栏 -->
c = c.replace('文字选中标注浮层工具' + p + '-->', '文字选中标注浮层工具栏 -->')

# L388: 标注选中文字：</span>
c = c.replace('标注选中文字' + p + '/span>', '标注选中文字：</span>')

# L407: ✓记录此问题</button>
c = c.replace(p + '记录此问' + p + '/button>', '记录此问题</button>')

# ── JS SECTION ────────────────────────────────────────────────────────────

# L463: status map
c = c.replace("open: '待处" + p + ", explained: '已解" + p + ", adopted: '已采" + p +
              ", adopted_resolved: '采纳·已解" + p + ", adopted_unresolved: '采纳·未解" + p + " }",
              "open: '待处理', explained: '已解释', adopted: '已采纳', adopted_resolved: '采纳·已解决', adopted_unresolved: '采纳·未解决' }")

# L544: 录音状态\nconst
c = c.replace('录音状' + p + 'const', '录音状态\nconst')

# L549: AI greeting
c = c.replace("您好！我" + p + "AI 助手", "您好！我是AI 助手")

# L577: 敏感词\nconst
c = c.replace('// 敏感' + p + 'const', '// 敏感词\nconst')

# L606: 逐字输出文件内容）\nconst
c = c.replace('逐字输出文件内容' + p + 'const', '逐字输出文件内容）\nconst')

# L655: ElMessage
c = c.replace('已填充到问题记录，点击' + p, '已填充到问题记录，点击确认')

# L666: .join('、')
c = c.replace(".join('" + p + "))", ".join('、'))")

# L673-678: regex patterns
c = c.replace("需要进一" + p + ",", "需要进一步',")
c = c.replace("不符" + p + ",", "不符合',")

# L686: string truncate
c = c.replace("+ '..." + p + " : match[0]", "+ '...' : match[0]")

# L704: 问题已记录
c = c.replace("ElMessage.success('问题已记" + p + ")", "ElMessage.success('问题已记录')")

# L708: 关闭选择工具栏
c = c.replace('关闭选择工具' + p + 'function', '关闭选择工具栏 function')

# L713: comment AI
c = c.replace('不自动关' + p + 'AI', '不自动关闭 AI')

# L716: 关键讨论点
c = c.replace("'关键讨论" + p + ",", "'关键讨论点',")

# L731: 合并局部标注
c = c.replace('  // 合并局部标' + p + '  selectionAnnotations', '  // 合并局部标注\n  selectionAnnotations')

# L752: 会议进行中
c = c.replace("title || '会议进行" + p + ",", "title || '会议进行中',")

# L754: date format
c = c.replace("format('MM月DD" + p + "HH:mm')", "format('MM月DD日 HH:mm')")

# L768: comment
c = c.replace('// 启动全局选择监听' + p + 'AI', '// 启动全局选择监听与 AI')

# L797: 管理员
c = c.replace("|| '管理" + p + ",", "|| '管理员',")

# L822: 纪要编辑
c = c.replace('进入纪要编辑' + p + ", '结束会议'", "进入纪要编辑。', '结束会议'")

# L833: 会议已结束
c = c.replace("ElMessage.success('会议已结" + p + ")", "ElMessage.success('会议已结束')")

# L841: comment
c = c.replace('自动滚动到底部（尊重用户手动滚动' + p + 'watch', '自动滚动到底部（尊重用户手动滚动）\nwatch')

# L857: comment
c = c.replace("'idle' → 全新开" + p, "'idle' → 全新开始")

# L880: error message
c = c.replace('请确认 frontend/会议记录.txt 存在' + p + "']", "请确认 frontend/会议记录.txt 存在。']")

# L1000: comment
c = c.replace('关闭小工具' + p + '    selPopover', '关闭小工具栏\n    selPopover')

# L1063: AI unavailable
c = c.replace("AI服务暂时不可用，请稍后重试" + p + ",", "AI服务暂时不可用，请稍后重试。',")

# L1068: comment
c = c.replace('// 滚动到底' + p + '    nextTick', '// 滚动到底部\n    nextTick')

# L1098: 采纳修改建议
c = c.replace("'已采纳修改建" + p + ")", "'已采纳修改建议')")

# L1106: AI分类
c = c.replace("'AI 自动分类已触" + p + ")", "'AI 自动分类已触发')")

# L1126-1127: issue items
c = c.replace("'各模块开发进度整" + p + "5%'", "'各模块开发进度整合85%'")
c = c.replace("存在延期风" + p + ", importance:", "存在延期风险', importance:")

# L1139: importance labels
c = c.replace("return { high: '重要', medium: '一" + p + ", low: '次要', normal: '普" + p,
              "return { high: '重要', medium: '一般', low: '次要', normal: '普通'")

# L1147: warning
c = c.replace("暂无会议记录，无法生成摘" + p + ")", "暂无会议记录，无法生成摘要')")

# L1153: AI question (template literal - careful with $)
c = c.replace('请对以下完整会议记录生成专业会议摘要' + p + '00字以内）',
              '请对以下完整会议记录生成专业会议摘要（300字以内）')

# L1156: AI response fallback
c = c.replace("'摘要生成完成，请参阅详细记录" + p, "'摘要生成完成，请参阅详细记录。'")

# L1159: comment
c = c.replace('// 持久化供纪要页参' + p, '// 持久化供纪要页参考')

# L1166: ElMessage
c = c.replace("'摘要与要点已生成，可在纪要编辑页查看参考资" + p + ")", "'摘要与要点已生成，可在纪要编辑页查看参考资料')")

# L1168: AI unavailable
c = c.replace("'（AI 服务暂时不可用，请在纪要页面重新生成" + p, "'（AI 服务暂时不可用，请在纪要页面重新生成）'")

# L1169: warning
c = c.replace("'AI 服务暂时不可" + p + ")", "'AI 服务暂时不可用')")

# L1697: CSS comment
c = c.replace('/* ===== 文字选中标注工具' + p + ' ===== */', '/* ===== 文字选中标注工具栏 ===== */')

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

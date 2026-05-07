#!/usr/bin/env python3
"""Second-pass fix for MeetingCreate.vue - 105 remaining corruptions"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# L107: <!-- 分割线 -->
c = c.replace('<!-- 分割' + p + '-->', '<!-- 分割线 -->')

# L118: 已选 {{ ... }} 人
c = c.replace('已' + p + '{{ form.participant_ids.length }} ' + p, '已选 {{ form.participant_ids.length }} 人')

# L137: 可选人员</span>
c = c.replace('<span>可选人' + p + '/span>', '<span>可选人员</span>')

# L143: 加载中..</span>
c = c.replace('<span>加载' + p + '..</span>', '<span>加载中..</span>')

# L191: content="删除此人员" (first occurrence - with is_participant_only)
c = c.replace('content="删除此人' + p + ' placement="top">\n                            <el-tooltip v-if',
              'content="删除此人员" placement="top">\n                            <el-tooltip v-if')

# L244: content="删除此人员" (second occurrence - without is_participant_only)
c = c.replace('content="删除此人' + p + ' placement="top">\n                            <el-button',
              'content="删除此人员" placement="top">\n                            <el-button')

# L260: 已选人员</span>
c = c.replace('<span>已选人' + p + '/span>', '<span>已选人员</span>')

# L317: 时间冲突（end of line, newline absorbed）
c = c.replace('时间冲' + p + '\n', '时间冲突\n')

# L338: 姓名。</p>
c = c.replace('姓名' + p + '/p>', '姓名。</p>')

# L413 & L642 & L796: 上一步  (button text + newline absorbed)  
c = c.replace('</el-icon> 上一' + p + '\n', '</el-icon> 上一步\n')

# L421: Tab 3 comment
c = c.replace(' & 签到' + p + ' ==================== --> -->', ' & 签到表 ==================== -->')

# L425: 会议材料与签到表
c = c.replace('>会议材料与签' + p + '\n', '>会议材料与签到表\n')

# L446: 拖到此处，或<em>
c = c.replace('到此处，' + p + 'em>点击上传</em>', '到此处，或<em>点击上传</em>')

# L453: <!-- 分割线 --> (already handled above, skip)

# L470: 生成签到表\n (button text + newline absorbed)
c = c.replace('</el-icon>生成签到' + p + '\n', '</el-icon>生成签到表\n')

# L501..L624: row.X || '　' patterns — fullwidth space U+3000  last byte absorbed the quote
# The pattern is: row.xxx || '\ufffd? }}
c = c.replace("row.name || '" + p + " }}", "row.name || '　' }}")
c = c.replace("row.dept || '" + p + " }}", "row.dept || '　' }}")
c = c.replace("row.title || '" + p + " }}", "row.title || '　' }}")
c = c.replace("row.time || '" + p + " }}", "row.time || '　' }}")
c = c.replace("row.sign || '" + p + " }}", "row.sign || '　' }}")
c = c.replace("row.idCard || '" + p + " }}", "row.idCard || '　' }}")
c = c.replace("row.bankCard || '" + p + " }}", "row.bankCard || '　' }}")
c = c.replace("row.fee || '" + p + " }}", "row.fee || '　' }}")

# L520-522 & L627-629: 上 下 删 buttons
c = c.replace('moveExpertRowUp(idx)">上' + p + '/el-button>', 'moveExpertRowUp(idx)">上</el-button>')
c = c.replace('moveExpertRowDown(idx)">下' + p + '/el-button>', 'moveExpertRowDown(idx)">下</el-button>')
c = c.replace('removeExpertRow(idx)">删' + p + '/el-button>', 'removeExpertRow(idx)">删</el-button>')
c = c.replace('moveOtherRowUp(idx)">上' + p + '/el-button>', 'moveOtherRowUp(idx)">上</el-button>')
c = c.replace('moveOtherRowDown(idx)">下' + p + '/el-button>', 'moveOtherRowDown(idx)">下</el-button>')
c = c.replace('removeOtherRow(idx)">删' + p + '/el-button>', 'removeOtherRow(idx)">删</el-button>')

# L676: 🤖</span>
c = c.replace('"quick-icon">🤖' + p + '/span>自动', '"quick-icon">🤖</span>自动')

# L678: 详细议程
c = c.replace('总结的详细议' + p + '")', '总结的详细议程")')

# L682: 📝</span> + 简洁议程\n
c = c.replace('"quick-icon">📝' + p + '/span>简洁议' + p + '\n', '"quick-icon">📝</span>简洁议程\n')

# L694: typing-dot •</span>
c = c.replace('"typing-dot">•' + p + '/span>', '"typing-dot">•</span>')

# L723: 发送\n
c = c.replace('</el-icon>发' + p + '\n', '</el-icon>发送\n')

# L736: 生成中\n (inside el-tag)
c = c.replace('</el-icon>生成' + p + '\n', '</el-icon>生成中\n')

# L737: ✅ 已生成</el-tag>
c = c.replace('style="margin-left:8px">✅ 已生' + p + '/el-tag>', 'style="margin-left:8px">✅ 已生成</el-tag>')

# L811: form.title || '　'
c = c.replace("form.title || '" + p + " }}</span>", "form.title || '　' }}</span>")
# L813: form.startDate || '　'
c = c.replace("form.startDate || '" + p + " }}</span>", "form.startDate || '　' }}</span>")
# L815: durationText || '　'
c = c.replace("durationText || '" + p + " }}</span>", "durationText || '　' }}</span>")
# L816: form.location || '　'
c = c.replace("form.location || '" + p + " }}</span>", "form.location || '　' }}</span>")

# L819: agendaContent ? '✅已生成' : '未生成'
c = c.replace("agendaContent ? '" + p + " 已生" + p + " : '未生" + p, 
              "agendaContent ? '✅ 已生成' : '未生成'")

# L882: tpl.cols.join('、')
c = c.replace("tpl.cols.join('" + p + ")", "tpl.cols.join('、')")

# L947: 政务外联例会\n
c = c.replace('有政务外联例' + p + '\n', '有政务外联例会\n')

# L1074: 从 form.location 匹配，找不到则回退到第一个可用布局
c = c.replace('  // 优先' + p + ' form.location', '  // 优先从 form.location')

# L1187: 基本信息与人员
c = c.replace("label: '基本信息与人" + p, "label: '基本信息与人员'")

# L1189: 材料与签到表
c = c.replace("label: '材料与签" + p, "label: '材料与签到表'")

# L1312: array items
c = c.replace("'被评审项目方" + p, "'被评审项目方案'")
c = c.replace("'相关计算" + p, "'相关计算书'")
c = c.replace("'局面文" + p, "'局面文件'")

# L1389: conflict message template literal
c = c.replace(" " + p + " ${extConflict.timeRange} 有", " 在 ${extConflict.timeRange} 时间段有")
c = c.replace("冲突，无法添加" + p, "冲突，无法添加。")

# L1422: conflict auto-remove message
c = c.replace("已选人" + p + " ${u.real_name}", "已选人员 ${u.real_name}")
c = c.replace("冲突，已自动移除" + p, "冲突，已自动移除。")

# L1562: Markdown语法等）。
c = c.replace("Markdown语法" + p + p + "）" + p, "Markdown语法等）。")

# L1566: 格式：序号
c = c.replace("格式" + p + " 序号", "格式：序号")

# L1567: 备注：最后
c = c.replace("备注" + p + " 最后", "备注：最后")

# L1570: 开场5分钟
c = c.replace("开" + p + " 分钟", "开场5分钟")

# L1599: 保存当前议程用于上下文\n
c = c.replace("// 保存当前议程用于上下" + p + "\n", "// 保存当前议程用于上下文\n")

# L1603: .join('、')
c = c.replace(".join('" + p + ") || '待定'", ".join('、') || '待定'")

# L1609: 会议名称：
c = c.replace("会议名称" + p + " {form.title}", "会议名称：${form.title}")

# L1614: form.description || '（无）'
c = c.replace("description || '" + p, "description || '（无）'")

# L1703-1706: template agendas (散会 at end)
c = c.replace("\\n五、散" + p + ",\n    review:", "\\n五、散会',\n    review:")
c = c.replace("\\n六、散" + p + ",\n    special:", "\\n六、散会',\n    special:")
c = c.replace("\\n五、散" + p + ",\n    decision:", "\\n五、散会',\n    decision:")
c = c.replace("\\n六、散" + p + ",\n    decision:", "\\n六、散会',\n    decision:")

# L1735: !trimmed.includes('】')
c = c.replace("!trimmed.includes('" + p + ")", "!trimmed.includes('】')")

# L1741-1746: 基本信息行
c = c.replace('// \u57fa\u672c\u4fe1\u606f\u884c\uff08\u5305\u542b\u201c' + p, '// \u57fa\u672c\u4fe1\u606f\u884c\uff08\u5305\u542b\u201c\uff1a\u201d')
c = c.replace("[" + p + ":]/.test", "[：:]/.test")
c = c.replace("trimmed.split(/[" + p + ":]/)","trimmed.split(/[：:]/)")
c = c.replace("rest.join('" + p + "')", "rest.join('：')")
c = c.replace(">${label}" + p + "</span>", ">${label}：</span>")

# L1756: 备注行 comment
c = c.replace("    // 备注" + p + "\n    if (trimmed.startsWith", "    // 备注行\n    if (trimmed.startsWith")

# L1795-1796: template names
c = c.replace("name: '专家签到" + p, "name: '专家签到表'")
c = c.replace("name: '其他人员签到" + p, "name: '其他人员签到表'")

# L1922-1974: HTML generation
c = c.replace("|| '会议'} - 签到" + p + "</h3>", "|| '会议'} - 签到表</h3>")
c = c.replace("时间：${form.startDate || '待定'} ${timeRangeLabel.value}</p>\n", 
              "时间：${form.startDate || '待定'} ${timeRangeLabel.value}</p>\n")
# just in case:
c = c.replace("会议时间" + p + "{form.startDate", "会议时间：${form.startDate")
c = c.replace("会议地点" + p + "{form.location", "会议地点：${form.location")
c = c.replace("一、专家签到" + p + "{checkinExpertRows", "一、专家签到表（${checkinExpertRows")
c = c.replace("二、其他人员签到" + p + "{checkinOtherRows", "二、其他人员签到表（${checkinOtherRows")
c = c.replace("|| '会议'} - 签到" + p + "</title>", "|| '会议'} - 签到表</title>")

# L3775: CSS comment
c = c.replace("/* ===== 签到表编辑模" + p + "===== */", "/* ===== 签到表编辑模式 ===== */")

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

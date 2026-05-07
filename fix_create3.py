#!/usr/bin/env python3
"""Third-pass fix for MeetingCreate.vue - 60 remaining"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# L191 & L244: content="删除此人员"  --- 此人\ufffd? placement
c = c.replace('content="删除此人' + p + ' placement="top">', 'content="删除此人员" placement="top">')

# L317: 时间冲突\n  (absorbed newline)
c = c.replace('时间冲' + p + '                  <span class="conflict-time">', 
              '时间冲突\n                  <span class="conflict-time">')

# L413, L642, L796: 上一步\n (absorbed newline after 步)
c = c.replace('</el-icon> 上一' + p + '              </el-button>\n',
              '</el-icon> 上一步\n              </el-button>\n')
c = c.replace('</el-icon> 上一' + p + '            </el-button>\n',
              '</el-icon> 上一步\n            </el-button>\n')

# L421: 签到表 ==================== -->
c = c.replace('& 签到' + p + ' ==================== --> -->', '& 签到表 ==================== -->')

# L425: 会议材料与签到表\n absorbed
c = c.replace('>会议材料与签' + p + '              <span class="optional-badge">', 
              '>会议材料与签到表\n              <span class="optional-badge">')

# L470: 生成签到表\n absorbed
c = c.replace('</el-icon>生成签到' + p + '                </el-button>',
              '</el-icon>生成签到表\n                </el-button>')

# L520-522, L627-629: 上 下 删 buttons - single char absorbed 
c = c.replace('moveExpertRowUp(idx)">上' + p + '/el-button>', 'moveExpertRowUp(idx)">上</el-button>')
c = c.replace('moveExpertRowDown(idx)">下' + p + '/el-button>', 'moveExpertRowDown(idx)">下</el-button>')
c = c.replace('removeExpertRow(idx)">删' + p + '/el-button>', 'removeExpertRow(idx)">删</el-button>')
c = c.replace('moveOtherRowUp(idx)">上' + p + '/el-button>', 'moveOtherRowUp(idx)">上</el-button>')
c = c.replace('moveOtherRowDown(idx)">下' + p + '/el-button>', 'moveOtherRowDown(idx)">下</el-button>')
c = c.replace('removeOtherRow(idx)">删' + p + '/el-button>', 'removeOtherRow(idx)">删</el-button>')

# L676: 🤖\ufffd?</span>
c = c.replace('"quick-icon">🤖' + p + '/span>自动', '"quick-icon">🤖</span>自动')

# L678: 详细议程\ufffd?
c = c.replace('总结的详细议' + p + '")', '总结的详细议程")')

# L682: 📝\ufffd?</span> 简洁议\ufffd?\n
c = c.replace('"quick-icon">📝' + p + '/span>简洁议' + p + '                  </button>',
              '"quick-icon">📝</span>简洁议程\n                  </button>')

# L694: typing-dot •\ufffd?</span>
c = c.replace('"typing-dot">•' + p + '/span>', '"typing-dot">•</span>')

# L723: 发送\n absorbed (Position icon + 发送)
c = c.replace('</el-icon>发' + p + '                    </el-button>',
              '</el-icon>发送\n                    </el-button>')

# L736: 生成中\n absorbed
c = c.replace('</el-icon>生成' + p + '                  </el-tag>',
              '</el-icon>生成中\n                  </el-tag>')

# L737: ✅ 已生成</el-tag>
c = c.replace('style="margin-left:8px">✅ 已生' + p + '/el-tag>', 'style="margin-left:8px">✅ 已生成</el-tag>')

# L819: agendaContent ? '✅ 已生成' : '未生成'
c = c.replace("agendaContent ? '" + p + " 已生" + p + " : '未生" + p + " }}",
              "agendaContent ? '✅ 已生成' : '未生成' }}")

# L947: 政务外联例会\n absorbed
c = c.replace('有政务外联例' + p + 'const MOCK_EXTERNAL_BUSY', 
              '有政务外联例会\nconst MOCK_EXTERNAL_BUSY')

# L1074: 从 form.location  (优先\ufffd? → 优先从)
c = c.replace('  // 优先' + p + ' form.location', '  // 优先从 form.location')

# L1389: conflict message - 在 ${extConflict.timeRange}
c = c.replace(' ' + p + ' ${extConflict.timeRange} 有', ' 在 ${extConflict.timeRange} 时间段有')

# L1422: conflict message - 已选人员
c = c.replace('已选人' + p + ' ${u.real_name}', '已选人员 ${u.real_name}')
c = c.replace(' ' + p + ' ${info.timeRange} 有', ' 在 ${info.timeRange} 时间段有')

# L1562: Markdown语法等）。  — 等\ufffd?\ufffd?*等）\ufffd?
c = c.replace('Markdown语法' + p + p + '*等）' + p, 'Markdown语法、##、*等）。')

# L1566: 格式\ufffd? 序号 → 格式：序号
c = c.replace('格式' + p + ' 序号', '格式：序号')

# L1567: 备注：最后一\ufffd?\n → 备注：最后一行
c = c.replace('4. 备注：最后一' + p + '\n', '4. 备注：最后一行\n')

# L1570: 开\ufffd?分钟 → 开场5分钟
c = c.replace('开' + p + ' 分钟、每个议程5-', '开场5分钟、每个议程5-')

# L1599: 上下文\n absorbed
c = c.replace('// 保存当前议程用于上下' + p + '  const previousAgenda',
              '// 保存当前议程用于上下文\n  const previousAgenda')

# L1609: 会议名称：
c = c.replace('会议名称' + p + ' {form.title}', '会议名称：${form.title}')

# L1704-L1706: 散会 (散\ufffd?) at end of strings
c = c.replace("五、宣读评审结论（5分钟）\\n六、散" + p + "',", 
              "五、宣读评审结论（5分钟）\\n六、散会',")
c = c.replace("四、总结发言" + p + "0分钟）\\n五、散" + p + "',",
              "四、总结发言（10分钟）\\n五、散会',")
c = c.replace("五、宣布决定（5分钟）\\n六、散" + p + ",",
              "五、宣布决定（5分钟）\\n六、散会',")

# L1735: 第一\ufffd?\n absorbed
c = c.replace('、或者第一' + p + '    const isTitle', '、或者第一行\n    const isTitle')

# L1741: 包含"\ufffd?的) — Chinese full-width left double quote + ：
c = c.replace('// 基本信息行（包含"' + p + '的）', '// 基本信息行（包含"："的）')

# L1745: rest.join('：') 
c = c.replace("const value = rest.join('" + p + ")", "const value = rest.join('：')")

# L1746: ${label}：</span>
c = c.replace('>${label}' + p + '</span>', '>${label}：</span>')

# L1756: 备注行\n absorbed
c = c.replace('    // 备注' + p + '    if (trimmed.startsWith', '    // 备注行\n    if (trimmed.startsWith')

# L1922: - 签到表</h3>
c = c.replace("|| '会议'} - 签到" + p + '</h3>', "|| '会议'} - 签到表</h3>")

# L1931: 专家签到表（\ufffd? (absorbed open paren or text)  
c = c.replace('一、专家签到表' + p + '{checkinExpertRows', '一、专家签到表（${checkinExpertRows')

# L1943: 其他人员签到表（
c = c.replace('二、其他人员签到表' + p + '{checkinOtherRows', '二、其他人员签到表（${checkinOtherRows')

# L1974: 签到表</title>
c = c.replace("|| '会议'} - 签到" + p + '</title>', "|| '会议'} - 签到表</title>")

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

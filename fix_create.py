#!/usr/bin/env python3
"""Comprehensive fix for MeetingCreate.vue - 221 corruptions"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# ── TEMPLATE SECTION ───────────────────────────────────────────────────────

# L17: 步骤条导航 -->
c = c.replace('步骤条导' + p + '-->', '步骤条导航 -->')

# L40: 基本信息区 -->
c = c.replace('基本信息' + p + '-->', '基本信息区 -->')

# L46: placeholder="请输入会议名称"
c = c.replace('placeholder="请输入会议名' + p + ' size=', 'placeholder="请输入会议名称" size=')

# L72: format="YYYY年MM月DD日"
c = c.replace('format="YYYY年MM月DD' + p + '\n', 'format="YYYY年MM月DD日"\n')

# L79: 开始</span>
c = c.replace('"time-label">开' + p + '/span>', '"time-label">开始</span>')

# L80: placeholder="开始时间"
c = c.replace('placeholder="开始时' + p + ' size=', 'placeholder="开始时间" size=')

# L89: 快捷时长：</span>
c = c.replace('"shortcut-label">快捷时长' + p + '/span>', '"shortcut-label">快捷时长：</span>')

# L103: 签名功能。</el-checkbox>
c = c.replace('评审费签名功能' + p + '/el-checkbox>', '评审费签名功能。</el-checkbox>')

# L107: 分割线 -->
c = c.replace('<!-- 分割' + p + '-->\n            <!-- 参会', '<!-- 分割线 -->\n            <!-- 参会')

# L114: 参会人员区 -->  
c = c.replace('参会人员' + p + '-->', '参会人员区 -->')

# L118: 已选 {{ ... }} 人
c = c.replace('已' + p + '{{ form.participant_ids.length }} ' + p + '\n', '已选 {{ form.participant_ids.length }} 人\n')

# L125: 全选</el-button>
c = c.replace('@click="selectAll" link type="primary">全' + p + '/el-button>', '@click="selectAll" link type="primary">全选</el-button>')

# L134: 可选人员 -->
c = c.replace('<!-- 左侧：可选人' + p + '-->', '<!-- 左侧：可选人员 -->')

# L137: 可选人员</span>
c = c.replace('"header-left"><span>可选人' + p + '/span>', '"header-left"><span>可选人员</span>')

# L138: {{ allUsers.length }} 人</span>
c = c.replace('allUsers.length }} ' + p + '/span>', 'allUsers.length }} 人</span>')

# L143: 加载中..
c = c.replace('"loading-row"><span>加载' + p + '..', '"loading-row"><span>加载中..')

# L151: {{ expertUsers.length }} 人</span>
c = c.replace('expertUsers.length }} ' + p + '/span>', 'expertUsers.length }} 人</span>')

# L191: content="删除此人员"
c = c.replace('content="删除此人' + p + '" placement="top">\n                            <el-tooltip v-if', 
              'content="删除此人员" placement="top">\n                            <el-tooltip v-if')

# L204: {{ otherUsers.length }} 人</span>
c = c.replace('otherUsers.length }} ' + p + '/span>', 'otherUsers.length }} 人</span>')

# L244: content="删除此人员" (second occurrence)
c = c.replace('content="删除此人' + p + '" placement="top">\n                            <el-button', 
              'content="删除此人员" placement="top">\n                            <el-button')

# L257: 已选人员 -->
c = c.replace('<!-- 右侧：已选人' + p + '-->', '<!-- 右侧：已选人员 -->')

# L260: 已选人员</span>
c = c.replace('"header-left"><span>已选人' + p + '/span>', '"header-left"><span>已选人员</span>')

# L261: {{ form.participant_ids.length }} 人</span>
c = c.replace('participant_ids.length }} ' + p + '/span>', 'participant_ids.length }} 人</span>')

# L264: 专家区 -->
c = c.replace('                  <!-- 专家' + p + '-->', '                  <!-- 专家区 -->')

# L292: 其他人员区 -->
c = c.replace('<!-- 其他人员' + p + '-->', '<!-- 其他人员区 -->')

# L313: 冲突检测区 -->
c = c.replace('<!-- 冲突检' + p + '-->', '<!-- 冲突检测区 -->')

# L317: 时间冲突 (end of line)
c = c.replace('时间冲' + p + '\n', '时间冲突\n')

# L338: 姓名。</p> (end of sentence)
c = c.replace('姓名' + p + '</p>', '姓名。</p>')

# L349: 拖拽到右侧座位</div>
c = c.replace('"seat-sidebar-hint">拖拽到右侧座' + p + '/div>', '"seat-sidebar-hint">拖拽到右侧座位</div>')

# L361: 全部已分配</div>
c = c.replace('"drag-empty">全部已分' + p + '/div>', '"drag-empty">全部已分配</div>')

# L369: 清空所有座位</el-button>
c = c.replace('"clearAllSeats">清空所有座' + p + '/el-button>', '"clearAllSeats">清空所有座位</el-button>')

# L376: 大屏幕标识 -->
c = c.replace('大屏幕标' + p + '-->', '大屏幕标识 -->')

# L381: 大屏幕</div>  
c = c.replace('>大屏' + p + '/div>', '>大屏幕</div>')

# L382: 会议区 -->
c = c.replace('<!-- 会议' + p + '-->', '<!-- 会议区 -->')

# L413: 上一步</el-button>
c = c.replace('><el-icon><ArrowLeft /></el-icon> 上一' + p + '\n', '><el-icon><ArrowLeft /></el-icon> 上一步\n')

# L421: Tab 3 comment
c = c.replace(':: 会议材料 & 签到' + p + ' ==================', '::: 会议材料 & 签到表 ==================')

# L425: 会议材料与签到表
c = c.replace('会议材料与签\n', '会议材料与签到表\n')
c = c.replace('<el-icon color="#E6A23C"><Document /></el-icon>会议材料与签' + p + '\n', 
              '<el-icon color="#E6A23C"><Document /></el-icon>会议材料与签到表\n')

# L446: 点击上传</em>
c = c.replace('，或<em>点击上\n', '，或<em>点击上传</em>')
c = c.replace('或<em>点击上传\n', '，或<em>点击上传</em>\n')

# L448: 不超过 50MB</div>  
c = c.replace('单文件不超' + p + '50MB</div>', '单文件不超过 50MB</div>')

# L453: div/hr 分割线 -->
c = c.replace('<!-- 分割' + p + '-->\n            <!-- 签到', '<!-- 分割线 -->\n            <!-- 签到')

# L460: 签到表区 -->
c = c.replace('<!-- 签到' + p + '-->', '<!-- 签到表区 -->')

# L462: 生成签到表</h4>
c = c.replace('📋 生成签到' + p + '/h4>', '📋 生成签到表</h4>')

# L463: 导出 PDF 打印</p>
c = c.replace('支持编辑和导' + p + 'PDF 打印</p>', '支持编辑和导出 PDF 打印</p>')

# L470: 生成签到表</el-button>
c = c.replace('>生成签到' + p + '\n', '>生成签到表\n')

# L481: 专家签到表 -->
c = c.replace('<!-- 专家签到' + p + '-->', '<!-- 专家签到表 -->')

# L501,505,509,513,517: '待填' cell placeholders
c = c.replace("row.name || '" + p + "'", "row.name || '待填'")
c = c.replace("row.dept || '" + p + "'", "row.dept || '待填'")
c = c.replace("row.title || '" + p + "'", "row.title || '待填'")
c = c.replace("row.time || '" + p + "'", "row.time || '待填'")
c = c.replace("row.sign || '" + p + "'", "row.sign || '待填'")
c = c.replace("row.idCard || '" + p + "'", "row.idCard || '待填'")
c = c.replace("row.bankCard || '" + p + "'", "row.bankCard || '待填'")
c = c.replace("row.fee || '" + p + "'", "row.fee || '待填'")

# L520-522: 上↑ 下↓ 删×  table buttons
c = c.replace('moveExpertRowUp(idx)">上' + p + '/el-button>', 'moveExpertRowUp(idx)">上</el-button>')
c = c.replace('moveExpertRowDown(idx)">下' + p + '/el-button>', 'moveExpertRowDown(idx)">下</el-button>')
c = c.replace('removeExpertRow(idx)">删' + p + '/el-button>', 'removeExpertRow(idx)">删</el-button>')

# L528: 新增行</el-button>
c = c.replace('addExpertRow">+ 新增' + p + '/el-button>', 'addExpertRow">+ 新增行</el-button>')

# L532: 其他人员签到表 -->
c = c.replace('<!-- 其他人员签到' + p + '-->', '<!-- 其他人员签到表 -->')

# L566-568: other row up/down/del
c = c.replace('moveOtherRowUp(idx)">上' + p + '/el-button>', 'moveOtherRowUp(idx)">上</el-button>')
c = c.replace('moveOtherRowDown(idx)">下' + p + '/el-button>', 'moveOtherRowDown(idx)">下</el-button>')
c = c.replace('removeOtherRow(idx)">删' + p + '/el-button>', 'removeOtherRow(idx)">删</el-button>')

# L574: addOtherRow 新增行
c = c.replace('addOtherRow">+ 新增' + p + '/el-button>', 'addOtherRow">+ 新增行</el-button>')

# L580: 评审费签收表
c = c.replace('"checkin-table-title">三、评审费签收' + p + '/div>', '"checkin-table-title">三、评审费签收表</div>')

# L627-629: expert table 2nd instance (same func names)
# Already handled by the earlier block

# L635: addExpertRow 2nd instance
# Already handled by the earlier block

# L642: upper level previous button
# Already handled by the earlier block

# L650: AI 智能议程对话框
c = c.replace('//AI 智能议程（对' + p + '编辑器', '// AI 智能议程（对话编辑器')
c = c.replace('AI 智能议程（对' + p + '编辑器）==================', 'AI 智能议程（对话编辑器）==================')

# L668-669: AI greeting
c = c.replace('你好！我是智能会议助手' + p + '/p>', '你好！我是智能会议助手。</p>')
c = c.replace('也可以随时对话修改已有内容' + p + '/p>', '也可以随时对话修改已有内容。</p>')

# L673: 快捷操作（仅首次显示） -->
c = c.replace('（仅首次显示' + p + '-->', '（仅首次显示） -->')

# L676: 🤖 icon
c = c.replace('"quick-icon">🤖' + p + '/span>自动', '"quick-icon">🤖</span>自动')

# L678: 总结的详细议程
c = c.replace('讨论环节、总结的详细议' + p + '")', '讨论环节、总结的详细议程")')

# L682: 🧾 icon + 简洁议程
c = c.replace('"quick-icon">📝' + p + '/span>简洁议' + p + '\n', '"quick-icon">📝</span>简洁议程\n')

# L694: typing dot
c = c.replace('"typing-dot">•' + p + '/span>', '"typing-dot">•</span>')

# L710: placeholder
c = c.replace('描述您的议程需' + p + '..', '描述您的议程需求..')

# L717: Ctrl+Enter 发送
c = c.replace('"input-hint">Ctrl + Enter 发' + p + '/span>', '"input-hint">Ctrl + Enter 发送</span>')

# L723: 发送</el-button>
c = c.replace('>发' + p + '\n    </el-button>', '>发送\n    </el-button>')

# L736: 生成中</el-tag>
c = c.replace('>生成' + p + '\n                  </el-tag>', '>生成中\n                  </el-tag>')

# L737: ✅ 已生成</el-tag>
c = c.replace('round style="margin-left:8px">✅ 已生' + p + '/el-tag>', 'round style="margin-left:8px">✅ 已生成</el-tag>')

# L773: 空状态 -->
c = c.replace('<!-- 空状' + p + '-->', '<!-- 空状态 -->')

# L776: 议程内容将在此展示</p>
c = c.replace('"empty-main">议程内容将在此展' + p + '/p>', '"empty-main">议程内容将在此展示</p>')

# L777: AI 将自动生成议程</p>
c = c.replace('AI 将自动生成议' + p + '/p>', 'AI 将自动生成议程</p>')

# L779: 预览模式 / 生成中 -->
c = c.replace('<!-- 预览模式 / 生成' + p + '-->', '<!-- 预览模式 / 生成中 -->')

# L788: 源文本编辑模式 -->
c = c.replace('<!-- 源文本编辑模' + p + '-->', '<!-- 源文本编辑模式 -->')

# L796: prev step button
# Already handled

# L811-818: summary rows
c = c.replace("form.title || '" + p + "'", "form.title || '待填'")
c = c.replace("form.startDate || '" + p + "'", "form.startDate || '待填'")
c = c.replace("durationText || '" + p + "'", "durationText || '待填'")
c = c.replace("form.location || '" + p + "'", "form.location || '待填'")

# L817: 参会人数
c = c.replace('"s-label">参会' + p + '/span>', '"s-label">参会人数</span>')

# L817: participant_ids.length }} 人</span>
c = c.replace('participant_ids.length }} ' + p + '/span></div>\n              <div class="s-row"><span class="s-label">附件',
              'participant_ids.length }} 人</span></div>\n              <div class="s-row"><span class="s-label">附件')

# L818: fileList.length }} 个</span>
c = c.replace('fileList.length }} ' + p + '/span>', 'fileList.length }} 个</span>')

# L819: ✅已生成/未生成
c = c.replace("agendaContent ? '" + p + "已生" + p + " : '未生" + p + "'",
              "agendaContent ? '✅已生成' : '未生成'")

# L829: 新建人员对话框 -->
c = c.replace('<!-- 新建人员对话' + p + '-->', '<!-- 新建人员对话框 -->')

# L833: placeholder="请输入姓名"
c = c.replace('placeholder="请输入姓' + p + ' />', 'placeholder="请输入姓名" />')

# L842: 高级工程师、教授
c = c.replace('如：高级工程师、教' + p + ' />', '如：高级工程师、教授" />')

# L845: 用于评审费签收
c = c.replace('用于评审费签' + p + ' />', '用于评审费签收" />')

# L850: label="手机号">
c = c.replace('label="手机' + p + '>', 'label="手机号">')

# L863: 签到表模板选择对话框 -->
c = c.replace('<!-- 签到表模板选择对话' + p + '-->', '<!-- 签到表模板选择对话框 -->')

# L864: title="选择签到表模板"
c = c.replace('title="选择签到表模' + p + ' width=', 'title="选择签到表模板" width=')

# L882: tpl.cols.join('、')
c = c.replace("tpl.cols.join('" + p + "')", "tpl.cols.join('、')")

# L886: 模板预览区 -->
c = c.replace('<!-- 模板预览' + p + '-->', '<!-- 模板预览区 -->')

# L901: 高级工程师</span>
c = c.replace("=== '职称'\">高级工程" + p + '/span>', "=== '职称'\">高级工程师</span>")

# L905: （签名区）</span>
c = c.replace('tpl-sign-placeholder">（签名区' + p + '/span>', 'tpl-sign-placeholder">（签名区）</span>')

# ── JS SECTION ────────────────────────────────────────────────────────────

# L940: // ======= 状态 =======
c = c.replace('// ======= 状' + p + '=======', '// ======= 状态 =======')

# L946: // ===== 外部系统冲突检测（前端模拟） ====
c = c.replace('// ===== 外部系统冲突检测（前端模拟' + p + '====', '// ===== 外部系统冲突检测（前端模拟） =====')

# L947: 每天 18:00-20:00 有政务外联例会
c = c.replace('有政务外联例' + p + '\n', '有政务外联例会\n')

# L957: JSDoc comment
c = c.replace('（含 username 字段' + p + ' * @returns', '（含 username 字段）\n * @returns')

# L1044: 自动选择唯一会议室
c = c.replace('// 自动选择唯一会议' + p + '    if', '// 自动选择唯一会议室\n    if')

# L1048: ElMessage
c = c.replace("console.error('获取会议室列表失" + p + "',", "console.error('获取会议室列表失败',")

# L1072: 注释
c = c.replace('// 优先从 form.location 匹配，找不到则回退到第一个可用布' + p + '\n', 
              '// 优先从 form.location 匹配，找不到则回退到第一个可用布局\n')

# L1185: 基本信息与人员
c = c.replace("label: '基本信息与人" + p + "',", "label: '基本信息与人员',")

# L1187: 材料与签到表
c = c.replace("label: '材料与签" + p + "',", "label: '材料与签到表',")

# L1240: validation message
c = c.replace("message: '请输入会议名" + p + ",", "message: '请输入会议名称',")

# L1310: 局面文件
c = c.replace("'局面文" + p + "'],", "'局面文件'],")

# L1319: 未分配部门
c = c.replace("|| '未分配部" + p + "\n", "|| '未分配部门'\n")

# L1387 & L1420: conflict messages  
c = c.replace('有「${extConflict.task}」，与本次会议时间冲突，无法添加', '有「${extConflict.task}」与本次会议时间冲突，无法添加')
c = c.replace('有「${info.task}」，与变更后的会议时间冲突，已自动移除', '有「${info.task}」与变更后的会议时间冲突，已自动移除')

# L1387: 有${extConflict.task}」  pattern with absortion
c = c.replace(' 有' + p + '{extConflict.task}」，', " 有「${extConflict.task}」，")
c = c.replace(' 有' + p + '{info.task}」，', " 有「${info.task}」，")

# L1473: confirm delete
c = c.replace('确认删除「${user.real_name}」？', '确认删除「${user.real_name}」？')  # already OK
c = c.replace('`确认删除' + p + '{user.real_name}」？', '`确认删除「${user.real_name}」？')

# L1482: comment
c = c.replace('// 从本地列表移' + p + '    allUsers', '// 从本地列表移除\n    allUsers')

# L1486: ElMessage
c = c.replace('ElMessage.success(`已删除' + p + '{user.real_name}」`)', 'ElMessage.success(`已删除「${user.real_name}」`)')

# L1507: validation
c = c.replace("message: '请输入姓" + p + ",", "message: '请输入姓名',")

# L1539: comment
c = c.replace('// 自动勾选刚创建的人' + p + '    if', '// 自动勾选刚创建的人员\n    if')

# L1552: comment
c = c.replace('// v-model:file-list 已自动同' + p + '}', '// v-model:file-list 已自动同步\n}')

# L1556-1563: AI prompt template
c = c.replace('撰写规范的会议议程' + p + '\n', '撰写规范的会议议程。\n')
c = c.replace('Markdown语法' + p + '等）' + p + '\n', 'Markdown语法等）。\n')
c = c.replace('格式要求' + p + '1.', '格式要求：\n1.')
c = c.replace('每条一行，' + p + '会议时间', '每条一行，如：会议时间')
c = c.replace('内容（负责人：XXX' + p + '4.', '内容（负责人：XXX）\n4.')
c = c.replace('注意' + p + '-', '注意：\n-')
c = c.replace('分钟、每个议' + p + '5-', '分钟、每个议程5-')
c = c.replace('语言正式、简洁、专' + p + '-', '语言正式、简洁、专业\n-')

# L1594: .join('、')
c = c.replace(".map(p => p.real_name).join('" + p + ")'", ".map(p => p.real_name).join('、')'")
c = c.replace('.map(p => p.real_name).join(' + "'" + p + "'", ".map(p => p.real_name).join('、')")

# L1599-1607: prompt construction
c = c.replace('会议信息' + p + '会议名称', '会议信息：\n会议名称')
c = c.replace('会议类型' + p + '{meetingTypeLabel', '会议类型：${meetingTypeLabel')
c = c.replace('会议时间' + p + '{timeInfo}', '会议时间：${timeInfo}')
c = c.replace('会议时长' + p + '{durationText', '会议时长：${durationText')
c = c.replace('会议地点' + p + '{form.location', '会议地点：${form.location')
c = c.replace('会议描述' + p + '{form.description', '会议描述：${form.description')
c = c.replace("'描述' || '" + p + "'", "'（无）'")
c = c.replace("description || '" + p + "'", "description || '（无）'")
c = c.replace("|| '待" + p + "'\n", "|| '待定'\n")
c = c.replace('参会人员' + p + '{participantNames}', '参会人员：${participantNames}')
c = c.replace('用户要求' + p + '{input}', '用户要求：${input}')

# L1649: comment
c = c.replace('// 同时更新对话气泡和右侧议程内' + p + '        chatMessages', '// 同时更新对话气泡和右侧议程内容\n        chatMessages')

# L1652: comment
c = c.replace('// 自动滚动对话' + p + '        if (chatMessagesRef', '// 自动滚动对话栏\n        if (chatMessagesRef')

# L1655: comment
c = c.replace('// 自动滚动预览' + p + '        if (agendaPreviewRef', '// 自动滚动预览区\n        if (agendaPreviewRef')

# L1666: ElMessage
c = c.replace("ElMessage.info('已停止生" + p + ")", "ElMessage.info('已停止生成')")

# L1669: ElMessage
c = c.replace("ElMessage.error('生成失败，请检查网络连" + p + ")", "ElMessage.error('生成失败，请检查网络连接')")

# L1690-1693: template agendas
c = c.replace("\\n五、散" + p + "',", "\\n五、散会',")

# L1722: comment
c = c.replace("!trimmed.includes('" + p + "') && !trimmed.includes", "!trimmed.includes('】') && !trimmed.includes")

# L1728: comment
c = c.replace('// 基本信息行（包含\u201c' + p + '\u201d的）', '// 基本信息行（包含"："的）')

# L1729: regex pattern
c = c.replace('[' + p + ']/.test', '[：:]/.test')

# L1731: split regex
c = c.replace("trimmed.split(/[" + p + "]/)", "trimmed.split(/[：:]/)")

# L1732: join
c = c.replace("rest.join('" + p + "')", "rest.join('：')")

# L1733: span html
c = c.replace('>${label}' + p + '</span>', '>${label}：</span>')

# L1743: comment
c = c.replace("if (trimmed.startsWith('备注') || trimmed.startsWith('注：') || trimmed.startsWith('" + p + "'))", 
              "if (trimmed.startsWith('备注') || trimmed.startsWith('注：'))")

# L1777: 签到表 =======
c = c.replace('// ======= 签到' + p + '=======', '// ======= 签到表 =======')

# L1782-1783: template names
c = c.replace("name: '专家签到" + p + "',", "name: '专家签到表',")
c = c.replace("name: '其他人员签到" + p + "',", "name: '其他人员签到表',")

# L1867: ElMessage
c = c.replace("ElMessage.success('已生成评审费发放" + p + ")", "ElMessage.success('已生成评审费发放表')")

# L1898-1900: ElMessage  
c = c.replace("ElMessage.success('签到表生成成" + p + ")", "ElMessage.success('签到表生成成功')")
c = c.replace("ElMessage.error('签到表生成失" + p + ")", "ElMessage.error('签到表生成失败')")

# L1909-1911: HTML generation
c = c.replace("会议' - 签到" + p + "</h3>", "会议' - 签到表</h3>")
c = c.replace("'会议时间" + p + "{form.startDate", "'会议时间：${form.startDate")
c = c.replace("'会议地点" + p + "{form.location", "'会议地点：${form.location")

# L1913: comment
c = c.replace('// 专家签到' + p + '  if', '// 专家签到表\n  if')

# L1917: table header
c = c.replace("一、专家签到表（${checkinExpertRows", "一、专家签到表（${checkinExpertRows")  # already OK
c = c.replace("一、专家签到" + p + "{checkinExpertRows", "一、专家签到表（${checkinExpertRows")

# L1924: comment
c = c.replace('// 其他人员签到' + p + '  if', '// 其他人员签到表\n  if')

# L1928: table header
c = c.replace("二、其他人员签到表（${checkinOtherRows", "二、其他人员签到表（${checkinOtherRows")
c = c.replace("二、其他人员签到" + p + "{checkinOtherRows", "二、其他人员签到表（${checkinOtherRows")

# L1940: table header
c = c.replace("三、评审费签收" + p + "/h4>", "三、评审费签收表</h4>")

# L1942: th column
c = c.replace("<th>銀行卡" + p + "/th>", "<th>银行卡号</th>")

# L1952: ElMessage
c = c.replace("ElMessage.warning('请先生成签到" + p + ")", "ElMessage.warning('请先生成签到表')")

# L1959: title
c = c.replace("会议' - 签到" + p + "</title>", "会议' - 签到表</title>")

# L1974: ElMessage
c = c.replace("ElMessage.error('弹窗被浏览器拦截，请允许弹窗后重" + p + ")", 
              "ElMessage.error('弹窗被浏览器拦截，请允许弹窗后重试')")

# L2004: ElMessage
c = c.replace("ElMessage.warning('请完善基本信" + p + ")", "ElMessage.warning('请完善基本信息')")

# L2063: 初始化 =======
c = c.replace('// ======= 初始' + p + '=======', '// ======= 初始化 =======')

# CSS comments
c = c.replace('/* ===== 步骤' + p + '===== */', '/* ===== 步骤条 ===== */')
c = c.replace('/* ===== 分割' + p + '===== */', '/* ===== 分割线 ===== */')
c = c.replace('/* ===== AI 议程：聊' + p + '编辑器双栏布局 ===== */', '/* ===== AI 议程：聊天编辑器双栏布局 ===== */')
c = c.replace('/* -- 输入' + p + '-- */', '/* -- 输入区 -- */')
c = c.replace('/* -- 右侧编辑器面' + p + '-- */', '/* -- 右侧编辑器面板 -- */')
c = c.replace('/* ===== 响应' + p + '===== */', '/* ===== 响应式 ===== */')

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

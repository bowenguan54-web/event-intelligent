#!/usr/bin/env python3
"""
Comprehensive fix script for MeetingArchiveTab.vue
Fixes 228 UTF-8 corruption occurrences (XX YY 3F pattern)
"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingArchiveTab.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before_count = c.count('\ufffd')
print(f'Before: {before_count} FFFD chars')

# ─── HTML TEMPLATE SECTION ─────────────────────────────────────────────────

# L3: 页面标题区
c = c.replace(f'页面标题{p}-->', '页面标题区 -->')

# L11: 左列表 + 右详情
c = c.replace(f'左列表 + 右详{p}-->', '左列表 + 右详情 -->')

# L19: range-separator="—" start-placeholder="开始"
c = c.replace(f'range-separator="{p} start-placeholder="开{p}\n',
              'range-separator="—" start-placeholder="开始"\n')

# L23: 共<b> and 个归档</span>
c = c.replace(f'"ov-item">{p}<b>', '"ov-item">共<b>')
c = c.replace(f'个归{p}/span>', '个归档</span>')

# L40: }}人</span>
c = c.replace(f'participants_count }}{p}/span>', 'participants_count }}人</span>')

# L46: 无待办</span>
c = c.replace(f'无待{p}/span>', '无待办</span>')

# L60: description="请从左侧选择一个归档会议" />
c = c.replace(f'归档会{p} />', '归档会议" />')

# L64: 加载中..
c = c.replace(f'加载{p}..', '加载中..')

# L68: <!-- 会议信息头 -->
c = c.replace(f'会议信息{p}-->', '会议信息头 -->')

# L81: 纯文本(.txt)
c = c.replace(f'纯文{p}(.txt)', '纯文本(.txt)')

# L91: }} — {{ fmtTime
c = c.replace(f'start_time) }} {p}{{{{ fmtTime', 'start_time) }} — {{ fmtTime')

# L93: 人参会</span>
c = c.replace(f'}}人参{p}/span></div>', '}}人参会</span></div>')

# L94: 已归档</el-tag>
c = c.replace(f'已归{p}/el-tag>', '已归档</el-tag>')

# L101: <!-- ①会议摘要 -->
c = c.replace(f'<!-- {p}会议摘要 -->', '<!-- ①会议摘要 -->')

# L134: 自动生成</div>
c = c.replace(f'自动生{p}/div>', '自动生成</div>')

# L140: <!-- ②会议记录（含音频转写） -->
c = c.replace(f'<!-- {p}会议记录（含音频转写{p}-->', '<!-- ②会议记录（含音频转写） -->')

# L162: 转写结果                  </div>
c = c.replace(f'修改转写结{p}', '修改转写结果')

# L166: {{ seg.speaker }}：</span>
c = c.replace(f'seg.speaker }}{p}/span>', 'seg.speaker }}：</span>')

# L179: <!-- ③待办分发 -->
c = c.replace(f'<!-- {p}待办分发 -->', '<!-- ③待办分发 -->')

# L180: label="③待办分发"
c = c.replace(f'label="{p}待办分发"', 'label="③待办分发"')

# L192: label="责任人"
c = c.replace(f'label="责任{p} width="90"', 'label="责任人" width="90"')

# L193: label="优先级"
c = c.replace(f'label="优先{p} width="80"', 'label="优先级" width="80"')

# L198: label="状态"
c = c.replace(f'label="状{p} width="130"', 'label="状态" width="130"')

# L200: content="状态由关联流程驱动，不可直接修改" placement=
c = c.replace(f'不可直接修{p} placement=', '不可直接修改" placement=')

# L203: 未关联流程</div>
c = c.replace(f'未关联流{p}/div>', '未关联流程</div>')

# L207: '未设置'
c = c.replace(f"|| '未设{p} }}", "|| '未设置' }}")

# L230: <!-- ④进度跟踪 -->
c = c.replace(f'<!-- {p}进度跟踪 -->', '<!-- ④进度跟踪 -->')

# L235: 已完成</span>
c = c.replace(f'"ts-label">已完{p}/span>', '"ts-label">已完成</span>')

# L236: 进行中</span>
c = c.replace(f'"ts-label">进行{p}/span>', '"ts-label">进行中</span>')

# L240: 完成率</span>
c = c.replace(f'"ts-label">完成{p}/span>', '"ts-label">完成率</span>')

# L256: <!-- ⑤评审结论 -->
c = c.replace(f'<!-- {p}评审结论 -->', '<!-- ⑤评审结论 -->')

# L266: <!-- ⑥问题清单 -->
c = c.replace(f'<!-- {p}问题清单 -->', '<!-- ⑥问题清单 -->')

# L271: <!-- 校对状态标记 -->
c = c.replace(f'校对状态标{p}-->', '校对状态标记 -->')

# L277: '已校对（锁定）' : '未校对'
c = c.replace(f"'已校对（锁定{p} : '未校{p} }}", "'已校对（锁定）' : '未校对' }}")

# L283: 保存并锁定</el-button>
c = c.replace(f'保存并锁{p}/el-button>', '保存并锁定</el-button>')

# L299: <!-- 未校对问题可修改一次 -->
c = c.replace(f'未校对问题可修改一{p}-->', '未校对问题可修改一次 -->')

# L326: <!-- ─── 问题回复对话框 ─── -->
c = c.replace(f'问题回复对话{p}───', '问题回复对话框 ───')

# L332: label="处理状态">
c = c.replace(f'label="处理状{p}>', 'label="处理状态">')

# L335: label="采纳-未解决"
c = c.replace(f'label="采纳-未解{p} value="adopted_unresolved"', 'label="采纳-未解决" value="adopted_unresolved"')

# L336: label="采纳-已解决"
c = c.replace(f'label="采纳-已解{p} value="adopted_resolved"', 'label="采纳-已解决" value="adopted_resolved"')

# L340: placeholder="请输入回复内容（选填）"
c = c.replace(f'（选填{p} maxlength=', '（选填）" maxlength=')

# L349: <!-- ─── AI 提取待办对话框 ─── -->
c = c.replace(f'待办对话{p}───', '待办对话框 ───')

# L369: placeholder="指定责任人"
c = c.replace(f'placeholder="指定责任{p} size="small"', 'placeholder="指定责任人" size="small"')

# L383: title="关联工作流"
c = c.replace(f'title="关联工作{p} width=', 'title="关联工作流" width=')

# L386: placeholder="输入 OA 工作流 ID 或流程编号"
c = c.replace(f'工作{p}ID 或流程编{p} />', '工作流 ID 或流程编号" />')

# L395: <!-- 手动新建待办对话框 -->
c = c.replace(f'手动新建待办对话{p}-->', '手动新建待办对话框 -->')

# L399: placeholder="请输入待办事项描述"
c = c.replace(f'待办事项描{p} />', '待办事项描述" />')

# L404: label="责任人" prop=
c = c.replace(f'label="责任{p} prop=', 'label="责任人" prop=')

# L405: placeholder="选择责任人" filterable
c = c.replace(f'placeholder="选择责任{p} filterable', 'placeholder="选择责任人" filterable')

# L412: label="优先级">
c = c.replace(f'label="优先{p}>', 'label="优先级">')

# L414-416: radio values 高/中/低
c = c.replace(f'value="high">{p}/el-radio>', 'value="high">高</el-radio>')
c = c.replace(f'value="medium">{p}/el-radio>', 'value="medium">中</el-radio>')
c = c.replace(f'value="low">{p}/el-radio>', 'value="low">低</el-radio>')

# ─── JS SECTION ────────────────────────────────────────────────────────────

# Block comment separators ═══\ufffd? → ════
# Replace ═\ufffd? with ══ everywhere (decorative comments only)
c = c.replace(f'═{p}   示例数据', '═══   示例数据')
c = c.replace(f'═{p}*/\n', '════*/\n')
c = c.replace(f'═{p}   响应式状态', '═══   响应式状态')
c = c.replace(f'═{p}   响应式状\ufffd?', '═══   响应式状态')
c = c.replace(f'响应式状{p}   ═', '响应式状态   ═')
c = c.replace(f'═{p}   列表 & 选择', '═══   列表 & 选择')
c = c.replace(f'═{p}   会议摘要内联编辑', '═══   会议摘要内联编辑')
c = c.replace(f'═{p}   会议记录关键点编\ufffd?', '═══   会议记录关键点编辑')
c = c.replace(f'会议记录关键点编{p}   ═', '会议记录关键点编辑   ═')
c = c.replace(f'═{p}   会议摘要 & 导出', '═══   会议摘要 & 导出')
c = c.replace(f'═{p}   音字对照：模拟播放器', '═══   音字对照：模拟播放器')
c = c.replace(f'═{p}   待办 / AI 提取 / 工作\ufffd?', '═══   待办 / AI 提取 / 工作流')
c = c.replace(f'工作{p}   ═', '工作流   ═')
c = c.replace(f'═{p}   手动新建待办', '═══   手动新建待办')
c = c.replace(f'═{p}   ECharts 饼图', '═══   ECharts 饼图')
c = c.replace(f'═{p}   工具函数', '═══   工具函数')
# catch-all for any remaining ═\ufffd?
c = c.replace(f'═{p}', '══')

# Demo participants
c = c.replace(f"'王建{p},", "'王建国',")
c = c.replace(f"'主持{p} }}", "'主持人' }}")
c = c.replace(f"'李敏{p},", "'李敏华',")
c = c.replace(f"'办公{p},", "'办公室',")
c = c.replace(f"'记录{p} }}", "'记录员' }}")
c = c.replace(f"'张伟{p},", "'张伟东',")
c = c.replace(f"'汇报{p} }}", "'汇报人' }}")
c = c.replace(f"'陈秀{p},", "'陈秀芳',")
c = c.replace(f"'财务{p},", "'财务科',")
c = c.replace(f"'参会{p} }}", "'参会人' }}")
c = c.replace(f"'刘志{p},", "'刘志强',")
c = c.replace(f"'综合{p},", "'综合科',")
c = c.replace(f"'赵丽{p},", "'赵丽娜',")
c = c.replace(f"'人事{p},", "'人事科',")
c = c.replace(f"'杨浩{p},", "'杨浩然',")
c = c.replace(f"'技术科', role: '参会{p} }}", "'技术科', role: '参会人' }}")
c = c.replace(f"'周婉{p},", "'周婉茹',")
c = c.replace(f"'行政{p},", "'行政科',")

# Location
c = c.replace(f"'行政{p}楼第一会议{p},", "'行政大楼第一会议室',")

# Summary text corruptions (demo data)
c = c.replace(f'主持，{p}人参会，历时2.5小时{p}\n', '主持，八人参会，历时2.5小时。\n')
c = c.replace(f'开发完{p}5%，预{p}月中旬', '开发完成85%，预计4月中旬')
c = c.replace(f'支出进度{p}\n', '支出进度。\n')
c = c.replace(f'机制优化{p}\n', '机制优化。\n')
c = c.replace(f'各科室{p}{p}日前', '各科室于4月5日前')
c = c.replace(f'人事科牵头{p}{p}0日前', '人事科牵头于4月3')  # 牵头于4月30日前
# Better fix for the 牵头 context:
c = c.replace(f'牵头于4月3', '牵头于4月30日前')

# keypoints section
c = c.replace(f"'预算执行与资金使用情{p},", "'预算执行与资金使用情况',")
c = c.replace(f'开发完{p}5%，数据库', '开发完成85%，数据库')
c = c.replace(f'预计4{p}5日可完', '预计4月15日可完')
c = c.replace(f'建议增{p}名运维', '建议增加2名运维')
c = c.replace(f'对执行率低{p}0%', '对执行率低于60%')
c = c.replace(f'考核指标{p} }},', '考核指标。 }},')
# Zhao lina training schedule
c = c.replace(f'培训{p}月中旬开展', '培训：4月中旬开展')
c = c.replace(f'应用培训{p}月安排', '应用培训，5月安排')
c = c.replace(f'规范培训{p}月组织', '规范培训，6月组织')
c = c.replace(f'外部讲{p}名，内部', '外部讲师2名，内部')
c = c.replace(f'费用预算18万元{p} }},', '费用预算18万元。 }},')
c = c.replace(f"'会议室智能化改造方{p},", "'会议室智能化改造方案',")
c = c.replace(f"杨浩然副科长介绍{p}楼", "杨浩然副科长介绍3楼")
c = c.replace(f'不影响日常会议使用{p} }},', '不影响日常会议使用。 }},')
c = c.replace(f"'跨部门协作机制优化建{p},", "'跨部门协作机制优化建议',")
c = c.replace(f'跨部门项目{p} }},', '跨部门项目。 }},')

# Transcripts - speaker names (same pattern as participants)
c = c.replace(f"speaker: '王建{p},", "speaker: '王建国',")
c = c.replace(f"speaker: '张伟{p},", "speaker: '张伟东',")
c = c.replace(f"speaker: '陈秀{p},", "speaker: '陈秀芳',")
c = c.replace(f"speaker: '赵丽{p},", "speaker: '赵丽娜',")
c = c.replace(f"speaker: '杨浩{p},", "speaker: '杨浩然',")
c = c.replace(f"speaker: '刘志{p},", "speaker: '刘志强',")
# 全体
c = c.replace(f"text: '谢谢王局{p} }},", "text: '谢谢王局长' },")
# Speaker texts ending with corrupted char
c = c.replace(f'信息中心张主任{p} }},', '信息中心张主任。 },')
c = c.replace(f'系统的稳定运行{p} }},', '系统的稳定运行。 },')
c = c.replace(f'汇报财务情况{p} }},', '汇报财务情况。 },')
c = c.replace(f'进行重点督办{p} }},', '进行重点督办。 },')
c = c.replace(f'培训情况{p} }},', '培训情况。 },')
c = c.replace(f'培训总预算十八万元{p} }},', '培训总预算十八万元。 },')
c = c.replace(f'建议五月份启动施工{p} }},', '建议五月份启动施工。 },')
c = c.replace(f'信息化项目上试行{p} }},', '信息化项目上试行。 },')
c = c.replace(f'今天的会议精神和工作部署{p} }},', '今天的会议精神和工作部署。 },')
c = c.replace(f'四月十日前定稿{p} }},', '四月十日前定稿。 },')
c = c.replace(f'谢谢大家{p} }},', '谢谢大家。 },')

# Todos
c = c.replace(f"'完成二期信息化系统全面部{p},", "'完成二期信息化系统全面部署',")
c = c.replace(f"'张伟{p}, priority:", "'张伟东', priority:")
c = c.replace(f"'提交二季度预算调整方{p},", "'提交二季度预算调整方案',")
c = c.replace(f"'陈秀{p}, priority:", "'陈秀芳', priority:")
c = c.replace(f"'赵丽{p}, priority:", "'赵丽娜', priority:")
c = c.replace(f"'杨浩{p}, priority:", "'杨浩然', priority:")
c = c.replace(f"'起草跨部门协作管理办{p},", "'起草跨部门协作管理办法',")
c = c.replace(f"'刘志{p}, priority:", "'刘志强', priority:")
c = c.replace(f"'周婉{p}, priority:", "'周婉茹', priority:")

# review_conclusion
c = c.replace(f'按期落实{p},', '按期落实。',)

# issues
c = c.replace(f'执行率偏低{p}8%', '执行率偏低（58%')
c = c.replace(f"reporter_name: '陈秀{p}, status:", "reporter_name: '陈秀芳', status:")
c = c.replace(f"预{p}月底前完{p} }},", "预计5月底前完成。 },")
c = c.replace(f"需增加2名专职运{p},", "需增加2名专职运维',")
c = c.replace(f"reporter_name: '张伟{p}, status:", "reporter_name: '张伟东', status:")
c = c.replace(f"2名运维人{p}{p}日到{p} }},", "2名运维人员已于4月1日到岗。 },")
c = c.replace(f"'会议室改造预算需进一步细化明确各项开{p},", "'会议室改造预算需进一步细化明确各项开支',")
c = c.replace(f"reporter_name: '杨浩{p}, status:", "reporter_name: '杨浩然', status:")
c = c.replace(f"各项开支均有依{p} }},", "各项开支均有依据。 },")

# JS reactive state section
c = c.replace(f'响应式状{p}   ═', '响应式状态   ═')
# comment IDs  
c = c.replace(f'会议记录关键点编{p}\nconst editingKpId', '会议记录关键点编辑\nconst editingKpId')
c = c.replace(f"open: '待处{p},", "open: '待处理',")
c = c.replace(f"'采纳-未解{p},", "'采纳-未解决',")
c = c.replace(f"'采纳-已解{p},", "'采纳-已解决',")
c = c.replace(f"resolved: '采纳-已解{p} }}", "resolved: '已解决' }")
c = c.replace(f"ElMessage.success('已更{p})", "ElMessage.success('已更新')")
c = c.replace(f"确认删除会议{p}{{{{meetingTitle}}}}", "确认删除会议「{{meetingTitle}}」")
c = c.replace(f"ElMessage.success('会议已删{p})", "ElMessage.success('会议已删除')")

# List & select section
c = c.replace(f'列表保持{p}  }}', '列表保持不变  }')
c = c.replace(f'自动选中第一{p}  if', '自动选中第一条  if')

# Summary edit section
c = c.replace(f"ElMessage.success('摘要已保{p})", "ElMessage.success('摘要已保存')")
c = c.replace(f"ElMessage.success('记录已保{p})", "ElMessage.success('记录已保存')")

# Export section
c = c.replace(f"ElMessage.success(`正在导出{p}${{format", "ElMessage.success(`正在导出 ${format")
c = c.replace('start_time)} ' + p + '${fmtTime', 'start_time)} — ${fmtTime')
c = c.replace(f"`参会{p} ${{fullData", "`参会人员：${fullData")
c = c.replace("p.real_name).join('" + p + "')",  "p.real_name).join('、')")
c = c.replace(f"'【会议摘要{p}, fullData", "'【会议摘要】', fullData")
c = c.replace(f"'【转写记录{p},", "'【转写记录】',")
c = c.replace(f"s.speaker}}{p}{{{{s.text}}", "s.speaker}}：${s.text}")

# Status update
c = c.replace(f"ElMessage.error('状态更新失{p})", "ElMessage.error('状态更新失败')")

# AI dialog section
c = c.replace(f'/* ─── AI 对话{p}─── */', '/* ─── AI 对话框 ─── */')

# AI todo candidates
c = c.replace(f"招聘2名运维人{p},", "招聘2名运维人员',")
c = c.replace(f"'赵丽{p}, _assignee_id:", "'赵丽娜', _assignee_id:")
c = c.replace(f"加快招标进{p},", "加快招标进度',")
c = c.replace(f"'陈秀{p}, _assignee_id:", "'陈秀芳', _assignee_id:")
c = c.replace(f"与物业协{p}月施工", "与物业协调5月施工")
c = c.replace(f"不影响日常会{p},", "不影响日常会议',")

# Workflow binding  
c = c.replace(f"ElMessage.success('工作流绑定成{p})", "ElMessage.success('工作流绑定成功')")

# Manual todo form  
c = c.replace(f"message: '请输入事项描{p},", "message: '请输入事项描述',")
c = c.replace(f"message: '请选择责任{p},", "message: '请选择责任人',")
c = c.replace(f"ElMessage.success('待办事项已创{p})", "ElMessage.success('待办事项已创建')")

# ECharts
c = c.replace(f"{{ name: '已完{p}, value:", "{ name: '已完成', value:")
c = c.replace(f"{{ name: '进行{p}, value:", "{ name: '进行中', value:")
c = c.replace(f"{{ name: '待处{p}, value:", "{ name: '待处理', value:")
c = c.replace(f"series: [{{ name: '待办状{p},", "series: [{ name: '待办状态',")

# Utility functions
c = c.replace(f"return {{ high: '{p}, medium: '{p}, low: '{p}", "return { high: '高', medium: '中', low: '低'")
c = c.replace(f"return {{ high: '高优', medium: '{p}, low: '{p}", "return { high: '高优', medium: '中', low: '低'")
c = c.replace(f"{{ pending: '待处{p}, in_progress: '进行{p}, completed: '已完{p},",
              "{ pending: '待处理', in_progress: '进行中', completed: '已完成',")

after_count = c.count('\ufffd')
print(f'After: {after_count} FFFD chars')
print(f'Fixed: {before_count - after_count}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print('Done!')

"""综合修复脚本 - 修复所有剩余 Vue 文件的 UTF-8 损坏"""
import re, os

p = '\ufffd?'  # 损坏模式

def fix_file(path, replacements, post_fix=None):
    """读取文件、应用替换规则、写回"""
    with open(path, encoding='utf-8', errors='replace') as f:
        c = f.read()
    before = c.count('\ufffd')
    for old, new in replacements:
        if callable(old):
            c = old(c)
        else:
            c = c.replace(old, new)
    if post_fix:
        c = post_fix(c)
    after = c.count('\ufffd')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    name = os.path.basename(path)
    print(f'{name}: {before} -> {after} corruptions')
    return after

# ===========================================================
# MeetingDetail.vue (69 corruptions)
# ===========================================================
md_path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingDetail.vue'
md_fixes = [
    # HTML 注释
    ('<!-- 顶部标题' + p + '-->', '<!-- 顶部标题栏 -->'),
    ('<!-- 主操作按' + p + '-->', '<!-- 主操作按钮 -->'),
    ('<!-- 参会人员 ' + p + '名牌展示 -->', '<!-- 参会人员 — 名牌展示 -->'),
    ('<!-- 编辑模式：拖拽列' + p + '-->', '<!-- 编辑模式：拖拽列表 -->'),
    ('<!-- 展示模式：名牌卡' + p + '-->', '<!-- 展示模式：名牌卡片 -->'),
    # 按钮文字
    ('<el-icon><VideoPlay /></el-icon>开始会' + p, '<el-icon><VideoPlay /></el-icon>开始会议\n        </el-button>'),
    ('<el-icon><VideoPlay /></el-icon>进入会议' + p, '<el-icon><VideoPlay /></el-icon>进入会议端\n        </el-button>'),
    ('<el-icon><VideoPlay /></el-icon>等待发起人准' + p, '<el-icon><VideoPlay /></el-icon>等待发起人准备\n        </el-button>'),
    # descriptions-item label 属性
    ('label="开始时' + p + '>', 'label="开始时间">'),
    ('label="结束时' + p + '>', 'label="结束时间">'),
    # 位置显示
    ("meeting.location || '" + p + "}", "meeting.location || '—'}"),
    # 日期格式化（格式字符串最后的日）
    ("format('YYYY年MM月DD" + p + "HH:mm')", "format('YYYY年MM月DD日 HH:mm')"),
    # 备用日期显示
    ("format('HH:mm') : '" + p + "}", "format('HH:mm') : '—'}"),
    ("format('YYYY年MM月DD日 HH:mm') : '" + p + "}", "format('YYYY年MM月DD日 HH:mm') : '—'}"),
    # 拖拽提示
    ('拖拽卡片可调整排列顺' + p + '/p>', '拖拽卡片可调整排列顺序</p>'),
    # 签到状态 tags
    ("element.checked_in ? '✓ 已签" + p + " : '未签" + p + "}", "element.checked_in ? '✓ 已签到' : '未签到'}"),
    ("p.checked_in ? '✓ 已签" + p + " : '未签" + p + "}", "p.checked_in ? '✓ 已签到' : '未签到'}"),
    # 准备中状态 tag
    ('>准备' + p + '/el-tag>', '>准备中</el-tag>'),
    # 会议准备阶段提示
    ('会议准备阶段，管理员可在此手动标记参会人员签到状态' + p, '会议准备阶段，管理员可在此手动标记参会人员签到状态。\n        </p>'),
    # 流程步骤 tags
    ('type="success" size="small">已完' + p + '/el-tag>', 'type="success" size="small">已完成</el-tag>'),
    # 流程箭头
    ('<div class="pf-arrow">' + p + '/div>', '<div class="pf-arrow">→</div>'),
    # 流程步骤标题
    ('提取关键信息与要' + p + '/div>', '提取关键信息与要点</div>'),
    ('自动识别会议决议、行动项、关键结' + p + '/div>', '自动识别会议决议、行动项、关键结论</div>'),
    # 待处理标签
    ('>待处' + p + '/el-tag>', '>待处理</el-tag>'),
    # 归档说明
    ('相关人员电子签署，纪要正式生效归' + p + '/div>', '相关人员电子签署，纪要正式生效归档</div>'),
    # 待编写完成按钮
    ('待编写完' + p, '待编写完成\n              </el-button>'),
    # 关键信息与要点
    ('<span>关键信息与要' + p + '/span>', '<span>关键信息与要点</span>'),
    # 发言者 span
    ("t.speaker_name || '未知'" + p + '/span>', "t.speaker_name || '未知'\"}}</span>"),
    # 下载查看
    ('请下载查' + p + '/div>', '请下载查看</div>'),
    # JS 日期格式化中
    ("start_time).format('YYYY年MM月DD" + p + "HH:mm')", "start_time).format('YYYY年MM月DD日 HH:mm')"),
    # 排序已保存
    ("ElMessage.success('排序已保" + p + ")", "ElMessage.success('排序已保存')"),
    # 会议类型 map 默认
    ("meeting.value.meeting_type || '" + p + "'", "meeting.value.meeting_type || ''"),
    # 座位号映射注释
    ('// 座位号映' + p + ' userId', '// 座位号映射 userId'),
    # 状态 map
    ("pending: '待开" + p + ', preparing:', "pending: '待开始', preparing:"),
    ("preparing: '准备" + p + ', in_progress:', "preparing: '准备中', in_progress:"),
    ("in_progress: '进行" + p + ', finished:', "in_progress: '进行中', finished:"),
    ("finished: '已结" + p, "finished: '已结束'"),
    ("archived: '已归" + p, "archived: '已归档'"),
    # ElMessage
    ("开始会议失" + p + ")", "开始会议失败')"),
    # 结束会议确认
    ("确认结束本次会议？结束后可生成摘要、提取要点，再编写会议纪要" + p, "确认结束本次会议？结束后可生成摘要、提取要点，再编写会议纪要。'"),
    ("会议已结束，请依次完成会后处理流" + p + ")", "会议已结束，请依次完成会后处理流程')"),
    # AI 摘要模板
    ('aiSummary.value = `本次会议' + p, "aiSummary.value = `本次会议于"),
    # 各科室须按期...
    ("各科室须按期提交工作计划，信息化项目纳入月度督办，培训方案由人事科牵头制定" + p, "各科室须按期提交工作计划，信息化项目纳入月度督办，培训方案由人事科牵头制定。'"),
    ("各责任人须在规定时间节点前完成对应工作任务，超期将启动督办程序" + p, "各责任人须在规定时间节点前完成对应工作任务，超期将启动督办程序。'"),
    # 强制完成确认
    ("'当前尚有参会人员未完成审签，是否强制结束签署流程？强制完成后纳入占签记录将标注为「管理员强制完成」" + p, "'当前尚有参会人员未完成审签，是否强制结束签署流程？强制完成后纳入占签记录将标注为「管理员强制完成」'"),
    ("审签流程已强制结束，纪要状态已更新为「已完成" + p, "审签流程已强制结束，纪要状态已更新为「已完成」'"),
    # 删除会议
    ("确定要删除该会议吗？此操作不可恢复" + p + ", '确认删除'", "确定要删除该会议吗？此操作不可恢复', '确认删除'"),
    ("ElMessage.success('会议已删" + p + ")", "ElMessage.success('会议已删除')"),
    # CSS 注释
    ('/* 上半区：大名' + p + '*/', '/* 上半区：大名牌 */'),
]

fix_file(md_path, md_fixes)

# ===========================================================
# RoomManagement.vue (39 corruptions)
# ===========================================================
rm_path = r'E:\event-intelligent\frontend\src\views\room\RoomManagement.vue'
rm_fixes = [
    # HTML template
    ('<h2>会议室管' + p + '/h2>', '<h2>会议室管理</h2>'),
    ('<!-- 座位布局编辑' + p + '-->', '<!-- 座位布局编辑器 -->'),
    ('{{ editingRoom.name }} ' + p + ' 座位布局编辑', '{{ editingRoom.name }} — 座位布局编辑'),
    # 按钮
    (p + ' 撤销', '← 撤销'),
    (p + ' 重做', '→ 重做'),
    # 大屏幕
    ('>大屏' + p + '/div>', '>大屏幕</div>'),
    # 右侧属性面板注释
    ('<!-- 右侧：属性面' + p + '-->', '<!-- 右侧：属性面板 -->'),
    ('<h4>大屏幕位' + p + '/h4>', '<h4>大屏幕位置</h4>'),
    # 宽/高 spans
    ('>宽' + p + '</span><el-input-number v-model="editorScreen.w"', '>宽</span><el-input-number v-model="editorScreen.w"'),
    ('>高' + p + '</span><el-input-number v-model="editorScreen.h"', '>高</span><el-input-number v-model="editorScreen.h"'),
    # 选中座位属性
    ('<!-- 选中座位属' + p + '-->', '<!-- 选中座位属性 -->'),
    ('座位属' + p + ' — #', '座位属性 — #'),
    ('placeholder="如：1' + p + ' />', 'placeholder="如：1号" />'),
    ('删除此座' + p + '/el-button>', '删除此座位</el-button>'),
    # 选中桌子属性
    ('<!-- 选中桌子属' + p + '-->', '<!-- 选中桌子属性 -->'),
    ('<h4>桌子属' + p + '/h4>', '<h4>桌子属性</h4>'),
    ('placeholder="如：会议' + p + ' />', 'placeholder="如：会议桌" />'),
    # 表单 label
    ('label="宽' + p + '>', 'label="宽">'),
    ('label="高' + p + '>', 'label="高">'),
    ('删除此桌' + p + '/el-button>', '删除此桌子</el-button>'),
    # 座位属性提示
    ('座位或桌子查' + p + ' 编辑属' + p + '/p>', '座位或桌子查看/编辑属性</p>'),
    ('拖拽可移动位' + p + '/p>', '拖拽可移动位置</p>'),
    # 所有座位
    ('<h4>所有座' + p + '(', '<h4>所有座位 ('),
    # 座位 label 显示  
    ("s.label || s.id + '" + p + " }}", "s.label || s.id + '号' }}"),
    # JS 注释和变量
    ('// 编辑器数' + p + '\nconst editorWidth', '// 编辑器数据\nconst editorWidth'),
    ("// 选中状" + p + "\nconst selectedType", '// 选中状态\nconst selectedType'),
    ("// 拖拽状" + p + "\nlet dragging", '// 拖拽状态\nlet dragging'),
    ("// 缩放拖拽状" + p + "\nlet resizing", '// 缩放拖拽状态\nlet resizing'),
    # ElMessage
    ("加载会议室列表失" + p + ")", "加载会议室列表失败')"),
    ("会议室创建成" + p + ")", "会议室创建成功')"),
    ('确定删除会议' + p + '\\', '确定删除会议室"${room.name}"？`, \''),
    ("已删" + p + ")", "已删除')"),
    ("布局已保" + p + ")", "布局已保存')"),
    # 键盘和生命周期
    ('// ===== 键盘和生命周' + p + '=====', '// ===== 键盘和生命周期 ====='),
    # CSS 注释
    ('/* ===== 深蓝科技风主题变' + p + '===== */', '/* ===== 深蓝科技风主题变量 ===== */'),
    ('/* ===== 编辑' + p + '===== */', '/* ===== 编辑器 ===== */'),
    ('/* ===== 属性面' + p + '===== */', '/* ===== 属性面板 ===== */'),
]

fix_file(rm_path, rm_fixes)

# ===========================================================
# MeetingIssueReview.vue (39 corruptions)
# ===========================================================
ir_path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingIssueReview.vue'
ir_fixes = [
    # HTML 模板
    ('纪要已签署，请逐条确认问题记录，完成后可批量归' + p + '/div>', '纪要已签署，请逐条确认问题记录，完成后可批量归档</div>'),
    ('<!-- 左侧：问题列' + p + '-->', '<!-- 左侧：问题列表 -->'),
    ('<!-- 工具' + p + '-->', '<!-- 工具栏 -->'),
    ('>全' + p + '/el-checkbox>', '>全选</el-checkbox>'),
    ('已选' + p + '{{ selectedIds.length }} / 共' + p + '{{ issues.length }} 条' + p, '已选 {{ selectedIds.length }} / 共 {{ issues.length }} 条'),
    ('active-text="需要审' + p + "'", 'active-text="需要审签"'),
    ('<!-- 勾' + p + ' + 校对状' + p + '-->', '<!-- 勾选 + 校对状态 -->'),
    ("issue.proofread ? '已校" + p + " : '未校" + p + "}", "issue.proofread ? '已校对' : '未校对'}"),
    ('>已归' + p + '/el-tag>', '>已归档</el-tag>'),
    ('<!-- 内容' + p + '-->', '<!-- 内容区 -->'),
    ('保存并确认校' + p + '/el-button>', '保存并确认校对</el-button>'),
    ('<!-- 未校对：可修改一' + p + '-->', '<!-- 未校对：可修改一次 -->'),
    ('<!-- 已校对：只读，显示提' + p + '-->', '<!-- 已校对：只读，显示提示 -->'),
    ('<el-icon><Lock /></el-icon> 已锁' + p, '<el-icon><Lock /></el-icon> 已锁定'),
    ('<!-- 右侧：统计面' + p + '-->', '<!-- 右侧：统计面板 -->'),
    ('class="stats-label">已校' + p + '/span>', 'class="stats-label">已校对</span>'),
    ('class="stats-label">未校' + p + '/span>', 'class="stats-label">未校对</span>'),
    ('class="stats-label">已归' + p + '/span>', 'class="stats-label">已归档</span>'),
    ("归档后无需签字，直接完成归" + p + "}", "归档后无需签字，直接完成归档'}"),
    ('<el-tag type="success" size="small" effect="plain">已校' + p + '/el-tag>', '<el-tag type="success" size="small" effect="plain">已校对</el-tag>'),
    ('<el-tag type="warning" size="small" effect="plain">未校' + p + '/el-tag>', '<el-tag type="warning" size="small" effect="plain">未校对</el-tag>'),
    ('可修改一次内容，修改后自动锁' + p + '/span>', '可修改一次内容，修改后自动锁定</span>'),
    ('即将对 <strong>{{ selectedIds.length }}</strong> 条问题记录进行归档' + p + '/p>', '即将对 <strong>{{ selectedIds.length }}</strong> 条问题记录进行归档。</p>'),
    ('title="未启用审签：问题将直接归' + p + "'", 'title="未启用审签：问题将直接归档"'),
    ('归档后问题状态不可再次修改，请确认无误后继续' + p + '/p>', '归档后问题状态不可再次修改，请确认无误后继续。</p>'),
    ('// 选择状' + p, '// 选择状态'),
    ("ElMessage.success('已标记为已校" + p + ")", "ElMessage.success('已标记为已校对')"),
    ("open: '待处" + p + ', explained:', "open: '待处理', explained:"),
    ("adopted_unresolved: '采纳-未解" + p + ', adopted_resolved:', "adopted_unresolved: '采纳-未解决', adopted_resolved:"),
    ("adopted_resolved: '采纳-已解" + p, "adopted_resolved: '采纳-已解决'"),
    ("adopted: '已采" + p, "adopted: '已采纳'"),
    ("return map[s] || s || '待处" + p, "return map[s] || s || '待处理'"),
    ("已归" + p + " ${selectedIds", "已归档 ${selectedIds"),
    ('// 为每条问题添' + p + ' proofread', '// 为每条问题添加 proofread'),
]

fix_file(ir_path, ir_fixes)

print('\n完成！')

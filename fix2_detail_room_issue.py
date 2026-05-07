"""第二轮修复 - MeetingDetail, RoomManagement, MeetingIssueReview"""

R = '\ufffd'  # 实际 U+FFFD 字符（第一轮写回后的形态）

def fix2(path, replacements):
    with open(path, encoding='utf-8', errors='replace') as f:
        c = f.read()
    before = c.count(R)
    for old, new in replacements:
        c = c.replace(old, new, 1) if old.count(R) > 0 else c.replace(old, new)
    after = c.count(R)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    import os; name = os.path.basename(path)
    print(f'{name}: {before} -> {after} remaining')

# ===========================================================
# MeetingDetail.vue (22 remaining)
# ===========================================================
md_path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingDetail.vue'
md_fixes = [
    # L115: location || '—' (closing quote was absorbed)
    (f"location || '{R}? }}", "location || '—' }}"),
    # L119,L123: '—' 备用时间显示 (closing quote absorbed)
    (f"') : '{R}? }}", "') : '—' }}"),
    (f"') : '{R}? }}", "') : '—' }}"),   # second occurrence (L123)
    # L175/195/227: checked_in ternary (✓ was corrupted, 到' absorbed)
    (f"? '{R}?已签{R}? : '未签{R}? }}", "? '✓ 已签到' : '未签到' }}"),
    (f"? '{R}?已签{R}? : '未签{R}? }}", "? '✓ 已签到' : '未签到' }}"),
    (f"? '{R}?已签{R}? : '未签{R}? }}", "? '✓ 已签到' : '未签到' }}"),
    # L357: el-tag importance display values (Chinese chars, quotes absorbed)
    (f"'high' ? '{R}? : kp.importance === 'medium' ? '{R}? : '{R}? }}",
     "'high' ? '高' : kp.importance === 'medium' ? '中' : '低' }}"),
    # L374: speaker span with fullwidth colon (：< absorbed)
    (f"}}{R}?/span>", "}}：</span>"),
    # L537: empty fallback value (—' absorbed → closing quote missing)
    (f"|| '{R}?\n", "|| '—'\n"),
    # L542: 座位号映射 (射 + space absorbed)
    (f"映{R}?userId", "映射 userId"),
    # L724: AI template literal ${...} ($ absorbed)
    (f"绕{R}?{{meeting", "绕${meeting"),
    # L739: keypoint content (项' absorbed → closing quote missing)
    (f"行动{R}?, content", "行动项', content"),
    # L740: keypoint optimization (化' absorbed → closing quote missing)
    (f"优化{R}?, importance", "优化', importance"),
]

fix2(md_path, md_fixes)

# ===========================================================
# RoomManagement.vue (14 remaining)
# ===========================================================
rm_path = r'E:\event-intelligent\frontend\src\views\room\RoomManagement.vue'
rm_fixes = [
    # L10: em dash separator (— + space absorbed)
    (f"}} {R}?座位布局编辑", "}} — 座位布局编辑"),
    # L13: ↩ undo arrow (↩ + space absorbed)
    (f"      {R}?撤销", "      ↩ 撤销"),
    # L16: ↪ redo arrow (↪ + space absorbed)
    (f"      {R}?重做", "      ↪ 重做"),
    # L115: 宽 span (宽 itself corrupted, < preserved)
    (f'<span>{R}?</span><el-input-number v-model="editorScreen.w"',
     '<span>宽</span><el-input-number v-model="editorScreen.w"'),
    # L116: 高 span (高 itself corrupted, < preserved)
    (f'<span>{R}?</span><el-input-number v-model="editorScreen.h"',
     '<span>高</span><el-input-number v-model="editorScreen.h"'),
    # L126: 座位属性 — # (two corruptions: 性 and — + space)
    (f"位属{R}?{R}?#{{{{", "位属性 — #{{"),
    # L162: label="宽" (宽 corrupted, > preserved) – first occurrence
    (f'label="{R}?>', 'label="宽">'),
    # L165: label="高" – second occurrence
    (f'label="{R}?>', 'label="高">'),
    # L179: 查看/编辑属性 (看/ and 性< both absorbed)
    (f"查{R}?编辑属{R}?/p>", "查看/编辑属性</p>"),
    # L241: 编辑器数据\nconst (据 + newline absorbed)
    (f"数{R}?const editorWidth", "数据\nconst editorWidth"),
    # L248: 选中状态\nconst (态 + newline absorbed)
    (f"状{R}?const selectedType", "状态\nconst selectedType"),
    # L251: 拖拽状态\nlet dragging (态 + newline absorbed)
    (f"拖拽状{R}?let dragging", "拖拽状态\nlet dragging"),
    # L259: 缩放拖拽状态\nlet resizing (态 + newline absorbed)
    (f"缩放拖拽状{R}?let resizing", "缩放拖拽状态\nlet resizing"),
    # L452: 会议室"${room.name}" (室 corrupted, " preserved)
    (f'会议{R}?"${{room.name}}"', '会议室"${room.name}"'),
]

fix2(rm_path, rm_fixes)

# ===========================================================
# MeetingIssueReview.vue (9 remaining)
# ===========================================================
ir_path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingIssueReview.vue'
ir_fixes = [
    # L20: 已选 {{ (选 + space absorbed)
    (f"已{R}?{{{{", "已选 {{"),
    # L20: / 共 {{ (共 + space absorbed)
    (f"/ {R}?{{{{", "/ 共 {{"),
    # L20: }} 条\n (条 + newline absorbed) – end of line
    (f"}} {R}?\r\n", "}} 条\r\n"),
    # L25: 需要审签" (签" absorbed closing quote)
    (f"审{R}?\r\n", '审签"\r\n'),
    # L57: 勾选 + (选 + space absorbed)
    (f"勾{R}?+", "勾选 +"),
    # L57: 校对状态 --> (态 + space absorbed)
    (f"状{R}?-->", "状态 -->"),
    # L70: 已校对' : '未校对' (对' absorbed)
    (f"已校{R}? : '未校{R}? }}", "已校对' : '未校对' }}"),
    # L163: 归档' }} (档' absorbed)
    (f"归{R}? }}", "归档' }}"),
    # L186: 对 <strong> (对 + space absorbed)
    (f"将{R}?<strong>", "将对 <strong>"),
    # L186: 归档。</p> (。< absorbed)
    (f"档{R}?/p>", "档。</p>"),
    # L196: 归档" end of line (档" absorbed)
    (f"归{R}?\r\n", '归档"\r\n'),
    # L319: 已归档 ${...} (档 + space absorbed)
    (f"归{R}?${{selectedIds", "归档 ${selectedIds"),
    # L338: 添加 proofread (加 + space absorbed)
    (f"添{R}?proofread", "添加 proofread"),
]

fix2(ir_path, ir_fixes)

print('\n全部完成！')

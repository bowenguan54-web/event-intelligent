#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix final JS syntax errors and HTML tag issues in ArchiveSearch.vue"""
import re

filepath = 'frontend/src/views/archive/ArchiveSearch.vue'
with open(filepath, encoding='utf-8') as f:
    c = f.read()

# ══ 1. Fix issue responses ══
# i1: missing end of response string
c = c.replace(
    "response: '已协调采购部加快招标流程，预4月底前完' },",
    "response: '已协调采购部加快招标流程，预计4月底前完成' },"
)

# i2: has extra '…日到岗' appended
c = c.replace(
    "response: '已完成招聘，2名运维人员已到岗。'…日到岗' },",
    "response: '已完成招聘，2名运维人员已到岗。' },"
)

# i3: content has duplicate data; clean up entire i3 entry
c = c.replace(
    "{ id: 'i3', content: '会议室改造预算需进一步细化明确各项开支均有依据' },, reporter_name: '杨浩然', status: 'explained', response: '已补充明细预算表，各项开支均有依据' },",
    "{ id: 'i3', content: '会议室改造预算需进一步细化明确各项开支', reporter_name: '杨浩然', status: 'explained', response: '已补充明细预算表，各项开支均有依据' },"
)

# ══ 2. Fix timeline strings missing closing quote ══
c = c.replace(
    "'会议召开，部署6项重点工作 },",
    "'会议召开，部署6项重点工作' },"
)
c = c.replace(
    "'会议纪要完成审签人'/8人签署）' },",
    "'会议纪要完成审签（7/8人签署）' },"
)
c = c.replace(
    "'杨浩然完成会议室改造方案细化 },",
    "'杨浩然完成会议室改造方案细化' },"
)
c = c.replace(
    "'赵丽娜完成全员培训计划制定 },",
    "'赵丽娜完成全员培训计划制定' },"
)

# ══ 3. Fix label functions ══
c = c.replace(
    "function importanceLabel(v) { return { high: '…, medium: '…, low: '' }[v] || v }",
    "function importanceLabel(v) { return { high: '高', medium: '中', low: '低' }[v] || v }"
)
c = c.replace(
    "function priorityLabel(v) { return { high: '高优', medium: '…, low: '' }[v] || v }",
    "function priorityLabel(v) { return { high: '高优', medium: '中', low: '低' }[v] || v }"
)

# ══ 4. Fix download link string ══
c = c.replace(
    "'导出任务已创建，完成后将通过通知推送下载链接)",
    "'导出任务已创建，完成后将通过通知推送下载链接')"
)

# ══ 5. Fix HTML closing tags (missing < before /tag>) ══
c = c.replace("返回检索结果/el-button>", "返回检索结果</el-button>")
c = c.replace("纯文本/el-dropdown-item>", "纯文本</el-dropdown-item>")
c = c.replace("}}人参会/span></div>", "}}人参会</span></div>")
c = c.replace("已归档/el-tag>", "已归档</el-tag>")

# ══ 6. Fix i1 response that got chopped ══
# The current i1 response is missing '成'
c = c.replace(
    "response: '已协调采购部加快招标流程，预4月底前完成' },",
    "response: '已协调采购部加快招标流程，预计4月底前完成' },"
)

print("All targeted fixes applied")
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(c)
print("Saved")

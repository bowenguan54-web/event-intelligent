#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix corrupted Chinese characters in ArchiveSearch.vue"""

filepath = 'frontend/src/views/archive/ArchiveSearch.vue'

with open(filepath, encoding='utf-8', errors='replace') as f:
    c = f.read()

p = '\ufffd?'
print(f'Initial corruptions: {c.count(p)}')

# ── Person names (last char + closing quote eaten) ──
names = [
    ('王建', '王建国'), ('李敏', '李敏华'), ('张伟', '张伟东'),
    ('陈秀', '陈秀芳'), ('刘志', '刘志强'), ('赵丽', '赵丽娜'),
    ('杨浩', '杨浩然'), ('周婉', '周婉莹'),
]
for prefix, full in names:
    c = c.replace(prefix + p, full + "'")

# ── Roles / Departments / Titles (longer first) ──
c = c.replace('高级工程' + p, "高级工程师'")
c = c.replace('主持' + p, "主持人'")
c = c.replace('记录' + p, "记录人'")
c = c.replace('汇报' + p, "汇报人'")
c = c.replace('参会' + p, "参会人'")
c = c.replace('研究' + p, "研究员'")
c = c.replace('工程' + p, "工程师'")
c = c.replace('副局' + p, "副局长'")
c = c.replace('审签' + p, "审签人'")
c = c.replace('办公' + p, "办公室'")
c = c.replace('财务' + p, "财务科'")
c = c.replace('综合' + p, "综合科'")
c = c.replace('人事' + p, "人事科'")
c = c.replace('行政' + p, "行政科'")
c = c.replace('技术' + p, "技术科'")

print(f'After names/roles: {c.count(p)}')

# ── Template corruptions (HTML) ──
c = c.replace('搜索' + p + ' -->', '搜索栏 -->')
c = c.replace('转写文' + p + '..', '转写文字..')
c = c.replace('语义检' + p, '语义检索"')
c = c.replace('关键词匹' + p, '关键词匹配"')
c = c.replace('高级筛' + p + ' -->', '高级筛选 -->')
c = c.replace('title="高级筛' + p + ' name=', 'title="高级筛选" name=')
c = c.replace('range-separator="' + p, 'range-separator="至"')
c = c.replace('开始日' + p, '开始日期"')
c = c.replace('批量操作' + p + ' -->', '批量操作栏 -->')
c = c.replace('条记' + p + '/span>', '条记录</span>')
c = c.replace('检索结果列' + p + ' -->', '检索结果列表 -->')
c = c.replace('description="暂无检索结' + p, 'description="暂无检索结果"')
c = c.replace('返回检索结' + p, '返回检索结果')
c = c.replace('纯文' + p, '纯文本')
# Date range separator in time span
c = c.replace('}} ' + p + ' {{ fmtTime', '}} 至 {{ fmtTime')
c = c.replace('}}人参' + p, '}}人参会')
c = c.replace('已归' + p, '已归档')
# Tab labels with corrupted emoji
c = c.replace('label="' + p + ' 签到' + p + ' name="checkin"', 'label="📋 签到表" name="checkin"')
c = c.replace('签到' + p + ' -->', '签到表 -->')
c = c.replace('|| \'' + p + ' }}', "|| '—' }}")
c = c.replace('已签' + p, "已签到'")
c = c.replace('未签' + p, "未签到 }")
c = c.replace('sig-empty">' + p + '/span>', 'sig-empty">—</span>')
c = c.replace('title || \'' + p, "title || '—'")
c = c.replace('关键讨论' + p, '关键讨论点')

print(f'After HTML template: {c.count(p)}')

# ── HTML table headers ──
c = c.replace('任务' + p + '</th>', '任务数</th>')
c = c.replace('已完' + p + '</th>', '已完成</th>')
c = c.replace('进行' + p + '</th>', '进行中</th>')
c = c.replace('完成' + p + '</th>', '完成率</th>')
c = c.replace('责任' + p + '</th>', '责任人</th>')
c = c.replace('优先' + p + '</th>', '优先级</th>')
c = c.replace('状' + p + '</th>', '状态</th>')

print(f'After table headers: {c.count(p)}')

# ── Section titles ──
c = c.replace('待办事项明' + p, '待办事项明细')
c = c.replace('会议摘要回' + p, '会议摘要回顾')
c = c.replace('关键时间节' + p, '关键时间节点')
c = c.replace('会议决定事' + p, '会议决定事项')
c = c.replace('参会人员' + p, '参会人员：')

print(f'After section titles: {c.count(p)}')

# ── JS strings in echarts / export ──
c = c.replace("'已完" + p, "'已完成'")
c = c.replace("'进行" + p, "'进行中'")
c = c.replace('participants.join(\'' + p, "participants.join('、'")
c = c.replace('至' + p + ' ${fmtTime', '至 ${fmtTime')
c = c.replace('参会' + p + ' ${', "参会人：${")
c = c.replace("'【会议摘要" + p, "'【会议摘要】'")
c = c.replace("'【转写记录" + p, "'【转写记录】'")
c = c.replace('正在导出' + p, "正在导出 ")
c = c.replace('下载链' + p, '下载链接')

print(f'After JS strings: {c.count(p)}')

# ── Template literal texts (demo data content) ──
c = c.replace('8' + p + '人参会', '8名人参会')
c = c.replace('完' + p + '5%', '成85%')
c = c.replace('预' + p + '月中旬', '预计4月中旬')
c = c.replace('进度' + p + '\n', '进度。\n')
c = c.replace('机制优化' + p + '\n', '机制优化。\n')
c = c.replace('方案制定。' + p + '`', '方案制定。`')
c = c.replace('纪' + p + '</h3>', '纪要</h3>')
c = c.replace('2026' + p + '3', '2026年3')
c = c.replace('3' + p + '18', '3月18')
c = c.replace('18' + p + '上午', '18日 上午')
c = c.replace('9:00' + p + '11', '9:00~11')
c = c.replace('行政' + p + '楼第一会议' + p, '行政楼第一会议室')
# Minutes HTML content
c = c.replace('张伟东' + p + '</strong>', '张伟东）</strong>')
c = c.replace('完' + p + '5%，数据库', '成85%，数据库')
c = c.replace('建议增' + p + '名', '建议增加2名')
c = c.replace('重点督办' + p + '</p>', '重点督办。</p>')
c = c.replace('内部讲' + p + '名', '内部讲师4名')
c = c.replace('外部讲' + p + '名', '外部讲师2名')
c = c.replace('决定事' + p + '</h4>', '决定事项</h4>')
c = c.replace('4' + p + '日前', '4月5日前')
c = c.replace('4' + p + '0日前', '4月10日前')
c = c.replace('报办公室' + p + '</li>', '报办公室。</li>')

# Transcript texts
c = c.replace('先\n请', '，先\n请')
c = c.replace('完成全面部署' + p, '完成全面部署。')
c = c.replace('稳定运行' + p, '稳定运行。')
c = c.replace('财务情况' + p, '财务情况。')
c = c.replace('重点督办' + p + ' },', '重点督办。 },')
c = c.replace('培训情况' + p, '培训情况。')
c = c.replace('十八万元' + p, '十八万元。')
c = c.replace('施工' + p + ' },', '施工。 },')
c = c.replace('试行' + p + ' },', '试行。 },')
c = c.replace('工作部署' + p + ' },', '工作部署。 },')
c = c.replace('月度督办' + p, '月度督办。')
c = c.replace('请杨\n科长细化后报办公室', '请杨浩然细化后报办公室')
c = c.replace('谢谢王局' + p, "谢谢王局长'")

# Todo items
c = c.replace('系统全面部' + p, '系统全面部署')
c = c.replace('预算调整方' + p, '预算调整方案')
c = c.replace('协作管理办' + p, '协作管理办法')

# Signing records
c = c.replace('抓紧落实' + p, "抓紧落实。'")
c = c.replace('准确无误' + p, "准确无误。'")
c = c.replace('表述准确' + p, "表述准确。'")
c = c.replace('同意' + p + "', signature_img:", "同意。', signature_img:")
c = c.replace('无异议' + p, "无异议。'")
c = c.replace('确认' + p + "', signature_img:", "确认。', signature_img:")
c = c.replace('进一步细化' + p, "进一步细化。'")

# Review conclusion
c = c.replace('按期落实' + p, "按期落实。'")

# Issues
c = c.replace('流程较长\',', "流程较长',")
c = c.replace('专职运' + p, "专职运维'")
c = c.replace('到' + p + ' },', "到岗' },")
c = c.replace('有依' + p + ' },', "有依据' },")

# Summary
c = c.replace('meeting_time: \'2026-03-28 09:00 ' + p + '11:30\'', "meeting_time: '2026-03-28 09:00~11:30'")
c = c.replace('location: \'行政' + p + '楼第一会议' + p, "location: '行政楼第一会议室'")

# Dept breakdown
c = c.replace("dept: '财务" + p, "dept: '财务科'")
c = c.replace("dept: '人事" + p, "dept: '人事科'")
c = c.replace("dept: '综合" + p, "dept: '综合科'")
c = c.replace("dept: '行政" + p, "dept: '行政科'")

# Recommendations
c = c.replace('建议如下' + p, '建议如下：\n')
c = c.replace('按时上线' + p, '按时上线。')
c = c.replace('采购通道' + p, '采购通道。')
c = c.replace('工作方法' + p, '工作方法。')
c = c.replace('审批流程' + p, '审批流程。')
c = c.replace('报名时间' + p, '报名时间。')
c = c.replace('本次会' + p + '项决议', '本次会议6项决议')

# Timeline
c = c.replace('部' + p + '项重点工' + p, '部署6项重点工作')
c = c.replace('改造方案细' + p, '改造方案细化')
c = c.replace('培训计划制' + p, '培训计划制定')

# Summary field (short)
c = c.replace('各科' + p + '026年', '各科室2026年')

# CSS comments (less critical)
c = c.replace('════' + p + '\n', '════\n')
c = c.replace('════' + p + '*/', '════\n*/')

print(f'After template literals: {c.count(p)}')

# Write  
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done! All fixed.')

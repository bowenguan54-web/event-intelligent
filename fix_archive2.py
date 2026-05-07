#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix remaining corruptions in ArchiveSearch.vue - Stage 2"""
import re

filepath = 'frontend/src/views/archive/ArchiveSearch.vue'
with open(filepath, encoding='utf-8', errors='replace') as f:
    c = f.read()

p = '\ufffd?'
print(f'Start: {c.count(p)} corruptions')

# FIX INTRODUCED BUG: 行政科'楼 → 行政楼
c = c.replace("行政科'楼第一会议" + p, "行政楼第一会议室'")
c = c.replace("行政科'楼第一会议室", "行政楼第一会议室")

# HTML comments
c = c.replace('搜索' + p + '-->', '搜索栏 -->')
c = c.replace('搜索' + p + ' -->', '搜索栏 -->')
c = c.replace('高级筛' + p + '-->', '高级筛选 -->')
c = c.replace('高级筛' + p + ' -->', '高级筛选 -->')
c = c.replace('批量操作' + p + '-->', '批量操作栏 -->')
c = c.replace('批量操作' + p + ' -->', '批量操作栏 -->')
c = c.replace('检索结果列' + p + '-->', '检索结果列表 -->')
c = c.replace('检索结果列' + p + ' -->', '检索结果列表 -->')
# Comments with emoji prefix (like <!-- 📝 会议纪要 -->)
c = c.replace('<!-- ' + p + ' 会议纪要 -->', '<!-- 📝 会议纪要 -->')
c = c.replace('<!-- ' + p + ' 会议记录（音' + p + ' 文本' + p + ' -->', '<!-- 🎧 会议记录（音频/文本） -->')
c = c.replace('<!-- ' + p + ' 会议摘要 -->', '<!-- 📊 会议摘要 -->')
c = c.replace('<!-- ' + p + ' 签到' + p + ' -->', '<!-- 📋 签到表 -->')
c = c.replace('<!-- 专家签到' + p + ' -->', '<!-- 专家签到表 -->')
c = c.replace('<!-- 其他人员签到' + p + ' -->', '<!-- 其他人员签到表 -->')
c = c.replace('<!-- ' + p + ' 评审结论 -->', '<!-- 📝 评审结论 -->')
c = c.replace('<!-- ' + p + ' 问题清单 -->', '<!-- 🔴 问题清单 -->')
c = c.replace('<!-- ' + p + ' 落实报表 -->', '<!-- 📄 落实报表 -->')

# Tab pane label (critical: fixes attribute parsing error)
c = c.replace('label="' + p + ' 签到' + p + ' name="checkin"',
              'label="📋 签到表" name="checkin"')
c = c.replace('label="' + p + ' 签到' + p + '"', 'label="📋 签到表"')
# Catch-all for remaining tab label corruption
if p + ' name="checkin"' in c:
    c = re.sub(r'label="[^"]*' + re.escape(p) + r'[^"]*" name="checkin"', 'label="📋 签到表" name="checkin"', c)

# fix collapse-item title (critical: attribute parsing)
c = c.replace('title="高级筛' + p + ' name="advanced">', 'title="高级筛选" name="advanced">')
c = c.replace('title="高级筛' + p + '"', 'title="高级筛选"')

# Table headers with missing </th>
c = c.replace('任务' + p + '/th>', '任务数</th>')
c = c.replace('已完' + p + '/th>', '已完成</th>')
c = c.replace('进行' + p + '/th>', '进行中</th>')
c = c.replace('完成' + p + '/th>', '完成率</th>')
c = c.replace('责任' + p + '/th>', '责任人</th>')
c = c.replace('优先' + p + '/th>', '优先级</th>')
c = c.replace('状' + p + '/th>', '状态</th>')

# sig-empty spans
c = c.replace('sig-empty">' + p + '/span>', 'sig-empty">—</span>')

# Already signed
c = c.replace("'已签" + p + " :", "'已签到' :")
c = c.replace("'已签" + p, "'已签到'")
c = c.replace("'未签" + p, "'未签到'")

# placeholder cells in data
c = c.replace("|| '" + p + " }}", "|| '—' }}")
c = c.replace("|| '" + p + "'", "|| '—'")
c = c.replace("|| '" + p, "|| '—'")

print(f'After HTML fixes: {c.count(p)}')

# JS data - person title fields
c = c.replace("'会议时间" + p, "'会议时间：'")
c = c.replace("'会议地点" + p, "'会议地点：'")
c = c.replace("'主" + p + "人：'", "'主持人：'")
c = c.replace("'记" + p + "人：'", "'记录人：'")

# === JS string fixes (missing closing quote) ===
# keypoint title
c = c.replace("'预算执行与资金使用情" + p, "'预算执行与资金使用情况'")

# keypoint content (backtick-style long strings)
c = c.replace("指标" + p + " },", "指标。' },")
c = c.replace("元" + p + " },", "万元。' },")
c = c.replace("18万元" + p + " },", "18万元。' },")

# transcript end-of-speech markers
c = c.replace("先请信息中心张主任" + p + " },", "先请信息中心张主任。' },")
c = c.replace("月度督办。第二," + p, "月度督办。第二，")
c = c.replace("月十日前定稿" + p + " },", "月十日前定稿。' },")  
c = c.replace("报办公室。第五" + p, "报办公室。第五，")
c = c.replace("好，今天的会就开到这里" + p, "好，今天的会就开到这里，谢谢大家。'")
c = c.replace("谢谢大家" + p, "谢谢大家。'")

# signing comments with closing quote issues
c = c.replace("'同意" + p + "', signature_img:", "'同意。', signature_img:")
c = c.replace("'同意" + p + ",", "'同意。',")
c = c.replace("培训预算部分确认" + p + "', signature_img:", "培训预算部分确认。', signature_img:")
c = c.replace("培训预算部分确认" + p, "培训预算部分确认。'")

# issue responses
c = c.replace("2名运维人" + p + "\n", "2名运维人员已到岗。'\n")
c = c.replace("2名运维人" + p + " \n", "2名运维人员已到岗。'\n")
c = c.replace("2名运维人" + p, "2名运维人员已到岗。'")

# issue content
c = c.replace("各项开" + p, "各项开支均有依据' },")

# closing quote for long content strings
c = c.replace("按期落实" + p + "',", "按期落实。',")
c = c.replace("按期落实" + p, "按期落实。'")

print(f'After JS string fixes: {c.count(p)}')

# === Template literal content (inside backtick strings) ===
c = c.replace("8" + p + " 人参会", "8名人参会")
c = c.replace("8" + p + "人参会", "8名人参会")
c = c.replace("历时2.5小时" + p, "历时2.5小时，")
c = c.replace("机制优化" + p, "机制优化。")
c = c.replace("方案制定。" + p + "`", "方案制定。`")

# Minutes heading
c = c.replace("会议纪" + p + "</h3>", "会议纪要</h3>")

# Minutes time/location
c = c.replace("2026" + p + "3月18", "2026年3月18")
c = c.replace("3月18" + p + " 上午", "3月18日 上午")
c = c.replace("9:00" + p + "11:30", "9:00~11:30")

# Minutes lines
c = c.replace("张伟东" + p + "</strong>", "张伟东）</strong>")
c = c.replace("4月5日" + p + "日前", "4月5日前")
c = c.replace("4" + p + "日前提交", "4月5日前提交")
c = c.replace("4" + p + "0日前完成方案", "4月10日前完成方案")
c = c.replace("报办公室" + p + "</li>", "报办公室。</li>")
c = c.replace("按期落实" + p + "</li>", "按期落实。</li>")
c = c.replace("尽快落实" + p + "</li>", "尽快落实。</li>")

# Month-based date patterns
c = c.replace("4" + p + "15日", "4月15日")
c = c.replace("4" + p + "5日", "4月5日")

# Training months
c = c.replace("培训—" + p + "月信息化", "培训——4月信息化")
c = c.replace("培训" + p + "月公文写作", "培训、5月公文写作")
c = c.replace("培训" + p + "月跨部门", "培训、6月跨部门")

# Content trailing punctuation
c = c.replace("重点督办" + p + "</p>", "重点督办。</p>")
c = c.replace("万元" + p + "</p>", "万元。</p>")

# Missing characters in middle of content
c = c.replace("低" + p + "0%", "低于60%")
c = c.replace("低" + p + "60%", "低于60%")

# Report data
c = c.replace("确" + p + " 4月15", "确保4月15")
c = c.replace("确" + p + "4月15", "确保4月15")

# Summary short desc
c = c.replace("各科" + p + "2026年", "各科室2026年")
c = c.replace("各科" + p + "026年", "各科室2026年")

# Export/print title
c = c.replace("} " + p + " 落实情况报表", "} - 落实情况报表")
c = c.replace("}\n" + p + " 落实情况报表", "} - 落实情况报表")

# Text separators  
c = c.replace("${formatTime(currentDetail.value.start_time)} " + p + " ${fmtTime", 
              "${formatTime(currentDetail.value.start_time)} 至 ${fmtTime")
c = c.replace("start_time) }} " + p + " {{ fmtTime", "start_time) }} 至 {{ fmtTime")

# Participants join
c = c.replace("participants.join('" + p + "')", "participants.join('、')")
c = c.replace(".join('" + p + ")", ".join('、')")

# Participants label in export
c = c.replace("`参会人' ${", "`参会人：${")
c = c.replace("参会人' ${currentDetail", "参会人：${currentDetail")

# Minutes/transcript section label
c = c.replace("'【会议摘要" + p, "'【会议摘要】'")
c = c.replace("'【转写记录" + p, "'【转写记录】'")

# Export message
c = c.replace("正在导出" + p + " ${format", "正在导出 ${format")
c = c.replace("正在导出" + p + "${format", "正在导出 ${format")
c = c.replace("下载链" + p + ")", "下载链接)")

# Time separator in export  
c = c.replace("${formatTime(currentDetail.value.start_time)} " + p + " ${fmtTime(currentDetail.value.end_time)}", 
              "${formatTime(currentDetail.value.start_time)} 至 ${fmtTime(currentDetail.value.end_time)}")

print(f'After template literal: {c.count(p)}')

# === JS label functions ===
c = c.replace("{ high: '" + p + "', medium: '" + p + "', low: '" + p + "' }", 
              "{ high: '高', medium: '中', low: '低' }")
c = c.replace("medium: '" + p + "', low:", "medium: '中', low:")
c = c.replace("low: '" + p + "' }[v]", "low: '低' }[v]")
c = c.replace("{ high: '高优', medium: '" + p + "', low:", "{ high: '高优', medium: '中', low:")
c = c.replace("low: '" + p + "' }[v]", "low: '低' }[v]")
# todoStatusLabel
c = c.replace("pending: '待处" + p, "pending: '待处理'")
# issueStatusLabel
c = c.replace("open: '待处" + p, "open: '待处理'")
c = c.replace("adopted: '采纳-已解" + p, "adopted: '采纳-已解决'")
c = c.replace("adopted_resolved: '采纳-已解" + p, "adopted_resolved: '采纳-已解决'")
c = c.replace("adopted_unresolved: '采纳-未解" + p, "adopted_unresolved: '采纳-未解决'")

# CSS section comments (non-critical)
c = c.replace('════' + p + '\n', '════\n')
c = c.replace('════' + p + '\n   ', '════\n   ')
c = c.replace('════\n   ' + p + '*/', '════\n   */')
# Clear any remaining CSS comment patterns
c = re.sub(r'═+' + re.escape(p), '═══════════════════════════════════════════════════════', c)

# Checkin section title
c = c.replace('─── 签到' + p + ' ───', '─── 签到表 ───')

# catch remaining /th> issues
c = re.sub(re.escape(p) + r'</th>', '…</th>', c)
c = re.sub(re.escape(p) + r'/th>', '…</th>', c)

print(f'After label/CSS: {c.count(p)}')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(c)
print('Stage 2 done')

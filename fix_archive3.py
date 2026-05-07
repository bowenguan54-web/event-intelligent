#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix remaining corruptions in ArchiveSearch.vue - Stage 3"""
import re

filepath = 'frontend/src/views/archive/ArchiveSearch.vue'
with open(filepath, encoding='utf-8', errors='replace') as f:
    c = f.read()

p = '\ufffd?'
print(f'Start: {c.count(p)} corruptions')

# Fix introduced bug: extra ' before /p>
c = c.replace("行政楼第一会议室'/p>", "行政楼第一会议室</p>")

# L144: time range separator  
c = re.sub(r'\}\}\s*' + re.escape(p) + r'\s*\{\{', '}} 至 {{', c)

# L230: tab pane label - use regex  
c = re.sub(r'label="' + re.escape(p) + r'\s*签到' + re.escape(p) + r'\s*(?=name=)', 'label="📋 签到表" ', c)
c = re.sub(r'label="[^"]*' + re.escape(p) + r'[^"]*"(\s*name="checkin")', r'label="📋 签到表"\1', c)

# HTML comments with emoji (try without space)
for comment_pattern in ['搜索', '高级筛', '批量操作', '检索结果列', '专家签到', '其他人员签到']:
    c = re.sub(re.escape(comment_pattern) + re.escape(p) + r'\s*-->', comment_pattern + ' -->', c)

# Emoji comments - try exact match  
c = re.sub(r'<!--\s*' + re.escape(p) + r'\s*会议纪要\s*-->', '<!-- 📝 会议纪要 -->', c)
c = re.sub(r'<!--\s*' + re.escape(p) + r'\s*会议记录[^>]*-->', '<!-- 🎧 会议记录 -->', c)  
c = re.sub(r'<!--\s*' + re.escape(p) + r'\s*会议摘要\s*-->', '<!-- 📊 会议摘要 -->', c)
c = re.sub(r'<!--\s*' + re.escape(p) + r'\s*签到[^>]*-->', '<!-- 📋 签到表 -->', c)
c = re.sub(r'<!--\s*' + re.escape(p) + r'\s*评审结论\s*-->', '<!-- 📝 评审结论 -->', c)
c = re.sub(r'<!--\s*' + re.escape(p) + r'\s*问题清单\s*-->', '<!-- 🔴 问题清单 -->', c)
c = re.sub(r'<!--\s*' + re.escape(p) + r'\s*落实报表\s*-->', '<!-- 📄 落实报表 -->', c)
# title sections in html comments
c = re.sub(r'<!--\s*' + re.escape(p) + r'\s*(主|记)\s*' + re.escape(p) + r'\s*人：\s*-->', '', c)

# L376: '未设? }}
c = re.sub(r"'未设" + re.escape(p) + r"\s*\}\}", "'未设置' }}", c)

# L482 summary issues
c = re.sub(r'，\s*' + re.escape(p) + r'\s*人参会', '，8名人参会', c)

# L485 月日期
c = re.sub(r'各科室' + re.escape(p) + r'\s*' + re.escape(p) + r'日前提交', '各科室于4月5日前提交', c)
c = re.sub(r'各科室' + re.escape(p) + r'\s+' + re.escape(p) + r'日前', '各科室于4月5日前', c)
c = re.sub(r'牵头' + re.escape(p) + r'\s*' + re.escape(p) + r'0日前', '牵头，4月10日前', c)
c = re.sub(r'各科室' + re.escape(p), '各科室于', c)
c = re.sub(r'牵头' + re.escape(p), '牵头，', c)

# Minutes content  
c = re.sub(r'纪' + re.escape(p) + r'</h3>', '纪要</h3>', c)
c = re.sub(r'会议时间' + re.escape(p) + r'</strong>', '会议时间：</strong>', c)
c = re.sub(r'会议地点' + re.escape(p) + r'</strong>', '会议地点：</strong>', c)
c = re.sub(r'主' + re.escape(p) + r'\s*' + re.escape(p) + r'人：', '主持人：', c)
c = re.sub(r'记' + re.escape(p) + r'\s*' + re.escape(p) + r'人：', '记录人：', c)
c = re.sub(r'2026' + re.escape(p), '2026年', c)
c = re.sub(r'3月18' + re.escape(p), '3月18日', c)
c = re.sub(r'9:00' + re.escape(p) + r'1:30', '9:00~11:30', c)
c = re.sub(r'张伟东' + re.escape(p) + r'</strong>', '张伟东）</strong>', c)
c = re.sub(r'运维人员' + re.escape(p) + r'</p>', '运维人员。</p>', c)
c = re.sub(r'重点督办' + re.escape(p) + r'</p>', '重点督办。</p>', c)
c = re.sub(r'万元' + re.escape(p) + r'</p>', '万元。</p>', c)
c = re.sub(r'4' + re.escape(p) + r'\s*月?\s*5日前', '4月5日前', c)
c = re.sub(r'4' + re.escape(p) + r'0日前', '4月10日前', c)
c = re.sub(r'报办公室' + re.escape(p), '报办公室。', c)
c = re.sub(r'尽快落实' + re.escape(p), '尽快落实。', c)
c = re.sub(r'方案制定' + re.escape(p), '方案制定。', c)

# L488 date: 2026年3月18日
c = re.sub(r'3' + re.escape(p) + r'18', '3月18', c)
c = re.sub(r'18' + re.escape(p) + r'上午', '18日 上午', c)

# L489 location extra quote
c = c.replace("行政楼第一会议室'</p>", "行政楼第一会议室</p>")

# keypoint content - month patterns
c = re.sub(re.escape(p) + r'月中旬', '4月中旬', c)
c = re.sub(re.escape(p) + r'月公文', '5月公文', c)
c = re.sub(re.escape(p) + r'月跨部门', '6月跨部门', c)
c = re.sub(re.escape(p) + r'月安排', '5月安排', c)
c = re.sub(re.escape(p) + r'月组织', '6月组织', c)

# Issue content
c = re.sub(r'经费执行率偏低' + re.escape(p), '经费执行率偏低（5', c)
c = re.sub(r'偏低\（5' , '偏低（5', c)

# Issue response
c = re.sub(re.escape(p) + r'月底前完', '4月底前完', c)

# Recommendation content
c = re.sub(r'确' + re.escape(p) + r'(4月15|\d)', r'确保\1', c)
c = re.sub(r'确' + re.escape(p), '确保', c)

# L608 short summary '? 人参会'
c = re.sub(r'，\s*' + re.escape(p) + r'\s*人参会', '，8人参会', c)

# Print/export title
c = re.sub(re.escape(p) + r'\s*落实情况报表', ' 落实情况报表', c)

# Time range in export
c = re.sub(r'start_time\)\s*' + re.escape(p) + r'\s*\$\{fmtTime', 'start_time) 至 ${fmtTime', c)

# importanceLabel function
c = re.sub(r"\{ high: '" + re.escape(p) + r"', medium: '" + re.escape(p) + r"', low: '" + re.escape(p) + r"' \}", "{ high: '高', medium: '中', low: '低' }", c)
c = re.sub(r"medium: '" + re.escape(p) + r"', low:", "medium: '中', low:", c)
c = re.sub(r"low: '" + re.escape(p) + r"' \}\[v\]", "low: '低' }[v]", c)

# todoSummaryLabel
c = re.sub(r"completion_[^}]*" + re.escape(p), "completion_rate: '完成率'", c)

# CSS comments
c = re.sub(r'═+' + re.escape(p) + r'\s*\n', '══════════════════════════════════════════════════════\n', c)
c = re.sub(r'───\s*签到' + re.escape(p) + r'\s*───', '─── 签到表 ───', c)

# Catch-all for remaining simple patterns
# /p> without opening </
c = re.sub(re.escape(p) + r'</p>', '。</p>', c)
c = re.sub(re.escape(p) + r'/p>', '。</p>', c)
c = re.sub(re.escape(p) + r'</li>', '。</li>', c)
c = re.sub(re.escape(p) + r'/li>', '。</li>', c)

print(f'After main fixes: {c.count(p)}')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(c)
print('Stage 3 done')

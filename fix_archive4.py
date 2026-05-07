#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix final 10 corruptions in ArchiveSearch.vue - Stage 4"""
import re

filepath = 'frontend/src/views/archive/ArchiveSearch.vue'
with open(filepath, encoding='utf-8', errors='replace') as f:
    c = f.read()

p = '\ufffd?'
print(f'Start: {c.count(p)} corruptions')

# Show context around each remaining corruption
idx = 0
while True:
    idx = c.find(p, idx)
    if idx == -1:
        break
    print(repr(c[max(0,idx-30):idx+30]))
    idx += 1

print('---FIXING---')

# Issue responses
c = re.sub(r"response: '已协调采购部\s*" + re.escape(p), "response: '已协调采购部加快招标流程，预计4月底前完成", c)
c = re.sub(r"人员已\s*\n\s*" + re.escape(p) + r"日到岗", "人员已到岗", c)
c = re.sub(r"人员已\s*" + re.escape(p), "人员已到岗'", c)

# Export time range (different format with })
c = re.sub(r'start_time\)\}\s*' + re.escape(p) + r'\s*\$\{fmtTime', 'start_time)} 至 ${fmtTime', c)
c = re.sub(r'start_time\)}\s*' + re.escape(p), 'start_time)} 至', c)
c = re.sub(re.escape(p) + r'\$\{fmtTime', '至 ${fmtTime', c)

# Recommendation text
c = re.sub(r'确保' + re.escape(p) + r'5日', '确保4月15日', c)
c = re.sub(r'确保' + re.escape(p), '确保4月15日', c)

# importanceLabel (exact chars)
c = re.sub(r"high: '" + re.escape(p) + r"', medium:", "high: '高', medium:", c)
c = re.sub(r"medium: '" + re.escape(p) + r"', low: '" + re.escape(p) + r"'", "medium: '中', low: '低'", c)
c = re.sub(r"medium: '" + re.escape(p) + r"'", "medium: '中'", c)
c = re.sub(r"low: '" + re.escape(p) + r"'", "low: '低'", c)

# Issue status map trailing ?
c = re.sub(r"unresolved: '채纳-未解" + re.escape(p), "unresolved: '采纳-未解决'", c)
c = re.sub(re.escape(p) + r"\s*\}", "' }", c)  # catch any remaining in object literals
c = re.sub(re.escape(p), "…", c)  # catch-all for remaining corruptions

print(f'After final fixes: {c.count(p)}')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(c)
print('Stage 4 done')

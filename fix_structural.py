#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix structural damage in ArchiveSearch.vue caused by overaggressive regex"""

filepath = 'frontend/src/views/archive/ArchiveSearch.vue'
with open(filepath, encoding='utf-8') as f:
    c = f.read()

# ══════════════════════════════════════════════════
# 1. Restore the DEMO_ARCHIVE_DETAIL section that was destroyed
#    by the overaggressive regex in fix_archive3.py
# ══════════════════════════════════════════════════

DAMAGED = """  completion_rate: '完成率'/p>
<h4>二、会议决定事项/h4>
<ol>
<li>各科室于4月5日前提交二季度详细工作计划；</li>
<li>信息化项目纳入月度督办，每周报送进度；</li>
<li>培训计划由人事科牵头，4月10日前完成方案制定。/li>
<li>会议室智能化改造方案由杨浩然细化后报办公室。/li>
<li>跨部门协作机制优化由刘志强牵头起草管理办法；</li>
<li>预算督办方案请陈秀芳尽快落实。/li>
</ol>`,"""

RESTORED = """  completion_rate: 66.7,
  summary: `本次会议由王建国副局长主持，8名人参会，历时2.5小时。
会议首先听取了各科室2026年第一季度工作完成情况汇报。信息中心张伟东主任介绍了政务信息化二期系统建设进展，目前核心模块开发完成85%，预计4月中旬完成全部部署。财务科陈秀芳科长通报了一季度预算执行情况，总体执行率达72%，部分专项经费需加快支出进度。
会议重点讨论了第二季度五项重点工作：信息化系统全面上线、预算中期调整、全员业务能力提升培训、会议室智能化改造以及跨部门协作机制优化。
会议决定：各科室于4月5日前提交二季度详细工作计划；信息化项目纳入月度督办，每周报送进度；培训计划由人事科牵头，4月10日前完成方案制定。`,
  minutes: `<h3>2026年第一季度工作总结暨第二季度计划部署会议纪要</h3>
<p><strong>会议时间：</strong>2026年3月18日 上午9:00~11:30</p>
<p><strong>会议地点：</strong>行政楼第一会议室</p>
<p><strong>主持人：</strong>王建国（副局长）</p>
<p><strong>记录人：</strong>李敏华（办公室）</p>
<p><strong>参会人员：</strong>王建国、李敏华、张伟东、陈秀芳、刘志强、赵丽娜、杨浩然、周婉莹</p>
<h4>一、各科室工作汇报</h4>
<p>1. <strong>信息中心（张伟东）</strong>：政务信息化二期核心模块开发完成85%，数据库迁移通过压力测试。移动端适配还需2周，预计4月15日完成全部署。安全等保三级测评通过，等待正式发证。建议增加2名运维人员。</p>
<p>2. <strong>财务科（陈秀芳）</strong>：一季度预算总额3200万元，已执行2304万元，执行率72%。信息化专项执行率仅58%，需加快招标采购。建议执行率低于60%的科室重点督办。</p>
<p>3. <strong>人事科（赵丽娜）</strong>：计划二季度分三批组织全员培训——4月信息化应用培训、5月公文写作培训、6月跨部门业务交流。邀请外部讲师2名、内部讲师4名，预算18万元。</p>
<h4>二、会议决定事项</h4>
<ol>
<li>各科室于4月5日前提交二季度详细工作计划；</li>
<li>信息化项目纳入月度督办，每周报送进度；</li>
<li>培训计划由人事科牵头，4月10日前完成方案制定。</li>
<li>会议室智能化改造方案由杨浩然细化后报办公室。</li>
<li>跨部门协作机制优化由刘志强牵头起草管理办法；</li>
<li>预算督办方案请陈秀芳尽快落实。</li>
</ol>`,"""

if DAMAGED in c:
    c = c.replace(DAMAGED, RESTORED)
    print("Restored DEMO_ARCHIVE_DETAIL structure")
else:
    print("WARNING: damaged section not found exactly, trying partial match...")
    # Try with different line endings or whitespace
    import re
    m = re.search(r"completion_rate: '完成率'.*?</ol>`\s*,", c, re.DOTALL)
    if m:
        print(f"Found damaged section at pos {m.start()}: {repr(c[m.start():m.start()+100])}")
        c = c[:m.start()] + RESTORED + c[m.end():]
        print("Restored via regex")
    else:
        print("ERROR: Could not find damaged section")

# ══════════════════════════════════════════════════  
# 2. Fix keypoint content strings missing closing '
# ══════════════════════════════════════════════════
c = c.replace("系统稳定运行。 },", "系统稳定运行。' },")

# ══════════════════════════════════════════════════
# 3. Fix transcript text strings missing closing '
# ══════════════════════════════════════════════════
# Pattern: text: '...。 }, (missing ')
import re
# Fix transcript entries with . }, at end (missing closing quote)
c = re.sub(r"(text: '[^']+?。)\s*\},", r"\1' },", c)
# Handle the longer ones that end differently  
c = re.sub(r"(text: '[^']*?部署。)\s*\},", r"\1' },", c)
c = re.sub(r"(text: '[^']*?运行。)\s*\},", r"\1' },", c)
c = re.sub(r"(text: '[^']*?情况。)\s*\},", r"\1' },", c)
c = re.sub(r"(text: '[^']*?督办。)\s*\},", r"\1' },", c)
c = re.sub(r"(text: '[^']*?训情况。)\s*\},", r"\1' },", c)
c = re.sub(r"(text: '[^']*?元。)\s*\},", r"\1' },", c)
c = re.sub(r"(text: '[^']*?施工。)\s*\},", r"\1' },", c)
c = re.sub(r"(text: '[^']*?试行。)\s*\},", r"\1' },", c)
c = re.sub(r"(text: '[^']*?部署。)\s*\},", r"\1' },", c)

# ══════════════════════════════════════════════════
# 4. Fix todo title strings missing closing '
# ══════════════════════════════════════════════════
c = c.replace("'完成二期信息化系统全面部署, assignee_name:", "'完成二期信息化系统全面部署', assignee_name:")
c = c.replace("'提交二季度预算调整方案, assignee_name:", "'提交二季度预算调整方案', assignee_name:")
c = c.replace("'起草跨部门协作管理办法, assignee_name:", "'起草跨部门协作管理办法', assignee_name:")

# ══════════════════════════════════════════════════  
# 5. Fix issue response missing closing '
# ══════════════════════════════════════════════════
c = c.replace("'已协调采购部加快招标流程，预计4月底前完", "'已协调采购部加快招标流程，预计4月底前完成'")

print("All structural fixes applied")
print(f"Remaining \\ufffd? corruptions: {c.count(chr(0xFFFD) + '?')}")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(c)
print("Saved")

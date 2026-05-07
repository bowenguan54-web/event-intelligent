R = '\ufffd'
ir_path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingIssueReview.vue'
md_path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingDetail.vue'

with open(ir_path, encoding='utf-8', errors='replace') as f:
    c = f.read()
print('IssueReview before:', c.count(R))
c = c.replace(f'}} {R}?\n', '}} 条\n', 1)
c = c.replace(f'审{R}?\n', '审签"\n', 1)
c = c.replace(f'归{R}?\n', '归档"\n', 1)
print('IssueReview after:', c.count(R))
for i, line in enumerate(c.split('\n'), 1):
    if R in line:
        print(f'  L{i}:', repr(line)[:100])
with open(ir_path, 'w', encoding='utf-8') as f:
    f.write(c)

with open(md_path, encoding='utf-8', errors='replace') as f:
    ct = f.read()
print('MeetingDetail FFFD:', ct.count(R))

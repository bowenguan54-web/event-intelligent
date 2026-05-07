import sys, os

files = {
    'MeetingDetail': r'E:\event-intelligent\frontend\src\views\meeting\MeetingDetail.vue',
    'RoomManagement': r'E:\event-intelligent\frontend\src\views\room\RoomManagement.vue',
    'MeetingIssueReview': r'E:\event-intelligent\frontend\src\views\meeting\MeetingIssueReview.vue',
}
out = []
for name, path in files.items():
    c = open(path, encoding='utf-8', errors='replace').read()
    lines = c.split('\n')
    out.append(f'=== {name} ===')
    for i, line in enumerate(lines, 1):
        if '\ufffd' in line:
            out.append(f'L{i}: ' + repr(line[:130]))
    out.append('')
open(r'E:\event-intelligent\check_output.txt', 'w', encoding='utf-8').write('\n'.join(out))



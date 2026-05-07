"""生成所有剩余文件的 \ufffd? 上下文，用于编写修复规则"""
import os, json

p = '\ufffd?'
files = [
    ('MeetingLive',    r'E:\event-intelligent\frontend\src\views\meeting\MeetingLive.vue'),
    ('MeetingMinutes', r'E:\event-intelligent\frontend\src\views\meeting\MeetingMinutes.vue'),
    ('MeetingCreate',  r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'),
    ('MeetingArchive', r'E:\event-intelligent\frontend\src\views\meeting\MeetingArchiveTab.vue'),
]

all_data = {}
for name, path in files:
    with open(path, encoding='utf-8', errors='replace') as f:
        content = f.read()
    entries = []
    idx = 0
    while True:
        pos = content.find(p, idx)
        if pos == -1:
            break
        before = content[max(0, pos-50):pos]
        after  = content[pos+2:min(len(content), pos+50)]
        entries.append({'pos': pos, 'before': before, 'after': after})
        idx = pos + 2
    all_data[name] = entries
    print(f'{name}: {len(entries)} occurrences of \\ufffd?')

with open(r'E:\event-intelligent\ctx_dump.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print('Saved ctx_dump.json')

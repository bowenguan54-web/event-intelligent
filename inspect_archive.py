p = r'E:\event-intelligent\frontend\src\views\meeting\MeetingArchiveTab.vue'
with open(p, 'rb') as f:
    raw_lines = f.readlines()
for ln in [19,23,40,46,60,64,81,91,93,94,166,203,207,335,340]:
    raw = raw_lines[ln-1]
    print(f'L{ln}: {repr(raw.decode("utf-8",errors="replace").rstrip())[:160]}')

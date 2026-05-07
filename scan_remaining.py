"""扫描剩余 5 个文件的所有损坏行"""
import os

files = [
    r'E:\event-intelligent\frontend\src\views\meeting\MeetingLive.vue',
    r'E:\event-intelligent\frontend\src\views\meeting\MeetingMinutes.vue',
    r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue',
    r'E:\event-intelligent\frontend\src\views\meeting\MeetingArchiveTab.vue',
    r'E:\event-intelligent\frontend\src\views\meeting\MeetingTerminal.vue',
]

out = []
for path in files:
    name = os.path.basename(path)
    with open(path, 'rb') as f:
        all_lines = f.readlines()
    total = 0
    file_out = []
    for i, raw in enumerate(all_lines):
        if b'\xe6\xa0\x3f' in raw or b'\xef\xbf\xbd' in raw:
            dec = raw.decode('utf-8', errors='replace').rstrip()
            n = dec.count('\ufffd')
            total += n
            file_out.append(f'  L{i+1}({n}): {repr(dec)[:120]}')
            # byte context for each FFFD
            for j in range(len(raw)-2):
                if raw[j:j+3] in (b'\xef\xbf\xbd', b'\xe6\xa0\x3f'):
                    kind = 'FFFD' if raw[j:j+3] == b'\xef\xbf\xbd' else 'E6A03F'
                    bef = raw[max(0,j-6):j].hex(' ')
                    aft = raw[j:j+8].hex(' ')
                    file_out.append(f'    @{j} {kind}: {bef} | {aft}')
    out.append(f'=== {name} (total {total} FFFD, {len(file_out)} lines) ===')
    out.extend(file_out)
    out.append('')

with open(r'E:\event-intelligent\scan_remaining.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('Done, saved to scan_remaining.txt')
print('Summary:')
for line in out:
    if line.startswith('==='):
        print(line)

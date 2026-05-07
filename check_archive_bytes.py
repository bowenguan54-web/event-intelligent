with open(r'E:\event-intelligent\frontend\src\views\meeting\MeetingArchiveTab.vue', 'rb') as f:
    raw_lines = f.readlines()

for ln in [19, 23, 40, 46, 60, 91, 94, 162, 166, 203, 207, 332, 335, 340]:
    raw = raw_lines[ln-1]
    positions = []
    i = 0
    while i < len(raw) - 2:
        b0, b1, b2 = raw[i], raw[i+1], raw[i+2]
        if raw[i:i+3] == b'\xef\xbf\xbd':
            positions.append((i, 'FFFD'))
        elif 0xe0 <= b0 <= 0xef and 0x80 <= b1 <= 0xbf and b2 == 0x3f:
            positions.append((i, 'E6A03F'))
        i += 1
    for pos, kind in positions:
        bef = raw[max(0,pos-10):pos].hex()
        aft = raw[pos+3:pos+12].hex()
        print(f'L{ln} @{pos} {kind}: before={bef} after={aft}')

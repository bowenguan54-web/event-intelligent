import json

d = json.load(open(r'E:\event-intelligent\ctx_dump.json', encoding='utf-8'))
items = d['MeetingArchive']
print(f'Total: {len(items)}')

for i, x in enumerate(items):
    before = x.get('before', '')[-35:]
    after = x.get('after', '')[:35]
    prefix = x.get('prefix_hex', x.get('byte_prefix_hex', ''))
    line = x.get('line', 0)
    print(f'[{i:3d}] L{line} {prefix} | ...{repr(before)} | {repr(after)}...')

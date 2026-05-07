import json

with open(r'E:\event-intelligent\ctx_dump.json', encoding='utf-8') as f:
    data = json.load(f)

items = [x for x in data if 'MeetingArchiveTab' in x.get('file', '')]
print(f'Total: {len(items)}')

for i, x in enumerate(items):
    before = x.get('before', '')[-35:]
    after = x.get('after', '')[:35]
    prefix = x.get('byte_prefix_hex', '')
    line = x.get('line', 0)
    print(f'[{i:3d}] L{line} prefix={prefix} | ...{repr(before)} | {repr(after)}...')

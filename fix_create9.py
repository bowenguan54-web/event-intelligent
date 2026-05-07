#!/usr/bin/env python3
"""Fix last 2 with exact 18-space pattern"""
p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()
before = c.count('\ufffd')
print(f'Before: {before}')

# Exact pattern from hex: FFFD 003F + 18×0020 + </button>
old = '"quick-icon">' + p + '/span>简洁议' + p + '                  </button>\n'
new = '"quick-icon">📝</span>简洁议程\n                  </button>\n'
if old in c:
    c = c.replace(old, new)
    print('Replaced!')
else:
    print('NOT FOUND')

after = c.count('\ufffd')
print(f'After: {after}')
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

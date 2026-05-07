#!/usr/bin/env python3
"""Final fix - last 3 corruptions with exact patterns"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# L683: 议\ufffd?)" →  议程)"
# hex: 8BAE FFFD 003F 0029  = 议\ufffd?)"
c = c.replace('详细议' + p + ')">', '详细议程)">')

# L687: quick-icon">\ufffd?/span>简洁议\ufffd?      </button>
# First FFFD: emoji absorbed < — so the original char before was 📝 (F0 9F 93 9D)
# Pos 45: 0063 006F 006E 0022 003E FFFD 003F 002F = con">   \ufffd?/
# So pattern: con">\ufffd?/span>
c = c.replace('"quick-icon">' + p + '/span>简洁议' + p + '      </button>\n',
              '"quick-icon">📝</span>简洁议程\n                  </button>\n')

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

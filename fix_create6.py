#!/usr/bin/env python3
"""Final fix - last 3 corruptions"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# L683: 详细议\ufffd?)" → 详细议程)"
c = c.replace('总结的详细议' + p + '")', '总结的详细议程")')

# L687: 📝 icon was restored to wrong emoji already... let's check the actual state
# repr shows: 'quick-icon">\ufffd?/span>简洁议\ufffd?   </button>'
# First FFFD: the emoji (📝 = F0 9F 93 9D = 4-byte, last byte 9D→3F WITH absorption of <)
# Second FFFD: 程 in 简洁议程 (E7 A8 8B, last byte 8B→3F WITH absorption of ' ')
c = c.replace('"quick-icon">' + p + '/span>简洁议' + p + '   </button>', 
              '"quick-icon">📝</span>简洁议程\n                  </button>')

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

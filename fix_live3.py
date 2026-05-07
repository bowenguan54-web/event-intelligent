#!/usr/bin/env python3
"""Final fix for last 5 MeetingLive corruptions"""

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingLive.vue'

with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

before = c.count('\ufffd')
print(f'Before: {before}')

# 整行标注，<strong> - the < was absorbed!
c = c.replace('，' + p + 'strong>选中文字</strong>', '，或<strong>选中文字</strong>')

# 确认') 
c = c.replace('确' + p + ')\n}', "确认')\n}")

# '...' string - maybe diff char encoding
idx = c.find("'...")
if idx >= 0:
    seg = c[idx:idx+30]
    print(f'found: {repr(seg)}')

# Try direct byte-level approach for '...'
raw = c.encode('utf-8', errors='surrogateescape')
bad = '\ufffd?'.encode('utf-8', errors='surrogateescape')
print(f'bad bytes repr: {bad!r}')

# All remaining '?' replacements that are simply single chars with no absorption
# '...' in if-else:  slice(0,60)+'...' : (where ' was absorbed)
pos = c.find("+ '..." + p)
if pos >= 0:
    print(f'Found at {pos}: {repr(c[pos:pos+30])}')
    c = c[:pos] + "+ '...'" + ' : ' + c[pos + len("+ '..." + p) + 3:]
else:
    print("Not found with standard search, trying alt")
    # The string might be using the exact bytes
    for i in range(len(c)-10):
        if c[i:i+6] == "slice(" and p in c[i:i+50]:
            print(f"Found near slice at {i}: {repr(c[i:i+50])}")
            break

# Replace all remaining for → arrow (two instances of idle comment)  
c = c.replace('// idle ' + p + ' 全新开' + p + '    recordingStatus',
              '// idle → 全新开始\n    recordingStatus')

after = c.count('\ufffd')
print(f'After: {after}')
print(f'Fixed: {before - after}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

#!/usr/bin/env python3
"""Fix last 2 exactly"""
p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()
before = c.count('\ufffd')
print(f'Before: {before}')

# L687: two FFFD
# First: "quick-icon">\ufffd?/span>  (emoji ate <)
# Second: 简洁议\ufffd?      </button>\n  (程 ate \n then 5 leading spaces of next line)
# But actual: "      </button>\n" at end shows \n just before L688's </div>
# So the line literally is: ...\ufffd?      </button>\n

old = '"quick-icon">' + p + '/span>简洁议' + p + '      </button>\n'
new = '"quick-icon">📝</span>简洁议程\n                  </button>\n'
if old in c:
    c = c.replace(old, new)
    print('Replaced!')
else:
    print('NOT FOUND, trying variant...')
    # Maybe whitespace differs - count spaces in repr
    # repr showed: 'quick-icon">\\ufffd?/span>简洁议\\ufffd?      </button>\\n'
    # Let's find what's actually there
    idx = c.find('quick-icon">' + '\ufffd')
    if idx >= 0:
        snippet = c[idx:idx+60]
        hexs = ' '.join(f'{ord(ch):04X}' for ch in snippet)
        import io
        with io.open('hex_out.txt', 'w', encoding='utf-8') as f2:
            f2.write(f'found at {idx}\n')
            f2.write(repr(snippet) + '\n')
            f2.write(hexs + '\n')
        print('Wrote hex')

after = c.count('\ufffd')
print(f'After: {after}')
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')

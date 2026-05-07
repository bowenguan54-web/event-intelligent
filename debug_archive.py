with open('frontend/src/views/archive/ArchiveSearch.vue', encoding='utf-8', errors='replace') as f:
    c = f.read()
lines = c.split('\n')
print(repr(lines[449][:100]))
print()
# Find all occurrences of \ufffd?
idx = 0
count = 0
while True:
    idx = c.find('\ufffd?', idx)
    if idx == -1 or count > 5:
        break
    print(repr(c[max(0,idx-10):idx+15]))
    idx += 1
    count += 1

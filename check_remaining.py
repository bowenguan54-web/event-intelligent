with open('frontend/src/views/archive/ArchiveSearch.vue', encoding='utf-8', errors='replace') as f:
    c = f.read()
p = '\ufffd?'
lines = c.split('\n')
count = 0
for i, line in enumerate(lines):
    if p in line:
        print(f'L{i+1}: {line.strip()[:120]}')
        count += 1
print(f'\nTotal remaining: {count} lines, {c.count(p)} occurrences')

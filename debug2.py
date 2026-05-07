with open('frontend/src/views/archive/ArchiveSearch.vue', encoding='utf-8', errors='replace') as f:
    c = f.read()
lines = c.split('\n')
line450 = lines[449]
print('Line 450 repr:', repr(line450[:150]))
print()
# Check if names are present
for name in ['王建', '李敏', '张伟', '陈秀', '刘志', '赵丽', '杨浩', '周婉']:
    idx = c.find(name)
    if idx >= 0:
        context = c[idx:idx+20]
        print(f'{name}: {repr(context)}')
    else:
        print(f'{name}: NOT FOUND in file')

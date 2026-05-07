import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = '\ufffd?'
path = r'E:\event-intelligent\frontend\src\views\meeting\MeetingLive.vue'
with open(path, encoding='utf-8', errors='replace') as f:
    c = f.read()

# Find all remaining
idx = 0
while True:
    pos = c.find(p, idx)
    if pos < 0: break
    ctx = c[max(0,pos-60):pos+80]
    print(repr(ctx))
    # show individual chars
    for i, ch in enumerate(ctx):
        if ord(ch) > 127:
            print(f'  char[{i}]: U+{ord(ch):04X} = {ch!r}')
    print()
    idx = pos + 2

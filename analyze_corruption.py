"""分析和修复 XX YY 3F 类型损坏 - 通用脚本"""
import sys, os, re

R = '\ufffd'

def analyze_file(path):
    """分析文件中的损坏模式和上下文"""
    with open(path, 'rb') as f:
        raw = f.read()
    
    # 找所有 E0-EF 开头、中间是 80-BF、末尾是 3F 的无效 3 字节序列
    findings = []
    i = 0
    while i < len(raw) - 2:
        b0 = raw[i]
        b1 = raw[i+1]
        b2 = raw[i+2]
        # 3-byte UTF-8 start: E0-EF
        # Valid continuation: 80-BF
        # Corruption: last byte is 3F (not in 80-BF)
        if 0xE0 <= b0 <= 0xEF and 0x80 <= b1 <= 0xBF and b2 == 0x3F:
            # Get surrounding context (as bytes)
            ctx_start = max(0, i - 30)
            ctx_end = min(len(raw), i + 40)
            ctx = raw[ctx_start:ctx_end]
            ctx_dec = ctx.decode('utf-8', errors='replace')
            findings.append({
                'pos': i,
                'prefix': (b0, b1),
                'hex': f'{b0:02x} {b1:02x} 3f',
                'after': raw[i+3:i+8].hex(' '),
                'context': repr(ctx_dec),
                'line': raw[max(0, ctx_start):].split(b'\n')[0].decode('utf-8', errors='replace'),
            })
        i += 1
    return findings

def get_candidate_char(b0, b1, context_before, context_after):
    """根据前缀字节和上下文推断正确字符"""
    # 已知常见字符映射：对于每个 (b0, b1) 前缀，列出可能字符
    candidates = {
        # E5 86 → U+5180-U+519F
        (0xe5, 0x86): [
            (0x85, '内'), (0x8d, '再'), (0x92, '冒'), (0x88, '冈'),
            (0x89, '冉'), (0x8b, '冋'), (0x8c, '册'), (0x8e, '冎'),
            (0x90, '冐'), (0x91, '冑'), (0x93, '冓'), (0x9e, '冞'),
        ],
        # EF BC → U+FF00-U+FF3F (全角字符)
        (0xef, 0xbc): [
            (0x81, '！'), (0x82, '＂'), (0x83, '＃'), (0x84, '＄'),
            (0x85, '％'), (0x86, '＆'), (0x87, '＇'), (0x88, '（'),
            (0x89, '）'), (0x8a, '＊'), (0x8b, '＋'), (0x8c, '，'),
            (0x8d, '－'), (0x8e, '．'), (0x8f, '／'), (0x90, '０'),
            (0x91, '１'), (0x92, '２'), (0x93, '３'), (0x9a, '：'),
            (0x9b, '；'), (0x9c, '＜'), (0x9d, '＝'), (0x9e, '＞'),
            (0x9f, '？'), (0xa0, '＠'),
        ],
        # E3 80 → U+3000-U+303F (中文标点)
        (0xe3, 0x80): [
            (0x80, '　'), (0x81, '、'), (0x82, '。'), (0x83, '〃'),
            (0x84, '〄'), (0x88, '〈'), (0x89, '〉'), (0x8a, '《'),
            (0x8b, '》'), (0x8c, '「'), (0x8d, '」'), (0x8e, '『'),
            (0x8f, '』'), (0x90, '【'), (0x91, '】'), (0x98, '〘'),
            (0x99, '〙'), (0x9a, '〚'), (0x9b, '〛'),
        ],
        # E6 80 → U+6000-U+603F
        (0xe6, 0x80): [
            (0x81, '态'), (0x82, '怂'), (0x83, '怃'), (0x84, '怄'),
            (0x85, '怅'), (0x86, '怆'), (0x87, '怇'), (0x88, '忽'),
            (0xa7, '性'), (0x9d, '忽'), (0x80, '悠'),
        ],
        # E9 A1 → U+9840-U+987F
        (0xe9, 0xa1): [
            (0x85, '项'), (0x87, '顿'), (0x88, '顿'), (0x90, '顐'),
            (0x98, '願'), (0xb9, '项'),
        ],
    }
    return candidates.get((b0, b1), [])

if __name__ == '__main__':
    files = [
        r'E:\event-intelligent\frontend\src\views\meeting\MeetingLive.vue',
        r'E:\event-intelligent\frontend\src\views\meeting\MeetingMinutes.vue',
        r'E:\event-intelligent\frontend\src\views\meeting\MeetingCreate.vue',
        r'E:\event-intelligent\frontend\src\views\meeting\MeetingArchiveTab.vue',
        r'E:\event-intelligent\frontend\src\views\meeting\MeetingTerminal.vue',
    ]
    
    with open(r'E:\event-intelligent\analysis.txt', 'w', encoding='utf-8') as out:
        for path in files:
            name = os.path.basename(path)
            findings = analyze_file(path)
            # Group by prefix
            from collections import Counter
            prefix_counts = Counter(f['prefix'] for f in findings)
            out.write(f'=== {name}: {len(findings)} corruptions ===\n')
            for prefix, cnt in sorted(prefix_counts.items(), key=lambda x: -x[1]):
                b0, b1 = prefix
                range_start = ((b0 & 0xF) << 12) | ((b1 & 0x3F) << 6)
                range_end = range_start + 0x3F
                out.write(f'  Prefix {b0:02x} {b1:02x} → U+{range_start:04X}-U+{range_end:04X}: {cnt} times\n')
            out.write('\n')
            # Show first 10 examples per prefix
            shown = {}
            for f in findings:
                p = f['prefix']
                if shown.get(p, 0) < 3:
                    out.write(f"  [{f['hex']}] pos={f['pos']} after={f['after']}\n")
                    out.write(f"    ctx: {f['context'][:100]}\n")
                    shown[p] = shown.get(p, 0) + 1
            out.write('\n')
            print(f'{name}: {len(findings)} corruptions, prefix groups: {dict(sorted(prefix_counts.items(), key=lambda x: -x[1])[:5])}')
    
    print('Analysis saved to analysis.txt')

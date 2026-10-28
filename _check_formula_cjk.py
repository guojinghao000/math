# -*- coding: utf-8 -*-
"""工具：检查 Markdown 文档中「公式定界符之间的汉字」。只读，不改文件。

用法：
    python _check_formula_cjk.py [目录]
默认检查 E:\\复习\\数学复习 下所有 高等数学-*.md。
输出每处违规的文件、行号与片段，最后给出合计。

判定依据：`文档撰写标准.md` 六.5——公式定界符之间出现任何汉字即违规
（含 `\text{中文}`）。
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else r"E:\复习\数学复习")
CJK = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")


def check(path: Path):
    hits = []
    in_display = False
    start = 0
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip() == "$$":
            if in_display:
                in_display = False
            else:
                in_display = True
                start = i
            continue
        if in_display:
            if CJK.search(line):
                hits.append((start, i, line.strip()[:70]))
            continue
        # 行内公式切片（跳过代码行与续行标记）
        if line.lstrip().startswith("```"):
            continue
        for m in re.finditer(r"\$([^$\n]+)\$", line):
            if CJK.search(m.group(1)):
                hits.append((i, i, "$" + m.group(1)[:70] + "$"))
    return hits


targets = sorted(ROOT.glob("高等数学-*.md"))
total = 0
for p in targets:
    hits = check(p)
    if hits:
        total += len(hits)
        print(f"\n=== {p.name}  命中 {len(hits)} 处 ===")
        for a, b, txt in hits:
            loc = f"L{a}" if a == b else f"L{a}-{b}"
            print(f"  {loc}: {txt}")
print(f"\n合计：扫描 {len(targets)} 个文件，公式内中文 {total} 处")

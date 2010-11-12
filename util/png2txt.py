#!/usr/bin/env python
import png
import sys

fn = sys.argv[1]
f = open(fn)
r = png.Reader(file=f)
it = r.read()
P = it[2]
#pixels = [X for X in [Y for Y in P]]
pixels = [X for X in (list(Y) for Y in P)]
txt = ''
offset = 0

fontbin = []
for ch_idx in range(128):
    ch = []
    for Y in range(8):
        row = []
        for X in range(8):
            if int(pixels[Y][X+offset]):
                row.append(0)
            else:
                row.append(1)
        ch.append(row)
    fontbin.append(ch)
    offset += 8

"""
print 
for font in range(ord('a'), ord('z')):
    fn_lines = fontbin[font]
    for line in fn_lines:
        for ch in line:
            if ch: sys.stdout.write('#')
            else: sys.stdout.write(' ')
        sys.stdout.write('\n')
    print
"""

fonts = []
for font in range(128):
    fn_lines = fontbin[font]
    rows = []
    for fn_line in fn_lines:
        p_row = []
        for col_ch in fn_line:
            if col_ch: p_row.append(' ')
            else: p_row.append('#')
        txt_row = '("%s")' % str.join('', p_row)
        rows.append(txt_row)
    #rows = [str.join(',\n', R) for R in rows]
    rows = "  (\n    %s\n  )" % str.join(',\n    ', rows)
    fonts.append(rows)
fonts = str.join(',\n', fonts)
fonts = "Font8x8 = (\n%s\n)\n" % fonts
print fonts




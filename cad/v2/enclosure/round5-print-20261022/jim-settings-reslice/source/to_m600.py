"""Replace the R5 M0 colour-stop blocks with Jim's M600 filament change (AGENTS.md, 2026-10-22).
M600 X5 Y200 Z10 goes right after ;_SET_FAN_SPEED_CHANGING_LAYER of the first layer of the new colour.
Check: the output differs from the clean slicer output only by the inserted M600 lines."""
import re, sys, difflib
src, dst = sys.argv[1], sys.argv[2]
data = open(src, newline='').read()
clean = re.sub(r'^;R5_SD_COLOUR_BEGIN (\w+)\n.*?^;R5_SD_COLOUR_END[^\n]*\n', '', data, flags=re.M | re.S)
colours = re.findall(r'^;R5_SD_COLOUR_BEGIN (\w+)$', data, re.M)
# the layer that followed each removed block is the first layer of the new colour
starts = [m.end() for m in re.finditer(r'^;R5_SD_COLOUR_END[^\n]*\n', data, re.M)]
targets = []
for s in starts:
    m = re.match(r';LAYER_CHANGE\n;Z:([\d.]+)', data[s:]); targets.append(m.group(1))
out = clean; report = []
for z, col in zip(targets, colours):
    m = re.search(r'^;LAYER_CHANGE\n;Z:' + re.escape(z) + r'\n', out, re.M)
    f = out.index(';_SET_FAN_SPEED_CHANGING_LAYER\n', m.end()) + len(';_SET_FAN_SPEED_CHANGING_LAYER\n')
    nxt = out.find(';LAYER_CHANGE', m.end())
    assert f < nxt, 'fan marker not in this layer'
    ins = ';GLAD_COLOUR_CHANGE load %s for layer Z%s\nM117 Load %s\nM600 X5 Y200 Z10\n' % (col, z, col)
    out = out[:f] + ins + out[f:]
    report.append('%s before layer Z%s' % (col, z))
assert '\nM0 ' not in out and 'R5_SD_COLOUR' not in out
added = [l for l in difflib.ndiff(clean.splitlines(), out.splitlines()) if l.startswith(('+ ', '- '))]
assert all(l.startswith('+ ') for l in added) and len(added) == 3 * len(colours), added
open(dst, 'w', newline='').write(out)
print(dst.split('/')[-1], '| M600 count', out.count('\nM600 '), '|', '; '.join(report), '| only change vs slicer output: the inserted lines')

"""Replay each SD colour pause: the printer state (XYZ, E, feed, temps, modes) must come back exactly; no homing, no motor release,
all moves inside 220x220x250, and the park move must clear everything already printed."""
import re, sys
for g in sys.argv[1:]:
    st = dict(x=0., y=0., z=0., e=0., f=0., abs=True, rel=False, noz=0., bed=0.); saved = None; maxz = 0.; out = []
    printed_top = 0.
    for line in open(g, errors='ignore'):
        line = line.rstrip('\r\n')
        if line.startswith(';R5_SD_COLOUR_BEGIN'): saved = dict(st); top_at_pause = printed_top; name = line.split()[-1]; lifts = []; continue
        if line.startswith(';R5_SD_COLOUR_END'):
            err = max(abs(st[k] - saved[k]) for k in ('x', 'y', 'z', 'e', 'f', 'noz', 'bed'))
            ok = err < 2e-5 and st['abs'] == saved['abs'] and st['rel'] == saved['rel']
            out.append('%s at Z%.2f: state restored %s (max err %.6f), park Z %.2f vs printed top %.2f' % (name, saved['z'], ok, err, max(lifts), top_at_pause))
            assert ok and max(lifts) >= top_at_pause + 4.9, out[-1]
            saved = None; continue
        raw = line.split(';')[0].strip()
        if not raw: continue
        c = raw.split()[0]; v = {a: float(b) for a, b in re.findall(r'\b([XYZEFS])([-+]?\d*\.?\d+)', raw)}
        if saved is not None:
            assert c not in ('G28', 'G29', 'M500', 'M502', 'M600', 'M601', 'M25'), c
            if c == 'M84': assert 'S' in v, 'motor release in pause'
        if c in ('G90', 'G91'): st['abs'] = c == 'G90'
        elif c == 'M82': st['rel'] = False
        elif c == 'M83': st['rel'] = True
        elif c == 'G92':
            for k in 'XYZE':
                if k in v: st[k.lower()] = v[k]
        elif c in ('M104', 'M109') and 'S' in v: st['noz'] = v['S']
        elif c in ('M140', 'M190') and 'S' in v: st['bed'] = v['S']
        elif c in ('G0', 'G1'):
            for k in 'XYZ':
                if k in v: st[k.lower()] = v[k] if st['abs'] else st[k.lower()] + v[k]
            if 'E' in v:
                st['e'] = st['e'] + v['E'] if st['rel'] else v['E']
                if v['E'] > 0 and saved is None and ('X' in v or 'Y' in v): printed_top = max(printed_top, st['z'])
            if 'F' in v: st['f'] = v['F']
            if saved is not None: lifts.append(st['z'])
            assert -.01 <= st['x'] <= 220.01 and -.01 <= st['y'] <= 220.01 and st['z'] <= 250, (st, line)
    print(g.split('/')[-1]); [print('   ' + o) for o in out]; print('   pauses checked:', len(out))

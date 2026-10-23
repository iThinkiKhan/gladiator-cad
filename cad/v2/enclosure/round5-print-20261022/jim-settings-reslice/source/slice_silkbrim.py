import sys
src = open('/home/buralien/scratch_claude/jimslice.py').read()
src = src.replace("JOBS = {\n", "JOBS = {\n '02B': ('GLAD_02_SILK_BRIM', CAD / 'round5-calibrated-28-20261022/print/plates/R5_06_Silk_Aquila_and_Trim.3mf', 'silk', True, None),\n", 1)
src = src.replace("    ps['enable_support'] = '1' if sup else '0'\n", "    ps['enable_support'] = '1' if sup else '0'\n    ps['brim_type'] = 'outer_only'; ps['brim_width'] = '5'\n", 1)
sys.argv = ['jimslice.py', '02B']
exec(compile(src, 'jimslice.py', 'exec'))

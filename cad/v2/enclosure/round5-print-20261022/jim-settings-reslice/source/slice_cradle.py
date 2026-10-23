import sys
src = open('/home/buralien/scratch_claude/jimslice.py').read()
src = src.replace("JOBS = {\n", "JOBS = {\n '01C': ('GLAD_01_WHITE_EMBLEMS_CRADLE', Path('/home/buralien/scratch_claude/emblem_cradle/GLAD_01_WHITE_EMBLEMS_V2_CRADLE_src.3mf'), 'std', False, None),\n", 1)
sys.argv = ['jimslice.py', '01C']
exec(compile(src, 'jimslice.py', 'exec'))

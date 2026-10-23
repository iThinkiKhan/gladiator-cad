import sys
src = open('/home/buralien/scratch_claude/jimslice.py').read()
src = src.replace("JOBS = {\n", "JOBS = {\n '04N': ('GLAD_04_HOOD_NORMALSUP', INC / 'Round5_MOUNT_CHECKED_20261022/plates/GLAD_04_HOOD_SD_M2_28.3mf', 'std', True, '07'),\n '05N': ('GLAD_05_PANELS_NORMALSUP', INC / 'Round5_MOUNT_CHECKED_20261022/plates/GLAD_05_PANELS_SD_M2_28.3mf', 'std', True, '08'),\n", 1)
src = src.replace("    ps['enable_support'] = '1' if sup else '0'\n", "    ps['enable_support'] = '1' if sup else '0'\n    ps['support_type'] = 'normal(auto)'; ps['support_style'] = 'snug'; ps['support_threshold_angle'] = '45'\n", 1)
assert "normal(auto)" in src
sys.argv = ['jimslice.py'] + sys.argv[1:]
exec(compile(src, 'jimslice.py', 'exec'))

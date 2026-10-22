import os, runpy, sys, traceback
def trace(frame, event, arg):
    if event == 'line' and frame.f_code.co_filename.endswith('apply_mast_front_orientation.py'):
        os.write(2, ('orientation line %d\n' % frame.f_lineno).encode())
    return trace
sys.settrace(trace)
try:
    runpy.run_path('scripts/apply_mast_front_orientation.py', run_name='__main__')
except BaseException:
    os.write(2, traceback.format_exc().encode())
    raise

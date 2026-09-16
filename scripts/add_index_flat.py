import FreeCAD as App
import Part

MASTER = '/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd'
HEAD = '/home/buralien/projects/gladiator-cad/cad/head/v01/Gladiator_Head_v01.FCStd'

master = App.openDocument(MASTER)
head = App.openDocument(HEAD)

# extract the exact removed volume from the head candidate's own feature history
before = head.getObject('MastTubePinCut').Shape
after = head.getObject('HeadMastIndexFlat').Shape
tool_shape = before.cut(after)
print('tool shape volume:', round(tool_shape.Volume, 4), 'bbox:', tool_shape.BoundBox)

for nm in ('MastIndexFlatTool', 'MastIndexFlatCut'):
    if master.getObject(nm):
        master.removeObject(nm)
master.recompute()

tool = master.addObject('Part::Feature', 'MastIndexFlatTool')
tool.Label = 'Head index flat cut tool (from head-candidate geometry)'
tool.Shape = tool_shape
tool.Visibility = False

body = master.getObject('MastTube')
old_tip = body.Tip
print('current tip:', old_tip.Name)

cut = body.newObject('PartDesign::Boolean', 'MastIndexFlatCut')
cut.Label = 'Head index flat -- anti-rotation key for the neck interface'
cut.Type = 'Cut'
cut.Group = [tool]
cut.BaseFeature = old_tip
body.Tip = cut
master.recompute()

s = body.Shape
print()
print('MastTube after: valid=%s solids=%d shells=%d vol=%.4f'
      % (s.isValid(), len(s.Solids), len(s.Shells), s.Volume))
print('(expect ~22324.66 - 75.18 = ~22249.48, matching the head candidate exactly)')

App.closeDocument(head.Name)

neck = master.getObject('Neck_Main')
fixed = master.getObject('GH44_Fixed_Head_Adapter')
c1 = round(neck.Shape.common(s).Volume, 4)
c2 = round(fixed.Shape.common(s).Volume, 4)
print()
print('Neck_Main vs new MastTube:', c1)
print('GH44_Fixed_Head_Adapter vs new MastTube:', c2)

print()
print('=== re-verify all head parts against the whole master, nothing else broke ===')
robot_names = ['ChassisDeck', 'BatteryBox', 'SideRailLeft', 'SideRailRight', 'MastBase',
               'MastTube', 'UpperDeck', 'S3Board', 'Breadboard', 'PowerShield',
               'DriverMountLeft', 'DriverMountRight', 'AntennaPost',
               'DriverBoardLeft', 'DriverBoardRight']
head_group = master.getObject('HeadCandidate_v01')


def walk(g):
    for o in g.Group:
        if o.TypeId == 'App::DocumentObjectGroup':
            yield from walk(o)
        else:
            yield o


found = False
for hobj in walk(head_group):
    if not hasattr(hobj, 'Shape'):
        continue
    for rname in robot_names:
        robj = master.getObject(rname)
        v = round(hobj.Shape.common(robj.Shape).Volume, 4)
        if v > 0.001:
            found = True
            print('  CLASH %-24s vs %-18s %s' % (hobj.Name, rname, v))
print('  none' if not found else '')

master.save()
print()
print('SAVED')
bad = [(o.Name, o.State) for o in master.Objects if o.State and 'Invalid' in str(o.State)]
print('invalid:', bad if bad else 'none')

import FreeCAD as App

MASTER = '/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd'
HEAD = '/home/buralien/projects/gladiator-cad/cad/head/v01/Gladiator_Head_v01.FCStd'

master = App.openDocument(MASTER)

# remove a prior import if this is being re-run
old = master.getObject('HeadCandidate_v01')
if old:
    def remove_group_recursive(g):
        for o in list(g.Group):
            if o.TypeId == 'App::DocumentObjectGroup':
                remove_group_recursive(o)
            else:
                master.removeObject(o.Name)
        master.removeObject(g.Name)
    remove_group_recursive(old)
    master.recompute()

head = App.openDocument(HEAD)

GROUP_NAMES = ['FixedNeck', 'PanAssembly', 'TiltAssembly', 'CarrierVariants',
               'HardwareReferences', 'CableReferences', 'FixedOption', 'FitCoupons']

part_objs = []
for g in GROUP_NAMES:
    part_objs.extend(head.getObject(g).Group)

print('Copying %d objects from the head candidate...' % len(part_objs))
copied = master.copyObject(part_objs, False)
mapping = dict(zip([o.Name for o in part_objs], copied))

top = master.addObject('App::DocumentObjectGroup', 'HeadCandidate_v01')
top.Label = 'Mast head v0.1 -- review candidate, interface NOT frozen (see docs/MAST_HEAD_DIRECTION.md)'

sub_groups = []
for gname in GROUP_NAMES:
    src = head.getObject(gname)
    ng = master.addObject('App::DocumentObjectGroup', gname)
    ng.Label = src.Label
    ng.Group = [mapping[o.Name] for o in src.Group]
    sub_groups.append(ng)
top.Group = sub_groups

master.recompute()
App.closeDocument(head.Name)
master.save()

print()
print('=== import summary ===')
bad = []
for name, obj in mapping.items():
    if not hasattr(obj, 'Shape') or obj.Shape is None:
        continue
    if not obj.Shape.isValid():
        bad.append(name)
print('invalid shapes after copy:', bad if bad else 'none')
print('objects copied:', len(mapping))

print()
print('=== clash check: head parts vs our CURRENT master geometry ===')
robot_names = ['ChassisDeck', 'BatteryBox', 'SideRailLeft', 'SideRailRight', 'MastBase',
               'MastTube', 'UpperDeck', 'S3Board', 'Breadboard', 'PowerShield',
               'DriverMountLeft', 'DriverMountRight', 'AntennaPost',
               'DriverBoardLeft', 'DriverBoardRight']
found = False
for hname, hobj in mapping.items():
    if not hasattr(hobj, 'Shape'):
        continue
    for rname in robot_names:
        robj = master.getObject(rname)
        if robj is None:
            continue
        v = round(hobj.Shape.common(robj.Shape).Volume, 4)
        if v > 0.001:
            found = True
            print('  CLASH %-24s vs %-18s %s' % (hname, rname, v))
print('  none' if not found else '')

print()
print('=== bounds sanity ===')
neck = master.getObject('Neck_Main')
print('imported Neck_Main bbox:', neck.Shape.BoundBox)
mast = master.getObject('MastTube')
print('our own MastTube bbox:  ', mast.Shape.BoundBox)
